import random

# Lista de User-Agents
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
]

# Función para obtener headers dinámicos
def get_headers():
    """
    Genera un diccionario de cabeceras HTTP dinámicas para realizar peticiones web,
    seleccionando aleatoriamente un User-Agent de la lista.

    Return:
        dict: Diccionario con las cabeceras HTTP.
    """
    return {
        "User-Agent": random.choice(user_agents),
        "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp",
        "Referer": "https://www.transfermarkt.com/",
        "Connection": "keep-alive",
    }