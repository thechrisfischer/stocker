import { Link } from 'react-router-dom';

export default function NotFound() {
    return (
        <section style={{ textAlign: 'center', paddingTop: 48 }}>
            <h1>404</h1>
            <p style={{ color: 'var(--color-text-secondary)', marginTop: 8 }}>Page not found.</p>
            <Link to="/" className="btn btn-primary" style={{ marginTop: 24 }}>
                Go Home
            </Link>
        </section>
    );
}
