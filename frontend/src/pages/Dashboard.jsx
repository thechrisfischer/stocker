import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import * as api from '../utils/api';

export default function Dashboard() {
    const { token, user } = useAuth();
    const [userData, setUserData] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        api.getUserData(token)
            .then((data) => setUserData(data.result))
            .catch(() => {})
            .finally(() => setLoading(false));
    }, [token]);

    if (loading) return <p>Loading...</p>;

    return (
        <div>
            <h1>Dashboard</h1>
            <p style={{ color: 'var(--color-text-secondary)', marginTop: 8 }}>
                Welcome back, {userData?.email || user?.email}
            </p>

            <div className="card" style={{ marginTop: 24 }}>
                <h3>Your Account</h3>
                <table className="data-table" style={{ marginTop: 12 }}>
                    <tbody>
                        <tr>
                            <td style={{ fontWeight: 500 }}>Email</td>
                            <td>{userData?.email || user?.email}</td>
                        </tr>
                        <tr>
                            <td style={{ fontWeight: 500 }}>User ID</td>
                            <td>{userData?.id || user?.id}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    );
}
