import { useParams } from 'react-router-dom';

export default function RecordPage() {
  const { token } = useParams<{ token: string }>();

  return (
    <div className="page-container" id="record-page">
      <header className="page-header">
        <div>
          <span className="badge badge-success">Public Verification</span>
          <h1 className="page-title">Service Completion Record</h1>
          <p className="page-subtitle">
            Cryptographic proof and field completion audit
          </p>
        </div>
      </header>

      <main className="record-main">
        <section className="card">
          <div className="card-header">
            <h2>Record Token: <code>{token || 'unknown'}</code></h2>
            <span className="badge badge-neutral">Tamper-Evident</span>
          </div>
          <p className="placeholder-text">
            Public verification page showing job outcome, timestamps, GPS plausibility, photo evidence, and SHA-256 hash match.
          </p>
          <div className="audit-box">
            <p><strong>Hash Verification:</strong> <code>sha256:verifying...</code></p>
            <p><strong>Status:</strong> COMPLETED</p>
          </div>
        </section>
      </main>
    </div>
  );
}
