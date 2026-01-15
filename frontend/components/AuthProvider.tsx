/**
 * Authentication context provider
 */
import React, { createContext, useContext, useState, useEffect } from 'react';
import { authAPI } from '@/lib/api';

interface User {
  id: string;
  email: string;
  name: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  loading: boolean;
  login: () => void;
  logout: () => void;
  setToken: (token: string) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setTokenState] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check for existing token
    const storedToken = localStorage.getItem('token');
    if (storedToken) {
      setTokenState(storedToken);
      checkAuthStatus(storedToken);
    } else {
      setLoading(false);
    }
  }, []);

  const checkAuthStatus = async (authToken: string) => {
    try {
      const response = await authAPI.getStatus(authToken);
      if (response.authenticated) {
        setUser(response.user);
      } else {
        localStorage.removeItem('token');
        setTokenState(null);
      }
    } catch (error) {
      console.error('Auth status check failed:', error);
      localStorage.removeItem('token');
      setTokenState(null);
    } finally {
      setLoading(false);
    }
  };

  const login = async () => {
    try {
      const response = await authAPI.login();
      window.location.href = response.redirect_url;
    } catch (error) {
      console.error('Login failed:', error);
    }
  };

  const logout = async () => {
    try {
      if (token) {
        await authAPI.logout(token);
      }
    } catch (error) {
      console.error('Logout failed:', error);
    } finally {
      localStorage.removeItem('token');
      setTokenState(null);
      setUser(null);
    }
  };

  const setToken = (newToken: string) => {
    localStorage.setItem('token', newToken);
    setTokenState(newToken);
    checkAuthStatus(newToken);
  };

  return (
    <AuthContext.Provider value={{ user, token, loading, login, logout, setToken }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
