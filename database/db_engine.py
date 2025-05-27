import psycopg2

# Nota general:
# Esta clase centraliza operaciones comunes sobre PostgreSQL, facilitando la gestión de bases de datos

class DBUtils:
    """
    Clase utilitaria para operaciones comunes sobre bases de datos PostgreSQL.
    Permite verificar la existencia de una base de datos, listar todas las bases y crear nuevas bases de datos.
    """

    @staticmethod
    def get_postgres_connection(host, port, user, password, dbname='postgres'):
        """
        Establece y retorna una conexión a PostgreSQL.
        param host: Host del servidor.
        param port: Puerto de conexión.
        param user: Usuario de la base de datos.
        param password: Contraseña del usuario.
        param dbname: Nombre de la base de datos (por defecto 'postgres').
        return: Objeto de conexión psycopg2.
        """
        return psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            dbname=dbname
        )

    def check_db_exists(self, host, port, user, password, db_name):
        """
        Verifica si una base de datos existe en el servidor PostgreSQL.
        param host: Host del servidor.
        param port: Puerto de conexión.
        param user: Usuario de la base de datos.
        param password: Contraseña del usuario.
        param db_name: Nombre de la base de datos a verificar.
        return: True si existe, False en caso contrario.
        """
        try:
            with self.get_postgres_connection(host, port, user, password) as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s;", (db_name,))
                    return cur.fetchone() is not None

        except Exception as e:
            print(f"Error checking database existence: {e}")
            return False

    def list_all_databases(self, host, port, user, password):
        """
        Lista todas las bases de datos disponibles en el servidor PostgreSQL (excluyendo templates).
        param host: Host del servidor.
        param port: Puerto de conexión.
        param user: Usuario de la base de datos.
        param password: Contraseña del usuario.
        """
        try:
            with self.get_postgres_connection(host, port, user, password) as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT datname FROM pg_database WHERE datistemplate = false;")
                    databases = cur.fetchall()
                    print("Available databases:")
                    for db in databases:
                        print(f"- {db[0]}")

        except Exception as e:
            print(f"Error listing databases: {e}")

    def create_database(self, host, port, user, password, db_name):
        """
        Crea una nueva base de datos en el servidor PostgreSQL si no existe previamente.
        param host: Host del servidor.
        param port: Puerto de conexión.
        param user: Usuario de la base de datos.
        param password: Contraseña del usuario.
        param db_name: Nombre de la nueva base de datos.
        return: True si se crea correctamente, False si ya existe o hay error.
        """
        if self.check_db_exists(host, port, user, password, db_name):
            print(f"The database '{db_name}' already exists.")
            return False

        try:
            conn = self.get_postgres_connection(host, port, user, password)
            conn.autocommit = True  # ¡ACTIVA autocommit antes de abrir el cursor!
            with conn.cursor() as cur:
                cur.execute(f"CREATE DATABASE {db_name};")
                print(f"Database '{db_name}' created successfully.")
                conn.close()
                return True

        except Exception as e:
            print(f"Error creating database: {e}")
            return False