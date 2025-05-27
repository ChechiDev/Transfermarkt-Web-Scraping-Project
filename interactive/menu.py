from scraping.ws_engine import clear_terminal
from interactive.menu_engine import MenuUtils, BaseMenu, run_settings_menu
from database.db_connection import DBConnection
from config.config import EnvironmentConfig
from database.db_engine import DBUtils

# Nota general:
# Este archivo define los menús principales y de configuración para la gestión de bases de datos PostgreSQL.
# El flujo principal es: LandingMenu -> connect_postgres() -> SettingsMenu.

class LandingMenu(BaseMenu):
    """
    Menú principal de la aplicación.
    Permite al usuario conectarse al servidor PostgreSQL o salir del programa.
    """
    def __init__(self):
        super().__init__()
        self.menu_utils = MenuUtils()
        self.db_utils = DBUtils()
        self.db_conn = None
        self.env = None
        self.menu_options = {
            "1": "Connect to PostgreSQL server",
            "0": "Exit"
        }
        self.menu_actions = {
            "1": self.connect_postgres,
            "0": self.exit_menu
        }

    def connect_postgres(self):
        """
        Maneja la opción de conexión al servidor PostgreSQL.
        Llama a la clase DBConnection para establecer la conexión y luego muestra el menú de configuración.
        """
        self.db_conn, self.env = DBConnection.connect_postgres()

        # Si la conexión falla, self.env puede ser None y el menú de settings no funcionará correctamente.
        settings_menu = MainMenu(self.env, self.db_utils)
        settings_menu.run_menu()


class MainMenu(BaseMenu):
    def __init__(self, env, db_utils):
        super().__init__()
        self.menu_utils = MenuUtils()
        self.env = env
        self.db_utils = db_utils
        self.menu_options = {
            # "1": "Web scraping",
            "2": "Database management",
            "0": "Back to main menu"
        }
        self.menu_actions = {
            # "1": self.create_database,
            "2": self.get_settings_menu,
            "0": self.exit_menu
        }

    def get_settings_menu(self):
        """
        Retorna una instancia del menú de configuración de la base de datos.
        """
        run_settings_menu(self.env, self.db_utils)


class WebScrapingMenu(BaseMenu):
    """
    Menú para operaciones de web scraping.
    """
    def __init__(self, env, db_utils):
        super().__init__()
        self.menu_utils = MenuUtils()
        self.env = env
        self.db_utils = db_utils
        self.menu_options = {
            "1": "Iniciar scraping de jugadores",
            "2": "Iniciar scraping de equipos",
            "0": "Volver al menú anterior"
        }
        self.menu_actions = {
            "1": self.scrape_players,
            "2": self.scrape_teams,
            "0": self.exit_menu
        }

    def scrape_players(self):
        print("Scraping de jugadores iniciado...")
        # Aquí va la lógica real de scraping
        input("Presiona Enter para volver al menú.")

    def scrape_teams(self):
        print("Scraping de equipos iniciado...")
        # Aquí va la lógica real de scraping
        input("Presiona Enter para volver al menú.")






































class SettingsMenu(BaseMenu):
    """
    Menú de configuración de la base de datos.
    Permite crear una nueva base de datos o listar todas las bases de datos disponibles.
    """
    def __init__(self, env, db_utils):
        super().__init__()
        self.menu_utils = MenuUtils()
        self.env = env
        self.db_utils = db_utils
        self.menu_options = {
            "1": "Create a new database",
            "3": "List all databases",
            "0": "Back to main menu"
        }
        self.menu_actions = {
            "1": self.create_database,
            "3": self.list_all_db,
            "0": self.exit_menu
        }

    def create_database(self):
        """
        Permite al usuario crear una nueva base de datos ingresando el nombre.
        Si no hay conexión, muestra un mensaje de advertencia.
        """
        if not self.env:
            print("You must connect to the PostgreSQL server first.")
            input("\nPress Enter to continue...")
            return

        db_name = input("Enter the name of the new database: ")
        self.db_utils.create_database(
            self.env.host,
            self.env.port,
            self.env.user,
            self.env.password,
            db_name
        )

        input("Press Enter to continue...")

    def list_all_db(self):
        """
        Lista todas las bases de datos disponibles en el servidor PostgreSQL.
        Si no hay conexión, muestra un mensaje de advertencia.
        """
        if not self.env:
            print("You must connect to the PostgreSQL server first.")
            input("\nPress Enter to continue...")
            return

        self.menu_utils.main_menu()
        self.db_utils.list_all_databases(
            self.env.host,
            self.env.port,
            self.env.user,
            self.env.password
        )

        self.menu_utils.separator()
        input("Press Enter to continue...")