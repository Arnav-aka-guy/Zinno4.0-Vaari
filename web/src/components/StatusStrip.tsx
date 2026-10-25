import { useEffect, useState } from 'react';
import { getHealth, ApiError } from '../api';
import type { Health } from '../types';

export default function StatusStrip() {
  const [health, setHealth] = useState<Health | null>(null);
  const [error, setError] = useState<string | null>(null);

  const fetchStatus = async () => {
    try {
      const data = await getHealth();
      setHealth(data);
      setError(null);
    } catch (err) {
      if (err instanceof ApiError && err.error_code === 'NETWORK_DOWN') {
        setError('Server unreachable (NETWORK_DOWN)');
      } else {
        setError('Failed to fetch system status');
      }
    }
  };

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 15000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="status-strip" id="status-strip" role="region" aria-label="System Status">
      <div className="status-strip-inner">
        {error ? (
          <div className="status-item status-error">
            <span className="status-dot dot-error" />
            <span className="status-label">{error}</span>
          </div>
        ) : health ? (
          <>
            <div className="status-item">
              <span className={`status-dot ${health.status === 'ok' ? 'dot-ok' : 'dot-warn'}`} />
              <span className="status-label">System: <strong>{health.status}</strong></span>
            </div>
            <div className="status-item">
              <span className="status-label">DB: {health.database}</span>
            </div>
            <div className="status-item">
              <span className="status-label">Reader: {health.reader}</span>
            </div>
            <div className="status-item">
              <span className="status-label">Messages: {health.messaging}</span>
            </div>
            <div className="status-item">
              <span className="status-label">Today: {health.today}</span>
            </div>
            {health.demo_clock && (
              <div className="badge badge-warning" id="demo-clock-badge">
                DEMO CLOCK
              </div>
            )}
          </>
        ) : (
          <div className="status-item">
            <span className="status-label">Checking status…</span>
          </div>
        )}
      </div>
    </div>
  );
}
