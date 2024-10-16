import os
import logging
import django
from typing import List, Tuple, Dict
import bittensor as bt
from find_parentkeys.utils.get_parentkey import RPCRequest
from find_parentkeys.database_manage.db_manage import DataBaseManager
from validators.models import HotkeyModel, ChildHotkeyModel

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bt_childkey_monitor.settings')
django.setup()

class ParentkeyMonitor:
    """Monitors and manages parent keys in the blockchain network."""
    
    def __init__(self, config: Dict) -> None:
        """Initialize the ParentkeyMonitor class."""
        self.config = config

    def get_subnet_uids(self, subtensor) -> List[int]:
        """Retrieve subnet UIDs from the subtensor."""
        try:
            subnet_uids = subtensor.get_subnets()
            logging.info(f"Subnet UIDs: {subnet_uids}")
            return subnet_uids
        except Exception as e:
            logging.error(f"Error retrieving subnet UIDs: {e}")
            return []

    def get_subnet_validators(self, netuid: int, subtensor) -> List[HotkeyModel]:
        """Retrieve validators for a specific subnet."""
        big_validators: Dict[HotkeyModel, HotkeyModel] = {}
        try:
            metagraph = subtensor.metagraph(netuid)
            neuron_uids = metagraph.uids.tolist()
            stakes = metagraph.S.tolist()
            hotkeys = metagraph.hotkeys

            for i in range(len(neuron_uids)):
                if stakes[i] > 1000:
                    hotkey = HotkeyModel(hotkey=hotkeys[i])
                    big_validators[hotkey] = hotkey
        except Exception as e:
            logging.error(f"Error retrieving validators for subnet {netuid}: {e}")

        return list(big_validators.values())

    def get_all_validators_subnets(self, subtensor) -> Tuple[List[HotkeyModel], List[int]]:
        """Retrieve all validators and their associated subnets."""
        all_validators: Dict[HotkeyModel, HotkeyModel] = {}
        subnet_net_uids = self.get_subnet_uids(subtensor)
        subnet_net_uids.remove(0)  # Remove the root subnet
        subnet_net_uids = [1, 3]  # Example: specify subnets of interest
        
        for netuid in subnet_net_uids:
            subnet_validators = self.get_subnet_validators(netuid, subtensor)
            for validator in subnet_validators:
                all_validators.setdefault(validator, validator)

        logging.info("Created entries for all parent validators")
        return list(all_validators.values()), subnet_net_uids

    def monitor_parentkeys(self) -> None:
        """Monitors parent keys and updates the database with the latest information."""
        print("here1")
        full_proportion = self.config.get("FULL_PROPORTION")
        subtensor_call_module = self.config.get("SUBTENSORMODULE")
        parent_keys_call_function = self.config.get("PARENTKEYS_FUNCTION")
        total_hotkey_stake_call_function = self.config.get("TOTALHOTKEYSTAKE_FUNCTION")
        chain_endpoint = self.config.get("CHAIN_ENDPOINT")

        subtensor = bt.Subtensor(network=chain_endpoint)
        sdk_call = RPCRequest(chain_endpoint, full_proportion)
        print(self.config)
        db_path = os.path.join(self.config.get("DATABASE_DIR"), 'db.sqlite3')
        db_manager = DataBaseManager(db_path)
        print("here2")
        db_manager.delete_database_file()
        db_manager.migrate_db()

        all_validators, subnet_uids = self.get_all_validators_subnets(subtensor)
        print("here 6")
        for validator in all_validators:
            logging.info(f"Processing validator: {validator.hotkey}")
            validator.stake = sdk_call.get_stake_from_hotkey(
                subtensor_call_module,
                total_hotkey_stake_call_function,
                validator.hotkey
            )
            validator.save()
        print("here3")
        for validator in all_validators:
            parent_keys = sdk_call.get_parent_keys(
                subtensor_call_module,
                parent_keys_call_function,
                validator.hotkey,
                subnet_uids
            )
            print("here4")
            self._process_parent_keys(parent_keys, validator)

    def _process_parent_keys(self, parent_keys: List[Dict], validator: HotkeyModel) -> None:
        """Process and save parent keys for a given validator."""
        for parent_key in parent_keys:
            parent_validator = self._get_or_create_parent_validator(parent_key)
            ChildHotkeyModel.objects.create(
                parent=parent_validator,
                child=validator,
                netuid=parent_key['net_uid'],
                proportion=parent_key['proportion']
            )

    def _get_or_create_parent_validator(self, parent_key: Dict) -> HotkeyModel:
        """Retrieve or create a parent validator."""
        if HotkeyModel.objects.filter(hotkey=parent_key['hotkey']).exists():
            return HotkeyModel.objects.get(hotkey=parent_key['hotkey'])
        else:
            cur_stake = self._get_current_stake(parent_key['hotkey'])
            return HotkeyModel.objects.create(
                hotkey=parent_key['hotkey'],
                stake=cur_stake,
            )

    def _get_current_stake(self, hotkey: str) -> float:
        """Get the current stake for a hotkey."""
        subtensor_call_module = self.config.get("SUBTENSORMODULE")
        total_hotkey_stake_call_function = self.config.get("TOTALHOTKEYSTAKE_FUNCTION")
        sdk_call = RPCRequest(self.config.get("CHAIN_ENDPOINT"), self.config.get("FULL_PROPORTION"))
        
        return sdk_call.get_stake_from_hotkey(
            subtensor_call_module,
            total_hotkey_stake_call_function,
            hotkey
        )

# Example usage
if __name__ == "__main__":
    config = {
        "FULL_PROPORTION": 18446744073709551615,
        "SUBTENSORMODULE": '658faa385070e074c85bf6b568cf0555',
        "PARENTKEYS_FUNCTION": 'de41ae13ae40a9d3c5fd9b3bdea86fe2',
        "TOTALHOTKEYSTAKE_FUNCTION": '7b4e834c482cd6f103e108dacad0ab65',
        "CHAIN_ENDPOINT": "wss://entrypoint-finney.opentensor.ai:443",
        "DATABASE_DIR": "db"
    }
    
    monitor = ParentkeyMonitor(config)
    monitor.monitor_parentkeys()
