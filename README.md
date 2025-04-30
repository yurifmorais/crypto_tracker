# Crypto Tracker
### Yuri Fonseca de Morais

## Descricao
Esse é um projeto em Python que coleta dados atualizados das principais criptomoedas usando a API da [CoinCap](https://pro.coincap.io/api-docs), armazenando essas informações em um banco de dados PostgreSQL. Ele permite o monitoramento contínuo das variações de preço ao longo do tempo.

## Funcionalidades
- Consulta das top 50 criptomoedas da CoinCap.
- Armazenamento em banco de dados com atualizações automáticas.
- Registro histórico de preços com timestamp UTC.

## Requisitos
- Python 3.8 ou superior
- PostgreSQL
- Acesso à internet

## Instalacao das dependencias
No terminal, execute:

```bash
pip install -r requirements.txt
```

## Conexao com o Banco de dados e API
O projeto já inclui um arquivo .env com as variáveis necessárias para a configuração. Substitua os campos de conexão ao banco de dados e também a variável com a chave da API no arquivo .env.

## Criacao do banco de dados
Execute o script SQL para criar o schema e as tabelas:
```bash
psql -U postgres -d NOME_DO_BANCO -f schema.sql
```
OBS: Substitua NOME_DO_BANCO pelo nome do banco de dados que você está utilizando no projeto.

## Como Rodar o Projeto
Depois de ter configurado o ambiente e as dependências, utilize o comando abaixo: 
```bash
python src/main.py
```
OBS: Certifique-se de estar no diretório raiz do projeto antes de executar o comando acima.