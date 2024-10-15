import logging
import os
import json
from typing import List
from django.core.management import call_command
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bt_childkey_monitor.settings')
django.setup()

from validators.models import ValidatorChildKeyInfo, Validators

class DataBaseManager:
    """
    Manages database operations such as migration, deletion, and data insertion.
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
        Logs the action taken.
        """
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
            logging.info("Deleted database file.")
        else:
            logging.info("Database file does not exist, skipping deletion.")

    def migrate_db(self) -> None:
        """
        Applies Django migrations to set up or update the database schema.
        Logs success or errors encountered during the process.
        """
        try:
            call_command('makemigrations', verbosity=1)
            call_command('migrate', verbosity=1)
            logging.info("Database migrated successfully.")
        except Exception as e:
            logging.error(f"Error migrating database: {e}")

    def create_validator_childkey_tables(self, parent_validators: List[Validators]) -> None:
        """
        Creates entries in the ValidatorChildKeyInfo table for each child key of the given parent validators.
        
        :param parent_validators: List of Validators objects representing parent validators.
        """
        for validator in parent_validators:
            try:
                parent_coldkey = validator.coldkey
                parent_stake = validator.stake
                childkeys_info = validator.childkeys if isinstance(validator.childkeys, list) else json.loads(validator.childkeys)

                if not childkeys_info:
                    continue

                for child_info in childkeys_info:
                    ValidatorChildKeyInfo.objects.create(
                        parent_hotkey=validator,
                        parent_coldkey=parent_coldkey,
                        parent_stake=parent_stake,
                        child_hotkey=child_info['child_hotkey'],
                        stake_proportion=child_info['proportion'],
                        subnet_uid=child_info['net_uid'],
                    )
                    logging.info(f"Created child key info for {validator.hotkey}: {child_info['child_hotkey']}")
            except Exception as e:
                logging.error(f"Error creating child key info for {validator.hotkey}: {e}")

# Example usage
# db_manager = DataBaseManager('/path/to/db.sqlite3')
# db_manager.delete_database_file()
# db_manager.migrate_db()
# db_manager.create_validator_childkey_tables(parent_validators_list)
