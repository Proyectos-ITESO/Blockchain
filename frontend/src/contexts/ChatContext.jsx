/**
 * Chat context for managing messages and conversations
 */

import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { chatAPI } from '../services/api';
import wsService from '../services/websocket';
import { encryptMessage, decryptMessage, hashMessage, getContactPublicKey, saveContactPublicKey } from '../utils/crypto';
import { useAuth } from './AuthContext';

const ChatContext = createContext(null);

export function ChatProvider({ children }) {
  const { user, keypair } = useAuth();
  const [contacts, setContacts] = useState([]);
  const [messages, setMessages] = useState({});
  const [selectedContact, setSelectedContact] = useState(null);
  const [onlineUsers, setOnlineUsers] = useState([]);
  const [loading, setLoading] = useState(false);

  // Load contacts
  useEffect(() => {
    if (user) {
      loadContacts();
    }
  }, [user]);

  // WebSocket message listener
  useEffect(() => {
    if (!keypair) return;

    const handleMessage = async (data) => {
      if (data.type === 'message') {
        try {
          // Get sender's public key
          const senderPublicKey = getContactPublicKey(data.from_user_id);

          if (!senderPublicKey) {
            console.error('Sender public key not found for user:', data.from_user_id);
            // Store encrypted message anyway
            addMessage(data.from_user_id, {
              id: data.message_id,
              senderId: data.from_user_id,
              senderUsername: data.from_username,
              encryptedPayload: data.payload,
              messageHash: data.message_hash,
              timestamp: data.timestamp,
              decrypted: false,
              content: '[Unable to decrypt - missing sender key]',
            });
            return;
          }

          // Decrypt message
          const decryptedContent = await decryptMessage(
            data.payload,
            senderPublicKey,
            keypair.privateKey
          );

          // Add to messages
          addMessage(data.from_user_id, {
            id: data.message_id,
            senderId: data.from_user_id,
            senderUsername: data.from_username,
            content: decryptedContent,
            encryptedPayload: data.payload,
            messageHash: data.message_hash,
            timestamp: data.timestamp,
            decrypted: true,
          });
        } catch (error) {
          console.error('Failed to decrypt message:', error);
        }
      }
    };

    const unsubscribe = wsService.on('message', handleMessage);
    return unsubscribe;
  }, [keypair]);

  const loadContacts = async () => {
    try {
      setLoading(true);
      const contactList = await chatAPI.getContacts();
      setContacts(contactList);

      // Automatically save public keys of contacts
      contactList.forEach(contact => {
        if (contact.public_key) {
          console.log(`Saving public key for user ${contact.username} (${contact.id})`);
          saveContactPublicKey(contact.id, contact.public_key);
        } else {
          console.warn(`No public key found for user ${contact.username} (${contact.id})`);
        }
      });
    } catch (error) {
      console.error('Failed to load contacts:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadChatHistory = async (contactId) => {
    if (!keypair) return;

    try {
      setLoading(true);
      const history = await chatAPI.getChatHistory(contactId);

      // Decrypt messages
      const decryptedMessages = await Promise.all(
        history.map(async (msg) => {
          try {
            // Determine if we are sender or receiver
            const isSender = msg.sender_id === user.id;
            const otherUserId = isSender ? msg.receiver_id : msg.sender_id;

            // Get other user's public key
            const otherPublicKey = getContactPublicKey(otherUserId);

            if (!otherPublicKey) {
              return {
                ...msg,
                content: '[Unable to decrypt - missing key]',
                decrypted: false,
              };
            }

            // Decrypt
            const decryptedContent = await decryptMessage(
              msg.encrypted_payload,
              otherPublicKey,
              keypair.privateKey
            );

            return {
              id: msg.id,
              senderId: msg.sender_id,
              receiverId: msg.receiver_id,
              content: decryptedContent,
              encryptedPayload: msg.encrypted_payload,
              messageHash: msg.message_hash,
              blockchainTxHash: msg.blockchain_tx_hash,
              timestamp: msg.timestamp,
              decrypted: true,
            };
          } catch (error) {
            console.error('Failed to decrypt message:', error);
            return {
              ...msg,
              content: '[Decryption failed]',
              decrypted: false,
            };
          }
        })
      );

      setMessages((prev) => ({
        ...prev,
        [contactId]: decryptedMessages,
      }));
    } catch (error) {
      console.error('Failed to load chat history:', error);
    } finally {
      setLoading(false);
    }
  };

  const sendMessage = async (recipientId, messageContent) => {
    if (!keypair || !messageContent.trim()) return;

    try {
      // Get recipient's public key
      const recipientPublicKey = getContactPublicKey(recipientId);

      if (!recipientPublicKey) {
        throw new Error('Recipient public key not found. Please exchange keys first.');
      }

      // Encrypt message
      const encryptedPayload = await encryptMessage(
        messageContent,
        recipientPublicKey,
        keypair.privateKey
      );

      // Calculate hash of plaintext
      const messageHash = await hashMessage(messageContent);

      // Send via WebSocket
      const sent = wsService.sendMessage(recipientId, encryptedPayload, messageHash);

      if (!sent) {
        throw new Error('Failed to send message - WebSocket not connected');
      }

      // Optimistically add to local state
      addMessage(recipientId, {
        id: `temp-${Date.now()}`,
        senderId: user.id,
        receiverId: recipientId,
        content: messageContent,
        encryptedPayload,
        messageHash,
        timestamp: new Date().toISOString(),
        decrypted: true,
        sending: true,
      });

      return true;
    } catch (error) {
      console.error('Failed to send message:', error);
      throw error;
    }
  };

  const addMessage = (contactId, message) => {
    setMessages((prev) => ({
      ...prev,
      [contactId]: [...(prev[contactId] || []), message],
    }));
  };

  const searchUsers = async (query) => {
    try {
      const results = await chatAPI.searchUsers(query);
      return results;
    } catch (error) {
      console.error('Failed to search users:', error);
      return [];
    }
  };

  const addContact = async (userId) => {
    try {
      await chatAPI.addContact(userId);
      await loadContacts();
    } catch (error) {
      console.error('Failed to add contact:', error);
      throw error;
    }
  };

  const exchangePublicKey = (userId, publicKeyStr) => {
    saveContactPublicKey(userId, publicKeyStr);
  };

  const value = {
    contacts,
    messages,
    selectedContact,
    onlineUsers,
    loading,
    setSelectedContact,
    loadContacts,
    loadChatHistory,
    sendMessage,
    searchUsers,
    addContact,
    exchangePublicKey,
  };

  return <ChatContext.Provider value={value}>{children}</ChatContext.Provider>;
}

export function useChat() {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error('useChat must be used within ChatProvider');
  }
  return context;
}
