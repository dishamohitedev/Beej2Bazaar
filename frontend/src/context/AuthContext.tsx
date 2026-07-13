import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../services/api';

export interface User {
  id: string;
  email?: string;
  phone?: string;
  name: string;
  role: string;
  is_profile_complete: boolean;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, pass: string) => Promise<any>;
  signup: (email: string, pass: string) => Promise<any>;
  logout: () => void;
  submitOnboarding: (data: any) => Promise<any>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchCurrentUser = async () => {
    try {
      const response = await api.get('/api/auth/me');
      setUser(response.data);
    } catch (error) {
      setUser(null);
      localStorage.removeItem('bb_access_token');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const token = localStorage.getItem('bb_access_token');
    if (token) {
      fetchCurrentUser();
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (email: string, pass: string) => {
    const response = await api.post('/api/auth/login', {
      email,
      password: pass,
    });
    const { access_token } = response.data;
    localStorage.setItem('bb_access_token', access_token);
    
    // Fetch user details
    const meRes = await api.get('/api/auth/me');
    setUser(meRes.data);
    return meRes.data;
  };

  const signup = async (email: string, pass: string) => {
    await api.post('/api/auth/signup', {
      email,
      password: pass,
    });
    // Immediately log in after successful signup
    return await login(email, pass);
  };

  const logout = () => {
    localStorage.removeItem('bb_access_token');
    setUser(null);
  };

  const submitOnboarding = async (data: any) => {
    const response = await api.post('/api/onboarding', data);
    // After submitting onboarding, the profile status is completed
    if (user) {
      const updatedUser = { 
        ...user, 
        is_profile_complete: true, 
        name: data.full_name || user.name 
      };
      setUser(updatedUser);
    }
    return response.data;
  };

  const refreshUser = async () => {
    await fetchCurrentUser();
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, signup, logout, submitOnboarding, refreshUser }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
