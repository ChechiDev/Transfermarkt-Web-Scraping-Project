from scraping.ws_engine import clear_terminal
from database.db_engine import DBManager
from interactive.menu_engine import MenuUtils, MenuValidation

# Nota general:
# Esta clase centraliza la recolección y validación de los datos de conexión a PostgreSQL.

class EnvironmentConfig:
    """
    Clase para gestionar y recolectar la configuración de entorno necesaria para conectarse a una base de datos PostgreSQL.
    Solicita al usuario los datos de conexión y valida cada campo.
    """

    def __init__(self):
        """
        Inicializa la configuración de entorno y solicita los datos de conexión al usuario.
        """
        self.menu_utils = MenuUtils()
        self.db_utils = DBManager()
        self._collect_config()

    def _input_field(self, name, default, validate, error, values):
        """
        Solicita al usuario un campo de configuración, valida el valor y repite hasta que sea válido.

        Args:
            name (str): Nombre del campo.
            default (str): Valor por defecto.
            validate (Callable): Función de validación.
            error (str): Mensaje de error.
            values (dict): Diccionario con los valores actuales.

        Return:
            str: Valor validado.
        """
        while True:
            self._show_fields(values)
            value = input(f"{name} (default: {default}): ") or default

            if validate(value):
                return value
            print(error)
            input("Presiona Enter para continuar...")

    def _show_fields(self, values):
        """
        Muestra en pantalla los campos actuales de configuración.

        Args:
            values (dict): Diccionario con los valores actuales.
        """

        clear_terminal()
        self.menu_utils.main_menu()
        print("Enter the database connection details:\n")

        for n in ["Host", "Port", "User", "Password", "Database"]:
            print(f"{n}: {values.get(n, '')}")

        print()
        self.menu_utils.separator()

    def _collect_config(self):
        """
        Recolecta todos los datos de configuración necesarios para la conexión a la base de datos.
        """
        fields = [
            ("Host", "localhost", MenuValidation.validate_host, ""),
            ("Port", "5432", MenuValidation.validate_port, ""),
            ("User", "postgres", MenuValidation.validate_user, ""),
            ("Password", "postgres", MenuValidation.validate_password, ""),
            ("Database", "postgres", self._validate_database, ""),
        ]

        values = {}
        for name, default, validate, error in fields:
            # Para validar la base de datos, primero se deben tener los otros campos.
            if name == "Database":
                self.host = values["Host"]
                self.port = values["Port"]
                self.user = values["User"]
                self.password = values["Password"]

            values[name] = self._input_field(name, default, validate, error, values)

        self.host = values["Host"]
        self.port = values["Port"]
        self.user = values["User"]
        self.password = values["Password"]
        self.db_name = values["Database"]

        self._show_fields(values)

    def _validate_database(self, db_name):
        """
        Valida si la base de datos existe en el servidor PostgreSQL.

        Args:
            db_name (str): Nombre de la base de datos.

        Return:
            bool: True si existe, False en caso contrario.
        """
        return self.db_utils.check_db_exists(
            self.host,
            self.port,
            self.user,
            self.password,
            db_name
        )

    def __str__(self):
        """
        Devuelve una representación en texto plano de la configuración de entorno.

        Return:
            str: Representación de la configuración.
        """
        return (
            f"Host: {self.host}\n"
            f"Port: {self.port}\n"
            f"User: {self.user}\n"
            f"Password: {self.password}\n"
            f"Database: {self.db}\n"
        )