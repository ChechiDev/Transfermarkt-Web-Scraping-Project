from config.config import EnvironmentConfig
from database.db_connection import DatabaseConnection
from database.db_creator import DatabaseCreator
from scraping.scrapping_engine import HttpClient
from scraping.league_scraper import LeagueScraper
from config.headers import headers

def main():
    """
    Función principal que ejecuta todo el flujo del proyecto:
    1. Configuración del entorno.
    2. Conexión a la base de datos.
    3. Ejecución del scraping.
    4. Inserción de datos en la base de datos.
    """
    try:
        # 1. Configuración del entorno
        print("🔧 Cargando configuración del entorno...")
        env = EnvironmentConfig()
        print(env)

        # 2. Conexión a la base de datos
        print("🔗 Estableciendo conexión con la base de datos...")
        db_creator = DatabaseCreator(env)
        db_creator.create_database_if_not_exists()

        db = DatabaseConnection(env)
        db.connect()

        # 3. Ejecución del scraping
        print("Iniciando scraping de ligas...")
        http_client = HttpClient(headers=headers)
        league_scraper = LeagueScraper(http_client)
        league_scraper.get_url_from_env()

        # Descargar y parsear las ligas
        leagues = league_scraper.get_leagues("url_tmkt_eur_leagues", page=1)
        if not leagues:
            print("❌ No se encontraron ligas para insertar.")
        else:
            print(f"✅ {len(leagues)} ligas encontradas. Insertando en la base de datos...")

            # 4. Inserción de datos en la base de datos
            for league in leagues:
                db.insert_data(
                    table_name=env.table,
                    data={
                        "name": league["name"],
                        "url": league["url"]
                    }
                )
            print("✅ Inserción completada.")

        # Cerrar la conexión a la base de datos
        db.disconnect()
        print("🔒 Conexión cerrada correctamente.")

    except Exception as e:
        print(f"❌ Error en el flujo principal: {e}")

if __name__ == "__main__":
    main()