import React, { createContext, useContext, useState, useEffect } from 'react';

interface User {
  id: number;
  name: string;
  email: string;
  monthlyIncome: number;
  householdSize: number;
  householdId?: number;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (name: string, email: string, password: string, monthlyIncome: number, householdSize: number) => Promise<void>;
  logout: () => void;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://poverty-alleviation.onrender.com';

  useEffect(() => {
    // Check for stored auth data on app load
    const storedUser = localStorage.getItem('user');
    
    if (storedUser) {
      try {
        const parsedUser = JSON.parse(storedUser);
        setUser(parsedUser);
      } catch (error) {
        console.error('Error parsing stored user data:', error);
        localStorage.removeItem('user');
      }
    }
    setLoading(false);
  }, []);

  const register = async (name: string, email: string, password: string, monthlyIncome: number, householdSize: number): Promise<void> => {
    try {
      setLoading(true);
      
      // For now, create a mock successful registration since backend endpoints may not be deployed yet
      // This will be replaced once the backend is properly deployed with authentication
      
      // Simulate API call delay
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // Create user data from registration form
      const userData: User = {
        id: Date.now(), // Use timestamp as unique ID
        name,
        email,
        monthlyIncome,
        householdSize,
        householdId: Date.now() // Mock household ID
      };
      
      setUser(userData);
      localStorage.setItem('user', JSON.stringify(userData));
    } catch (error) {
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const login = async (email: string, password: string): Promise<void> => {
    try {
      setLoading(true);
      
      // For now, create a mock successful login since backend endpoints may not be deployed yet
      // This will be replaced once the backend is properly deployed with authentication
      
      // Simulate API call delay
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Create mock user data
      const mockUser: User = {
        id: Date.now(), // Use timestamp as unique ID
        name: email.split('@')[0] || 'User',
        email: email,
        monthlyIncome: 3000,
        householdSize: 4,
        householdId: 1
      };
      
      setUser(mockUser);
      localStorage.setItem('user', JSON.stringify(mockUser));
      
    } catch (error) {
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('user');
    setUser(null);
  };

  const value = {
    user,
    isAuthenticated: !!user,
    login,
    register,
    logout,
    loading
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};