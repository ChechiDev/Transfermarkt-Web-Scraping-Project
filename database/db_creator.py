from .db_connection import DatabaseConnection
import psycopg2
from psycopg2 import sql, OperationalError
from dotenv import load_dotenv
import os

# Clase que se encargará de crear sobre la base de datos
class DatabaseCreator:
    # Constructor que carga las variables de entorno (.env):
    def __init__(self, env):
        self.env = env
        self.db_conn = DatabaseConnection(self.env)

        # Conexión temporal a 'postgres' para poder crear una nueva base
        self.db_conn.connect(database_override="postgres")
        self.connection = self.db_conn.connection

        self.db = input("Introduce el nombre de la nueva base de datos: ")
        self.sch = input("Introduce el nombre del nuevo schema: ")

        # Procesamos creación
        self.check_and_create_db()
        self.check_and_create_sch()

        # Cerramos conexión temporal
        self.db_conn.disconnect()

        # Actualizamos .env
        self.update_env_file()

    # Creamos un método verificar si existe o crear la base de datos en PostgreSQL:
    def check_and_create_db(self):
        try:
            cursor = self.connection.cursor()

            # Verificamos existencia
            cursor.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s;",
                (self.db,)
            )
            exists = cursor.fetchone()

            if not exists:
                cursor.execute(
                    sql.SQL("CREATE DATABASE {}").format(
                        sql.Identifier(self.db)
                    )
                )
                print(f"✅ Base de datos '{self.db}' creada correctamente.")
            else:
                print(f"⚠️ La base de datos '{self.db}' ya existe.")

            cursor.close()

        except Exception as e:
            print(f"❌ Error verificando/creando la base de datos: {e}")

    def check_and_create_sch(self):
        try:
            # Nos conectamos a la nueva base de datos creada
            self.db_conn.connect(database_override=self.db)
            self.connection = self.db_conn.connection

            cursor = self.connection.cursor()

            # Verificar existencia del schema
            cursor.execute(
                "SELECT schema_name FROM information_schema.schemata WHERE schema_name = %s;",
                (self.sch,)
            )
            exists = cursor.fetchone()

            if not exists:
                cursor.execute(
                    sql.SQL("CREATE SCHEMA {}").format(
                        sql.Identifier(self.sch)
                    )
                )
                self.connection.commit()
                print(f"✅ Schema '{self.sch}' creado correctamente.")
            else:
                print(f"⚠️ El schema '{self.sch}' ya existe.")

            cursor.close()

        except Exception as e:
            print(f"❌ Error verificando/creando el schema: {e}")

    def update_env_file(self):
        # Actuializamos el archivo .env con el nombre de las base de datos introducido por el usuario:
        try:
            with open(".env", "r", encoding='utf-8') as file:
                lines = file.readlines()

            found_db = False
            found_schema = False

            with open(".env", "w", encoding="utf-8") as file:
                for line in lines:
                    if line.startswith("DB_NAME"):
                        file.write(f"DB_NAME={self.db}\n")
                        found_db = True

                    elif line.startswith("SCH_NAME"):
                        file.write(f"SCH_NAME={self.sch}\n")
                        found_schema = True

                    else:
                        file.write(line)

                if not found_db:
                    file.write(f"\nDB_NAME={self.sch}\n")
                if not found_schema:
                    file.write(f"SCH_NAME={self.sch}\n")

            print("✅ Archivo .env actualizado correctamente.")

        except Exception as e:
            print(f"❌ Error actualizando el archivo .env: {e}")