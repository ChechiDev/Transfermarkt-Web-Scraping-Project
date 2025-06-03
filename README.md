![Work in Progress](https://img.shields.io/badge/Status-Work%20in%20Progress-yellow)
# Transfermarkt Web Scraping Project

## Propósito del Proyecto

Este proyecto tiene un propósito **totalmente educacional y de aprendizaje**, sin ningún fin lucrativo. Su objetivo principal es desarrollar habilidades en **web scraping**, **procesamiento de datos**, **organización de proyectos** y **gestión de datos estructurados** utilizando Python.

El objetivo es realizar un scraping exhaustivo de la página [Transfermarkt](https://www.transfermarkt.es/), extrayendo datos estructurados de regiones, ligas, equipos y jugadores. El foco está en la arquitectura modular, la reutilización de código y la robustez ante cambios en la estructura HTML.

---

## Estado Actual del Proyecto

- **Scraping**: En desarrollo activo. Toda la lógica se encuentra en la carpeta `scraping`.
- **Base de datos**: En stand-by. Los datos extraídos se almacenan temporalmente en la carpeta `Data Output` en formato JSON.
- **Interactividad**: En desarrollo futuro. Se planea añadir un módulo interactivo para explorar los datos extraídos.

---

## Flujo de Trabajo Actual

1. **Inicialización**:
   - Se configuran los componentes principales: cliente HTTP (`HTTPClient`), motor de scraping (`ScrapingEngine`), gestores de URL, regiones, ligas, equipos y jugadores.
2. **Extracción de datos**:
   - Se recorren las regiones configuradas, extrayendo sus ligas, equipos y jugadores asociados.
   - El flujo es jerárquico: Región → Ligas → Equipos → Jugadores.
3. **Procesamiento y cálculo de estadísticas**:
   - Se calculan estadísticas agregadas a nivel de región, liga y equipo.
4. **Almacenamiento temporal**:
   - Los datos se guardan en la carpeta `Data Output` en formato JSON, listos para análisis o integración futura con una base de datos.
5. **(Próximamente) Interactividad**:
   - Se prevé un módulo para explorar y consultar los datos extraídos de forma interactiva.

---

## Estructura del Proyecto

```bash
├── config/
│   ├── __init__.py
│   ├── config.py           # Configuración y validación de entorno para conexión a PostgreSQL
│   ├── exceptions.py       # Excepciones personalizadas para configuración
│   ├── headers.py          # Headers HTTP para scraping
│   └── run_scraper.py      # (Opcional) Script para lanzar el scraper desde config
├── database/
│   ├── __init__.py
│   ├── db_connection.py    # Lógica de conexión a la base de datos
│   ├── db_engine.py        # Funciones y clases para gestión de la base de datos
│   └── db_creator.py       # Creación y validación de la base de datos
├── interactive/
│   ├── __init__.py
│   ├── menu.py             # Menús interactivos para CLI
│   └── menu_engine.py      # Utilidades y validaciones de menús
├── scraping/
│   ├── ws_engine.py        # Motor base para scraping y utilidades HTML
│   ├── ws_leagues.py       # Gestión y extracción de ligas
│   ├── ws_teams.py         # Gestión y extracción de equipos
│   ├── ws_players.py       # Gestión y extracción de jugadores
│   ├── ws_dataManager.py   # Gestión y serialización de datos extraídos
│   ├── ws_entities.py      # Definición de entidades y modelos de datos
│   ├── ws_urls.py          # Gestión dinámica de URLs y paginación
│   ├── ws_region.py        # Gestión y procesamiento de regiones
│   └── ws_httpClient.py    # Cliente HTTP robusto con reintentos y validación
├── Data Output/
│   └── all_regions_with_leagues_and_teams.json
├── main.py                 # Script principal para ejecutar el scraping
├── transfermarkt_project.ipynb # Notebook de ejemplo y pruebas
├── requirements.txt        # Dependencias del proyecto
├── README.md               # Documentación del proyecto
├── .env                    # Variables de entorno (no versionado)
├── .gitignore
└── LICENSE
```

---

## Lógica y Arquitectura Modular

### 1. Módulo `config/`
- **config.py**: Clase `EnvironmentConfig` para recolectar y validar datos de conexión a PostgreSQL.
  - Métodos: `_input_field`, `_show_fields`, `_collect_config`, `_validate_database`, `__str__`
- **exceptions.py**: Excepciones personalizadas para errores de configuración.
- **headers.py**: Headers HTTP para requests.
- **run_scraper.py**: (Si existe) Script para lanzar el scraper desde la configuración.

### 2. Módulo `database/`
- **db_connection.py**: Funciones para conectar a la base de datos.
- **db_engine.py**: Clase `DBManager` para operaciones sobre la base de datos (validación, inserción, etc.).
- **db_creator.py**: Clase `DatabaseCreator` para crear y validar la existencia de la base de datos.

### 3. Módulo `interactive/`
- **menu.py**: Menús interactivos para la CLI.
- **menu_engine.py**: Clases `MenuUtils` y `MenuValidation` para utilidades y validaciones de menús.

### 4. Módulo `scraping/`
- **ws_engine.py**: Clase `ScrapingEngine` con utilidades para scraping:
  - Métodos: `expand_collpased_cells`, `get_total_pages`, `get_table_headers`, `measure_row_lengths`, `get_country_info`, `get_league_tier`, `get_seasons`, `calculate_avg_value`, y otros auxiliares.
- **ws_entities.py**: Modelos de datos con `@dataclass`:
  - Clases: `Player`, `Team`, `League`, `Region`, `Country`, `TransferMarket`, `Stats`
  - Métodos: `to_dict`, agregación de entidades hijas, validación de integridad.
- **ws_dataManager.py**: Clase `DataManager` para centralizar y serializar datos:
  - Métodos: `add_region`, `to_dict`, `to_json`
- **ws_urls.py**: Gestión dinámica de URLs y paginación:
  - Clases: `URLManager`, `TransfermarktURLManager`
  - Métodos: `initialize_urls`, `build_url`, `fetch_html`, `extract_total_pages`, `generate_urls`
- **ws_region.py**: Clase `RegionManager` para orquestar el scraping de una región:
  - Métodos: `create_region`, `process_region`
- **ws_leagues.py**: Clase `LeagueManager` para gestionar ligas:
  - Métodos: `get_league_data`, `process_league_season`, `extract_cell_value`
- **ws_teams.py**: Clase `TeamManager` para equipos:
  - Métodos: `get_team_data`, `process_team_players`, `extract_cell_value`
- **ws_players.py**: Clase `PlayerManager` para jugadores:
  - Métodos: `get_player_data`, `extract_cell_value`
- **ws_httpClient.py**: Cliente HTTP robusto:
  - Métodos: `make_request`, `get_html`, `get_json`

---

## Ejemplo de Flujo Completo

1. **main.py** inicializa los componentes principales.
2. Se recorren las regiones configuradas en `ws_urls.py`.
3. Por cada región:
   - Se crea la entidad `Region` y se procesan sus páginas.
   - Se extraen países, ligas y equipos.
   - Por cada liga, se procesan sus temporadas y equipos.
   - Por cada equipo, se extraen y agregan jugadores.
4. Se calculan estadísticas agregadas.
5. Se exportan los datos a JSON.
6. (Futuro) Los datos pueden ser migrados a una base de datos y explorados de forma interactiva.

---

## Cómo Ejecutar el Proyecto

### 1. Instalación de Dependencias
```bash
pip install -r requirements.txt
```

### 2. Ejecución del Scraping
```bash
python main.py
```

### 3. Verificación de Datos
Los datos extraídos se almacenan en la carpeta `Data Output` en formato JSON:
```bash
Data Output/
├── all_regions_with_leagues_and_teams.json
```

---

## Notas Importantes

- Este proyecto es **educacional** y está diseñado para aprender y practicar scraping y procesamiento de datos.
- El scraping depende de la estructura HTML de Transfermarkt; cambios en la web pueden requerir ajustes en el código.
- Los datos se almacenan temporalmente en JSON; la integración con base de datos y exploración interactiva están planificadas.
- Se recomienda revisar y respetar los términos de uso de Transfermarkt.

---

## Licencia

Este proyecto está licenciado bajo la [GNU General Public License v3.0](LICENSE).