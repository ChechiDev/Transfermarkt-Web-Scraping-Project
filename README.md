# <u>Transfermarkt Web Scrapping Project:

## <u>*Descripción general*
*Este proyecto es totalmente personal e educacional, sin ninguna intención lucrativa sobre los datos que se puedan extraer.*

- Se realizará un web scrapping de datos sobre la web <url>[Transfermarket](https://www.transfermarkt.es/), almacenamiento en base de datos y finalmente se realizará un ejercicio de Machine Learning sobre la data extraída.
- Éste se estructurará de manera profesional, utilizando programación orientada a objetos (POO) con **Python**, **Jupyter Notebooks** y **PostgreSQL**

*Este README irá documentando paso a paso el desarrollo del proyecto, detallando cada decisión técnica y bloque de código implementado.*

---

## 1. <u>Conexión con la base de datos:
- Para estructurar correctamente el proyecto, primero creamos una **clase** que gestiona la conexión con la base de datos de PostgreSQL de manera segura.

**Archivo:** `database/db_connection.py`