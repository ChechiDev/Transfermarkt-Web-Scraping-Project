# Librerías necesarias
import psycopg2
from psycopg2 import OperationalError
from config.cfg_environment import EnvironmentConfig

# Clase que gestiona la conexión y desconexión a una base de datos PostgreSQL.
# Utiliza la configuración almacenada en el archivo .env.
class DatabaseConnection:
    def __init__(self, env):
        # Constructor que inicializa las variables de entorno.
        self.env = EnvironmentConfig()
        self.connection = None

    def connect(self, database_override=None):
        # Establece la conexión con la base de datos.
        # Si se pasa database_override, se conecta a esa base temporalmente (por ejemplo, a 'postgres').
        try:
            db_to_use = database_override if database_override else self.env.db
            self.connection = psycopg2.connect(
                host=self.env.host,
                port=self.env.port,
                user=self.env.user,
                password=self.env.password,
                dbname=db_to_use
            )
            print(f"✅ Conexión establecida con la base de datos: {db_to_use}")

        except OperationalError as e:
            print(f"❌ Error de conexión con la base de datos: {e}")

    def disconnect(self):
        # Cierra la conexión con la base de datos.
        if self.connection:
            self.connection.close()
            print("✅ Conexión cerrada.")
