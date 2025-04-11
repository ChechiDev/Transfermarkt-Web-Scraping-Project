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
   - Uso de la clase `Scraper` para construir URLs dinámicas y realizar el scraping.
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
│   ├── config.py          # Gestión de variables de entorno
│   ├── headers.py         # Headers para las solicitudes HTTP
│   ├── run_scraper.py     # Lógica principal para ejecutar el scraping
├── database/
│   ├── db_connection.py   # Clase para gestionar la conexión a PostgreSQL
│   ├── db_creator.py      # Clase para crear y validar la base de datos
├── scraping/
│   ├── wscrap_engine.py   # Motor base para realizar scraping
│   ├── wscrap_league.py   # Scraper para ligas
│   ├── wscrap_teams.py    # (En desarrollo) Scraper para equipos
│   ├── [wscrap_players.py]  # (En desarrollo) Scraper para jugadores
├── tests/
│   ├── testing.py         # Pruebas para verificar el funcionamiento del scraping
├── [transfermarkt_project.ipynb] # Notebook principal con el flujo del proyecto
├── [main.py]             # (En desarrollo) Script principal para ejecutar el flujo completo
├── [requirements.txt]       # Dependencias del proyecto
├── .env                   # Variables de entorno (no incluido en el repositorio)
````

---

## <u>*Actualización: Depuración y Ajustes en el Scraper de Ligas*</u>

### **Problema Detectado**
Durante el desarrollo del scraper de ligas (`LeagueScraper`), se identificó un problema en la construcción de URLs. El método `build_url` estaba recibiendo una URL completa en lugar de la clave definida en el archivo `.env`, lo que provocaba un error al intentar encontrar la clave en el diccionario `self.urls`.

### **Solución Implementada**
1. **Depuración del Método `build_url`**:
   - Se agregó impresión de las claves disponibles y la clave recibida para identificar inconsistencias.
   - Se corrigió el manejo de espacios en blanco y caracteres invisibles al cargar las claves desde el archivo `.env`.

2. **Ajuste en el Método `get_data`**:
   - Se aseguró que `get_data` reciba la clave `url_key` en lugar de una URL completa.

3. **Ajuste en el Método `get_leagues`**:
   - Se corrigió para que pase correctamente la clave `url_tmkt_eur_leagues` al método `get_data`.

4. **Pruebas Realizadas**:
   - Se ejecutaron pruebas unitarias en `testing.py` para verificar:
     - La correcta construcción de URLs.
     - La carga de claves desde el archivo `.env`.
     - La extracción de datos de ligas desde la tabla HTML.

### **Notas para Depuración Futura**
- Si el método `build_url` falla, verifica:
  1. Las claves cargadas desde el archivo `.env` (`self.urls`).
  2. La clave pasada al método (`url_key`).
  3. La plantilla de la URL en el archivo `.env`.

- Si el método `get_data` no extrae datos, verifica:
  1. Que la tabla HTML exista en la página.
  2. Que el `row_parser` esté procesando correctamente las filas de la tabla.

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
TBL_NAME=nombre_tabla
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
- Este proyecto está en desarrollo, y algunas funcionalidades como los scrapers específicos (`wscrap_leagues.py`, `wscrap_teams.py`, `wscrap_players.py`) están en progreso.

---

## <u>*Licencia*</u>
Este proyecto está licenciado bajo la [GNU General Public License v3.0](LICENSE).