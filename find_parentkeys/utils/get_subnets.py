import bittensor as bt
from dotenv import load_dotenv

from substrateinterface import SubstrateInterface


def get_subnet_uids(subtensor):
    subnet_uids = subtensor.get_subnets()
    print(subnet_uids)
    return subnet_uids