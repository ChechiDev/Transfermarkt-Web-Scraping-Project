import logging

# Configuramos logging:
logging.basicConfig(
    level = logging.INFO,
    format = "%(asctime)s - %(levelname)s - %(message)s",
    datefmt = "%Y-%m-%d %H:%M:%S",
)

# Excepciones Personalizadas:
class HTTPClientError(Exception):
    """
    Excepción base para errores en el cliente HTTP.
    """
    pass

class HTTPConnectionError(HTTPClientError):
    """
    Excepción para errores de conexión.
    """
    pass

class HTTPTimeoutError(HTTPClientError):
    """
    Excepción para errores de tiempo de espera.
    """
    pass

class HTTPResponseError(HTTPClientError):
    """
    Excepción para errores en la respuesta HTTP.
    """
    def __init__(self, status_code, message = "Error en la respuesta HTTP"):
        self. status_code = status_code
        self.message = message
        super().__init__(self.message)