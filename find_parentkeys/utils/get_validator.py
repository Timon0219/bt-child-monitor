import bittensor as bt
import os

from dotenv import load_dotenv

def get_subnet_validators(netuid, subtensor):
    big_validators = []
    metagraph = subtensor.metagraph(netuid)
    neuron_uids = metagraph.uids.tolist()
    stakes = metagraph.S.tolist()
    hotkeys = metagraph.hotkeys
    coldkeys = metagraph.coldkeys
    for i in range(len(neuron_uids)):
        if stakes[i] > 1000:
            big_validators.append({'coldkey' : coldkeys[i], 'hotkey' : hotkeys[i], 'stake' : stakes[i], 'net_uid' : netuid})
    return big_validators
        
if __name__ == "__main__":
    get_subnet_validators()