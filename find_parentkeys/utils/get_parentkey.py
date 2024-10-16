import json
import hashlib
import asyncio
import websockets
from dotenv import load_dotenv
from substrateinterface import Keypair
from substrateinterface.utils.ss58 import ss58_encode, ss58_decode
from typing import List, Dict

load_dotenv()

class RPCRequest:
    """Handles RPC requests and address conversions."""

    def __init__(self, chain_endpoint: str, full_proportion: int) -> None:
        """Initialize with chain endpoint and full proportion."""
        self.chain_endpoint = chain_endpoint
        self.full_proportion = full_proportion

    def convert_ss58_to_hex(self, ss58_address: str) -> str:
        """Convert SS58 address to hex format."""
        address_bytes = ss58_decode(ss58_address)
        if isinstance(address_bytes, str):
            address_bytes = bytes.fromhex(address_bytes)
        return address_bytes.hex()

    def convert_hex_to_ss58(self, hex_string: str, ss58_format: int = 42) -> str:
        """Convert hex string to SS58 address."""
        public_key_hex = hex_string[-64:]
        public_key = bytes.fromhex(public_key_hex)
        if len(public_key) != 32:
            raise ValueError('Public key should be 32 bytes long')
        keypair = Keypair(public_key=public_key, ss58_format=ss58_format)
        return keypair.ss58_address

    def ss58_to_blake2_128concat(self, ss58_address: str) -> bytes:
        """Convert SS58 address to Blake2b hash with original account ID."""
        keypair = Keypair(ss58_address=ss58_address)
        account_id = keypair.public_key
        blake2b_hash = hashlib.blake2b(account_id, digest_size=16)
        return blake2b_hash.digest() + account_id

    def decimal_to_hex(self, decimal_num: int) -> str:
        """Convert decimal number to hexadecimal string."""
        return hex(decimal_num)[2:].zfill(4) + '00'  # Ensure 4 digits

    async def call_rpc(self, call_params: List[str]) -> List[Dict]:
        """Call the RPC and return the results."""
        async with websockets.connect(self.chain_endpoint, ping_interval=None) as ws:
            await ws.send(json.dumps({
                "jsonrpc": "2.0",
                "id": 1,
                "method": "state_subscribeStorage",
                'params': [call_params],
            }))
            await ws.recv()  # Ignore confirmation response
            response = await ws.recv()
            changes = json.loads(response)["params"]["result"]["changes"]
            return changes

    def reverse_hex(self, hex_string: str) -> str:
        """Reverse a hexadecimal string."""
        if len(hex_string) != 16:
            raise ValueError("Input must be a 16-character hexadecimal string.")
        return '0x' + ''.join(reversed([hex_string[i:i + 2] for i in range(0, len(hex_string), 2)]))

    def hex_to_decimal(self, hex_str: str) -> int:
        """Convert hexadecimal string to decimal number."""
        return int(hex_str, 16)

    def extract_net_uid(self, net_uid_info: str) -> int:
        """Extract net UID from the given information."""
        return self.hex_to_decimal(net_uid_info[-4:-2])

    def get_num_results(self, results: str) -> int:
        """Get the number of results from the hex string."""
        num_results = self.hex_to_decimal(results[:4])
        return num_results // 4

    def get_parent_keys(self, call_module: str, call_function: str, hotkey: str, net_uids: List[int]) -> List[Dict]:
        """Retrieve parent keys for a given hotkey."""
        call_params = []
        blake2_128concat = self.ss58_to_blake2_128concat(hotkey).hex()
        for net_uid in net_uids:
            net_uid_hex = self.decimal_to_hex(net_uid)
            call_hex = '0x' + call_module + call_function + blake2_128concat + net_uid_hex
            call_params.append(call_hex)
        call_results = asyncio.run(self.call_rpc(call_params))
        return self._parse_parent_keys(call_results)

    def _parse_parent_keys(self, call_results: List[Dict]) -> List[Dict]:
        """Parse parent keys from the call results."""
        parent_keys = []
        for call_result in call_results:
            if call_result[1] is not None:
                net_uid = self.extract_net_uid(call_result[0])
                parent_hex = call_result[1]
                parent_hotkey_hexs = [parent_hex[i:i + 80] for i in range(4, len(parent_hex), 80)]
                for parent_hotkey_hex in parent_hotkey_hexs:
                    parent_hotkey = self.convert_hex_to_ss58(parent_hotkey_hex)
                    parent_proportion_decimal = self.hex_to_decimal(self.reverse_hex(parent_hotkey_hex[:16]))
                    parent_proportion = round(parent_proportion_decimal / self.full_proportion, 4)
                    parent_keys.append({
                        'hotkey': parent_hotkey,
                        'proportion': parent_proportion,
                        'net_uid': net_uid,
                    })
        return parent_keys

    def get_stake_from_hotkey(self, call_module: str, call_function: str, hotkey: str) -> float:
        """Retrieve stake for the given hotkey."""
        hex_address = self.convert_ss58_to_hex(hotkey)
        call_hex = '0x' + call_module + call_function + hex_address
        call_params = [call_hex]
        call_results = asyncio.run(self.call_rpc(call_params))
        if call_results[0][1] is not None:
            stake_hex = call_results[0][1][2:]
            stake = self.hex_to_decimal(self.reverse_hex(stake_hex))
            return round(stake / 1e9, 4)
        return 0.0
