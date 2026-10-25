import { useState, useEffect } from 'react';
import { getWillMiss, ApiError } from '../api';
import { friendlyError } from '../errors';
import type { WillMissItem } from '../types';

interface Props {
  onSelectRequest?: (requestId: number) => void;
}

export default function WillMissTab({ onSelectRequest }: Props) {
  const [items, setItems] = useState<WillMissItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadWillMiss = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getWillMiss();
      setItems(data);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(friendlyError(err.error_code) || err.message);
      } else {
        setError('Failed to load will-miss list.');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadWillMiss();
  }, []);

  if (loading) {
    return <div className="loading-state">Loading will-miss requests…</div>;
  }

  if (error) {
    return (
      <div className="outcome-banner outcome-error">
        {error}
        <button type="button" className="btn btn-secondary btn-sm ml-2" onClick={loadWillMiss}>
          Retry
        </button>
      </div>
    );
  }

  if (items.length === 0) {
    return (
      <div className="empty-state card">
        <p>No unserved requests! Every open request is scheduled within its sowing window.</p>
      </div>
    );
  }

  return (
    <div className="will-miss-container" id="will-miss-tab">
      <div className="table-header-info">
        <h3>Unserved Requests ({items.length})</h3>
        <p className="card-subtitle">
          Requests that cannot meet their deadline with current capacity or constraints
        </p>
      </div>

      <div className="table-responsive">
        <table className="data-table will-miss-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Village</th>
              <th>Acres</th>
              <th>Service</th>
              <th>Deadline</th>
              <th>Reason Code</th>
              <th>Explanation & Next Action</th>
              <th>Alternative Centre</th>
            </tr>
          </thead>
          <tbody>
            {items.map(item => (
              <tr
                key={item.request_id}
                className="clickable-row"
                onClick={() => onSelectRequest?.(item.request_id)}
                title="Click to view details"
              >
                <td>
                  <strong>VR-{item.request_id}</strong>
                </td>
                <td>{item.village}</td>
                <td>{item.acres}</td>
                <td className="text-capitalize">{item.service_type.replace('_', ' ')}</td>
                <td>{item.deadline_date || '—'}</td>
                <td>
                  <span className={`reason-chip chip-${item.reason_code.toLowerCase()}`}>
                    {item.reason_code}
                  </span>
                </td>
                <td className="explanation-cell">
                  <div className="reason-sentence">{item.reason}</div>
                  {item.next_action && (
                    <div className="next-action-text">
                      <strong>Next: </strong>
                      <span>{item.next_action}</span>
                    </div>
                  )}
                </td>
                <td>
                  {item.nearest_alternative ? (
                    <span className="alternative-tag">
                      {item.nearest_alternative}
                      {item.alternative_distance_km != null && (
                        <span className="text-muted"> ({item.alternative_distance_km} km)</span>
                      )}
                    </span>
                  ) : (
                    <span className="text-muted">None available</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
