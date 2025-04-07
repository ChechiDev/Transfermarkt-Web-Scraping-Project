![Work in Progress](https://img.shields.io/badge/Status-Work%20in%20Progress-yellow)
# <u>Transfermarkt Web Scrapping Project:</u>

## <u>*Descripción general*</u>
*Este proyecto es totalmente personal y educacional, sin ninguna intención lucrativa sobre los datos que se puedan extraer.*

- Se realizará un web scrapping de datos sobre la web <url>[Transfermarket](https://www.transfermarkt.es/), almacenamiento en base de datos y finalmente se realizará un ejercicio de Machine Learning sobre la data extraída.
- Éste se estructurará de manera profesional, utilizando programación orientada a objetos (POO) con **Python**, **Jupyter Notebooks** y **PostgreSQL**.

*Este README irá documentando paso a paso el desarrollo del proyecto, detallando cada decisión técnica y bloque de código implementado.*

---

### 1. <u>Conexión con la base de datos:</u>

- Para estructurar correctamente el proyecto, primero creamos una **clase** que gestiona la conexión con la base de datos de PostgreSQL de manera segura en *localhost*.

**Archivo:** `database/db_connection.py`

[Ver archivo db_connection.py](https://github.com/ChechiDev/wscrapping_Transfermarkt/blob/main/database/db_connection.py)

Este archivo contiene la clase `DatabaseConnection`, que permite conectar y desconectar de forma segura a la base de datos PostgreSQL utilizando variables de entorno almacenadas en `.env`.

---

### 2. <u>Creación automática de la base de datos:</u>
Cuando se instancia la clase `DatabaseConnection`, el script pregunta automáticamente al usuario el nombre de la base de datos que desea utilizar.
Si la base de datos no existe en el servidor `PostgreSQL`, se creará automáticamente.
Además, si el archivo `.env` no tiene el nombre de la base de datos actualizado, se modifica automáticamente para reflejar el nombre introducido y de esta manera se mantendrá activa la base de datos introducida para posteriores acciones.

**Detalles del proceso automático**
- Se conecta primero a la base de datos general `postgres`
- Se verifica si la base de datos especificada ya existe.
Si no existe:
    - Se crea la nueva base de datos.
    - Se actualiza el archivo `.env`
Finalmente, se establece conexión a la base de datos seleccionada

### 2.1. <u>Prueba de conexión:</u>

Para probar que la clase funciona correctamente, ejecutamos el siguiente script básico:

```python
from database.db_connection import DatabaseConnection

if __name__ == "__main__":
    db = DatabaseConnection()
    db.connect()
    db.disconnect()
```

***Notas importantes en este punto***
- A partir de este punto, todos los scripts del proyecto prodrán utilizar la base de datos creada o seleccionada automáticamente.
- En caso de querer cambiar el nombre de la base de datos, simplemente se puede:
    - Editar manualmente el archivo `.env`.
    - Ejecutar de nuevo el script y proporcionar un nuevo nombre cuando se solicite.