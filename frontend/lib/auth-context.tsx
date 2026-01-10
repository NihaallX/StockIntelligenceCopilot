"use client";

import React, { createContext, useContext, useState, useEffect } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { User, AuthTokens } from '@/lib/api';

interface AuthContextType {
  user: User | null;
  tokens: AuthTokens | null;
  isLoading: boolean;
  login: (user: User, tokens: AuthTokens) => void;
  logout: () => void;
  handleAuthError: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [tokens, setTokens] = useState<AuthTokens | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    // Load auth from localStorage on mount
    const storedUser = localStorage.getItem('user');
    const storedTokens = localStorage.getItem('tokens');
    
    if (storedUser && storedTokens) {
      try {
        const parsedUser = JSON.parse(storedUser);
        const parsedTokens = JSON.parse(storedTokens);
        setUser(parsedUser);
        setTokens(parsedTokens);
      } catch (error) {
        console.error('Failed to parse stored auth data:', error);
        // Clear corrupted data
        localStorage.removeItem('user');
        localStorage.removeItem('tokens');
      }
    }
    setIsLoading(false);
  }, []);

  const login = (newUser: User, newTokens: AuthTokens) => {
    setUser(newUser);
    setTokens(newTokens);
    localStorage.setItem('user', JSON.stringify(newUser));
    localStorage.setItem('tokens', JSON.stringify(newTokens));
  };

  const logout = () => {
    setUser(null);
    setTokens(null);
    localStorage.removeItem('user');
    localStorage.removeItem('tokens');
    router.push('/login');
  };

  const handleAuthError = () => {
    // Store the current path to redirect back after login
    if (pathname && !pathname.includes('/login') && !pathname.includes('/register')) {
      localStorage.setItem('redirect_after_login', pathname);
    }
    
    // Clear auth state
    setUser(null);
    setTokens(null);
    localStorage.removeItem('user');
    localStorage.removeItem('tokens');
    
    // Redirect to login
    router.push('/login?session_expired=true');
  };

  return (
    <AuthContext.Provider value={{ user, tokens, isLoading, login, logout, handleAuthError }}>
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
