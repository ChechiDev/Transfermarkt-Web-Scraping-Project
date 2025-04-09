from dotenv import load_dotenv
import os

# Cargamos el archivo .env
load_dotenv(dotenv_path=".env")

# # TEST: mostramos las variables por que está dando problemas con UTF-8:
# print("DB_USER:", os.getenv("DB_USER"))
# print("DB_PASSWORD:", os.getenv("DB_PASSWORD"))
# print("DB_HOST:", os.getenv("DB_HOST"))
# print("DB_PORT:", os.getenv("DB_PORT"))
# print("DB_NAME:", os.getenv("DB_NAME"))
# print("SCH_NAME:", os.getenv("SCH_NAME"))
# print("TBL_NAME:", os.getenv("TBL_NAME"))

def load_scrap_names():
    scrap_names = {}
    for key, value in os.environ.items():
        if key.startswith("USER_SCRAP_LIST"):
            try:
                url_key, user_list_name = value.split(":", 1)
                scrap_names[url_key.lower()] = user_list_name
            except ValueError:
                print(f"Formato inválido en variable {key}: {value}")

    return scrap_names

if __name__ == "__main__":
    scrap_names = load_scrap_names()

    # Mostramos las variables encontradas
    if not scrap_names:
        print("⚠️ No se han encontrado opciones en las variables de entorno.")
    else:
        print("✅ Variables encontradas:")
        for k, v in scrap_names.items():
            print(f" - {k} ➔ {v}")