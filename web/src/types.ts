// Types matching CONTRACT.md section 11 output shapes exactly.

// ── Error shape ──────────────────────────────────────────────
export interface ApiErrorShape {
  error_code: string;
  message: string;
  details: Record<string, unknown>;
}

// ── Health ───────────────────────────────────────────────────
export interface Health {
  status: string;
  database: string;
  reader: string;
  messaging: string;
  satellite: string;
  today: string;
  demo_clock: boolean;
  version: string;
}

// ── RequestOut ───────────────────────────────────────────────
export interface RequestFarmer {
  name: string | null;
  phone: string;
}

export interface RequestExplanation {
  reason_code: string | null;
  reason: string | null;
  data_used: Record<string, unknown>;
  next_action: string | null;
  nearest_alternative: string | null;
  alternative_distance_km: number | null;
}

export interface RequestSlot {
  id: number;
  machine_id: number;
  machine_name: string;
  service_date: string;
  seq: number;
  status: string;
}

export interface RequestOut {
  id: number;
  status: string;
  source: string;
  farmer: RequestFarmer;
  village: string;
  acres: number;
  service_type: string;
  harvest_date: string | null;
  sow_by: string | null;
  deadline_date: string | null;
  explanation: RequestExplanation;
  slot: RequestSlot | null;
  badges: string[];
  created_at: string;
}

// ── MachineOut ───────────────────────────────────────────────
export interface MachineOut {
  id: number;
  name: string;
  type: string;
  service_types: string[];
  capacity_acres_per_day: number;
  status: string;
  active_from: string | null;
  active_to: string | null;
  driver_path: string;
}

// ── SlotOut ──────────────────────────────────────────────────
export interface SlotLocation {
  lat: number | null;
  lon: number | null;
  source: string;
}

export interface SlotMachine {
  id: number;
  name: string;
}

export interface SlotOut {
  id: number;
  seq: number;
  status: string;
  service_date: string;
  machine: SlotMachine;
  request_id: number;
  farmer_name: string | null;
  village: string;
  acres: number;
  deadline_date: string;
  location: SlotLocation;
  est_distance_km: number;
  link_token: string | null;
  needs_review: boolean;
  flags: string[];
  started_at: string | null;
  done_at: string | null;
  record_token: string | null;
}

// ── SlotEvidenceOut ──────────────────────────────────────────
export interface EvidenceDetail {
  kind: string;
  lat: number | null;
  lon: number | null;
  accuracy_m: number | null;
  distance_to_plot_m: number | null;
  plausible: boolean | null;
  position_state: string;
  photo: string;
  timestamp: string;
}

export interface SlotEvidenceOut {
  slot_id: number;
  status: string;
  evidence: EvidenceDetail;
  flags: string[];
  needs_review: boolean;
  record_url: string | null;
}

// ── RecordOut ────────────────────────────────────────────────
export interface RecordOut {
  request_id: string;
  village: string;
  machine: string;
  acres: number;
  service_type: string;
  scheduled: string;
  deadline_date: string;
  started_at: string | null;
  done_at: string | null;
  start_position: string;
  done_position: string;
  start_photo: string;
  done_photo: string;
  evidence_note: string | null;
  farmer_confirmed: boolean | null;
  outcome: string;
  on_time: boolean;
  flags: string[];
  needs_review: boolean;
  badges: string[];
  record_hash: string;
  hash_version: string;
}

export interface RecordVerify {
  stored: string;
  recomputed: string;
  match: boolean;
}

// ── Will-miss item ───────────────────────────────────────────
export interface WillMissItem {
  request_id: number;
  village: string;
  acres: number;
  service_type: string;
  deadline_date: string;
  status: string;
  reason_code: string;
  reason: string;
  data_used: Record<string, unknown>;
  next_action: string;
  nearest_alternative: string | null;
  alternative_distance_km: number | null;
}

// ── Schedule day ─────────────────────────────────────────────
export interface ScheduleDay {
  machine_id: number;
  machine_name: string;
  date: string;
  capacity_acres: number;
  used_acres: number;
  slots: SlotOut[];
}

// ── Dashboard summary ────────────────────────────────────────
export interface DashboardSummary {
  total: number;
  needs_info: number;
  scheduled: number;
  in_progress: number;
  completed: number;
  will_miss: number;
  needs_review: number;
  capacity_used_pct: number;
  by_reason: Record<string, number>;
  by_village: Record<string, number>;
  today: string;
}

// ── Slot message ─────────────────────────────────────────────
export interface SlotMessage {
  slot_id: number;
  language: string;
  body: string;
  body_en: string;
  wa_link: string;
  tel_link: string;
  service_code: string;
}

// ── Schedule run result ──────────────────────────────────────
export interface ScheduleRunResult {
  total: number;
  needs_info: number;
  open: number;
  scheduled: number;
  done: number;
  will_miss: number;
  cancelled: number;
  ran_in_ms: number;
  today: string;
}

// ── Driver page response ─────────────────────────────────────
export interface DriverResponse {
  machine: SlotMachine;
  date: string;
  slots: SlotOut[];
}

// ── Request body types ───────────────────────────────────────
export interface CreateRequestBody {
  phone: string;
  name?: string;
  village: string;
  lat?: number;
  lon?: number;
  acres: number;
  service_type: string;
  harvest_date?: string;
  deadline_date?: string;
  consent_service: boolean;
  consent_evidence: boolean;
  consent_share: boolean;
}

export interface PatchRequestBody {
  name?: string;
  village?: string;
  lat?: number;
  lon?: number;
  acres?: number;
  service_type?: string;
  harvest_date?: string;
  deadline_date?: string;
}
