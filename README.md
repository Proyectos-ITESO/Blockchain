# Blockchain - Insanidad

A simple yet functional blockchain implementation in Python featuring proof-of-work mining, transaction management, and chain validation.

## Features

- **Block Creation**: Create blocks with transactions, timestamps, and cryptographic hashing
- **Proof-of-Work Mining**: Adjustable difficulty for mining new blocks
- **Transaction Management**: Add and process transactions between addresses
- **Balance Tracking**: Check balances for any address in the network
- **Chain Validation**: Verify the integrity of the entire blockchain
- **Mining Rewards**: Miners receive rewards for successfully mining blocks

## Installation

No external dependencies required! This implementation uses only Python's standard library.

```bash
# Clone the repository
git clone https://github.com/Proyectos-ITESO/Blockchain.git
cd Blockchain

# Run the demo
python3 blockchain.py

# Run tests
python3 -m unittest test_blockchain.py -v
```

## Usage

### Basic Example

```python
from blockchain import Blockchain

# Create a new blockchain with difficulty 4
blockchain = Blockchain(difficulty=4)

# Add transactions
blockchain.add_transaction("Alice", "Bob", 50)
blockchain.add_transaction("Bob", "Charlie", 25)

# Mine the pending transactions
blockchain.mine_pending_transactions("Miner1")

# Check balances
print(f"Alice's balance: {blockchain.get_balance('Alice')}")
print(f"Bob's balance: {blockchain.get_balance('Bob')}")
print(f"Charlie's balance: {blockchain.get_balance('Charlie')}")

# Validate the blockchain
print(f"Is blockchain valid? {blockchain.is_chain_valid()}")
```

### Running the Demo

```bash
python3 blockchain.py
```

This will run a demonstration that:
1. Creates a new blockchain
2. Adds several transactions
3. Mines blocks
4. Shows balances for all participants
5. Validates the blockchain integrity
6. Displays detailed information about each block

## Architecture

### Block Class

Represents a single block in the blockchain with:
- Index (position in chain)
- Timestamp
- List of transactions
- Previous block hash
- Nonce (for proof-of-work)
- Current block hash

### Blockchain Class

Manages the entire blockchain with methods for:
- Creating genesis block
- Adding transactions
- Mining blocks with proof-of-work
- Calculating balances
- Validating chain integrity

## Testing

Run the comprehensive test suite:

```bash
python3 -m unittest test_blockchain.py -v
```

The test suite includes:
- Block creation and hashing tests
- Transaction validation tests
- Mining functionality tests
- Balance calculation tests
- Chain validation tests
- Tampering detection tests

## Technical Details

- **Hashing**: Uses SHA-256 for cryptographic hashing
- **Proof-of-Work**: Adjustable difficulty (default: 4 leading zeros)
- **Mining Reward**: 100 units per block (configurable)
- **Consensus**: Longest valid chain wins

## Security Features

- Cryptographic hashing ensures data integrity
- Proof-of-work prevents easy chain manipulation
- Chain validation detects tampering attempts
- Transaction validation prevents invalid operations

## License

This project is for educational purposes.