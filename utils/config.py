import os

# DB connection
DB_HOST = os.environ.get('DB_HOST')
DB_NAME = os.environ.get('DB_NAME')
DB_USER = os.environ.get('DB_USER')
DB_PASS = os.environ.get('DB_PASS')
DB_PORT = os.environ.get('DB_PORT')

# Scraper settings
URL_BASE = 'https://www.sreality.cz/hledani/prodej/byty/praha'
BROWSER = 'firefox'
