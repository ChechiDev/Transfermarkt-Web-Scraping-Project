from dotenv import load_dotenv
import os

# Módulo para la carga centralizada de variables de entorno.
# Clase que gestionará las varibles de entorno de forma ordenada:

class EnvironmentConfig:
    def __init__(self):
        # Constructor que cargará las variables de entorno automáticamente al insertar la clase.
        load_dotenv(dotenv_path=".env")

        # Asignamos las varibles a atributos de instancia:
        self.user = os.getenv("DB_USER")
        self.password = os.getenv("DB_PASSWORD")
        self.host = os.getenv("DB_HOST")
        self.port = os.getenv("DB_PORT")
        self.db = os.getenv("DB_NAME")
        self.sch = os.getenv("SCH_NAME")
        self.tbl = os.getenv("TB__NAME")

    def __str__(self):
        # Devolvemos la configuración actual de las variables de entorno
        return str({
            f"User: {self.user}\n"
            f"Password: {self.password}\n"
            f"Host: {self.host}\n"
            f"Port: {self.port}\n"
            f"Database: {self.db}"
        })