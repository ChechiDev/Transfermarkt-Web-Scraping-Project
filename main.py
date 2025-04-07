from database.db_connection import DatabaseConnection
from config.cfg_environment import EnvironmentConfig

if __name__ == "__main__":
    env = EnvironmentConfig()
    db = DatabaseConnection()
    db.connect()
    db.disconnect()