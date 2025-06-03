import psycopg2

class DBManager:
    """
    Clase utilitaria para operaciones comunes sobre bases de datos PostgreSQL.
    Permite verificar la existencia de una base de datos, listar todas las bases y crear nuevas bases de datos.
    """

    @staticmethod
    def get_postgres_connection(host, port, user, password, dbname='postgres'):
        """
        Establece y retorna una conexión a PostgreSQL.

        Args:
            host (str): Host del servidor.
            port (str): Puerto de conexión.
            user (str): Usuario de la base de datos.
            password (str): Contraseña del usuario.
            dbname (str): Nombre de la base de datos (por defecto 'postgres').

        Return:
            connection: Objeto de conexión psycopg2.
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

        Args:
            host (str): Host del servidor.
            port (str): Puerto de conexión.
            user (str): Usuario de la base de datos.
            password (str): Contraseña del usuario.
            db_name (str): Nombre de la base de datos a verificar.

        Return:
            bool: True si existe, False en caso contrario.
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

        Args:
            host (str): Host del servidor.
            port (str): Puerto de conexión.
            user (str): Usuario de la base de datos.
            password (str): Contraseña del usuario.
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

        Args:
            host (str): Host del servidor.
            port (str): Puerto de conexión.
            user (str): Usuario de la base de datos.
            password (str): Contraseña del usuario.
            db_name (str): Nombre de la nueva base de datos.

        Return:
            bool: True si se crea correctamente, False si ya existe o hay error.
        """
        if self.check_db_exists(host, port, user, password, db_name):
            print(f"The database '{db_name}' already exists.")

            return False

        try:
            conn = self.get_postgres_connection(host, port, user, password)
            conn.autocommit = True

            with conn.cursor() as cur:
                cur.execute(f"CREATE DATABASE {db_name};")
                print(f"Database '{db_name}' created successfully.")
                conn.close()

                return True

        except Exception as e:
            print(f"Error creating database: {e}")

            return False

    def create_schema(self, host, port, user, password, db_name, schema_name):
        """
        Crea un esquema en la base de datos especificada si no existe.

        Args:
            host (str): Host del servidor.
            port (str): Puerto de conexión.
            user (str): Usuario de la base de datos.
            password (str): Contraseña del usuario.
            db_name (str): Nombre de la base de datos.
            schema_name (str): Nombre del esquema a crear.
        """
        try:
            conn = psycopg2.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                dbname=db_name
            )
            conn.autocommit = True
            cur = conn.cursor()
            cur.execute(f'CREATE SCHEMA IF NOT EXISTS "{schema_name}";')
            print(f"Schema '{schema_name}' created or already exists.")
            cur.close()
            conn.close()

        except Exception as e:
            print(f"Error creating schema '{schema_name}': {e}")

    def create_table_region(self, host, port, user, password, db_name, schema_name):
        try:
            conn = self.get_postgres_connection(host, port, user, password, db_name)
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    CREATE TABLE IF NOT EXISTS "{schema_name}"."tbl_region_info"(
                        id_region VARCHAR(4) PRIMARY KEY,
                        region_name VARCHAR(100),
                        url_region TEXT
                    );
                    """
                )
                conn.commit()
                print(f"Tabla 'region' creada correctamente en el schema '{schema_name}'.")

            conn.close()

        except Exception as e:
            print(f"Error creando la tabla 'region': {e}")

    def create_table_country(self, host, port, user, password, db_name, schema_name):
        """
        Crea la tabla 'tbl_region_info' en el esquema especificado si no existe.

        Args:
            host (str): Host del servidor.
            port (str): Puerto de conexión.
            user (str): Usuario de la base de datos.
            password (str): Contraseña del usuario.
            db_name (str): Nombre de la base de datos.
            schema_name (str): Nombre del esquema donde crear la tabla.
        """
        try:
            conn = self.get_postgres_connection(host, port, user, password, db_name)
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    CREATE TABLE IF NOT EXISTS "{schema_name}"."tbl_countries"(
                        id_country VARCHAR(10) PRIMARY KEY,
                        fk_region VARCHAR(4),
                        country_name VARCHAR(100),
                        country_flag TEXT,

                        CONSTRAINT fk_region
                            FOREIGN KEY(fk_region)
                            REFERENCES "{schema_name}"."tbl_region_info"(id_region)
                            ON UPDATE CASCADE
                            ON DELETE SET NULL
                    );
                    """
                )
                conn.commit()
                print(f"Tabla 'countries' creada correctamente en el schema '{schema_name}'.")

            conn.close()

        except Exception as e:
            print(f"Error creando la tabla 'countries': {e}")