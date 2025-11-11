/**
 * End-to-End Encryption utilities using libsodium
 *
 * Uses X25519-XSalsa20-Poly1305 for encryption
 * SHA-256 for message hashing
 */

import sodium from 'libsodium-wrappers';

// Initialize sodium
let sodiumReady = false;

export async function initSodium() {
  if (!sodiumReady) {
    await sodium.ready;
    sodiumReady = true;
  }
  return sodium;
}

/**
 * Generate a new keypair for a user
 * Returns: { publicKey: Uint8Array, privateKey: Uint8Array }
 */
export async function generateKeyPair() {
  await initSodium();
  const keyPair = sodium.crypto_box_keypair();

  return {
    publicKey: keyPair.publicKey,
    privateKey: keyPair.privateKey,
  };
}

/**
 * Convert Uint8Array to base64 string for storage/transmission
 */
export function keyToString(key) {
  return sodium.to_base64(key, sodium.base64_variants.ORIGINAL);
}

/**
 * Convert base64 string back to Uint8Array
 */
export function stringToKey(keyString) {
  return sodium.from_base64(keyString, sodium.base64_variants.ORIGINAL);
}

/**
 * Encrypt a message for a recipient
 *
 * @param {string} message - Plaintext message
 * @param {Uint8Array} recipientPublicKey - Recipient's public key
 * @param {Uint8Array} senderPrivateKey - Sender's private key
 * @returns {string} - Base64 encoded encrypted message
 */
export async function encryptMessage(message, recipientPublicKey, senderPrivateKey) {
  await initSodium();

  const messageBytes = sodium.from_string(message);
  const nonce = sodium.randombytes_buf(sodium.crypto_box_NONCEBYTES);

  const ciphertext = sodium.crypto_box_easy(
    messageBytes,
    nonce,
    recipientPublicKey,
    senderPrivateKey
  );

  // Combine nonce + ciphertext
  const combined = new Uint8Array(nonce.length + ciphertext.length);
  combined.set(nonce);
  combined.set(ciphertext, nonce.length);

  return keyToString(combined);
}

/**
 * Decrypt a message
 *
 * @param {string} encryptedMessage - Base64 encoded encrypted message
 * @param {Uint8Array} senderPublicKey - Sender's public key
 * @param {Uint8Array} recipientPrivateKey - Recipient's private key
 * @returns {string} - Decrypted plaintext message
 */
export async function decryptMessage(encryptedMessage, senderPublicKey, recipientPrivateKey) {
  await initSodium();

  try {
    const combined = stringToKey(encryptedMessage);

    // Extract nonce and ciphertext
    const nonce = combined.slice(0, sodium.crypto_box_NONCEBYTES);
    const ciphertext = combined.slice(sodium.crypto_box_NONCEBYTES);

    const decrypted = sodium.crypto_box_open_easy(
      ciphertext,
      nonce,
      senderPublicKey,
      recipientPrivateKey
    );

    return sodium.to_string(decrypted);
  } catch (error) {
    console.error('Decryption failed:', error);
    throw new Error('Failed to decrypt message');
  }
}

/**
 * Calculate SHA-256 hash of a message
 * Returns hex string with 0x prefix for blockchain
 *
 * @param {string} message - Message to hash
 * @returns {string} - Hex hash with 0x prefix
 */
export async function hashMessage(message) {
  await initSodium();

  const messageBytes = sodium.from_string(message);
  const hash = sodium.crypto_hash_sha256(messageBytes);

  return '0x' + sodium.to_hex(hash);
}

/**
 * Store keypair in localStorage
 */
export function saveKeypair(keypair) {
  const publicKeyStr = keyToString(keypair.publicKey);
  const privateKeyStr = keyToString(keypair.privateKey);

  localStorage.setItem('publicKey', publicKeyStr);
  localStorage.setItem('privateKey', privateKeyStr);

  return { publicKey: publicKeyStr, privateKey: privateKeyStr };
}

/**
 * Load keypair from localStorage
 */
export function loadKeypair() {
  const publicKeyStr = localStorage.getItem('publicKey');
  const privateKeyStr = localStorage.getItem('privateKey');

  if (!publicKeyStr || !privateKeyStr) {
    return null;
  }

  return {
    publicKey: stringToKey(publicKeyStr),
    privateKey: stringToKey(privateKeyStr),
    publicKeyStr,
    privateKeyStr,
  };
}

/**
 * Clear keypair from localStorage
 */
export function clearKeypair() {
  localStorage.removeItem('publicKey');
  localStorage.removeItem('privateKey');
}

/**
 * Store public keys of contacts
 */
export function saveContactPublicKey(userId, publicKey) {
  const contacts = JSON.parse(localStorage.getItem('contactKeys') || '{}');
  contacts[userId] = publicKey;
  localStorage.setItem('contactKeys', JSON.stringify(contacts));
}

/**
 * Get contact's public key
 */
export function getContactPublicKey(userId) {
  const contacts = JSON.parse(localStorage.getItem('contactKeys') || '{}');
  const publicKeyStr = contacts[userId];

  if (!publicKeyStr) {
    return null;
  }

  return stringToKey(publicKeyStr);
}

/**
 * Export keypair for backup
 */
export function exportKeypair(keypair) {
  const publicKeyStr = keyToString(keypair.publicKey);
  const privateKeyStr = keyToString(keypair.privateKey);

  return JSON.stringify({
    publicKey: publicKeyStr,
    privateKey: privateKeyStr,
    exportedAt: new Date().toISOString(),
  }, null, 2);
}

/**
 * Import keypair from backup
 */
export function importKeypair(jsonString) {
  try {
    const data = JSON.parse(jsonString);

    return {
      publicKey: stringToKey(data.publicKey),
      privateKey: stringToKey(data.privateKey),
      publicKeyStr: data.publicKey,
      privateKeyStr: data.privateKey,
    };
  } catch (error) {
    console.error('Failed to import keypair:', error);
    throw new Error('Invalid keypair format');
  }
}
