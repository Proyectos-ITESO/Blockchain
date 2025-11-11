"""
Python script to interact with the deployed Notary contract
Usage: python interact.py
"""
import os
import sys
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from web3 import Web3
from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path(__file__).parent.parent.parent / '.env')


def load_contract():
    """Load contract ABI and address"""
    # Load ABI
    abi_path = Path(__file__).parent.parent.parent / 'app' / 'services' / 'notary_abi.json'
    with open(abi_path, 'r') as f:
        abi = json.load(f)

    # Load deployment info
    network = "sepolia"  # Change as needed
    deployment_path = Path(__file__).parent.parent / 'deployments' / f'{network}.json'

    if not deployment_path.exists():
        raise FileNotFoundError(f"Deployment file not found: {deployment_path}")

    with open(deployment_path, 'r') as f:
        deployment_info = json.load(f)

    return abi, deployment_info['address']


def main():
    """Main interaction script"""
    # Connect to blockchain
    rpc_url = os.getenv('BLOCKCHAIN_RPC_URL')
    if not rpc_url:
        raise ValueError("BLOCKCHAIN_RPC_URL not set in .env")

    w3 = Web3(Web3.HTTPProvider(rpc_url))

    if not w3.is_connected():
        raise ConnectionError("Failed to connect to blockchain")

    print(f"Connected to blockchain: {w3.is_connected()}")
    print(f"Chain ID: {w3.eth.chain_id}")

    # Load contract
    abi, contract_address = load_contract()
    contract = w3.eth.contract(address=contract_address, abi=abi)

    print(f"\nContract address: {contract_address}")

    # Example: Register a hash
    test_hash = "0x" + "a" * 64  # Example hash
    print(f"\nTest hash: {test_hash}")

    # Check if hash is already registered
    is_registered = contract.functions.verifyHash(test_hash).call()
    print(f"Is hash registered: {is_registered}")

    if not is_registered:
        print("\nTo register this hash, you need to send a transaction.")
        print("This requires gas fees and a private key.")

        private_key = os.getenv('BLOCKCHAIN_PRIVATE_KEY')
        if private_key:
            account = w3.eth.account.from_key(private_key)
            print(f"Account address: {account.address}")

            # Build transaction
            nonce = w3.eth.get_transaction_count(account.address)

            transaction = contract.functions.registerHash(test_hash).build_transaction({
                'chainId': w3.eth.chain_id,
                'gas': 100000,
                'gasPrice': w3.eth.gas_price,
                'nonce': nonce,
            })

            # Sign transaction
            signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)

            # Send transaction
            print("\nSending transaction...")
            tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            print(f"Transaction hash: {tx_hash.hex()}")

            # Wait for receipt
            print("Waiting for transaction receipt...")
            tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
            print(f"Transaction successful! Block: {tx_receipt['blockNumber']}")

            # Verify registration
            is_registered = contract.functions.verifyHash(test_hash).call()
            print(f"Hash now registered: {is_registered}")
    else:
        # Get hash info
        registered, timestamp, registrar = contract.functions.getHashInfo(test_hash).call()
        print(f"\nHash info:")
        print(f"  Registered: {registered}")
        print(f"  Timestamp: {timestamp}")
        print(f"  Registrar: {registrar}")


if __name__ == "__main__":
    main()
