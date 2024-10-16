import logging
import os
from typing import List
from django.core.management import call_command
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bt_childkey_monitor.settings')
django.setup()

class DataBaseManager:
    """
    Manages database operations such as setting up database path, migration, deletion.
    """

    def __init__(self, db_path: str) -> None:
        """
        Initialize the database manager with the path to the database file.
        :param db_path: Path to the SQLite database file.
        """
        self.db_path = db_path

    def delete_database_file(self) -> None:
        """
        Deletes the database file if it exists.
        """
        print("here5")
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
            logging.info("Deleted database file.")
            print("removed")
        else:
            logging.info("Database file does not exist, skipping deletion.")

    def migrate_db(self) -> None:
        """
        Applies Django migrations to set up or update the database schema.
        """
        try:
            call_command('makemigrations', verbosity=0)
            call_command('migrate', verbosity=0)
            print("migrated")
            logging.info("Database migrated successfully.")
        except Exception as e:
            logging.error(f"Error migrating database: {e}")
