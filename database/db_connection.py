import psycopg2
from psycopg2 import OperationalError
import os
from dotenv import load_dotenv

# Creamos la clase que gestionará la conexión con la base de entorno:
class DatabaseConnection:
    def __init__(self):
        # Cargamos las  variables de entorno
        load_dotenv()

        self.host = os.getenv("DB_HOST")
        self.port = os.getenv("DB_PORT")
        self.user = os.getenv("DB_USER")
        self.password = os.getenv("DB_PASSWORD")
        self.database = os.getenv("DB_NAME")
        self.connection = None