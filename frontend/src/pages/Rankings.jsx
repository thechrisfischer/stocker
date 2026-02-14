import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import * as api from '../utils/api';

const STRATEGY_LABELS = {
    magic_formula_trailing: 'Magic Formula (Trailing)',
    magic_formula_future: 'Magic Formula (Future)',
    ebitda: 'EBITDA',
    pe_ratio_ttm: 'P/E Ratio (TTM)',
    pe_ratio_ftm: 'P/E Ratio (FTM)',
    garp_ratio: 'GARP Ratio',
    return_on_assets: 'Return on Assets',
    return_on_equity: 'Return on Equity',
    dividend_yield: 'Dividend Yield',
};

function StrategyPicker({ current }) {
    return (
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginBottom: 24 }}>
            {Object.entries(STRATEGY_LABELS).map(([key, label]) => (
                <Link
                    key={key}
                    to={`/rankings/${key}`}
                    className={`btn ${current === key ? 'btn-primary' : 'btn-secondary'}`}
                    style={{ fontSize: 13, padding: '6px 12px' }}
                >
                    {label}
                </Link>
            ))}
        </div>
    );
}

export default function Rankings() {
    const { strategy } = useParams();
    const [rankings, setRankings] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const activeStrategy = strategy || 'magic_formula_trailing';

    useEffect(() => {
        setLoading(true);
        setError(null);
        api.getRankings(activeStrategy)
            .then((data) => setRankings(data.rankings || []))
            .catch((err) => setError(err.data?.error || 'Failed to load rankings'))
            .finally(() => setLoading(false));
    }, [activeStrategy]);

    return (
        <div>
            <h1>Stock Rankings</h1>
            <p style={{ color: 'var(--color-text-secondary)', marginTop: 4, marginBottom: 20 }}>
                {STRATEGY_LABELS[activeStrategy] || activeStrategy}
            </p>

            <StrategyPicker current={activeStrategy} />

            {error && <div className="alert alert-error">{error}</div>}

            {loading ? (
                <p>Loading rankings...</p>
            ) : rankings.length === 0 ? (
                <div className="card">
                    <p style={{ color: 'var(--color-text-secondary)' }}>
                        No ranking data available for this strategy. Import stock data to see results.
                    </p>
                </div>
            ) : (
                <div className="card" style={{ padding: 0, overflow: 'auto' }}>
                    <table className="data-table">
                        <thead>
                            <tr>
                                <th>Rank</th>
                                <th>Symbol</th>
                                <th>Name</th>
                                <th>Score</th>
                                <th>P/E (TTM)</th>
                                <th>P/E (FTM)</th>
                                <th>GARP</th>
                                <th>PEG</th>
                                <th>ROA</th>
                            </tr>
                        </thead>
                        <tbody>
                            {rankings.map((row, i) => (
                                <tr key={row.symbol}>
                                    <td>{row.rank ?? i + 1}</td>
                                    <td style={{ fontWeight: 600 }}>{row.symbol}</td>
                                    <td>{row.name || '—'}</td>
                                    <td>{row.score != null ? row.score.toFixed(2) : '—'}</td>
                                    <td>{row.pe_ratio_ttm?.toFixed(2) ?? '—'}</td>
                                    <td>{row.pe_ratio_ftm?.toFixed(2) ?? '—'}</td>
                                    <td>{row.garp_ratio?.toFixed(2) ?? '—'}</td>
                                    <td>{row.peg_ratio?.toFixed(2) ?? '—'}</td>
                                    <td>{row.return_on_assets?.toFixed(2) ?? '—'}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
}
