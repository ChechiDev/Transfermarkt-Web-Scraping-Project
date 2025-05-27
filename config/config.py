from scraping.ws_engine import clear_terminal
from database.db_engine import DBUtils
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
        self.db_utils = DBUtils()
        self._collect_config()

    def _input_field(self, name, default, validate, error, values):
        """
        Solicita al usuario un campo de configuración, valida el valor y repite hasta que sea válido.
        param name: Nombre del campo.
        param default: Valor por defecto.
        param validate: Función de validación.
        param error: Mensaje de error.
        param values: Diccionario con los valores actuales.

        return: Valor validado.
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
        parm values: Diccionario con los valores actuales.
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
            # Para validar la base de datos, primero se deben tener los otros campos
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
        self.db = values["Database"]

        self._show_fields(values)
        # input(f"Conexión a la base de datos '{self.db}' establecida con éxito. Presiona Enter para continuar...")

    def _validate_database(self, db_name):
        """
        Valida si la base de datos existe en el servidor PostgreSQL.
        parm db_name: Nombre de la base de datos.

        return: True si existe, False en caso contrario.
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
        """
        return (
            f"Host: {self.host}\n"
            f"Port: {self.port}\n"
            f"User: {self.user}\n"
            f"Password: {self.password}\n"
            f"Database: {self.db}\n"
        )