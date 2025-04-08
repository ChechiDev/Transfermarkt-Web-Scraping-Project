from dotenv import load_dotenv
import os

# Cargamos el archivo .env
load_dotenv(dotenv_path=".env")

# TEST: mostramos las variables por que está dando problemas con UTF-8:
print("DB_USER:", os.getenv("DB_USER"))
print("DB_PASSWORD:", os.getenv("DB_PASSWORD"))
print("DB_HOST:", os.getenv("DB_HOST"))
print("DB_PORT:", os.getenv("DB_PORT"))
print("DB_NAME:", os.getenv("DB_NAME"))
print("SCH_NAME:", os.getenv("SCH_NAME"))
print("TBL_NAME:", os.getenv("TBL_NAME"))