import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Home() {
    const { isAuthenticated } = useAuth();

    return (
        <section style={{ textAlign: 'center', paddingTop: 48 }}>
            <h1>Welcome to Stocker</h1>
            <p style={{ color: 'var(--color-text-secondary)', marginTop: 8, fontSize: 18 }}>
                Stock market analysis and investment strategy rankings.
            </p>
            <div style={{ marginTop: 32, display: 'flex', gap: 12, justifyContent: 'center' }}>
                <Link to="/rankings" className="btn btn-primary">View Rankings</Link>
                {!isAuthenticated && (
                    <Link to="/register" className="btn btn-secondary">Get Started</Link>
                )}
            </div>
        </section>
    );
}
