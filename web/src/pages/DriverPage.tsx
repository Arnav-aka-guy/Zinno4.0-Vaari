import { useParams } from 'react-router-dom';

export default function DriverPage() {
  const { machineToken } = useParams<{ machineToken: string }>();

  return (
    <div className="page-container" id="driver-page">
      <header className="page-header">
        <div>
          <span className="badge badge-accent">Driver Mobile View</span>
          <h1 className="page-title">Machine Job Queue</h1>
          <p className="page-subtitle">
            Token: <code>{machineToken || 'unknown'}</code>
          </p>
        </div>
      </header>

      <main className="driver-main">
        <section className="card">
          <div className="card-header">
            <h2>Today's Allocated Slots</h2>
            <span className="badge badge-neutral">In-Field Execution</span>
          </div>
          <p className="placeholder-text">
            Slot cards, GPS location check, start/done photo uploads, and farmer completion code entry.
          </p>
          <div className="driver-slot-mock">
            <div className="slot-mock-header">
              <span className="slot-mock-seq">Slot #1</span>
              <span className="status-pill pill-scheduled">scheduled</span>
            </div>
            <p><strong>Village:</strong> Pind Kalan (3.2 acres)</p>
            <p><strong>Service:</strong> Super Seeder</p>
            <div className="action-row">
              <button className="btn btn-primary" disabled>Start Job (Upload Photo)</button>
              <button className="btn btn-secondary" disabled>Complete</button>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}
