import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './Header.css';

export default function Header() {
    const { isAuthenticated, user, logout } = useAuth();
    const [menuOpen, setMenuOpen] = useState(false);
    const navigate = useNavigate();

    function handleLogout() {
        logout();
        setMenuOpen(false);
        navigate('/');
    }

    return (
        <header className="header">
            <div className="header-inner">
                <button
                    className="menu-btn"
                    onClick={() => setMenuOpen(!menuOpen)}
                    aria-label="Toggle menu"
                >
                    <span className="menu-icon" />
                </button>
                <Link to="/" className="header-title">Stocker</Link>
                <nav className="header-nav">
                    <Link to="/rankings">Rankings</Link>
                    {isAuthenticated ? (
                        <>
                            <Link to="/dashboard">Dashboard</Link>
                            <Link to="/analytics">Analytics</Link>
                        </>
                    ) : null}
                </nav>
                <div className="header-right">
                    {isAuthenticated ? (
                        <div className="user-menu">
                            <span className="user-email">{user?.email}</span>
                            <button className="btn btn-secondary btn-sm" onClick={handleLogout}>
                                Logout
                            </button>
                        </div>
                    ) : (
                        <div className="auth-links">
                            <Link to="/login">Login</Link>
                            <Link to="/register" className="btn btn-primary btn-sm">Register</Link>
                        </div>
                    )}
                </div>
            </div>

            {menuOpen && (
                <div className="mobile-menu" onClick={() => setMenuOpen(false)}>
                    <Link to="/rankings">Rankings</Link>
                    {isAuthenticated ? (
                        <>
                            <Link to="/dashboard">Dashboard</Link>
                            <Link to="/analytics">Analytics</Link>
                            <button onClick={handleLogout}>Logout</button>
                        </>
                    ) : (
                        <>
                            <Link to="/login">Login</Link>
                            <Link to="/register">Register</Link>
                        </>
                    )}
                </div>
            )}
        </header>
    );
}
