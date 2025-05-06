![Work in Progress](https://img.shields.io/badge/Status-Work%20in%20Progress-yellow)
# Transfermarkt Web Scraping Project

## Descripción General

Este proyecto tiene como objetivo realizar un **scraping total** de la página [Transfermarkt](https://www.transfermarkt.es/), extrayendo datos estructurados de regiones, ligas, equipos y jugadores.
Actualmente, el enfoque principal está en el desarrollo del módulo de **scraping**, ubicado en la carpeta `scraping`, que contiene toda la lógica para interactuar con la página y procesar los datos.

El proyecto está diseñado con una estructura modular y profesional, utilizando:
- **Python** para la extracción y procesamiento de datos.
- **BeautifulSoup** para analizar el HTML de las páginas.
- **Estrategias de scraping dinámico** para manejar múltiples regiones y ligas.

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
El archivo principal del scraping. Contiene la clase `ScrapingEngine`, que incluye métodos para:
- Extraer encabezados de tablas (`get_table_headers`).
- Medir longitudes de filas en tablas (`measure_row_lengths`).
- Obtener información de países, ligas y temporadas.

### 2. `ws_leagues.py`
Gestiona la extracción de datos relacionados con las ligas, como:
- Nombre de la competición.
- País asociado.
- URL de la liga.

### 3. `ws_teams.py`
(En desarrollo) Gestionará la extracción de datos relacionados con los equipos, como:
- Nombre del equipo.
- Estadísticas generales.
- Jugadores asociados.

### 4. `ws_dataManager.py`
Se encarga de procesar y almacenar los datos extraídos en formato JSON dentro de la carpeta `Data Output`.

### 5. `ws_urls.py`
Gestiona la construcción dinámica de URLs para manejar múltiples regiones y paginación.

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

- Actualmente, el enfoque principal está en el desarrollo del módulo de **scraping**.
- Los datos extraídos se almacenan temporalmente en formato JSON y no se están integrando con una base de datos.
- Asegúrate de que la estructura HTML de Transfermarkt no haya cambiado, ya que esto podría afectar el scraping.

---

## Licencia

Este proyecto está licenciado bajo la [GNU General Public License v3.0](LICENSE).