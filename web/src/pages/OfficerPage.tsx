import StatusStrip from '../components/StatusStrip';

export default function OfficerPage() {
  return (
    <div className="page-container" id="officer-page">
      <StatusStrip />
      <header className="page-header">
        <div>
          <span className="badge badge-accent">Officer Overview</span>
          <h1 className="page-title">Operations & Oversight</h1>
          <p className="page-subtitle">Aggregate metrics, village distribution, and evidence review queue</p>
        </div>
      </header>

      <main className="officer-grid">
        <section className="card">
          <div className="card-header">
            <h2>Today's Summary Metrics</h2>
          </div>
          <div className="metrics-row">
            <div className="metric-box">
              <span className="metric-val">40</span>
              <span className="metric-lbl">Total Requests</span>
            </div>
            <div className="metric-box">
              <span className="metric-val">28</span>
              <span className="metric-lbl">Scheduled</span>
            </div>
            <div className="metric-box">
              <span className="metric-val">7</span>
              <span className="metric-lbl">Will Miss</span>
            </div>
            <div className="metric-box">
              <span className="metric-val">5</span>
              <span className="metric-lbl">Needs Info</span>
            </div>
          </div>
        </section>

        <section className="card">
          <div className="card-header">
            <h2>Review & Flagged Exceptions</h2>
            <span className="badge badge-warning">Needs Review</span>
          </div>
          <p className="placeholder-text">
            Flagged slots requiring officer review (distance anomalies, photo verification, GPS accuracy).
          </p>
        </section>
      </main>
    </div>
  );
}
