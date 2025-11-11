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

      // Load or generate keypair
      let userKeypair = loadKeypair();

      if (!userKeypair) {
        console.log('Generating new keypair for user');
        const newKeypair = await generateKeyPair();
        saveKeypair(newKeypair);
        userKeypair = loadKeypair();
      }

      setKeypair(userKeypair);

      // Connect to WebSocket
      await wsService.connect(access_token);

      return userData;
    } catch (err) {
      const message = err.response?.data?.detail || 'Login failed';
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

      // Register user
      await authAPI.register(username, password);

      // Generate keypair
      const newKeypair = await generateKeyPair();
      const savedKeypair = saveKeypair(newKeypair);

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
