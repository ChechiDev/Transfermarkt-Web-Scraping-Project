# Librería que utilizaremos para conectarnos a PostgreSQL
import psycopg2
# Importamos el Exception específico para capturar errores de conexión.
from psycopg2 import OperationalError
# Importamos las variables de entorno del archivo .env
from dotenv import load_dotenv
import os

# Creamos la clase que gestionará la conexión con la base de entorno:
class DatabaseConnection:
    # Creamos el constructor que cargará las variables de entorno para la conexión.
    # Inicializará los atributos de configuración de la base de datos.
    def __init__(self):
        # Cargamos las  variables de entorno
        load_dotenv()

        self.host = os.getenv("DB_HOST")
        self.port = os.getenv("DB_PORT")
        self.user = os.getenv("DB_USER")
        self.password = os.getenv("DB_PASSWORD")
        self.database = os.getenv("DB_NAME")
        self.connection = None

    # Método para establecer conexión con la base de datos:
    def connect(self):
        try:
            # Comprobamos conexión usando psycopg2:
            self.connection = psycopg2.connect(
                host = self.host,
                port = self.port,
                user = self.user,
                password = self.password,
                dbname = self.database
            )
            print("✅ Conexión a la base de datos establecida correctamente.")

        # Capturamos cualquier error:
        except OperationalError as e:
            print(f"❌ Error de conexión con la base de datos: {e}")

    # Método para cerrar la conexión con la base de datos:
    def disconnect(self):
        if self.connection:
            # Si existe conexión activa, la cerramos:
            self.connection.close()
            print("Conexión cerrada")