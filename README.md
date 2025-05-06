![Work in Progress](https://img.shields.io/badge/Status-Work%20in%20Progress-yellow)
# Transfermarkt Web Scraping Project

## Propósito del Proyecto

Este proyecto tiene un propósito **totalmente educacional y de aprendizaje**, sin ningún fin lucrativo. Su objetivo principal es desarrollar habilidades en **web scraping**, **procesamiento de datos** y **organización de proyectos** utilizando Python.

El proyecto se centra en realizar un **scraping total** de la página [Transfermarkt](https://www.transfermarkt.es/), extrayendo datos estructurados de regiones, ligas, equipos y jugadores. Actualmente, el enfoque principal está en el desarrollo del módulo de **scraping**, ubicado en la carpeta `scraping`, que contiene toda la lógica para interactuar con la página y procesar los datos.

---

## Estado Actual del Proyecto

- **Scraping**: En desarrollo activo. Toda la lógica se encuentra en la carpeta `scraping`.
- **Base de datos**: En stand-by. Los datos extraídos se almacenan temporalmente en la carpeta `Data Output` en formato JSON.
- **Configuración del entorno**: En stand-by. Actualmente, las variables de entorno no son necesarias para el scraping.

---

## Flujo de Trabajo Actual

El flujo de trabajo actual se centra exclusivamente en el scraping de datos desde Transfermarkt:

1. **Inicialización del scraping**:
   - Se configuran los componentes principales, como el cliente HTTP (`HTTPClient`) y el motor de scraping (`ScrapingEngine`).

2. **Extracción de datos**:
   - Se extraen datos de regiones, ligas, equipos y jugadores utilizando clases específicas como `LeagueManager` y `TeamManager`.
   - Los datos se procesan dinámicamente para manejar múltiples páginas y tablas HTML.

3. **Almacenamiento temporal**:
   - Los datos extraídos se guardan en la carpeta `Data Output` en formato JSON para su posterior análisis o integración con una base de datos.

---

## Estructura del Proyecto

El proyecto está organizado de la siguiente manera:

```bash
├── scraping/              # Carpeta principal en desarrollo
│   ├── ws_engine.py       # Motor base para realizar scraping
│   ├── ws_leagues.py      # Gestión de ligas
│   ├── ws_teams.py        # Gestión de equipos
│   ├── ws_dataManager.py  # Gestión de datos extraídos
│   ├── ws_urls.py         # Gestión de URLs dinámicas
├── Data Output/           # Carpeta para almacenar temporalmente los datos extraídos
│   ├── all_regions_with_leagues_and_teams.json
├── main.py                # Script principal para ejecutar el scraping
├── README.md              # Documentación del proyecto
├── requirements.txt       # Dependencias del proyecto
```

---

## Detalles del Módulo de Scraping

### 1. `ws_engine.py`
El archivo principal del scraping. Contiene la clase `ScrapingEngine`, que incluye los siguientes métodos:

- **`expand_collpased_cells(table: BeautifulSoup)`**:
  Expande las celdas colapsadas en una tabla HTML utilizando el atributo `data-content`. Esto es útil para tablas que ocultan información adicional en celdas colapsadas.

- **`get_total_pages(url: str) -> int`**:
  Obtiene el número total de páginas disponibles para una región específica, analizando los elementos de paginación en el HTML.

- **`get_table_headers(table: BeautifulSoup, header_type: str = "default") -> dict`**:
  Extrae los encabezados de una tabla HTML, formateándolos para que sean consistentes y fáciles de usar en el procesamiento posterior.

- **`measure_row_lengths(table: BeautifulSoup) -> tuple`**:
  Calcula la longitud de cada fila en una tabla HTML y devuelve un resumen de las longitudes y la longitud máxima encontrada.

- **`get_country_info(table: BeautifulSoup) -> dict`**:
  Extrae información sobre los países desde una tabla HTML, incluyendo el nombre del país, su ID y la URL de su bandera.

- **`get_league_tier(table: BeautifulSoup) -> Dict[str, str]`**:
  Obtiene el nivel o categoría de las ligas a partir de una tabla HTML, asociando cada liga con su nivel correspondiente.

- **`get_seasons(url: str) -> list[int]`**:
  Extrae las temporadas disponibles desde un menú desplegable en una página HTML.

- **`calculate_avg_value(leagues: Dict[str, League], region_stats: RegionStats, stat_name: str) -> float`**:
  Calcula el valor promedio de una estadística específica para todas las ligas de una región.

---

### 2. `ws_leagues.py`
Gestiona la extracción de datos relacionados con las ligas.
Métodos principales:

- **`get_league_data()`**:
  Extrae información detallada de las ligas, como el nombre de la competición, el país asociado y la URL de la liga.

- **`process_league_table()`**:
  Procesa las tablas HTML específicas de las ligas para extraer datos estructurados.

---

### 3. `ws_teams.py`
(En desarrollo) Gestionará la extracción de datos relacionados con los equipos.
Métodos planificados:

- **`get_team_data()`**:
  Extraerá información básica de los equipos, como el nombre, el estadio y el entrenador.

- **`process_team_table()`**:
  Procesará las tablas HTML específicas de los equipos para extraer estadísticas y jugadores asociados.

---

### 4. `ws_dataManager.py`
Se encarga de procesar y almacenar los datos extraídos.
Métodos principales:

- **`add_region(region: Region) -> None`**:
  Añade una región al objeto central `TransferMarket`, validando que sea una instancia de la clase `Region`.

- **`to_dict() -> Dict`**:
  Convierte todos los datos almacenados en un diccionario estructurado.

- **`to_json(file_name: str) -> None`**:
  Exporta los datos almacenados a un archivo JSON en la carpeta `Data Output`.

---

### 5. `ws_urls.py`
Gestiona la construcción dinámica de URLs para manejar múltiples regiones y paginación.
Métodos principales:

- **`initialize_urls()`**:
  Inicializa las URLs base para cada región configurada.

- **`build_url(region: str, page: int) -> str`**:
  Construye una URL dinámica para una región específica y una página dada.

- **`fetch_html(url: str) -> BeautifulSoup`**:
  Realiza una solicitud HTTP y devuelve el HTML parseado.

- **`extract_total_pages(html: BeautifulSoup, region: str) -> int`**:
  Extrae el número total de páginas disponibles para una región desde el HTML.

- **`generate_urls(region: str, end_page: int) -> list`**:
  Genera una lista de URLs para todas las páginas de una región específica.

---

## Cómo Ejecutar el Proyecto

### 1. Instalación de Dependencias
Ejecuta el siguiente comando para instalar todas las dependencias necesarias:
```bash
pip install -r requirements.txt
```

### 2. Ejecución del Scraping
Ejecuta el script principal para iniciar el scraping completo:
```bash
python main.py
```

### 3. Verificación de Datos
Los datos extraídos se almacenan en la carpeta `Data Output` en formato JSON. Por ejemplo:
```bash
Data Output/
├── all_regions_with_leagues_and_teams.json
```

---

## Notas Importantes

- Este proyecto es **educacional** y está diseñado para aprender y practicar habilidades de scraping y procesamiento de datos.
- Actualmente, el enfoque principal está en el desarrollo del módulo de **scraping**.
- Los datos extraídos se almacenan temporalmente en formato JSON y no se están integrando con una base de datos.
- Asegúrate de que la estructura HTML de Transfermarkt no haya cambiado, ya que esto podría afectar el scraping.

---

## Licencia

Este proyecto está licenciado bajo la [GNU General Public License v3.0](LICENSE).