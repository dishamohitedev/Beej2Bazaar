import { createContext, useContext, useEffect, useState } from 'react';
import { fetchMe } from '../services/authService';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem('bb_user');
    return saved ? JSON.parse(saved) : null;
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('bb_access_token');
    if (!token) {
      setLoading(false);
      return;
    }
    fetchMe()
      .then((freshUser) => {
        setUser(freshUser);
        localStorage.setItem('bb_user', JSON.stringify(freshUser));
      })
      .catch(() => {
        logout();
      })
      .finally(() => setLoading(false));
  }, []);

  const login = ({ access_token, refresh_token, user: newUser }) => {
    localStorage.setItem('bb_access_token', access_token);
    localStorage.setItem('bb_refresh_token', refresh_token);
    localStorage.setItem('bb_user', JSON.stringify(newUser));
    setUser(newUser);
  };

  const logout = () => {
    localStorage.removeItem('bb_access_token');
    localStorage.removeItem('bb_refresh_token');
    localStorage.removeItem('bb_user');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
