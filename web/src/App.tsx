import { BrowserRouter, Routes, Route, Navigate, NavLink } from 'react-router-dom';
import PasscodeGate from './components/PasscodeGate';
import DeskPage from './pages/DeskPage';
import DriverPage from './pages/DriverPage';
import OfficerPage from './pages/OfficerPage';
import RecordPage from './pages/RecordPage';

export default function App() {
  return (
    <BrowserRouter>
      <div className="app-shell">
        <header className="app-navbar">
          <div className="navbar-container">
            <div className="brand-group">
              <span className="brand-leaf">🌾</span>
              <span className="brand-name">Vaari</span>
              <span className="brand-phase">v0.1</span>
            </div>
            <nav className="nav-links">
              <NavLink
                to="/desk"
                className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
                id="nav-desk"
              >
                Desk
              </NavLink>
              <NavLink
                to="/officer"
                className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
                id="nav-officer"
              >
                Officer
              </NavLink>
              <NavLink
                to="/driver/demo-machine"
                className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
                id="nav-driver"
              >
                Driver View
              </NavLink>
              <NavLink
                to="/record/demo-token"
                className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
                id="nav-record"
              >
                Record View
              </NavLink>
            </nav>
          </div>
        </header>

        <div className="app-content">
          <Routes>
            <Route path="/" element={<Navigate to="/desk" replace />} />
            <Route
              path="/desk"
              element={
                <PasscodeGate>
                  <DeskPage />
                </PasscodeGate>
              }
            />
            <Route path="/driver/:machineToken" element={<DriverPage />} />
            <Route
              path="/officer"
              element={
                <PasscodeGate>
                  <OfficerPage />
                </PasscodeGate>
              }
            />
            <Route path="/record/:token" element={<RecordPage />} />
            <Route path="*" element={<Navigate to="/desk" replace />} />
          </Routes>
        </div>
      </div>
    </BrowserRouter>
  );
}
