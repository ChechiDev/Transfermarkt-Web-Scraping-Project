from scraping.ws_engine import clear_terminal

# Nota general:
# Este archivo contiene utilidades y validaciones para la construcción de menús interactivos en consola.

class BaseMenu:
    """
    Clase base para la creación de menús interactivos en consola.
    Proporciona métodos para mostrar el menú, ejecutar acciones y manejar opciones inválidas.
    """
    def show_menu(self):
        """
        Muestra el menú actual en consola.
        """
        clear_terminal()
        self.menu_utils.main_menu()

        for key, desc in self.menu_options.items():
            print(f"{key}. {desc}")

        print()

    def run_menu(self):
        """
        Ejecuta el ciclo principal del menú, esperando la selección del usuario y ejecutando la acción correspondiente.
        """
        while True:
            self.show_menu()
            self.menu_utils.separator()
            option = input("Select an option: ")
            action = self.menu_actions.get(option, self.invalid_option)

            if action() == "exit":
                break

    def exit_menu(self):
        """
        Sale del menú actual mostrando un mensaje de despedida.
        """
        clear_terminal()
        self.menu_utils.main_menu()
        print("Goodbye!\n\n")
        self.menu_utils.separator()

        return "exit"

    def invalid_option(self):
        """
        Muestra un mensaje de opción inválida.
        """
        self.menu_utils.invalid_option()

class MenuUtils:
    """
    Utilidades para mostrar menús y formatear texto en consola.
    Permite centrar texto, mostrar separadores y menús principales.
    """
    def __init__(self, width=100):
        """
        Inicializa la utilidad de menús con un ancho específico para formateo.

        Args:
            width (int): Ancho de la consola para centrar texto y separadores.
        """
        self.width = width

    def separator(self):
        """
        Imprime una línea separadora en consola.
        """
        print("=" * self.width)

    def center_text(self, text, fill_char=" "):
        """
        Centra el texto dado en la consola.

        Args:
            text (str): Texto a centrar.
            fill_char (str): Carácter de relleno.

        Return:
            str: Texto centrado.
        """
        return text.center(self.width, fill_char)

    def main_menu(self):
        """
        Muestra el encabezado principal del menú.
        """
        clear_terminal()
        self.separator()
        print(self.center_text("Transfermarkt Web Scraper Main Menu"))
        self.separator()

    def invalid_option(self):
        """
        Muestra un mensaje de opción inválida.
        """
        self.main_menu()
        print("Invalid option. Please try again.\n\n\n")
        self.separator()
        input("Press Enter to continue...")

class MenuValidation:
    """
    Métodos estáticos para validar los campos de entrada del usuario en los menús.
    """

    @staticmethod
    def validate_host(host):
        """
        Valida que el host sea 'localhost' o una dirección IP válida.

        Args:
            host (str): Host a validar.

        Return:
            bool: True si es válido, False en caso contrario.
        """
        import re

        if host == "localhost":
            return True
        ip_pattern = r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$"

        if re.match(ip_pattern, host):
            parts = host.split('.')
            if all(0 <= int(part) <= 255 for part in parts):
                return True

        print("Host inválido. Usa 'localhost' o una dirección IP válida.")
        return False

    @staticmethod
    def validate_port(port):
        """
        Valida que el puerto sea un número entero entre 1 y 65535 y tenga al menos 4 dígitos.

        Args:
            port (str): Puerto a validar.

        Return:
            bool: True si es válido, False en caso contrario.
        """
        try:
            port_num = int(port)
            if not (1 <= port_num <= 65535):
                print("El puerto debe estar entre 1 y 65535.")
                return False

            if len(str(port)) < 4:
                print("El puerto debe tener al menos 4 dígitos.")
                return False
            return True

        except ValueError:
            print("El puerto debe ser un número entero.")
            return False

    @staticmethod
    def validate_user(user):
        """
        Valida que el usuario no esté vacío, no contenga espacios, números ni caracteres especiales.

        Args:
            user (str): Usuario a validar.

        Return:
            bool: True si es válido, False en caso contrario.
        """
        import re
        if not user.strip():
            print("El usuario no puede estar vacío.")
            return False

        if " " in user:
            print("El usuario no puede contener espacios.")
            return False

        if not re.match(r'^[A-Za-z]+$', user):
            print("El usuario solo puede contener letras (sin números ni caracteres especiales).")
            return False

        return True

    @staticmethod
    def validate_password(password):
        """
        Valida que la contraseña tenga al menos 8 caracteres.

        Args:
            password (str): Contraseña a validar.

        Return:
            bool: True si es válida, False en caso contrario.
        """
        if len(password) < 8:
            print("La contraseña debe tener al menos 8 caracteres.")
            return False
        return True

def run_webscraping_menu(env, db_utils):
    """
    Ejecuta el menú de web scraping.

    Args:
        env: Configuración de entorno.
        db_utils: Utilidad de base de datos.
    """
    from interactive.menu import WebScrapingMenu  # importo desde aquí para evitar posibles dependencias circulares
    menu_utils = MenuUtils()
    menu_utils.main_menu()
    print("Loading regions from Transfermarkt, please wait...\n\n\n")
    menu_utils.separator()
    ws_menu = WebScrapingMenu(env, db_utils)
    ws_menu.run_menu()

def run_settings_menu(env, db_utils):
    """
    Ejecuta el menú de configuración de la base de datos.

    Args:
        env: Configuración de entorno.
        db_utils: Utilidad de base de datos.
    """
    from interactive.menu import SettingsMenu  # importo desde aquí para evitar posibles dependencias circulares
    settings_menu = SettingsMenu(env, db_utils)
    settings_menu.run_menu()