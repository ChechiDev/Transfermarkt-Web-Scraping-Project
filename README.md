# <u>Transfermarkt Web Scrapping Project:</u>

## <u>*Descripción general*</u>
*Este proyecto es totalmente personal y educacional, sin ninguna intención lucrativa sobre los datos que se puedan extraer.*

- Se realizará un web scrapping de datos sobre la web <url>[Transfermarket](https://www.transfermarkt.es/), almacenamiento en base de datos y finalmente se realizará un ejercicio de Machine Learning sobre la data extraída.
- Éste se estructurará de manera profesional, utilizando programación orientada a objetos (POO) con **Python**, **Jupyter Notebooks** y **PostgreSQL**.

*Este README irá documentando paso a paso el desarrollo del proyecto, detallando cada decisión técnica y bloque de código implementado.*

---

## #1. <u>Conexión con la base de datos:</u>

- Para estructurar correctamente el proyecto, primero creamos una **clase** que gestiona la conexión con la base de datos de PostgreSQL de manera segura en *localhost*.

**Archivo:** `database/db_connection.py`

[Ver archivo db_connection.py](https://github.com/ChechiDev/wscrapping_Transfermarkt/blob/main/database/db_connection.py)

Este archivo contiene la clase `DatabaseConnection`, que permite conectar y desconectar de forma segura a la base de datos PostgreSQL utilizando variables de entorno almacenadas en `.env`.

---

## #2. <u>Prueba de conexión:</u>

Para probar que la clase funciona correctamente, ejecutamos el siguiente script básico:

```python
from database.db_connection import DatabaseConnection

if __name__ == "__main__":
    db = DatabaseConnection()
    db.connect()
    db.disconnect()