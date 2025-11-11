/**
 * User settings panel
 */

import { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { User, Key, LogOut, Copy, Download, X } from 'lucide-react';
import { exportKeypair, keyToString } from '../utils/crypto';

export default function UserSettings() {
  const { user, keypair, logout } = useAuth();
  const [showSettings, setShowSettings] = useState(false);
  const [copied, setCopied] = useState(false);

  const handleCopyPublicKey = () => {
    if (keypair) {
      navigator.clipboard.writeText(keypair.publicKeyStr);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleExportKeys = () => {
    if (keypair) {
      const exported = exportKeypair(keypair);
      const blob = new Blob([exported], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `keypair-${user.username}.json`;
      a.click();
      URL.revokeObjectURL(url);
    }
  };

  if (!showSettings) {
    return (
      <button
        onClick={() => setShowSettings(true)}
        className="fixed top-4 right-4 p-3 bg-white rounded-full shadow-lg hover:shadow-xl transition-shadow border border-gray-200"
        title="Settings"
      >
        <User className="w-5 h-5 text-gray-600" />
      </button>
    );
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-xl max-w-md w-full">
        {/* Header */}
        <div className="p-6 border-b border-gray-200 flex items-center justify-between">
          <h2 className="text-xl font-semibold text-gray-900">Settings</h2>
          <button
            onClick={() => setShowSettings(false)}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* User Info */}
          <div>
            <h3 className="text-sm font-medium text-gray-700 mb-3">Account</h3>
            <div className="p-4 bg-gray-50 rounded-lg">
              <div className="flex items-center">
                <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center text-blue-600 font-semibold text-lg">
                  {user.username[0].toUpperCase()}
                </div>
                <div className="ml-3">
                  <p className="font-medium text-gray-900">{user.username}</p>
                  <p className="text-xs text-gray-500">User ID: {user.id}</p>
                </div>
              </div>
            </div>
          </div>

          {/* Public Key */}
          <div>
            <h3 className="text-sm font-medium text-gray-700 mb-3">Public Key</h3>
            <div className="p-4 bg-gray-50 rounded-lg">
              <div className="flex items-start justify-between">
                <div className="flex-1 mr-2">
                  <p className="text-xs font-mono text-gray-600 break-all">
                    {keypair?.publicKeyStr.substring(0, 40)}...
                  </p>
                </div>
                <button
                  onClick={handleCopyPublicKey}
                  className="p-2 hover:bg-gray-200 rounded transition-colors flex-shrink-0"
                  title="Copy public key"
                >
                  <Copy className="w-4 h-4" />
                </button>
              </div>
              {copied && <p className="text-xs text-green-600 mt-2">Copied to clipboard!</p>}
              <p className="text-xs text-gray-500 mt-2">
                Share this key with contacts to enable encrypted messaging
              </p>
            </div>
          </div>

          {/* Key Management */}
          <div>
            <h3 className="text-sm font-medium text-gray-700 mb-3">Key Management</h3>
            <button
              onClick={handleExportKeys}
              className="w-full p-3 bg-blue-50 text-blue-700 rounded-lg hover:bg-blue-100 transition-colors flex items-center justify-center"
            >
              <Download className="w-4 h-4 mr-2" />
              Export Keys (Backup)
            </button>
            <p className="text-xs text-gray-500 mt-2">
              ⚠️ Keep your private key safe. Never share it with anyone.
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="p-6 border-t border-gray-200">
          <button
            onClick={logout}
            className="w-full p-3 bg-red-50 text-red-700 rounded-lg hover:bg-red-100 transition-colors flex items-center justify-center"
          >
            <LogOut className="w-4 h-4 mr-2" />
            Logout
          </button>
        </div>
      </div>
    </div>
  );
}
