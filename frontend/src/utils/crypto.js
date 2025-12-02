/**
 * End-to-End Encryption utilities using TweetNaCl
 *
 * Uses X25519-XSalsa20-Poly1305 for encryption (same as libsodium)
 * SHA-256 for message hashing
 */

import nacl from 'tweetnacl';
import { encodeBase64, decodeBase64, encodeUTF8, decodeUTF8 } from 'tweetnacl-util';

/**
 * Generate a new keypair for a user
 * Returns: { publicKey: Uint8Array, privateKey: Uint8Array }
 */
export function generateKeyPair() {
  const keyPair = nacl.box.keyPair();

  return {
    publicKey: keyPair.publicKey,
    privateKey: keyPair.secretKey,
  };
}

/**
 * Convert Uint8Array to base64 string for storage/transmission
 */
export function keyToString(key) {
  return encodeBase64(key);
}

/**
 * Convert base64 string back to Uint8Array
 */
export function stringToKey(keyString) {
  return decodeBase64(keyString);
}

/**
 * Encrypt a message for a recipient
 *
 * @param {string} message - Plaintext message
 * @param {Uint8Array} recipientPublicKey - Recipient's public key
 * @param {Uint8Array} senderPrivateKey - Sender's private key
 * @returns {string} - Base64 encoded encrypted message
 */
export function encryptMessage(message, recipientPublicKey, senderPrivateKey) {
  const messageBytes = new TextEncoder().encode(message);
  const nonce = nacl.randomBytes(nacl.box.nonceLength);

  console.log('DEBUG: encryptMessage', {
    messageType: typeof message,
    messageBytesType: messageBytes.constructor.name,
    nonceType: nonce.constructor.name,
    recipientKeyType: recipientPublicKey?.constructor?.name,
    senderKeyType: senderPrivateKey?.constructor?.name,
  });

  const ciphertext = nacl.box(
    messageBytes,
    nonce,
    recipientPublicKey,
    senderPrivateKey
  );

  // Combine nonce + ciphertext
  const combined = new Uint8Array(nonce.length + ciphertext.length);
  combined.set(nonce);
  combined.set(ciphertext, nonce.length);

  return encodeBase64(combined);
}

/**
 * Decrypt a message
 *
 * @param {string} encryptedMessage - Base64 encoded encrypted message
 * @param {Uint8Array} senderPublicKey - Sender's public key
 * @param {Uint8Array} recipientPrivateKey - Recipient's private key
 * @returns {string} - Decrypted plaintext message
 */
export function decryptMessage(encryptedMessage, senderPublicKey, recipientPrivateKey) {
  try {
    const combined = decodeBase64(encryptedMessage);

    // Extract nonce and ciphertext
    const nonce = combined.slice(0, nacl.box.nonceLength);
    const ciphertext = combined.slice(nacl.box.nonceLength);

    const decrypted = nacl.box.open(
      ciphertext,
      nonce,
      senderPublicKey,
      recipientPrivateKey
    );

    if (!decrypted) {
      throw new Error('Decryption failed');
    }

    return new TextDecoder().decode(decrypted);
  } catch (error) {
    console.error('Decryption failed:', error);
    throw new Error('Failed to decrypt message');
  }
}

/**
 * Calculate SHA-256 hash of a message using Web Crypto API
 * Returns hex string with 0x prefix for blockchain
 *
 * @param {string} message - Message to hash
 * @returns {Promise<string>} - Hex hash with 0x prefix
 */
export async function hashMessage(message) {
  const messageBytes = new TextEncoder().encode(message);
  const hashBuffer = await crypto.subtle.digest('SHA-256', messageBytes);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');

  return '0x' + hashHex;
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
