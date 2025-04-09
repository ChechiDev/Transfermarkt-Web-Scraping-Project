from scraping.scrapping_engine import ScrapeBase, HttpClient
from config.headers import headers
from IPython.display import clear_output
from dotenv import load_dotenv
import os
import time

# Carga un diccionario de nombres para el listado de opciones que escogerá el usuario.
def load_scrap_names(env_vars):
    scrap_names = {}
    for key, value in env_vars.items():
        if key.startswith("USER_SCRAP_LIST_NAME"):
            try:
                url_key, user_list_name = value.split(":", 1)
                scrap_names[url_key.lower()] = user_list_name
            except ValueError:
                print(f"Formato inválido en variable {key}: {value}")
    return scrap_names

# Busca el número total de páginas en el HTML descargado.
def get_total_pages(html):
    try:
        pagination_links = html.select('a[href*="page="]')
        page_numbers = [int(link.get_text(strip=True)) for link in pagination_links if link.get_text(strip=True).isdigit()]
        return max(page_numbers) if page_numbers else 1
    except Exception as e:
        print(f"❌ Error al determinar el número total de páginas: {e}")
        return 1

# Función principal que ejecuta todo el flujo de scraping.
def run_scraper():
    load_dotenv()

    # Crear instancia del cliente HTTP y scraper
    http_client = HttpClient(headers=headers)
    scraper = ScrapeBase(http_client)
    scraper.get_url_from_env()

    # Generar el diccionario de nombres de scraping
    scrap_names = load_scrap_names(os.environ)

    if not scrap_names:
        print("No se encontraron opciones de scraping en las variables de entorno.")
        return

    print("Listado de URL disponibles para hacer scrapping:")
    for i, (url_key, user_list_name) in enumerate(scrap_names.items(), start=1):
        print(f"{i}. {user_list_name}")

    try:
        option = int(input("\nIntroduce el número de la URL que quieres scrapear: ")) - 1
        if option < 0 or option >= len(scrap_names):
            print("❌ Opción no válida")
            return

        selected_url_key = list(scrap_names.keys())[option]
        print(f"\n➔ Has seleccionado: {scrap_names[selected_url_key]}")

        # Descargar la primera página para determinar el número total de páginas
        # print("Descargando la primera página para determinar el número total de páginas...")
        html = scraper.scrape(selected_url_key, page=1)
        if not html:
            print("❌ Error descargando la página 1.")
            return

        total_pages = get_total_pages(html)
        print(f"✅ Número total de páginas: {total_pages}")

        for page in range(1, total_pages + 1):
            # Limpiar el output antes de procesar cada página
            clear_output(wait=True)
            print(f"Descargando página {page} de {total_pages}...")

            html = scraper.scrape(selected_url_key, page=page)
            if not html:
                print(f"❌ Error descargando la página {page}.")
                continue

            # Aquí puedes agregar la lógica para procesar y almacenar los datos de cada página
            print(f"✅ Página {page} descargada correctamente.")

            # Esperar 2 segundos entre solicitudes
            time.sleep(2)

        print("✅ Scraping completado.")
    except Exception as e:
        print(f"❌ Error en el proceso: {e}")