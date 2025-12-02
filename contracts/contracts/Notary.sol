// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title Notary
 * @dev Smart contract for notarizing message hashes on blockchain
 * @notice This contract allows registering SHA-256 hashes of messages for verification
 */
contract Notary {
    // Mapping to track registered hashes
    mapping(bytes32 => bool) public isHashRegistered;

    // Mapping to track when a hash was registered
    mapping(bytes32 => uint256) public hashTimestamp;

    // Mapping to track who registered the hash
    mapping(bytes32 => address) public hashRegistrar;

    // Event emitted when a hash is registered
    event HashRegistered(
        address indexed registrar,
        bytes32 indexed hash,
        uint256 timestamp
    );

    /**
     * @dev Register a message hash on the blockchain
     * @param _hash The SHA-256 hash of the message (bytes32)
     */
    function registerHash(bytes32 _hash) public {
        require(!isHashRegistered[_hash], "Hash already registered");
        require(_hash != bytes32(0), "Invalid hash");

        isHashRegistered[_hash] = true;
        hashTimestamp[_hash] = block.timestamp;
        hashRegistrar[_hash] = msg.sender;

        emit HashRegistered(msg.sender, _hash, block.timestamp);
    }

    /**
     * @dev Check if a hash is registered
     * @param _hash The hash to verify
     * @return bool True if the hash is registered
     */
    function verifyHash(bytes32 _hash) public view returns (bool) {
        return isHashRegistered[_hash];
    }

    /**
     * @dev Get detailed information about a registered hash
     * @param _hash The hash to query
     * @return registered Whether the hash is registered
     * @return timestamp When the hash was registered
     * @return registrar Who registered the hash
     */
    function getHashInfo(bytes32 _hash) public view returns (
        bool registered,
        uint256 timestamp,
        address registrar
    ) {
        return (
            isHashRegistered[_hash],
            hashTimestamp[_hash],
            hashRegistrar[_hash]
        );
    }
}
