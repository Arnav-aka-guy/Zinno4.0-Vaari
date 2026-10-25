import { useEffect, useState } from 'react';
import StatusStrip from '../components/StatusStrip';
import { getRequests, ApiError } from '../api';
import { triggerReauth } from '../components/PasscodeGate';
import type { RequestOut } from '../types';

export default function DeskPage() {
  const [requests, setRequests] = useState<RequestOut[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    getRequests()
      .then((data) => {
        if (active) {
          setRequests(data);
          setLoading(false);
        }
      })
      .catch((err) => {
        if (active) {
          if (err instanceof ApiError && err.status === 401) {
            triggerReauth(err);
          } else {
            setError(err.message || 'Failed to load requests');
          }
          setLoading(false);
        }
      });
    return () => {
      active = false;
    };
  }, []);

  return (
    <div className="page-container" id="desk-page">
      <StatusStrip />
      <header className="page-header">
        <div>
          <h1 className="page-title">Operator Desk</h1>
          <p className="page-subtitle">Field service dispatch, request intake, and live machine schedules</p>
        </div>
      </header>

      <main className="desk-grid">
        <section className="card">
          <div className="card-header">
            <h2>Recent Requests ({loading ? '…' : requests.length})</h2>
            <span className="badge badge-info">Desk View</span>
          </div>
          {loading ? (
            <p className="placeholder-text">Loading requests from backend…</p>
          ) : error ? (
            <p className="placeholder-error">{error}</p>
          ) : (
            <div className="table-responsive">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Village</th>
                    <th>Acres</th>
                    <th>Service</th>
                    <th>Status</th>
                    <th>Deadline</th>
                  </tr>
                </thead>
                <tbody>
                  {requests.slice(0, 5).map((r) => (
                    <tr key={r.id}>
                      <td><strong>VR-{r.id}</strong></td>
                      <td>{r.village}</td>
                      <td>{r.acres}</td>
                      <td>{r.service_type}</td>
                      <td>
                        <span className={`status-pill pill-${r.status}`}>{r.status}</span>
                      </td>
                      <td>{r.deadline_date || '—'}</td>
                    </tr>
                  ))}
                  {requests.length === 0 && (
                    <tr>
                      <td colSpan={6} className="text-center">No requests found.</td>
                    </tr>
                  )}
                </tbody>
              </table>
              {requests.length > 5 && (
                <p className="table-note">+ {requests.length - 5} more requests queued.</p>
              )}
            </div>
          )}
        </section>

        <section className="card">
          <div className="card-header">
            <h2>Daily Schedule & Dispatch</h2>
            <span className="badge badge-neutral">Scheduled</span>
          </div>
          <p className="placeholder-text">
            Machine dispatch schedules, slot timelines, and will-miss alerts will be rendered here.
          </p>
        </section>
      </main>
    </div>
  );
}
