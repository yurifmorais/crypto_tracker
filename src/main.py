import logging
import os
from datetime import datetime
from typing import List, Optional

import psycopg2
import requests
from dotenv import load_dotenv
from psycopg2.extras import execute_batch

# carrega as variaveis do arquivo .env
load_dotenv()

# configuracoes
API_URL = "https://rest.coincap.io/v3/assets"
API_KEY = os.getenv("API_KEY", "")
DEFAULT_LIMIT = 50

FIELDS = [
    "id", "rank", "symbol", "name", "marketCapUsd", 
    "priceUsd", "changePercent24Hr", "volumeUsd24Hr", "vwap24Hr",
]

HEADERS = {
    "Accept": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

# setup do logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def connect_to_db() -> Optional[psycopg2.extensions.connection]:
    """Estabelece uma conexao com o banco de dados PostgreSQL usando as variaveis de ambiente."""
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
        )
        logging.info("Conexao com o BD estabelecida com sucesso.")
        return conn
    except psycopg2.DatabaseError as e:
        logging.error(f"Erro ao conectar ao BD: {e}")
        return None


def to_decimal(value: Optional[str]) -> Optional[float]:
    """Converte string para float, se possivel."""
    try:
        return float(value) if value else None
    except (ValueError, TypeError):
        return None


def fetch_cryptos(limit: int = DEFAULT_LIMIT) -> List[dict]:
    """Faz requisicao a API e retorna os dados de criptomoedas."""
    try:
        response = requests.get(API_URL, headers=HEADERS, params={"limit": limit})
        response.raise_for_status()
        data = response.json().get("data", [])
               
        filtered_cryptos = []
        for crypto in data:
            filtered = {field: crypto.get(field) for field in FIELDS}
            filtered_cryptos.append(filtered)
        return filtered_cryptos
    except requests.RequestException as e:
        logging.error(f"Erro ao acessar a API: {e}")
        return []


def prepare_data(cryptos: List[dict]):
    """Prepara os dados para insercao no banco."""
    crypto_rows = []
    price_rows = []

    for crypto in cryptos:
        crypto_rows.append((
            crypto.get("id"),
            int(crypto.get("rank", 0)) if crypto.get("rank") else None,
            crypto.get("symbol"),
            crypto.get("name")
        ))

        price_rows.append((
            crypto.get("id"),
            to_decimal(crypto.get("marketCapUsd")),
            to_decimal(crypto.get("priceUsd")),
            to_decimal(crypto.get("changePercent24Hr")),
            to_decimal(crypto.get("volumeUsd24Hr")),
            to_decimal(crypto.get("vwap24Hr")),
            datetime.utcnow()
        ))

    return crypto_rows, price_rows


def insert_data(crypto_rows: List[tuple], price_rows: List[tuple]):
    """Insere os dados de criptomoedas e precos no banco."""
    insert_crypto_query = """
        INSERT INTO crypto_tracker.cryptocurrencies (id, rank, symbol, name)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (id) DO UPDATE 
        SET rank = EXCLUDED.rank,
            symbol = EXCLUDED.symbol,
            name = EXCLUDED.name;
    """

    insert_price_query = """
        INSERT INTO crypto_tracker.crypto_prices (
            crypto_id, market_cap_usd, price_usd, change_percent_24hr,
            volume_usd_24hr, vwap_24hr, collected_at
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s);
    """

    try:
        with connect_to_db() as conn:
            with conn.cursor() as cur:
                execute_batch(cur, insert_crypto_query, crypto_rows)
                execute_batch(cur, insert_price_query, price_rows)
            conn.commit()
        logging.info("Dados inseridos/atualizados com sucesso.")
    except Exception as e:
        logging.error(f"Erro ao inserir dados no banco: {e}")
        raise


def main():
    logging.info("Iniciando coleta de dados de criptomoedas.")
    cryptos = fetch_cryptos()
    if not cryptos:
        logging.warning("Nenhum dado de criptomoeda foi retornado pela API.")
        return

    crypto_rows, price_rows = prepare_data(cryptos)
    insert_data(crypto_rows, price_rows)


if __name__ == "__main__":
    main()


# Tabela cryptocurrencies: Armazena os dados principais das criptomoedas (uma entrada por moeda).
# Tabela crypto_prices: Armazena os preços históricos e outras métricas com carimbo de tempo. Assim, é possível registrar variações ao longo do tempo.


# OBS: realizar tratamento adequado de erros e exceções, como falhas de rede ou problemas de autenticação.
