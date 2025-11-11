"""
Insanidad - A Simple Blockchain Implementation

This module implements a basic blockchain with proof-of-work mining,
transaction support, and chain validation.
"""

import hashlib
import json
import time
from typing import List, Dict, Any, Optional


class Block:
    """Represents a single block in the blockchain."""
    
    def __init__(
        self,
        index: int,
        timestamp: float,
        transactions: List[Dict[str, Any]],
        previous_hash: str,
        nonce: int = 0
    ):
        """
        Initialize a new block.
        
        Args:
            index: Position of the block in the chain
            timestamp: Time when the block was created
            transactions: List of transactions in this block
            previous_hash: Hash of the previous block
            nonce: Number used for proof-of-work mining
        """
        self.index = index
        self.timestamp = timestamp
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = self.calculate_hash()
    
    def calculate_hash(self) -> str:
        """
        Calculate the SHA-256 hash of the block.
        
        Returns:
            Hexadecimal string representation of the hash
        """
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": self.transactions,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert block to dictionary representation.
        
        Returns:
            Dictionary containing block data
        """
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": self.transactions,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
            "hash": self.hash
        }


class Blockchain:
    """Represents the blockchain and manages its operations."""
    
    def __init__(self, difficulty: int = 4):
        """
        Initialize a new blockchain.
        
        Args:
            difficulty: Number of leading zeros required in hash for proof-of-work
        """
        self.chain: List[Block] = []
        self.difficulty = difficulty
        self.pending_transactions: List[Dict[str, Any]] = []
        self.mining_reward = 100
        
        # Create the genesis block
        self.create_genesis_block()
    
    def create_genesis_block(self) -> None:
        """Create the first block in the blockchain."""
        genesis_block = Block(0, time.time(), [], "0")
        genesis_block.hash = self.mine_block(genesis_block)
        self.chain.append(genesis_block)
    
    def get_latest_block(self) -> Block:
        """
        Get the most recent block in the chain.
        
        Returns:
            The last block in the chain
        """
        return self.chain[-1]
    
    def mine_block(self, block: Block) -> str:
        """
        Mine a block using proof-of-work.
        
        Args:
            block: The block to mine
            
        Returns:
            The valid hash for the block
        """
        target = "0" * self.difficulty
        
        while block.hash[:self.difficulty] != target:
            block.nonce += 1
            block.hash = block.calculate_hash()
        
        return block.hash
    
    def add_transaction(
        self,
        sender: str,
        recipient: str,
        amount: float
    ) -> bool:
        """
        Add a new transaction to pending transactions.
        
        Args:
            sender: Address of the sender
            recipient: Address of the recipient
            amount: Amount to transfer
            
        Returns:
            True if transaction was added successfully
        """
        if amount <= 0:
            return False
        
        transaction = {
            "sender": sender,
            "recipient": recipient,
            "amount": amount,
            "timestamp": time.time()
        }
        
        self.pending_transactions.append(transaction)
        return True
    
    def mine_pending_transactions(self, miner_address: str) -> bool:
        """
        Mine all pending transactions and reward the miner.
        
        Args:
            miner_address: Address of the miner to receive the reward
            
        Returns:
            True if mining was successful
        """
        if not self.pending_transactions:
            return False
        
        # Create new block with pending transactions
        block = Block(
            index=len(self.chain),
            timestamp=time.time(),
            transactions=self.pending_transactions,
            previous_hash=self.get_latest_block().hash
        )
        
        # Mine the block
        block.hash = self.mine_block(block)
        self.chain.append(block)
        
        # Reset pending transactions and add mining reward
        self.pending_transactions = [{
            "sender": "network",
            "recipient": miner_address,
            "amount": self.mining_reward,
            "timestamp": time.time()
        }]
        
        return True
    
    def get_balance(self, address: str) -> float:
        """
        Get the balance of an address.
        
        Args:
            address: The address to check
            
        Returns:
            The balance of the address
        """
        balance = 0.0
        
        for block in self.chain:
            for transaction in block.transactions:
                if transaction.get("sender") == address:
                    balance -= transaction.get("amount", 0)
                if transaction.get("recipient") == address:
                    balance += transaction.get("amount", 0)
        
        # Include pending transactions
        for transaction in self.pending_transactions:
            if transaction.get("sender") == address:
                balance -= transaction.get("amount", 0)
            if transaction.get("recipient") == address:
                balance += transaction.get("amount", 0)
        
        return balance
    
    def is_chain_valid(self) -> bool:
        """
        Validate the entire blockchain.
        
        Returns:
            True if the chain is valid, False otherwise
        """
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            
            # Verify current block's hash
            if current_block.hash != current_block.calculate_hash():
                return False
            
            # Verify link to previous block
            if current_block.previous_hash != previous_block.hash:
                return False
            
            # Verify proof-of-work
            target = "0" * self.difficulty
            if current_block.hash[:self.difficulty] != target:
                return False
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert blockchain to dictionary representation.
        
        Returns:
            Dictionary containing blockchain data
        """
        return {
            "chain": [block.to_dict() for block in self.chain],
            "difficulty": self.difficulty,
            "pending_transactions": self.pending_transactions,
            "mining_reward": self.mining_reward
        }


def main():
    """Demonstrate the blockchain functionality."""
    print("=== Insanidad Blockchain Demo ===\n")
    
    # Create a new blockchain
    print("Creating blockchain with difficulty 4...")
    blockchain = Blockchain(difficulty=4)
    
    # Add transactions
    print("\nAdding transactions...")
    blockchain.add_transaction("Alice", "Bob", 50)
    blockchain.add_transaction("Bob", "Charlie", 25)
    
    # Mine the transactions
    print("Mining pending transactions...")
    start_time = time.time()
    blockchain.mine_pending_transactions("Miner1")
    end_time = time.time()
    print(f"Block mined in {end_time - start_time:.2f} seconds")
    
    # Add more transactions
    print("\nAdding more transactions...")
    blockchain.add_transaction("Alice", "Charlie", 30)
    
    # Mine again
    print("Mining pending transactions...")
    start_time = time.time()
    blockchain.mine_pending_transactions("Miner1")
    end_time = time.time()
    print(f"Block mined in {end_time - start_time:.2f} seconds")
    
    # Check balances
    print("\n=== Balances ===")
    print(f"Alice: {blockchain.get_balance('Alice')}")
    print(f"Bob: {blockchain.get_balance('Bob')}")
    print(f"Charlie: {blockchain.get_balance('Charlie')}")
    print(f"Miner1: {blockchain.get_balance('Miner1')}")
    
    # Validate chain
    print(f"\n=== Chain Validation ===")
    print(f"Is blockchain valid? {blockchain.is_chain_valid()}")
    
    # Display blockchain
    print(f"\n=== Blockchain Details ===")
    print(f"Total blocks: {len(blockchain.chain)}")
    for block in blockchain.chain:
        print(f"\nBlock #{block.index}")
        print(f"  Hash: {block.hash}")
        print(f"  Previous Hash: {block.previous_hash}")
        print(f"  Transactions: {len(block.transactions)}")
        print(f"  Nonce: {block.nonce}")


if __name__ == "__main__":
    main()
