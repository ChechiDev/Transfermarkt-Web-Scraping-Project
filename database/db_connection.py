# Librería que utilizaremos para conectarnos a PostgreSQL
import psycopg2
# Importamos el Exception específico para capturar errores de conexión.
from psycopg2 import sql, OperationalError
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
        self.database = input("Introduce el nombre da la base de datos: ")
        self.connection = None

        # Verificamos y creamos la base de datos si no existe en PostgreSQL
        self.check_and_create_db()

    # Creamos un método verificar si existe o crear la base de datos en PostgreSQL:
    def check_and_create_db(self):
        # Nos conectamos:
        conn = psycopg2.connect(
            host = self.host,
            port = self.port,
            user = self.user,
            password = self.password,
            dbname = 'postgres'
        )
        # Con autocommit le decimos a PostgreSQL que ejecute la consulta sin necesidad de hacer commit()
        conn.autocommit = True
        cursor = conn.cursor()

        # consultamos y comprobamos si la base de datos existe
        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s;", (self.database,)
            )
        exists = cursor.fetchone()

        if not exists:
            # Si no existe la base de datos, la creamos:
            cursor.execute(
                sql.SQL("CREATE DATABASE {}").format(
                    sql.Identifier(self.database)
                )
            )
            print(f"✅ Base de datos '{self.database}' creada correctamente")

            # Actualizamos el archivo .env con el nombre de la base de datos:
            self.update_env_file()

        else:
            print(f"⚠️ La base de datos {self.database}, ya existe.")

        cursor.close()
        conn.close()

    def update_env_file(self):
        # Actuializamos el archivo .env con el nombre de las base de datos introducido por el usuario:
        lines = []

        # Leemos le contenido de .env:
        with open(".env", "r") as file:
            lines = file.readlines()

        # Busscamos si  ya existe "DB_NAME" y lo actualizamos:
        with open(".env", "w") as file:
            found = False

            for line in lines:
                if line.startswith("DB_NAME"):
                    file.write(f"DB_NAME = {self.database}\n")
                    found = True

                else:
                    # Si existe dejamos la linea tal como está
                    file.write(line)

            if not found:
                # Si no existe lo agregamos:
                file.write(f"\nDB_NAME = {self.database}\n")

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
            print("✅ Conexión cerrada")