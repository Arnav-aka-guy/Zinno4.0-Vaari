import { useState, useEffect, useMemo } from 'react';
import type { RequestOut, ScheduleDay, SlotOut } from '../types';

interface Props {
  requests: RequestOut[];
  schedule: ScheduleDay[];
  todayDate: string;
  centreLat?: number;
  centreLon?: number;
  onSelectRequest?: (req: RequestOut) => void;
}

interface MapPoint {
  id: string;
  requestId: number;
  label: string;
  village: string;
  acres: number;
  status: string;
  machineName?: string;
  seq?: number;
  lat: number;
  lon: number;
}

const STATUS_COLORS: Record<string, { fill: string; stroke: string; label: string }> = {
  scheduled: { fill: '#15803d', stroke: '#14532d', label: 'Scheduled' },
  in_progress: { fill: '#0284c7', stroke: '#0c4a6e', label: 'In Progress' },
  done: { fill: '#475569', stroke: '#1e293b', label: 'Done' },
  will_miss: { fill: '#dc2626', stroke: '#7f1d1d', label: 'Will Miss' },
  needs_info: { fill: '#d97706', stroke: '#78350f', label: 'Needs Info' },
  open: { fill: '#0369a1', stroke: '#0c4a6e', label: 'Open' },
};

// Deterministic village coordinate lookup matching app/seed/villages.json offsets from home centre
const VILLAGE_OFFSETS_KM: Record<string, { north: number; east: number }> = {
  'Pind Kalan': { north: 2.0, east: 1.0 },
  'Bhucho Khurd': { north: -3.0, east: 2.0 },
  'Rampura Phul': { north: 4.0, east: -3.0 },
  'Kot Shamir': { north: -5.0, east: -4.0 },
  'Maur Mandi': { north: 6.0, east: 5.0 },
  'Sangat Kalan': { north: -7.0, east: 6.0 },
  'Talwandi Sabo': { north: 8.0, east: -7.0 },
  'Goniana Mandi': { north: -9.0, east: -7.0 },
  'Tibbi Far': { north: 35.0, east: 20.0 },
};

function lon2tile(lon: number, zoom: number): number {
  return Math.floor(((lon + 180) / 360) * Math.pow(2, zoom));
}

function lat2tile(lat: number, zoom: number): number {
  return Math.floor(
    ((1 -
      Math.log(
        Math.tan((lat * Math.PI) / 180) + 1 / Math.cos((lat * Math.PI) / 180),
      ) /
        Math.PI) /
      2) *
      Math.pow(2, zoom),
  );
}

export default function DeskMapPanel({
  requests,
  schedule,
  todayDate,
  centreLat = 30.7333,
  centreLon = 76.7794,
  onSelectRequest,
}: Props) {
  const [tilesFailed, setTilesFailed] = useState<boolean>(
    typeof navigator !== 'undefined' ? !navigator.onLine : false,
  );
  const [hoveredId, setHoveredId] = useState<string | null>(null);

  useEffect(() => {
    const handleOffline = () => setTilesFailed(true);
    const handleOnline = () => setTilesFailed(false);
    window.addEventListener('offline', handleOffline);
    window.addEventListener('online', handleOnline);
    return () => {
      window.removeEventListener('offline', handleOffline);
      window.removeEventListener('online', handleOnline);
    };
  }, []);

  // Build map points from today's scheduled slots + all active requests
  const points = useMemo<MapPoint[]>(() => {
    const slotByReqId = new Map<number, SlotOut>();
    schedule.forEach((day) => {
      day.slots.forEach((s) => {
        slotByReqId.set(s.request_id, s);
      });
    });

    return requests
      .filter((r) => r.status !== 'cancelled')
      .map((r, idx) => {
        const slot = slotByReqId.get(r.id);
        let lat = slot?.location?.lat ?? null;
        let lon = slot?.location?.lon ?? null;

        if (lat == null || lon == null) {
          const offset = VILLAGE_OFFSETS_KM[r.village];
          if (offset) {
            // Slight deterministic jitter per request id so same-village pins don't overlap
            const jitterLat = ((r.id % 5) - 2) * 0.0018;
            const jitterLon = (((r.id * 3) % 5) - 2) * 0.0018;
            lat = +(centreLat + offset.north / 111.0 + jitterLat).toFixed(4);
            lon = +(centreLon + offset.east / (111.0 * 0.8596) + jitterLon).toFixed(4);
          } else {
            lat = +(centreLat + ((idx % 7) - 3) * 0.01).toFixed(4);
            lon = +(centreLon + (((idx * 2) % 7) - 3) * 0.01).toFixed(4);
          }
        }

        const effectiveStatus = slot ? slot.status : r.status;
        return {
          id: `pt-${r.id}`,
          requestId: r.id,
          label: `VR-${r.id}`,
          village: r.village,
          acres: r.acres,
          status: effectiveStatus,
          machineName: slot?.machine?.name ?? r.slot?.machine_name,
          seq: slot?.seq ?? r.slot?.seq,
          lat,
          lon,
        };
      });
  }, [requests, schedule, centreLat, centreLon]);

  // Project lat/lon into a 720x380 viewport centered around the home centre
  const VIEW_W = 720;
  const VIEW_H = 380;
  const LAT_SPAN = 0.24; // ~26 km north-south
  const LON_SPAN = 0.32; // ~30 km east-west

  const projectPoint = (lat: number, lon: number) => {
    const x = ((lon - (centreLon - LON_SPAN / 2)) / LON_SPAN) * VIEW_W;
    const y = ((centreLat + LAT_SPAN / 2 - lat) / LAT_SPAN) * VIEW_H;
    return {
      x: Math.max(20, Math.min(VIEW_W - 20, x)),
      y: Math.max(20, Math.min(VIEW_H - 20, y)),
    };
  };

  // OpenStreetMap tile URLs (zoom 11 around centreLat, centreLon)
  const zoom = 11;
  const centerTileX = lon2tile(centreLon, zoom);
  const centerTileY = lat2tile(centreLat, zoom);
  const tileGrid = [
    { dx: -1, dy: -1 },
    { dx: 0, dy: -1 },
    { dx: 1, dy: -1 },
    { dx: -1, dy: 0 },
    { dx: 0, dy: 0 },
    { dx: 1, dy: 0 },
  ];

  const todaySlotsFlat = useMemo(() => {
    const list: SlotOut[] = [];
    schedule.forEach((d) => {
      d.slots.forEach((s) => list.push(s));
    });
    return list.sort((a, b) => a.machine.id - b.machine.id || a.seq - b.seq);
  }, [schedule]);

  return (
    <div className="card" id="desk-map-panel">
      <div className="desk-header mb-2">
        <div>
          <h3>Field & Dispatch Map ({todayDate || 'Today'})</h3>
          <p className="card-subtitle">
            Today&apos;s scheduled jobs and plots coloured by status around the home centre
          </p>
        </div>

        {/* Status Legend */}
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.6rem', alignItems: 'center' }}>
          {Object.entries(STATUS_COLORS).map(([key, cfg]) => (
            <span
              key={key}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '4px',
                fontSize: '0.75rem',
                fontWeight: 600,
              }}
            >
              <span
                style={{
                  width: '10px',
                  height: '10px',
                  borderRadius: '50%',
                  backgroundColor: cfg.fill,
                  display: 'inline-block',
                }}
              />
              {cfg.label}
            </span>
          ))}
        </div>
      </div>

      {/* Offline / Tile Failure Banner required by Step 10 */}
      {tilesFailed && (
        <div className="outcome-banner outcome-warning mb-3" id="map-offline-banner">
          Map needs internet — showing the plain job and plot list below.
        </div>
      )}

      {/* Interactive Spatial Canvas + OSM Tile Background (when online) */}
      <div
        id="desk-map-canvas"
        style={{
          position: 'relative',
          width: '100%',
          height: '380px',
          borderRadius: '8px',
          border: '1px solid #cbd5e1',
          overflow: 'hidden',
          backgroundColor: '#f1f5f9',
          marginBottom: '1rem',
        }}
      >
        {/* OSM Tile Layer (hidden automatically if tiles fail to load) */}
        {!tilesFailed && (
          <div
            style={{
              position: 'absolute',
              inset: 0,
              display: 'grid',
              gridTemplateColumns: 'repeat(3, 1fr)',
              gridTemplateRows: 'repeat(2, 1fr)',
              opacity: 0.35,
              pointerEvents: 'none',
            }}
          >
            {tileGrid.map(({ dx, dy }) => {
              const tx = centerTileX + dx;
              const ty = centerTileY + dy;
              return (
                <img
                  key={`${tx}-${ty}`}
                  src={`https://tile.openstreetmap.org/${zoom}/${tx}/${ty}.png`}
                  alt=""
                  style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                  onError={() => setTilesFailed(true)}
                />
              );
            })}
          </div>
        )}

        {/* Vector Spatial Overlay (works 100% offline and online) */}
        <svg
          viewBox={`0 0 ${VIEW_W} ${VIEW_H}`}
          style={{ width: '100%', height: '100%', position: 'relative', zIndex: 2 }}
        >
          {/* 25 km Service Radius Circle */}
          <circle
            cx={VIEW_W / 2}
            cy={VIEW_H / 2}
            r={155}
            fill="rgba(21, 128, 61, 0.04)"
            stroke="#94a3b8"
            strokeDasharray="6 4"
            strokeWidth="1.5"
          />
          <text
            x={VIEW_W / 2 + 100}
            y={VIEW_H / 2 - 135}
            fontSize="11"
            fill="#475569"
            fontWeight="600"
          >
            25 km service radius
          </text>

          {/* Home Centre Marker */}
          <g transform={`translate(${VIEW_W / 2}, ${VIEW_H / 2})`}>
            <rect
              x={-8}
              y={-8}
              width={16}
              height={16}
              rx={3}
              fill="#0f172a"
              stroke="#ffffff"
              strokeWidth="2"
            />
            <text x={12} y={4} fontSize="12" fontWeight="800" fill="#0f172a">
              Home Centre
            </text>
          </g>

          {/* Plot & Job Markers Coloured by Status */}
          {points.map((pt) => {
            const { x, y } = projectPoint(pt.lat, pt.lon);
            const color = STATUS_COLORS[pt.status] || STATUS_COLORS.open;
            const isHovered = hoveredId === pt.id;
            return (
              <g
                key={pt.id}
                id={`map-marker-${pt.requestId}`}
                transform={`translate(${x}, ${y})`}
                style={{ cursor: 'pointer' }}
                onMouseEnter={() => setHoveredId(pt.id)}
                onMouseLeave={() => setHoveredId(null)}
                onClick={() => {
                  const found = requests.find((r) => r.id === pt.requestId);
                  if (found && onSelectRequest) onSelectRequest(found);
                }}
              >
                <circle
                  r={isHovered ? 9 : 6.5}
                  fill={color.fill}
                  stroke="#ffffff"
                  strokeWidth="2"
                />
                {(isHovered || pt.seq === 1) && (
                  <text
                    x={10}
                    y={4}
                    fontSize="11"
                    fontWeight="700"
                    fill="#0f172a"
                    style={{
                      paintOrder: 'stroke',
                      stroke: '#ffffff',
                      strokeWidth: '3px',
                    }}
                  >
                    {pt.label} ({pt.village}, {pt.acres} ac)
                  </text>
                )}
              </g>
            );
          })}
        </svg>
      </div>

      {/* Plain List of Today's Jobs & Plots (Always rendered when tiles fail or for accessibility) */}
      <div className="table-responsive" id="desk-map-plain-list">
        <h4>Today&apos;s Scheduled Jobs & Plot Locations ({todaySlotsFlat.length} today)</h4>
        <table className="data-table mt-2">
          <thead>
            <tr>
              <th>Seq</th>
              <th>Request</th>
              <th>Machine</th>
              <th>Village</th>
              <th>Acres</th>
              <th>Coordinates</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {todaySlotsFlat.map((s) => (
              <tr
                key={s.id}
                className="clickable-row"
                onClick={() => {
                  const found = requests.find((r) => r.id === s.request_id);
                  if (found && onSelectRequest) onSelectRequest(found);
                }}
              >
                <td>
                  <strong>#{s.seq}</strong>
                </td>
                <td>VR-{s.request_id}</td>
                <td>{s.machine.name}</td>
                <td>{s.village}</td>
                <td>{s.acres} ac</td>
                <td className="text-muted text-sm">
                  {s.location.lat != null && s.location.lon != null
                    ? `${s.location.lat.toFixed(4)}, ${s.location.lon.toFixed(4)} (${s.location.source})`
                    : 'Village centre'}
                </td>
                <td>
                  <span className={`status-pill pill-${s.status}`}>{s.status}</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
