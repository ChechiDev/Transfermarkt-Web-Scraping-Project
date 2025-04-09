![Work in Progress](https://img.shields.io/badge/Status-Work%20in%20Progress-yellow)
# <u>Transfermarkt Web Scraping Project</u>

## <u>*Descripción general*</u>
Este proyecto tiene un propósito **educativo y personal**, sin fines lucrativos. Su objetivo principal es realizar un proceso completo de scraping de datos desde la web de [Transfermarkt](https://www.transfermarkt.es/), seguido de un almacenamiento estructurado en una base de datos PostgreSQL y un análisis posterior utilizando Python.

El proyecto está diseñado con una estructura profesional, utilizando:
- **Programación Orientada a Objetos (POO) con Python**
- **Jupyter Notebooks** para la documentación y ejecución interactiva
- **PostgreSQL** para la persistencia de datos

---

## <u>*Flujo de trabajo*</u>
El flujo principal del proyecto sigue los siguientes pasos:

1. **Configuración del entorno**:
   - Carga de variables de entorno desde un archivo `.env` utilizando la clase `EnvironmentConfig`.
   - Configuración de parámetros como usuario, contraseña, host, puerto y base de datos.

2. **Conexión y validación de la base de datos**:
   - Uso de la clase `DatabaseCreator` para verificar si la base de datos existe.
   - Si no existe, se crea automáticamente y se actualiza el archivo `.env` con el nuevo nombre.

3. **Scraping de datos**:
   - Uso de la clase `HttpClient` para realizar solicitudes HTTP.
   - Uso de la clase `ScrapeBase` para construir URLs dinámicas y realizar el scraping.
   - Ejecución del scraping mediante `run_scraper`, que permite seleccionar dinámicamente las URLs a scrapear.

4. **Almacenamiento en PostgreSQL**:
   - Inserción de los datos obtenidos en tablas normalizadas dentro de la base de datos PostgreSQL.

5. **Preparación para análisis**:
   - Los datos almacenados están listos para ser utilizados en análisis exploratorios o ejercicios de Machine Learning.

---

## <u>*Estructura del proyecto*</u>
El proyecto está organizado de la siguiente manera:

```bash
├── config/
│   ├── [config.py](http://_vscodecontentref_/1)          # Gestión de variables de entorno
│   ├── [headers.py](http://_vscodecontentref_/2)         # Headers para las solicitudes HTTP
│   ├── [run_scraper.py](http://_vscodecontentref_/3)     # Lógica principal para ejecutar el scraping
├── database/
│   ├── db_connection.py   # Clase para gestionar la conexión a PostgreSQL
│   ├── db_creator.py      # Clase para crear y validar la base de datos
├── scraping/
│   ├── [scrapping_engine.py](http://_vscodecontentref_/4) # Motor base para realizar scraping
│   ├── league_scraper.py   # (En desarrollo) Scraper para ligas
│   ├── team_scraper.py     # (En desarrollo) Scraper para equipos
│   ├── player_scraper.py   # (En desarrollo) Scraper para jugadores
├── tests/
 │   ├── test_env.py        # Pruebas para verificar la carga de variables de entorno
├── [transfermarkt_project.ipynb](http://_vscodecontentref_/5) # Notebook principal con el flujo del proyecto
├── [main.py](http://_vscodecontentref_/6)                # Script principal para ejecutar el flujo completo
├── [requirements.txt](http://_vscodecontentref_/7)       # Dependencias del proyecto
├── .env                   # Variables de entorno (no incluido en el repositorio)
```

---

## <u>*Clases y funciones principales*</u>

### 1. **`EnvironmentConfig`** (Archivo: `config/config.py`)
Clase encargada de cargar y gestionar las variables de entorno desde el archivo `.env`.

- **Atributos principales**:
  - `user`, `password`, `host`, `port`, `db`, `schema`, `table`
- **Métodos**:
  - `__str__`: Devuelve una representación legible de las variables cargadas.

---

### 2. **`DatabaseConnection`** (Archivo: `database/db_connection.py`)
Clase para gestionar la conexión y desconexión a una base de datos PostgreSQL.

- **Métodos principales**:
  - `connect`: Establece la conexión con la base de datos.
  - `disconnect`: Cierra la conexión.

---

### 3. **`DatabaseCreator`** (Archivo: `database/db_creator.py`)
Clase para verificar y crear la base de datos y el esquema si no existen.

- **Métodos principales**:
  - `check_and_create_db`: Verifica si la base de datos existe; si no, la crea.
  - `check_and_create_sch`: Verifica si el esquema existe; si no, lo crea.
  - `update_env_file`: Actualiza el archivo `.env` con los nuevos valores.

---

### 4. **`HttpClient`** (Archivo: `scraping/scrapping_engine.py`)
Clase para manejar las solicitudes HTTP.

- **Métodos principales**:
  - `get_html`: Realiza una solicitud HTTP y devuelve el contenido HTML parseado con BeautifulSoup.

---

### 5. **`ScrapeBase`** (Archivo: `scraping/scrapping_engine.py`)
Clase base para manejar el scraping.

- **Métodos principales**:
  - `add_url`: Añade una URL al diccionario base.
  - `get_url_from_env`: Carga automáticamente las URLs desde el archivo `.env`.
  - `build_url`: Construye una URL dinámica reemplazando variables.
  - `scrape`: Realiza el scraping para una URL específica.

---

### 6. **`run_scraper`** (Archivo: `config/run_scraper.py`)
Función principal para ejecutar el scraping.

- **Flujo**:
  1. Carga las URLs disponibles desde las variables de entorno.
  2. Permite al usuario seleccionar una URL para scrapear.
  3. Determina el número total de páginas y realiza el scraping de cada una.
  4. Procesa y almacena los datos obtenidos.

---

## <u>*Cómo ejecutar el proyecto*</u>

### 1. Instalación de dependencias
Ejecuta el siguiente comando para instalar todas las dependencias necesarias:
```bash
pip install -r requirements.txt
```

### 2. Configuración del entorno
Crea un archivo `.env` en la raíz del proyecto con las siguientes variables:
```env
DB_USER=tu_usuario
DB_PASSWORD=tu_contraseña
DB_HOST=localhost
DB_PORT=5432
DB_NAME=nombre_base_datos
SCH_NAME=nombre_schema
TB__NAME=nombre_tabla
```

### 3. Ejecución del flujo principal
Ejecuta el script principal para iniciar el flujo completo del proyecto:
```bash
python main.py
```

### 4. Uso del Notebook
Abre el archivo `transfermarkt_project.ipynb` en Jupyter Notebook para ejecutar y documentar el flujo de trabajo de manera interactiva.

---

## <u>*Notas importantes*</u>
- Este proyecto está en desarrollo, y algunas funcionalidades como los scrapers específicos (`league_scraper.py`, `team_scraper.py`, `player_scraper.py`) están en progreso.

---

## <u>*Licencia*</u>
Este proyecto está licenciado bajo la [GNU General Public License v3.0](LICENSE).