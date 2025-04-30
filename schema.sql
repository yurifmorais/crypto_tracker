-- cria o schema do projeto se não existir
CREATE SCHEMA IF NOT EXISTS crypto_tracker;

-- tabela de criptomoedas
CREATE TABLE crypto_tracker.cryptocurrencies (
    id TEXT PRIMARY KEY,
    rank INTEGER NOT NULL CHECK (rank > 0),
    symbol TEXT NOT NULL,
    name TEXT NOT NULL
);

-- tabela do historico de preços
CREATE TABLE crypto_tracker.crypto_prices (
    id SERIAL PRIMARY KEY,
    crypto_id TEXT NOT NULL REFERENCES cryptocurrencies(id) ON DELETE CASCADE,
    market_cap_usd NUMERIC(38, 18),
    price_usd NUMERIC(38, 18),
    change_percent_24hr NUMERIC(18, 10),
    volume_usd_24hr NUMERIC(38, 18),
    vwap_24hr NUMERIC(38, 18),
    collected_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- indice para facilitar buscas recentes por criptomoeda
CREATE INDEX idx_crypto_prices_crypto_id_collected_at
    ON crypto_prices (crypto_id, collected_at DESC);