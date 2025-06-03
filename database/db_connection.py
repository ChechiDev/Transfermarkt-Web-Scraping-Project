import psycopg2
import time
from psycopg2 import OperationalError
from config.config import EnvironmentConfig
from interactive.menu_engine import MenuUtils
from database.db_engine import DBManager

# Nota general:
# Esta clase centraliza la lógica de conexión y desconexión a PostgreSQL.

class DBConnection:
    """
    Clase para gestionar la conexión a una base de datos PostgreSQL.
    Permite conectar, desconectar y validar la existencia de la base de datos.
    """

    def __init__(self, env):
        """
        Inicializa la conexión con los parámetros del entorno.

        Args:
            env (EnvironmentConfig): Objeto con los datos de conexión.
        """
        self.menu_utils = MenuUtils()
        self.env = env
        self.connection = None

    def connect(self):
        """
        Establece la conexión con la base de datos PostgreSQL.
        Muestra información de conexión, valida la existencia de la base de datos y maneja errores.
        """
        self.menu_utils.main_menu()
        try:
            print("Enter the database connection details:\n")
            print(f"Host: {self.env.host}")
            print(f"Port: {self.env.port}")
            print(f"User: {self.env.user}")
            print(f"Password: {self.env.password}")
            print(f"Database: {self.env.db}")

            # Comprobamos si la base de datos existe antes de conectar
            db_utils = DBManager()
            if not db_utils.check_db_exists(
                self.env.host,
                self.env.port,
                self.env.user,
                self.env.password,
                self.env.db
            ):
                print(f"Database '{self.env.db}' does not exist. Connection aborted.")
                input("Press Enter to continue...")
                return

            print()
            self.menu_utils.separator()
            input("Press Enter to connect with the database...")
            self.connection = psycopg2.connect(
                host=self.env.host,
                port=self.env.port,
                user=self.env.user,
                password=self.env.password,
                dbname=self.env.db
            )

            self.connection.autocommit = True

            self.menu_utils.main_menu()
            print("Connecting...\n\n")
            self.menu_utils.separator()

            time.sleep(2)

            self.menu_utils.main_menu()
            print(f"Connection established successfully to database: {self.env.db}!\n\n")
            self.menu_utils.separator()
            input("Press Enter to continue...")

        except OperationalError as e:
            print(f"Database connection error: {e}")

        except Exception as e:
            print(f"Unexpected error: {e}")

    @classmethod
    def connect_postgres(cls):
        """
        Crea una instancia de DBConnection y conecta usando EnvironmentConfig.

        Return:
            tuple: (db_conn, env) con la conexión y la configuración de entorno.
        """
        env = EnvironmentConfig()
        db_conn = cls(env)
        db_conn.connect()
        return db_conn, env

    def disconnect(self):
        """
        Cierra la conexión activa con la base de datos, si existe.
        """
        if self.connection:
            self.connection.close()
            print("Connection closed.")