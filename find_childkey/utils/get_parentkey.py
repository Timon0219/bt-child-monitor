from substrateinterface.utils.ss58 import ss58_encode, ss58_decode
from substrateinterface import Keypair
import hashlib
import websockets
import asyncio
import json
from dotenv import load_dotenv
import os

load_dotenv()

# CHAIN_ENDPOINT = os.getenv("CHAIN_ENDPOINT") 
CHAIN_ENDPOINT = "wss://entrypoint-finney.opentensor.ai:443"
fullProportion = 18446744073709551615

class RPCRequest:
    def __init__(self, call_module, call_function):
        self.chain_endpoint = CHAIN_ENDPOINT
        self.fullProportion = fullProportion
        self.call_module = call_module
        self.call_function = call_function
            
    def convert_hex_to_ss58(self, hex_string: str, ss58_format: int = 42) -> str:
        # Extract the first 64 characters (32 bytes) for the public key
        public_key_hex = hex_string[-64:]
        
        # Convert hex string to bytes
        public_key = bytes.fromhex(public_key_hex)
        
        # Check if the public key is 32 bytes long
        if len(public_key) != 32:
            raise ValueError('Public key should be 32 bytes long')
        
        # Convert to SS58 address with specified ss58_format
        keypair = Keypair(public_key=public_key, ss58_format=ss58_format)
        return keypair.ss58_address

    def convert_ss58_to_hex(self, ss58_address):
        # Decode SS58 address to bytes
        address_str = ss58_decode(ss58_address)
        
        address_bytes = bytes(address_str, 'utf-8')
        
        # Convert bytes to hex string and add '0x' prefix
        hex_address = '0x' + address_bytes.hex()
        
        return hex_address

    def ss58_to_blake2_128concat(self, ss58_address: str) -> bytes:
        # Decode the SS58 address to get the raw account ID
        keypair = Keypair(ss58_address=ss58_address)
        account_id = keypair.public_key

        # Create a Blake2b hash object with a digest size of 16 bytes (128 bits)
        blake2b_hash = hashlib.blake2b(account_id, digest_size=16)
        # Get the digest
        hash_digest = blake2b_hash.digest()
        # Concatenate the hash with the original account ID
        result = hash_digest + account_id
        return result

    def decimal_to_hex(self, decimal_num):
        """
        Convert a decimal number to a hexadecimal string.
        
        :param decimal_num: Decimal number (e.g., 612345678901234567)
        :return: Hexadecimal string
        """
        hex_str = hex(decimal_num)[2:] + '00'  # Remove the '0x' prefix
        return hex_str.zfill(4) # Fill with leading zeros to ensure 4 digits

    async def call_rpc(self, call_params):
        async with websockets.connect(
            CHAIN_ENDPOINT, ping_interval=None
        ) as ws:
            await ws.send(json.dumps(
                {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "state_subscribeStorage",
                    'params' : [call_params]
                
                }
            ))
            ignore = await ws.recv()  # ignore the first response since it's a just a confirmation
            response = await ws.recv()
            changes = json.loads(response)["params"]["result"]["changes"]
            # print(changes)
            return changes

    def convert_hex_to_ss58(self, hex_string: str, ss58_format: int = 42) -> str:
        # Extract the first 64 characters (32 bytes) for the public key
        public_key_hex = hex_string[-64:]
        
        # Convert hex string to bytes
        public_key = bytes.fromhex(public_key_hex)
        
        # Check if the public key is 32 bytes long
        if len(public_key) != 32:
            raise ValueError('Public key should be 32 bytes long')
        
        # Convert to SS58 address with specified ss58_format
        keypair = Keypair(public_key=public_key, ss58_format=ss58_format)
        return keypair.ss58_address

    def reverse_hex(self, hex_string):
        # Ensure the string is exactly 16 characters long
        if len(hex_string) != 16:
            raise ValueError("Input must be a 16-character hexadecimal string.")
        
        # Split into pairs and reverse
        reversed_hex = ''.join(reversed([hex_string[i:i+2] for i in range(0, len(hex_string), 2)]))
        
        return '0x' + reversed_hex

    def hex_to_decimal(self, hex_str):
        """
        Convert a hexadecimal string to a decimal number.
        
        :param hex_str: Hexadecimal string (e.g., '0088eb51b81e85ab')
        :return: Decimal number
        """
        return int(hex_str, 16)

    def extract_net_uid(self, net_uid_info):
        net_uid = self.hex_to_decimal(net_uid_info[-4 : -2])
        return net_uid

    def get_num_results(self, results):
        num_results = self.hex_to_decimal(results[:4])
        return int(num_results / 4)

    def get_parent_keys(self, hotkey, net_uids):
        print("hotkey = ", hotkey, net_uids)
        blake2_128concat = self.ss58_to_blake2_128concat(hotkey).hex()
        call_params = []
        for net_uid in net_uids:
            net_uid_hex = self.decimal_to_hex(net_uid)
            call_hex = '0x' + self.call_module + self.call_function + blake2_128concat + net_uid_hex
            call_params.append(call_hex)

        call_results = asyncio.run(self.call_rpc(call_params))
        # result = call_parse(call_result)
        parent_keys = []
        print (call_results)

        for call_result in call_results:
            if call_result[1] is not None:
                net_uid = self.extract_net_uid(call_result[0])
                parent_hex = call_result[1]
                parent_hotkey_hexs = []
                # print(parent_hotkey_hexs)
                for i in range(4, len(parent_hex), 80):
                    parent_hotkey_hexs.append(parent_hex[i:i+80])
                for parent_hotkey_hex in parent_hotkey_hexs:
                    parent_hotkey = self.convert_hex_to_ss58(parent_hotkey_hex)
                    parent_proportion_demical = self.hex_to_decimal(self.reverse_hex(parent_hotkey_hex[:16]))
                    parent_proporton = parent_proportion_demical / self.fullProportion
                    parent_keys.append({'hotkey': parent_hotkey, 'proportion': parent_proporton, 'net_uid' : net_uid})
                
        # print(parent_keys)
        return parent_keys

