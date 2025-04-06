from database.db_connection import DatabaseConnection

if __name__ == "__main__":
    db = DatabaseConnection()
    db.connect()
    db.disconnect()