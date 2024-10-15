import os
import sys
import logging
import json
import django
from django.core.management import call_command
from django.db import connection
import bittensor as bt
from dotenv import load_dotenv
from find_childkey.utils.get_parentkey import RPCRequest

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bt_childkey_monitor.settings')

django.setup()

from validators.models import Validators, ValidatorChildKeyInfo

load_dotenv()

sys.stdout = open('output.txt', 'w')

logging.basicConfig(level=logging.INFO)

subtensorModule = '658faa385070e074c85bf6b568cf0555'  # fex code for SubtensorModule call_module
parentKeys = 'de41ae13ae40a9d3c5fd9b3bdea86fe2'  # fex code for parentkeys call_function

GetParentKeys = RPCRequest(subtensorModule, parentKeys)

# Retrieve chain endpoint from environment variables
chain_endpoint = os.getenv("CHAIN_ENDPOINT")
if not chain_endpoint:
    raise ValueError("CHAIN_ENDPOINT environment variable is not set.")

subtensor = bt.Subtensor(network=chain_endpoint)

def delete_database_file():
    print("Deleting database file")
    db_path = '/Users/mac/Documents/work/Rhef/bt-child-monitor/db/db.sqlite3'
    print(db_path)
    if os.path.exists(db_path):
        os.remove(db_path)
        print("Deleted database file")
    else:
        print("Database file does not exist, skipping deletion")

def recreate_validators_table():
    call_command('makemigrations')
    call_command('migrate')
    print("Recreated validators_validators table")

def get_subnet_validators(netuid, subtensor):
    big_validators = {}
    metagraph = subtensor.metagraph(netuid)
    neuron_uids = metagraph.uids.tolist()
    stakes = metagraph.S.tolist()
    hotkeys = metagraph.hotkeys
    coldkeys = metagraph.coldkeys
    for i in range(len(neuron_uids)):
        if stakes[i] > 1000:
            validator = Validators(coldkey=coldkeys[i], hotkey=hotkeys[i], stake=stakes[i])
            parentkey_netuids = validator.get_parentkey_netuids()  # Deserialize JSON to list
            parentkey_netuids.append(netuid)
            validator.parentkey_netuids = json.dumps(parentkey_netuids)  # Serialize back to JSON
            big_validators[validator] = validator
    return list(big_validators.values())

def get_all_validators(subnet_net_uids, subtensor):
    all_validators = {}
    for netuid in subnet_net_uids:
        subnet_validators = get_subnet_validators(netuid, subtensor)
        for validator in subnet_validators:
            if validator not in all_validators:
                all_validators[validator] = validator
    return list(all_validators.values())

def get_subnet_uids(subtensor):
    try:
        subnet_uids = subtensor.get_subnets()
        return subnet_uids
    except Exception as e:
        logging.error(f"Error retrieving subnet UIDs: {e}")
        return []

def create_validator_childkey_tables(parent_validators):
    for validator in parent_validators:
        parent_coldkey = validator.coldkey
        parent_hotkey = validator.hotkey
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
                # child_stake=child_info['proportion'],
                stake_proportion=child_info['proportion'],
                subnet_uid=child_info['net_uid']
            )

    print("Created entries for all parent validators")

if __name__ == "__main__":

    delete_database_file()

    recreate_validators_table()

    subnet_uids = get_subnet_uids(subtensor)
    
    subnet_uids.remove(0)    
    # subnet_uids = [49, 50]
    all_validators = get_all_validators(subnet_uids, subtensor)
    for validator in all_validators:
        logging.info(f"Validator: {validator.__dict__}")

    for validator in all_validators:     
        logging.info(f"Validator: {validator.__dict__}")
        parent_keys = GetParentKeys.get_parent_keys(validator.hotkey, subnet_uids)
        print(parent_keys)

        for parent_key in parent_keys:
            validator.add_parentkeys(parent_key['hotkey'], parent_key['proportion'], parent_key['net_uid'])
            
            parent_validator = next((v for v in all_validators if v.hotkey == parent_key['hotkey']), None)

            if parent_validator is None:
                # If parent validator does not exist, create a new Validator instance
                parent_validator = Validators(coldkey='', hotkey=parent_key['hotkey'], stake=0)
                all_validators.append(parent_validator)

            # Add the current validator's hotkey as a childkey to the parent validator
            parent_validator.add_childkeys(validator.hotkey, parent_key['proportion'], parent_key['net_uid'])

    print("\nAll Validators after adding parent and child keys:")
    for validator in all_validators:
        print(validator.__dict__)
        validator_model, created = Validators.objects.update_or_create(
            hotkey=validator.hotkey,
            defaults={
                        'coldkey': validator.coldkey,
                        'stake': validator.stake,
                        'parentkeys': json.dumps(validator.parentkeys),  # Serialize to JSON
                        'childkeys': json.dumps(validator.childkeys)   # Serialize to JSON
                    }
                    )

    # Create entries for all parent validators
    create_validator_childkey_tables(all_validators)

    # Run migrations after creating entries
    call_command('makemigrations')
    call_command('migrate')
    print("Migrations completed")