from scraping.ws_httpClient import HTTPClient

def main():
    """
    Punto de entrada principal del proyecto.
    """

    # Instancia al client HTTP:
    http_client = HTTPClient()
    test_url = "https://www.transfermarkt.com/wettbewerbe/europa/wettbewerbe?ajax=yw1&plus=22&page=1"

    try:
        html = http_client.get(test_url)
        if html:
            print("HTML descargado correctamente.")
            print(f"Titulo de la página {html.title.string}")
        else:
            print(f"No se ha podido obtener el HTML de {test_url}")

    except Exception as e:
        print(f"Error: {e}")


if __name__=="__main__":
    main()