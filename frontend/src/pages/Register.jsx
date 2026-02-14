import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { validateEmail } from '../utils/validation';

export default function Register() {
    const { register, statusText } = useAuth();
    const navigate = useNavigate();
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [emailError, setEmailError] = useState(null);
    const [passwordError, setPasswordError] = useState(null);
    const [submitting, setSubmitting] = useState(false);

    function validate() {
        let valid = true;
        if (!email || !validateEmail(email)) {
            setEmailError('Please enter a valid email.');
            valid = false;
        } else {
            setEmailError(null);
        }
        if (!password || password.length < 6) {
            setPasswordError('Password must be at least 6 characters.');
            valid = false;
        } else {
            setPasswordError(null);
        }
        return valid;
    }

    async function handleSubmit(e) {
        e.preventDefault();
        if (!validate()) return;
        setSubmitting(true);
        const success = await register(email, password);
        setSubmitting(false);
        if (success) navigate('/dashboard');
    }

    return (
        <div style={{ maxWidth: 400, margin: '48px auto' }}>
            <div className="card">
                <h2 style={{ textAlign: 'center', marginBottom: 24 }}>Create Account</h2>

                {statusText && <div className="alert alert-error">{statusText}</div>}

                <form onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label htmlFor="email">Email</label>
                        <input
                            id="email"
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            autoComplete="email"
                        />
                        {emailError && <div className="error-text">{emailError}</div>}
                    </div>

                    <div className="form-group">
                        <label htmlFor="password">Password</label>
                        <input
                            id="password"
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            autoComplete="new-password"
                        />
                        {passwordError && <div className="error-text">{passwordError}</div>}
                    </div>

                    <button
                        type="submit"
                        className="btn btn-primary"
                        style={{ width: '100%', marginTop: 8 }}
                        disabled={submitting}
                    >
                        {submitting ? 'Creating account...' : 'Register'}
                    </button>
                </form>

                <p style={{ textAlign: 'center', marginTop: 16, fontSize: 14, color: 'var(--color-text-secondary)' }}>
                    Already have an account? <Link to="/login">Login</Link>
                </p>
            </div>
        </div>
    );
}
