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
├── scraping/              # Módulo principal de scraping y gestión de datos
│   ├── ws_engine.py       # Motor base para scraping y utilidades HTML
│   ├── ws_leagues.py      # Gestión y extracción de ligas
│   ├── ws_teams.py        # Gestión y extracción de equipos
│   ├── ws_players.py      # Gestión y extracción de jugadores
│   ├── ws_dataManager.py  # Gestión y serialización de datos extraídos
│   ├── ws_entities.py     # Definición de entidades y modelos de datos
│   ├── ws_urls.py         # Gestión dinámica de URLs y paginación
│   ├── ws_region.py       # Gestión y procesamiento de regiones
│   ├── ws_httpClient.py   # Cliente HTTP robusto con reintentos y validación
├── database/              # (Futuro) Módulo para integración y gestión de base de datos
│   ├── models.py          # Modelos ORM para persistencia de datos
│   ├── db_manager.py      # Lógica de conexión, inserción y consultas
│   └── ...                # Scripts de migración y utilidades
├── interactive/           # (Futuro) Módulo para exploración y consulta interactiva
│   ├── cli.py             # Interfaz de línea de comandos para explorar datos
│   ├── dashboard.py       # (Opcional) Interfaz web o visualización
│   └── ...                # Utilidades para navegación y búsqueda
├── Data Output/           # Carpeta para almacenar temporalmente los datos extraídos
│   ├── all_regions_with_leagues_and_teams.json
├── main.py                # Script principal para ejecutar el scraping
├── README.md              # Documentación del proyecto
├── requirements.txt       # Dependencias del proyecto
```

---

## Lógica y Arquitectura Modular

### 1. Módulo `scraping/`

#### a) **ws_engine.py**
Contiene la clase `ScrapingEngine`, núcleo de utilidades para el scraping:
- **expand_collpased_cells(table: BeautifulSoup)**: Expande celdas HTML colapsadas.
- **get_total_pages(url: str) -> int**: Calcula el número de páginas de una tabla paginada.
- **get_table_headers(table: BeautifulSoup, header_type: str = "default") -> dict**: Extrae y normaliza encabezados de tablas.
- **measure_row_lengths(table: BeautifulSoup) -> tuple**: Analiza la longitud de filas para validar consistencia.
- **get_country_info(table: BeautifulSoup) -> dict**: Extrae información de países (ID, nombre, bandera).
- **get_league_tier(table: BeautifulSoup) -> Dict[str, str]**: Asocia ligas con su nivel/tier.
- **get_seasons(url: str) -> list[int]**: Extrae temporadas disponibles desde un menú desplegable.
- **calculate_avg_value(leagues, region_stats, stat_name) -> float**: Calcula promedios de estadísticas agregadas.
- Métodos auxiliares para fechas, monedas, IDs y validación de datos.

#### b) **ws_entities.py**
Define los modelos de datos usando `@dataclass`:
- **Player, Team, League, Region, Country, TransferMarket**: Estructuras jerárquicas y métodos `to_dict()` para serialización.
- **Stats**: Clases para estadísticas agregadas a cada nivel.
- Métodos para agregar entidades hijas y asegurar integridad de datos.

#### c) **ws_dataManager.py**
Clase `DataManager` para centralizar y serializar los datos:
- **add_region(region: Region) -> None**: Añade una región validando el tipo.
- **to_dict() -> Dict**: Convierte toda la estructura a diccionario.
- **to_json(file_name: str) -> None**: Exporta los datos a un archivo JSON en `Data Output`.

#### d) **ws_urls.py**
Gestión dinámica de URLs y paginación:
- **URLManager**: Clase base para almacenar y validar URLs.
- **TransfermarktURLManager**: Genera URLs para cada región y página, extrae encabezados y páginas totales.
  - **initialize_urls()**: Inicializa todas las URLs de regiones.
  - **build_url(region, page)**: Construye URLs dinámicas.
  - **fetch_html(url)**: Solicita y parsea HTML.
  - **extract_total_pages(html, region)**: Calcula páginas totales.
  - **generate_urls(region, end_page)**: Lista todas las URLs de una región.

#### e) **ws_region.py**
Clase `RegionManager` para orquestar el scraping de una región:
- **create_region(region_key, region_data) -> Region**: Instancia una región con estadísticas iniciales.
- **process_region(region, region_data) -> None**: Extrae países, ligas y equipos, y calcula estadísticas agregadas.

#### f) **ws_leagues.py**
Clase `LeagueManager` para gestionar ligas:
- **get_league_data(table, min_columns, region_id, region_countries) -> List[League]**: Extrae ligas de una tabla HTML.
- **process_league_season(league, region, team_manager)**: Procesa temporadas y equipos de una liga.
- **extract_cell_value(...)**: Utilidad para extraer y transformar celdas de tabla.

#### g) **ws_teams.py**
Clase `TeamManager` para equipos:
- **get_team_data(table, min_columns, region, league) -> List[Team]**: Extrae equipos de una tabla HTML.
- **process_team_players(team)**: Extrae y agrega jugadores a un equipo.
- **extract_cell_value(...)**: Utilidad para celdas de tabla.

#### h) **ws_players.py**
Clase `PlayerManager` para jugadores:
- **get_player_data(table, min_columns, fk_region, fk_league, team) -> List[Player]**: Extrae jugadores de una tabla HTML.
- **extract_cell_value(...)**: Utilidad para celdas de tabla.

#### i) **ws_httpClient.py**
Cliente HTTP robusto:
- **make_request(url, method="GET", ...)**: Solicitud HTTP con reintentos, validación y manejo de errores.
- **get_html(url, ...)**: Devuelve HTML parseado.
- **get_json(url, ...)**: Devuelve respuesta JSON.

---

### 2. Módulo `database/` (Futuro)

**Propósito:** Integrar y gestionar los datos extraídos en una base de datos relacional (ej. PostgreSQL, SQLite) o NoSQL.

**Estructura esperada:**
- **models.py**: Definición de modelos ORM (por ejemplo, usando SQLAlchemy o Django ORM) para reflejar la jerarquía de entidades (`Region`, `League`, `Team`, `Player`, etc.).
- **db_manager.py**: Lógica para la conexión, inserción masiva, migraciones y consultas eficientes.
- **migrations/**: Scripts para crear y actualizar el esquema de la base de datos.
- **utils.py**: Funciones auxiliares para validación, transformación y limpieza de datos antes de la inserción.

**Lógica esperada:**
- Conversión de los datos extraídos (actualmente en JSON) a instancias de modelos ORM.
- Inserción y actualización de registros de forma transaccional.
- Consultas complejas para análisis y visualización.
- Integridad referencial y validación de duplicados.

---

### 3. Módulo `interactive/` (Futuro)

**Propósito:** Permitir la exploración y consulta interactiva de los datos extraídos por usuarios finales o desarrolladores.

**Estructura esperada:**
- **cli.py**: Interfaz de línea de comandos para navegar por regiones, ligas, equipos y jugadores, con comandos de búsqueda y filtrado.
- **dashboard.py**: (Opcional) Interfaz web o panel visual para explorar los datos con gráficos y tablas interactivas (ej. usando Streamlit, Dash o Flask).
- **utils.py**: Funciones para formatear la salida, autocompletar comandos y exportar resultados.

**Lógica esperada:**
- Menús interactivos para seleccionar regiones, ligas, equipos o jugadores.
- Búsqueda por nombre, país, temporada, etc.
- Visualización de estadísticas agregadas y detalles individuales.
- Exportación de resultados a CSV, Excel o visualización directa.

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