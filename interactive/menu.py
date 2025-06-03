from interactive.menu_engine import MenuUtils, BaseMenu, run_settings_menu, run_webscraping_menu
from database.db_connection import DBConnection
from scraping.ws_urls import TransfermarktURLManager
from scraping.ws_httpClient import HTTPClient
from scraping.ws_engine import ScrapingEngine
from database.db_engine import DBManager

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
        self.db_utils = DBManager()
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

        settings_menu = MainMenu(self.env, self.db_utils)
        settings_menu.run_menu()

class MainMenu(BaseMenu):
    """
    Menú principal tras la conexión, permite elegir entre scraping o gestión de base de datos.
    """
    def __init__(self, env, db_utils):
        super().__init__()
        self.menu_utils = MenuUtils()
        self.env = env
        self.db_utils = db_utils
        self.menu_options = {
            "1": "Web scraping",
            "2": "Database management",
            "0": "Back to main menu"
        }
        self.menu_actions = {
            "1": self.run_webscraping_menu,
            "2": self.get_settings_menu,
            "0": self.exit_menu
        }

    def run_webscraping_menu(self):
        """
        Llama a la función recursiva para ejecutar el menú de web scraping.
        """
        run_webscraping_menu(self.env, self.db_utils)

    def get_settings_menu(self):
        """
        Retorna una instancia del menú de configuración de la base de datos.
        """
        run_settings_menu(self.env, self.db_utils)

class WebScrapingMenu(BaseMenu):
    """
    Menu to select scraping region on Transfermarkt.
    Options are generated dynamically from TransfermarktURLManager.
    """
    region_replace = {
        "EUR1": "Europe",
        "AME1": "America",
        "ASI1": "Asia",
        "AFR1": "Africa",
    }

    def __init__(self, env, db_utils):
        super().__init__()
        self.menu_utils = MenuUtils()
        self.env = env
        self.db_utils = db_utils
        self.http_client = HTTPClient()
        self.scraping_engine = ScrapingEngine(self.http_client)
        self.url_manager = TransfermarktURLManager(self.http_client, self.scraping_engine)
        self.region_keys = list(self.url_manager.regions.keys())
        self.selected_regions = []

        self.menu_options = {
            str(i + 1): self.region_replace.get(region, region)
            for i, region in enumerate(self.region_keys)
        }

        self.menu_options[str(len(self.region_keys) + 1)] = "All regions\n"
        self.menu_options["0"] = "Back to previous menu"

    def run_menu(self):
        """
        Ejecuta el menú de selección de regiones para scraping, permitiendo selección múltiple o individual.
        """

        while True:
            self.menu_utils.main_menu()
            print("Please select one or more regions to scrape data from Transfermarkt (e.g., 1,3):\n")

            for key, value in self.menu_options.items():
                print(f"{key}. {value}")

            self.menu_utils.separator()
            option = input("Select an option: ").strip()

            # Selección múltiple
            if "," in option:
                indices = [o.strip() for o in option.split(",")]
                selected_regions = []

                for idx in indices:
                    if idx.isdigit() and 1 <= int(idx) <= len(self.region_keys):
                        selected_regions.append(self.region_keys[int(idx) - 1])

                if selected_regions:
                    self.selected_regions = selected_regions

                    sub_menu = WebScrapingSubMenu(self.selected_regions, self.region_replace, self.db_utils, self.env)
                    sub_menu.run_menu()
                    break
                else:
                    self.invalid_option()

            # Selección de una sola opción
            elif option.isdigit():
                idx = int(option)
                if idx == 0:
                    break

                elif 1 <= idx <= len(self.region_keys):
                    self.selected_regions = [self.region_keys[idx - 1]]

                    sub_menu = WebScrapingSubMenu(self.selected_regions, self.region_replace, self.db_utils, self.env)
                    sub_menu.run_menu()
                    break

                elif idx == len(self.region_keys) + 1:
                    self.selected_regions = self.region_keys

                    sub_menu = WebScrapingSubMenu(self.selected_regions, self.region_replace, self.db_utils, self.env)
                    sub_menu.run_menu()
                    break

                else:
                    self.invalid_option()

            else:
                self.invalid_option()

    def create_region_schemas(self):
        """
        Crea los schemas en la base de datos para las regiones seleccionadas.
        """
        if not self.env:
            print("You must connect to the PostgreSQL server first.")
            input("\nPress Enter to continue...")
            return

        for region in self.selected_regions:
            schema_name = f"sch_region_{self.region_replace.get(region, region)}"
            self.db_utils.create_schema(
                self.env.host,
                self.env.port,
                self.env.user,
                self.env.password,
                self.env.db_name,
                schema_name
            )
            print(f"Schema '{schema_name}' created successfully.")

        input("Press Enter to continue...")

class WebScrapingSubMenu(BaseMenu):
    """
    Submenú para mostrar y operar sobre las regiones seleccionadas.
    """
    def __init__(self, selected_regions, region_replace, db_utils, env):
        super().__init__()
        self.menu_utils = MenuUtils()
        self.selected_regions = selected_regions
        self.region_replace = region_replace
        self.db_utils = db_utils
        self.env = env

        self.menu_options = {
            "1": "Start scraping",
            "0": "Back to previous menu"
        }
        self.menu_actions = {
            "1": self.start_scraping,
            "0": self.exit_menu
        }

    def run_menu(self):
        """
        Ejecuta el submenú para las regiones seleccionadas, permitiendo iniciar el scraping.
        """
        while True:
            self.menu_utils.main_menu()
            print("Regions selected for scraping:\n")

            for region in self.selected_regions:
                print(f"- {self.region_replace.get(region, region)}")

            print()
            self.menu_utils.separator()
            for key, value in self.menu_options.items():
                print(f"{key}. {value}")

            print()
            self.menu_utils.separator()
            option = input("Select an option: ").strip()
            action = self.menu_actions.get(option)

            if action:
                result = action()
                if result == "exit":
                    break

            else:
                self.invalid_option()

    def start_scraping(self):
        """
        Inicia el scraping para las regiones seleccionadas, creando los esquemas y tablas necesarios.
        """
        for region in self.selected_regions:
            schema_name = f"sch_region_{self.region_replace.get(region, region).lower()}"
            # Creamos el sch si no existe
            self.db_utils.create_schema(
                self.env.host,
                self.env.port,
                self.env.user,
                self.env.password,
                self.env.db_name,
                schema_name
            )

            # tbl_region
            self.db_utils.create_table_region(
                self.env.host,
                self.env.port,
                self.env.user,
                self.env.password,
                self.env.db_name,
                schema_name
            )

            # tbl_country
            self.db_utils.create_table_country(
                self.env.host,
                self.env.port,
                self.env.user,
                self.env.password,
                self.env.db_name,
                schema_name
            )
        print("Starting scraping for the following regions:")

        for region in self.selected_regions:
            region_name = self.region_replace.get(region, region)
            print(f"- {region_name}")
            # Aquí iría la lógica real de scraping por región.....Work in progress

        input("Scraping finished. Press Enter to return to the menu...")

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