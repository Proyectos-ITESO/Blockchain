/**
 * Message window component
 */

import { useEffect, useRef, useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useChat } from '../contexts/ChatContext';
import { format } from 'date-fns';
import { Send, Shield, ShieldCheck, ShieldAlert, AlertCircle } from 'lucide-react';
import { verificationAPI } from '../services/api';

function MessageBubble({ message, isOwn }) {
  const [verifying, setVerifying] = useState(false);
  const [verified, setVerified] = useState(message.blockchainTxHash ? true : null);

  const handleVerify = async () => {
    if (!message.id || typeof message.id === 'string') return; // Skip temp messages

    try {
      setVerifying(true);
      const result = await verificationAPI.verifyMessage(message.id);
      setVerified(result.verified);
    } catch (error) {
      console.error('Verification failed:', error);
      setVerified(false);
    } finally {
      setVerifying(false);
    }
  };

  return (
    <div className={`flex ${isOwn ? 'justify-end' : 'justify-start'} mb-4`}>
      <div className={`max-w-xs lg:max-w-md xl:max-w-lg ${isOwn ? 'order-2' : 'order-1'}`}>
        <div
          className={`rounded-2xl px-4 py-2 ${
            isOwn
              ? 'bg-blue-600 text-white rounded-br-none'
              : 'bg-gray-200 text-gray-900 rounded-bl-none'
          }`}
        >
          {!message.decrypted && (
            <div className="flex items-center text-xs mb-1 opacity-75">
              <AlertCircle className="w-3 h-3 mr-1" />
              <span>Unable to decrypt</span>
            </div>
          )}
          <p className="text-sm break-words">{message.content}</p>

          <div className="flex items-center justify-between mt-2 text-xs opacity-75">
            <span>{format(new Date(message.timestamp), 'HH:mm')}</span>

            {message.decrypted && (
              <button
                onClick={handleVerify}
                disabled={verifying || verified === true}
                className="ml-2 hover:opacity-80 transition-opacity"
                title={
                  verified === true
                    ? 'Verified on blockchain'
                    : verified === false
                    ? 'Not verified'
                    : 'Click to verify'
                }
              >
                {verifying ? (
                  <Shield className="w-3 h-3 animate-pulse" />
                ) : verified === true ? (
                  <ShieldCheck className="w-3 h-3" />
                ) : verified === false ? (
                  <ShieldAlert className="w-3 h-3" />
                ) : (
                  <Shield className="w-3 h-3" />
                )}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default function MessageWindow() {
  const { user } = useAuth();
  const { selectedContact, messages, sendMessage, loadChatHistory } = useChat();
  const [messageInput, setMessageInput] = useState('');
  const [sending, setSending] = useState(false);
  const messagesEndRef = useRef(null);

  const contactMessages = selectedContact ? messages[selectedContact.id] || [] : [];

  useEffect(() => {
    if (selectedContact) {
      loadChatHistory(selectedContact.id);
    }
  }, [selectedContact]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [contactMessages]);

  const handleSend = async (e) => {
    e.preventDefault();

    if (!messageInput.trim() || !selectedContact || sending) return;

    try {
      setSending(true);
      await sendMessage(selectedContact.id, messageInput);
      setMessageInput('');
    } catch (error) {
      alert('Failed to send message: ' + error.message);
    } finally {
      setSending(false);
    }
  };

  if (!selectedContact) {
    return (
      <div className="flex-1 flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <Shield className="w-16 h-16 mx-auto mb-4 text-gray-400" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No conversation selected</h3>
          <p className="text-sm text-gray-500">Choose a contact to start messaging</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col bg-white">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 bg-white">
        <div className="flex items-center">
          <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center text-blue-600 font-semibold">
            {selectedContact.username[0].toUpperCase()}
          </div>
          <div className="ml-3">
            <h3 className="font-semibold text-gray-900">{selectedContact.username}</h3>
            <p className="text-xs text-gray-500">🔒 End-to-end encrypted</p>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 bg-gray-50">
        {contactMessages.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <p className="text-gray-500 text-sm">No messages yet. Start the conversation!</p>
          </div>
        ) : (
          <>
            {contactMessages.map((message) => (
              <MessageBubble
                key={message.id}
                message={message}
                isOwn={message.senderId === user.id}
              />
            ))}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* Input */}
      <form onSubmit={handleSend} className="p-4 border-t border-gray-200 bg-white">
        <div className="flex items-center space-x-2">
          <input
            type="text"
            value={messageInput}
            onChange={(e) => setMessageInput(e.target.value)}
            placeholder="Type a message..."
            disabled={sending}
            className="flex-1 px-4 py-3 border border-gray-300 rounded-full focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          <button
            type="submit"
            disabled={!messageInput.trim() || sending}
            className="p-3 bg-blue-600 text-white rounded-full hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
        <p className="text-xs text-gray-500 mt-2 text-center">
          Messages are encrypted end-to-end and verified on blockchain
        </p>
      </form>
    </div>
  );
}
