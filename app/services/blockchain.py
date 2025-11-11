"""
Blockchain service for interacting with Notary smart contract
"""
import json
import logging
from pathlib import Path
from typing import Optional, Tuple

from web3 import Web3
from web3.exceptions import ContractLogicError
from eth_account import Account

from app.core.config import settings

logger = logging.getLogger(__name__)


class BlockchainService:
    """
    Service for interacting with the Notary smart contract
    """

    def __init__(self):
        """
        Initialize Web3 connection and contract
        """
        self.w3 = None
        self.contract = None
        self.account = None
        self._initialize()

    def _initialize(self):
        """
        Setup Web3 connection and load contract
        """
        try:
            # Connect to blockchain
            self.w3 = Web3(Web3.HTTPProvider(settings.BLOCKCHAIN_RPC_URL))

            if not self.w3.is_connected():
                logger.error("Failed to connect to blockchain")
                return

            logger.info(f"Connected to blockchain. Chain ID: {self.w3.eth.chain_id}")

            # Load account from private key
            if settings.BLOCKCHAIN_PRIVATE_KEY:
                self.account = Account.from_key(settings.BLOCKCHAIN_PRIVATE_KEY)
                logger.info(f"Loaded account: {self.account.address}")
            else:
                logger.warning("No private key configured. Read-only mode.")

            # Load contract ABI
            abi_path = Path(__file__).parent / 'notary_abi.json'
            if not abi_path.exists():
                logger.error(f"Contract ABI not found at {abi_path}")
                return

            with open(abi_path, 'r') as f:
                contract_abi = json.load(f)

            # Load contract
            if settings.CONTRACT_ADDRESS:
                self.contract = self.w3.eth.contract(
                    address=settings.CONTRACT_ADDRESS,
                    abi=contract_abi
                )
                logger.info(f"Loaded contract at: {settings.CONTRACT_ADDRESS}")
            else:
                logger.warning("No contract address configured")

        except Exception as e:
            logger.error(f"Error initializing blockchain service: {e}")

    def is_connected(self) -> bool:
        """
        Check if connected to blockchain
        """
        return self.w3 is not None and self.w3.is_connected()

    def verify_hash(self, message_hash: str) -> bool:
        """
        Verify if a hash is registered on the blockchain

        Args:
            message_hash: Hash to verify (hex string with 0x prefix)

        Returns:
            bool: True if hash is registered, False otherwise
        """
        if not self.contract:
            logger.error("Contract not initialized")
            return False

        try:
            # Convert hash string to bytes32
            if not message_hash.startswith('0x'):
                message_hash = '0x' + message_hash

            # Call contract function
            is_registered = self.contract.functions.verifyHash(message_hash).call()

            logger.info(f"Hash {message_hash[:10]}... verification: {is_registered}")
            return is_registered

        except Exception as e:
            logger.error(f"Error verifying hash: {e}")
            return False

    def register_hash(self, message_hash: str) -> Optional[str]:
        """
        Register a hash on the blockchain

        Args:
            message_hash: Hash to register (hex string with 0x prefix)

        Returns:
            Optional[str]: Transaction hash if successful, None otherwise
        """
        if not self.contract:
            logger.error("Contract not initialized")
            return None

        if not self.account:
            logger.error("No account configured. Cannot send transactions.")
            return None

        try:
            # Convert hash string to bytes32
            if not message_hash.startswith('0x'):
                message_hash = '0x' + message_hash

            # Check if already registered
            if self.verify_hash(message_hash):
                logger.warning(f"Hash {message_hash[:10]}... already registered")
                return None

            # Get nonce
            nonce = self.w3.eth.get_transaction_count(self.account.address)

            # Build transaction
            transaction = self.contract.functions.registerHash(message_hash).build_transaction({
                'chainId': self.w3.eth.chain_id,
                'gas': 100000,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': nonce,
            })

            # Sign transaction
            signed_txn = self.w3.eth.account.sign_transaction(
                transaction,
                private_key=self.account.key
            )

            # Send transaction
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            tx_hash_hex = tx_hash.hex()

            logger.info(f"Transaction sent: {tx_hash_hex}")
            logger.info(f"Registered hash: {message_hash[:10]}...")

            return tx_hash_hex

        except ContractLogicError as e:
            logger.error(f"Contract logic error: {e}")
            return None

        except Exception as e:
            logger.error(f"Error registering hash: {e}")
            return None

    def get_transaction_receipt(self, tx_hash: str) -> Optional[dict]:
        """
        Get transaction receipt

        Args:
            tx_hash: Transaction hash

        Returns:
            Optional[dict]: Transaction receipt if available
        """
        if not self.w3:
            return None

        try:
            receipt = self.w3.eth.get_transaction_receipt(tx_hash)
            return dict(receipt)
        except Exception as e:
            logger.error(f"Error getting transaction receipt: {e}")
            return None

    def wait_for_transaction(self, tx_hash: str, timeout: int = 120) -> Optional[dict]:
        """
        Wait for transaction to be mined

        Args:
            tx_hash: Transaction hash
            timeout: Timeout in seconds

        Returns:
            Optional[dict]: Transaction receipt if successful
        """
        if not self.w3:
            return None

        try:
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=timeout)
            logger.info(f"Transaction {tx_hash[:10]}... mined in block {receipt['blockNumber']}")
            return dict(receipt)
        except Exception as e:
            logger.error(f"Error waiting for transaction: {e}")
            return None

    def get_hash_info(self, message_hash: str) -> Optional[Tuple[bool, int, str]]:
        """
        Get detailed information about a registered hash

        Args:
            message_hash: Hash to query

        Returns:
            Tuple of (registered, timestamp, registrar) or None
        """
        if not self.contract:
            return None

        try:
            if not message_hash.startswith('0x'):
                message_hash = '0x' + message_hash

            registered, timestamp, registrar = self.contract.functions.getHashInfo(message_hash).call()

            return (registered, timestamp, registrar)

        except Exception as e:
            logger.error(f"Error getting hash info: {e}")
            return None


# Global blockchain service instance
blockchain_service = BlockchainService()
