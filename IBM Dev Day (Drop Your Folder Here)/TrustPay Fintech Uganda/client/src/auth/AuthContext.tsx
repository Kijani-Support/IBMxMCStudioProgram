import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from 'react';
import { api, storeToken } from '../lib/api';
import { clearSession, getSessionToken, getSessionUser, setSessionUser } from '../lib/session';
import type { User } from '../lib/types';

interface AuthContextValue {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  ready: boolean;
  login: (email: string, password: string) => Promise<User>;
  register: (input: {
    name: string;
    phone: string;
    email: string;
    password: string;
    role: 'BUSINESS' | 'RIDER';
  }) => Promise<User>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

function persist(user: User, token: string) {
  storeToken(token);
  setSessionUser(JSON.stringify(user));
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(() => {
    const raw = getSessionUser();
    if (!raw) return null;
    try {
      return JSON.parse(raw) as User;
    } catch {
      return null;
    }
  });
  const [token, setToken] = useState<string | null>(() => getSessionToken());
  const [ready, setReady] = useState(false);

  useEffect(() => {
    let cancelled = false;

    async function hydrate() {
      if (!token) {
        setReady(true);
        return;
      }
      try {
        const { user: profile } = await api.getMe();
        if (!cancelled) {
          setUser(profile);
          setSessionUser(JSON.stringify(profile));
        }
      } catch {
        if (!cancelled) {
          clearSession();
          setUser(null);
          setToken(null);
        }
      } finally {
        if (!cancelled) setReady(true);
      }
    }

    void hydrate();
    return () => {
      cancelled = true;
    };
  }, [token]);

  const login = useCallback(async (email: string, password: string) => {
    const result = await api.login({ email, password });
    persist(result.user, result.token);
    setUser(result.user);
    setToken(result.token);
    return result.user;
  }, []);

  const register = useCallback(
    async (input: {
      name: string;
      phone: string;
      email: string;
      password: string;
      role: 'BUSINESS' | 'RIDER';
    }) => {
      const result = await api.register(input);
      persist(result.user, result.token);
      setUser(result.user);
      setToken(result.token);
      return result.user;
    },
    []
  );

  const logout = useCallback(() => {
    clearSession();
    setUser(null);
    setToken(null);
  }, []);

  const value = useMemo(
    () => ({
      user,
      token,
      isAuthenticated: Boolean(user && token),
      ready,
      login,
      register,
      logout
    }),
    [user, token, ready, login, register, logout]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}

export function homeForRole(role: User['role']): string {
  return role === 'BUSINESS' ? '/business' : '/rider';
}
