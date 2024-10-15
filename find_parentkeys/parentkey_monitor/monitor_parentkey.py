import os
import sys
import logging
import json
import django
from typing import List, Tuple, Dict
import bittensor as bt
from find_parentkeys.utils.get_parentkey import RPCRequest
from find_parentkeys.database_manage.db_manage import DataBaseManager

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bt_childkey_monitor.settings')
django.setup()

from validators.models import Validators

# Configure logging
logging.basicConfig(level=logging.INFO)

class ParentkeyMonitor:
    """
    Monitors and manages parent keys in the blockchain network.
    """

    def __init__(self) -> None:
        """
        Initialize the ParentkeyMonitor class.
        """
        pass  # Consider adding initialization logic if needed

    def get_subnet_uids(self, subtensor) -> List[int]:
        """
        Retrieve subnet UIDs from the subtensor.

        :param subtensor: The subtensor object to interact with.
        :return: A list of subnet UIDs.
        """
        try:
            subnet_uids = subtensor.get_subnets()
            logging.info(f"Subnet UIDs: {subnet_uids}")
            return subnet_uids
        except Exception as e:
            logging.error(f"Error retrieving subnet UIDs: {e}")
            return []

    def get_subnet_validators(self, netuid: int, subtensor) -> List[Validators]:
        """
        Retrieve validators for a specific subnet.

        :param netuid: The network UID of the subnet.
        :param subtensor: The subtensor object to interact with.
        :return: A list of Validators objects.
        """
        big_validators: Dict[Validators, Validators] = {}
        try:
            metagraph = subtensor.metagraph(netuid)
            neuron_uids = metagraph.uids.tolist()
            stakes = metagraph.S.tolist()
            hotkeys = metagraph.hotkeys
            coldkeys = metagraph.coldkeys

            for i in range(len(neuron_uids)):
                if stakes[i] > 1000:
                    validator = Validators(
                        coldkey=coldkeys[i],
                        hotkey=hotkeys[i],
                        stake=stakes[i],
                    )
                    validator_installed_netuids = validator.get_validator_installed_netuids()
                    validator_installed_netuids.append(netuid)
                    validator.validator_installed_netuids = json.dumps(validator_installed_netuids)
                    big_validators[validator] = validator
        except Exception as e:
            logging.error(f"Error retrieving validators for subnet {netuid}: {e}")
        return list(big_validators.values())

    def get_all_validators_subnets(self, subtensor) -> Tuple[List[Validators], List[int]]:
        """
        Retrieve all validators and their associated subnets.

        :param subtensor: The subtensor object to interact with.
        :return: A tuple containing a list of all Validators and a list of subnet UIDs.
        """
        all_validators: Dict[Validators, Validators] = {}
        subnet_net_uids = self.get_subnet_uids(subtensor)
        subnet_net_uids.remove(0)  # Remove the root subnet
        subnet_net_uids = [39, 23]  # Example: specify subnets of interest

        if not subnet_net_uids:
            return [], []

        for netuid in subnet_net_uids:
            subnet_validators = self.get_subnet_validators(netuid, subtensor)
            for validator in subnet_validators:
                if validator not in all_validators:
                    all_validators[validator] = validator

        logging.info("Created entries for all parent validators")
        return list(all_validators.values()), subnet_net_uids

def monitor_parentkeys(config: Dict) -> None:
    """
    Monitors parent keys and updates the database with the latest information.

    :param config: A dictionary containing configuration settings.
    """
    parent_monitor = ParentkeyMonitor()

    full_proportion = config.get("FULL_PROPORTION")
    subtensor_module = config.get("SUBTENSORMODULE")
    parent_keys = config.get("PARENTKEYS")
    chain_endpoint = config.get("CHAIN_ENDPOINT")

    subtensor = bt.Subtensor(network=chain_endpoint)

    sdk_call = RPCRequest(chain_endpoint, subtensor_module, parent_keys, full_proportion)

    db_path = os.path.join(config.get("DATABASE_DIR"), 'db.sqlite3')
    db_manager = DataBaseManager(db_path)

    db_manager.delete_database_file()
    db_manager.migrate_db()

    all_validators, subnet_uids = parent_monitor.get_all_validators_subnets(subtensor)

    for validator in all_validators:
        parent_keys = sdk_call.get_parent_keys(validator.hotkey, subnet_uids)

        for parent_key in parent_keys:
            validator.add_parentkeys(parent_key['hotkey'], parent_key['proportion'], parent_key['net_uid'])

            parent_validator = next((v for v in all_validators if v.hotkey == parent_key['hotkey']), None)

            if parent_validator is None:
                parent_validator = Validators(
                    coldkey='',
                    hotkey=parent_key['hotkey'],
                    stake=0,
                )
                all_validators.append(parent_validator)

            parent_validator.add_childkeys(validator.hotkey, parent_key['proportion'], parent_key['net_uid'])

    for validator in all_validators:
        logging.info(f"Updating or creating validator: {validator.__dict__}")
        try:
            Validators.objects.update_or_create(
                hotkey=validator.hotkey,
                defaults={
                    'coldkey': validator.coldkey,
                    'stake': validator.stake,
                    'parentkeys': json.dumps(validator.parentkeys),
                    'childkeys': json.dumps(validator.childkeys),
                },
            )
        except Exception as e:
            logging.error(f"Error updating or creating validator {validator.hotkey}: {e}")

    db_manager.create_validator_childkey_tables(all_validators)
