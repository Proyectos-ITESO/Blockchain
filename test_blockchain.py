"""
Unit tests for the Insanidad blockchain implementation.
"""

import unittest
import time
from blockchain import Block, Blockchain


class TestBlock(unittest.TestCase):
    """Test cases for the Block class."""
    
    def test_block_creation(self):
        """Test that a block can be created with correct attributes."""
        block = Block(
            index=1,
            timestamp=time.time(),
            transactions=[{"sender": "Alice", "recipient": "Bob", "amount": 50}],
            previous_hash="0" * 64
        )
        
        self.assertEqual(block.index, 1)
        self.assertEqual(len(block.transactions), 1)
        self.assertIsNotNone(block.hash)
        self.assertEqual(len(block.hash), 64)  # SHA-256 produces 64 hex characters
    
    def test_hash_calculation(self):
        """Test that hash calculation is deterministic."""
        block1 = Block(1, 123456789, [], "0")
        block2 = Block(1, 123456789, [], "0")
        
        self.assertEqual(block1.hash, block2.hash)
    
    def test_hash_changes_with_data(self):
        """Test that hash changes when block data changes."""
        block1 = Block(1, 123456789, [], "0")
        block2 = Block(1, 123456789, [{"test": "data"}], "0")
        
        self.assertNotEqual(block1.hash, block2.hash)
    
    def test_to_dict(self):
        """Test block dictionary representation."""
        block = Block(1, 123456789, [], "0")
        block_dict = block.to_dict()
        
        self.assertIn("index", block_dict)
        self.assertIn("timestamp", block_dict)
        self.assertIn("transactions", block_dict)
        self.assertIn("previous_hash", block_dict)
        self.assertIn("nonce", block_dict)
        self.assertIn("hash", block_dict)


class TestBlockchain(unittest.TestCase):
    """Test cases for the Blockchain class."""
    
    def setUp(self):
        """Set up a blockchain for testing."""
        self.blockchain = Blockchain(difficulty=2)  # Lower difficulty for faster tests
    
    def test_genesis_block(self):
        """Test that genesis block is created correctly."""
        self.assertEqual(len(self.blockchain.chain), 1)
        self.assertEqual(self.blockchain.chain[0].index, 0)
        self.assertEqual(self.blockchain.chain[0].previous_hash, "0")
    
    def test_add_transaction(self):
        """Test adding a transaction."""
        result = self.blockchain.add_transaction("Alice", "Bob", 50)
        
        self.assertTrue(result)
        self.assertEqual(len(self.blockchain.pending_transactions), 1)
        self.assertEqual(self.blockchain.pending_transactions[0]["amount"], 50)
    
    def test_reject_negative_transaction(self):
        """Test that negative amount transactions are rejected."""
        result = self.blockchain.add_transaction("Alice", "Bob", -50)
        
        self.assertFalse(result)
        self.assertEqual(len(self.blockchain.pending_transactions), 0)
    
    def test_reject_zero_transaction(self):
        """Test that zero amount transactions are rejected."""
        result = self.blockchain.add_transaction("Alice", "Bob", 0)
        
        self.assertFalse(result)
        self.assertEqual(len(self.blockchain.pending_transactions), 0)
    
    def test_mine_block(self):
        """Test mining a block."""
        self.blockchain.add_transaction("Alice", "Bob", 50)
        result = self.blockchain.mine_pending_transactions("Miner1")
        
        self.assertTrue(result)
        self.assertEqual(len(self.blockchain.chain), 2)
        
        # Check that the new block's hash starts with required zeros
        new_block = self.blockchain.chain[-1]
        self.assertTrue(new_block.hash.startswith("0" * self.blockchain.difficulty))
    
    def test_no_mining_without_transactions(self):
        """Test that mining fails when there are no pending transactions."""
        result = self.blockchain.mine_pending_transactions("Miner1")
        
        self.assertFalse(result)
        self.assertEqual(len(self.blockchain.chain), 1)  # Only genesis block
    
    def test_balance_calculation(self):
        """Test balance calculation for addresses."""
        self.blockchain.add_transaction("Alice", "Bob", 50)
        self.blockchain.mine_pending_transactions("Miner1")
        
        self.blockchain.add_transaction("Bob", "Charlie", 25)
        self.blockchain.mine_pending_transactions("Miner1")
        
        # Alice sent 50
        self.assertEqual(self.blockchain.get_balance("Alice"), -50)
        
        # Bob received 50, sent 25
        self.assertEqual(self.blockchain.get_balance("Bob"), 25)
        
        # Charlie received 25
        self.assertEqual(self.blockchain.get_balance("Charlie"), 25)
        
        # Miner1 received rewards (should be in pending after second mining)
        miner_balance = self.blockchain.get_balance("Miner1")
        self.assertGreater(miner_balance, 0)
    
    def test_chain_validation(self):
        """Test blockchain validation."""
        self.blockchain.add_transaction("Alice", "Bob", 50)
        self.blockchain.mine_pending_transactions("Miner1")
        
        # Valid chain
        self.assertTrue(self.blockchain.is_chain_valid())
    
    def test_chain_invalidation_on_tampering(self):
        """Test that tampering invalidates the chain."""
        self.blockchain.add_transaction("Alice", "Bob", 50)
        self.blockchain.mine_pending_transactions("Miner1")
        
        # Tamper with a transaction
        self.blockchain.chain[1].transactions[0]["amount"] = 100
        
        # Chain should now be invalid
        self.assertFalse(self.blockchain.is_chain_valid())
    
    def test_get_latest_block(self):
        """Test getting the latest block."""
        latest = self.blockchain.get_latest_block()
        self.assertEqual(latest, self.blockchain.chain[-1])
        
        self.blockchain.add_transaction("Alice", "Bob", 50)
        self.blockchain.mine_pending_transactions("Miner1")
        
        new_latest = self.blockchain.get_latest_block()
        self.assertEqual(new_latest, self.blockchain.chain[-1])
        self.assertNotEqual(new_latest, latest)
    
    def test_to_dict(self):
        """Test blockchain dictionary representation."""
        blockchain_dict = self.blockchain.to_dict()
        
        self.assertIn("chain", blockchain_dict)
        self.assertIn("difficulty", blockchain_dict)
        self.assertIn("pending_transactions", blockchain_dict)
        self.assertIn("mining_reward", blockchain_dict)
        
        self.assertEqual(blockchain_dict["difficulty"], 2)
        self.assertIsInstance(blockchain_dict["chain"], list)


if __name__ == "__main__":
    unittest.main()
