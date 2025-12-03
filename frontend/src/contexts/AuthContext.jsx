/**
 * Authentication context for managing user state
 */

import { createContext, useContext, useState, useEffect } from 'react';
import { authAPI } from '../services/api';
import { generateKeyPair, saveKeypair, loadKeypair, clearKeypair } from '../utils/crypto';
import wsService from '../services/websocket';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [keypair, setKeypair] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Initialize - check for existing session
  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem('token');

      if (token) {
        try {
          // Get current user from API
          const userData = await authAPI.getCurrentUser();
          setUser(userData);

          // Load keypair from localStorage
          const loadedKeypair = loadKeypair();

          if (loadedKeypair) {
            setKeypair(loadedKeypair);
          } else {
            console.warn('No keypair found - user needs to generate keys');
          }

          // Connect to WebSocket
          await wsService.connect(token);
        } catch (err) {
          console.error('Failed to initialize auth:', err);
          localStorage.removeItem('token');
        }
      }

      setLoading(false);
    };

    initAuth();

    return () => {
      wsService.disconnect();
    };
  }, []);

  const login = async (username, password) => {
    try {
      setError(null);
      setLoading(true);

      // Login to get token
      const { access_token } = await authAPI.login(username, password);
      localStorage.setItem('token', access_token);

      // Get user data
      const userData = await authAPI.getCurrentUser();
      setUser(userData);

      // Check if user has public key in database
      if (!userData.public_key) {
        console.log("User doesn't have public key in database, generating...");

        // Load or generate keypair
        let existingKeypair = loadKeypair();

        if (!existingKeypair) {
          console.log('Generating new keypair for user');
          const newKeypair = generateKeyPair();
          saveKeypair(newKeypair);
          existingKeypair = loadKeypair();
        }

        // Update public key in database
        await authAPI.updatePublicKey(existingKeypair.publicKeyStr);
        console.log("Public key saved to database");

        setKeypair(existingKeypair);
      } else {
        console.log("User has public key in database:", userData.public_key.substring(0, 20) + "...");

        // Load or generate local keypair
        let existingKeypair = loadKeypair();

        if (!existingKeypair) {
          console.log('Generating local keypair for existing user');
          const newKeypair = generateKeyPair();
          saveKeypair(newKeypair);
          existingKeypair = loadKeypair();
        }

        // Check if local key matches database key
        if (existingKeypair.publicKeyStr !== userData.public_key) {
          console.log('Local key differs from database key. Updating database...');
          await authAPI.updatePublicKey(existingKeypair.publicKeyStr);
          console.log('Database public key updated');
        }

        setKeypair(existingKeypair);
      }

      // Connect to WebSocket
      await wsService.connect(access_token);

      return userData;
    } catch (err) {
      console.error('Login error:', err);
      let message = 'Login failed';

      if (err.response?.data?.detail) {
        const detail = err.response.data.detail;
        if (typeof detail === 'string') {
          message = detail;
        } else if (Array.isArray(detail)) {
          // Handle Pydantic validation errors
          message = detail.map(e => e.msg).join(', ');
        } else if (typeof detail === 'object') {
          message = JSON.stringify(detail);
        }
      }

      setError(message);
      throw new Error(message);
    } finally {
      setLoading(false);
    }
  };

  const register = async (username, password) => {
    try {
      setError(null);
      setLoading(true);

      // Generate keypair BEFORE registration
      const newKeypair = generateKeyPair();
      const savedKeypair = saveKeypair(newKeypair);

      // Register user with public key
      await authAPI.register(username, password, savedKeypair.publicKey);

      // Auto-login after registration
      await login(username, password);

      return { username, publicKey: savedKeypair.publicKey };
    } catch (err) {
      const message = err.response?.data?.detail || 'Registration failed';
      setError(message);
      throw new Error(message);
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
    setKeypair(null);
    wsService.disconnect();
  };

  const regenerateKeys = async () => {
    const newKeypair = await generateKeyPair();
    const savedKeypair = saveKeypair(newKeypair);
    setKeypair(loadKeypair());
    return savedKeypair;
  };

  const value = {
    user,
    keypair,
    loading,
    error,
    login,
    register,
    logout,
    regenerateKeys,
    isAuthenticated: !!user,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}
