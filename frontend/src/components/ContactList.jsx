/**
 * Contact list component
 */

import { useEffect, useState } from 'react';
import { useChat } from '../contexts/ChatContext';
import { Search, UserPlus, Users } from 'lucide-react';

export default function ContactList() {
  const { contacts, selectedContact, setSelectedContact, searchUsers, addContact, loading } = useChat();
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [showSearch, setShowSearch] = useState(false);
  const [addingContact, setAddingContact] = useState(null);

  useEffect(() => {
    if (searchQuery.length >= 2) {
      const timer = setTimeout(async () => {
        const results = await searchUsers(searchQuery);
        setSearchResults(results);
      }, 300);

      return () => clearTimeout(timer);
    } else {
      setSearchResults([]);
    }
  }, [searchQuery]);

  const handleAddContact = async (userId) => {
    try {
      console.log('Adding contact with ID:', userId);
      setAddingContact(userId);
      await addContact(userId);
      console.log('Contact added successfully');
      setSearchQuery('');
      setShowSearch(false);
      setSearchResults([]);
    } catch (error) {
      console.error('Failed to add contact:', error);
      alert('Failed to add contact: ' + error.message);
    } finally {
      setAddingContact(null);
    }
  };

  return (
    <div className="flex flex-col h-full bg-white border-r border-gray-200">
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-gray-900">Messages</h2>
          <button
            onClick={() => setShowSearch(!showSearch)}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            title="Add contact"
          >
            {showSearch ? <Users className="w-5 h-5" /> : <UserPlus className="w-5 h-5" />}
          </button>
        </div>

        {/* Search */}
        {showSearch && (
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search users..."
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />

            {/* Search Results */}
            {searchResults.length > 0 && (
              <div className="absolute top-full left-0 right-0 mt-2 bg-white border border-gray-200 rounded-lg shadow-lg max-h-64 overflow-y-auto z-10">
                {searchResults.map((user) => (
                  <div
                    key={user.id}
                    className="p-3 hover:bg-gray-50 flex items-center justify-between"
                  >
                    <span className="text-sm font-medium text-gray-900">{user.username}</span>
                    <button
                      onClick={() => handleAddContact(user.id)}
                      disabled={addingContact === user.id}
                      className="px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 disabled:opacity-50"
                    >
                      {addingContact === user.id ? 'Adding...' : 'Add'}
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Contact List */}
      <div className="flex-1 overflow-y-auto">
        {loading ? (
          <div className="flex items-center justify-center h-32">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
        ) : contacts.length === 0 ? (
          <div className="p-8 text-center text-gray-500">
            <Users className="w-12 h-12 mx-auto mb-3 text-gray-400" />
            <p className="text-sm">No contacts yet</p>
            <p className="text-xs mt-1">Use the + button to add contacts</p>
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {contacts.map((contact) => (
              <button
                key={contact.id}
                onClick={() => setSelectedContact(contact)}
                className={`w-full p-4 flex items-center hover:bg-gray-50 transition-colors ${
                  selectedContact?.id === contact.id ? 'bg-blue-50' : ''
                }`}
              >
                <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center text-blue-600 font-semibold text-lg">
                  {contact.username[0].toUpperCase()}
                </div>
                <div className="ml-3 flex-1 text-left">
                  <p className="font-medium text-gray-900">{contact.username}</p>
                  <p className="text-xs text-gray-500">Click to chat</p>
                </div>
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
