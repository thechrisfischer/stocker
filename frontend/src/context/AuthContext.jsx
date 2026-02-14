import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import * as api from '../utils/api';

const AuthContext = createContext(null);

function decodeToken(token) {
    try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        return payload;
    } catch {
        return null;
    }
}

export function AuthProvider({ children }) {
    const [token, setToken] = useState(localStorage.getItem('token'));
    const [user, setUser] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const [statusText, setStatusText] = useState(null);

    const isAuthenticated = !!token && !!user;

    // Validate stored token on mount
    useEffect(() => {
        const storedToken = localStorage.getItem('token');
        if (storedToken) {
            api.isTokenValid(storedToken)
                .then(() => {
                    setToken(storedToken);
                    const payload = decodeToken(storedToken);
                    if (payload) {
                        setUser({ email: payload.email, id: payload.id });
                    }
                })
                .catch(() => {
                    localStorage.removeItem('token');
                    setToken(null);
                    setUser(null);
                })
                .finally(() => setIsLoading(false));
        } else {
            setIsLoading(false);
        }
    }, []);

    const login = useCallback(async (email, password) => {
        setStatusText(null);
        try {
            const data = await api.getToken(email, password);
            localStorage.setItem('token', data.token);
            setToken(data.token);
            const payload = decodeToken(data.token);
            setUser({ email: payload.email, id: payload.id });
            return true;
        } catch {
            setStatusText('Invalid email or password.');
            return false;
        }
    }, []);

    const register = useCallback(async (email, password) => {
        setStatusText(null);
        try {
            const data = await api.createUser(email, password);
            localStorage.setItem('token', data.token);
            setToken(data.token);
            const payload = decodeToken(data.token);
            setUser({ email: payload.email, id: payload.id });
            return true;
        } catch (err) {
            setStatusText(err.data?.message || 'Registration failed.');
            return false;
        }
    }, []);

    const logout = useCallback(() => {
        localStorage.removeItem('token');
        setToken(null);
        setUser(null);
        setStatusText(null);
    }, []);

    const clearStatus = useCallback(() => setStatusText(null), []);

    return (
        <AuthContext.Provider value={{
            token,
            user,
            isAuthenticated,
            isLoading,
            statusText,
            login,
            register,
            logout,
            clearStatus,
        }}>
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const ctx = useContext(AuthContext);
    if (!ctx) throw new Error('useAuth must be used within AuthProvider');
    return ctx;
}
