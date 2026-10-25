/**
 * api.ts — the ONLY file that calls fetch.
 * One typed function per route the screens need.
 * Every non-2xx response becomes a thrown ApiError.
 * A network failure becomes error_code "NETWORK_DOWN".
 */
import type {
  ApiErrorShape,
  CreateRequestBody,
  DashboardSummary,
  DriverResponse,
  Health,
  MachineOut,
  PatchRequestBody,
  RecordOut,
  RecordVerify,
  RequestOut,
  ScheduleDay,
  ScheduleRunResult,
  SlotEvidenceOut,
  SlotMessage,
  SlotOut,
  WillMissItem,
} from './types';

// ── ApiError ─────────────────────────────────────────────────
export class ApiError extends Error {
  error_code: string;
  details: Record<string, unknown>;
  status: number;

  constructor(shape: ApiErrorShape, status: number) {
    super(shape.message);
    this.name = 'ApiError';
    this.error_code = shape.error_code;
    this.details = shape.details ?? {};
    this.status = status;
  }
}

// ── Helpers ──────────────────────────────────────────────────
function getPasscode(): string | null {
  return sessionStorage.getItem('vaari_passcode');
}

export function setPasscode(code: string): void {
  sessionStorage.setItem('vaari_passcode', code);
}

export function clearPasscode(): void {
  sessionStorage.removeItem('vaari_passcode');
}

function authHeaders(kind: 'passcode' | 'slot', token?: string): Record<string, string> {
  const h: Record<string, string> = {};
  if (kind === 'passcode') {
    const pc = getPasscode();
    if (pc) h['X-Vaari-Passcode'] = pc;
  } else if (kind === 'slot' && token) {
    h['X-Vaari-Slot-Token'] = token;
  }
  return h;
}

async function request<T>(url: string, init?: RequestInit): Promise<T> {
  let res: Response;
  try {
    res = await fetch(url, init);
  } catch {
    throw new ApiError(
      { error_code: 'NETWORK_DOWN', message: 'Cannot reach the server.', details: {} },
      0,
    );
  }
  if (res.status === 204) return undefined as unknown as T;
  const body = await res.json().catch(() => ({
    error_code: 'UNKNOWN',
    message: res.statusText,
    details: {},
  }));
  if (!res.ok) {
    throw new ApiError(body as ApiErrorShape, res.status);
  }
  return body as T;
}

function jsonReq(
  method: string,
  url: string,
  data?: unknown,
  auth: 'passcode' | 'none' = 'passcode',
): Promise<Response> {
  // This is only used internally; the public API uses request()
  void method; void url; void data; void auth;
  throw new Error('Use request() directly');
}
void jsonReq; // suppress unused warning

// ── Health (public) ──────────────────────────────────────────
export function getHealth(): Promise<Health> {
  return request<Health>('/api/health');
}

// ── Requests (passcode) ─────────────────────────────────────
export function getRequests(params?: {
  status?: string;
  village?: string;
  date?: string;
  service_type?: string;
}): Promise<RequestOut[]> {
  const q = new URLSearchParams();
  if (params?.status) q.set('status', params.status);
  if (params?.village) q.set('village', params.village);
  if (params?.date) q.set('date', params.date);
  if (params?.service_type) q.set('service_type', params.service_type);
  const qs = q.toString();
  return request<RequestOut[]>(`/api/requests${qs ? '?' + qs : ''}`, {
    headers: { ...authHeaders('passcode') },
  });
}

export function getRequest(id: number): Promise<RequestOut> {
  return request<RequestOut>(`/api/requests/${id}`, {
    headers: { ...authHeaders('passcode') },
  });
}

export function createRequest(body: CreateRequestBody): Promise<RequestOut> {
  return request<RequestOut>('/api/requests', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeaders('passcode') },
    body: JSON.stringify(body),
  });
}

export function patchRequest(id: number, body: PatchRequestBody): Promise<RequestOut> {
  return request<RequestOut>(`/api/requests/${id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json', ...authHeaders('passcode') },
    body: JSON.stringify(body),
  });
}

export function deleteRequest(id: number): Promise<RequestOut> {
  return request<RequestOut>(`/api/requests/${id}`, {
    method: 'DELETE',
    headers: { ...authHeaders('passcode') },
  });
}

// ── Machines (passcode) ──────────────────────────────────────
export function getMachines(): Promise<MachineOut[]> {
  return request<MachineOut[]>('/api/machines', {
    headers: { ...authHeaders('passcode') },
  });
}

export function patchMachine(
  id: number,
  body: {
    status?: string;
    name?: string;
    type?: string;
    service_types?: string[];
    capacity_acres_per_day?: number;
  },
): Promise<MachineOut> {
  return request<MachineOut>(`/api/machines/${id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json', ...authHeaders('passcode') },
    body: JSON.stringify(body),
  });
}

// ── Schedule (passcode) ──────────────────────────────────────
export function runSchedule(): Promise<ScheduleRunResult> {
  return request<ScheduleRunResult>('/api/schedule/run', {
    method: 'POST',
    headers: { ...authHeaders('passcode') },
  });
}

export function getSchedule(params?: {
  date?: string;
  machine_id?: number;
}): Promise<ScheduleDay[]> {
  const q = new URLSearchParams();
  if (params?.date) q.set('date', params.date);
  if (params?.machine_id != null) q.set('machine_id', String(params.machine_id));
  const qs = q.toString();
  return request<ScheduleDay[]>(`/api/schedule${qs ? '?' + qs : ''}`, {
    headers: { ...authHeaders('passcode') },
  });
}

export function getWillMiss(): Promise<WillMissItem[]> {
  return request<WillMissItem[]>('/api/schedule/will-miss', {
    headers: { ...authHeaders('passcode') },
  });
}

// ── Slots (passcode or machine token) ────────────────────────
export function getSlots(params?: {
  date?: string;
  machine_id?: number;
}): Promise<SlotOut[]> {
  const q = new URLSearchParams();
  if (params?.date) q.set('date', params.date);
  if (params?.machine_id != null) q.set('machine_id', String(params.machine_id));
  const qs = q.toString();
  return request<SlotOut[]>(`/api/slots${qs ? '?' + qs : ''}`, {
    headers: { ...authHeaders('passcode') },
  });
}

// ── Slot message (passcode) ──────────────────────────────────
export function getSlotMessage(slotId: number): Promise<SlotMessage> {
  return request<SlotMessage>(`/api/slots/${slotId}/message`, {
    headers: { ...authHeaders('passcode') },
  });
}

export function markMessageOpened(
  slotId: number,
  channel: 'wa_link' | 'tel',
): Promise<void> {
  return request<void>(`/api/slots/${slotId}/message/opened`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeaders('passcode') },
    body: JSON.stringify({ channel }),
  });
}

// ── Slot actions (slot token auth) ───────────────────────────
export function startSlot(
  slotId: number,
  slotToken: string,
  data: { photo?: File; lat?: number; lon?: number; accuracy_m?: number },
): Promise<SlotEvidenceOut> {
  const form = new FormData();
  if (data.photo) form.append('photo', data.photo);
  if (data.lat != null) form.append('lat', String(data.lat));
  if (data.lon != null) form.append('lon', String(data.lon));
  if (data.accuracy_m != null) form.append('accuracy_m', String(data.accuracy_m));
  return request<SlotEvidenceOut>(`/api/slots/${slotId}/start`, {
    method: 'POST',
    headers: { ...authHeaders('slot', slotToken) },
    body: form,
  });
}

export function doneSlot(
  slotId: number,
  slotToken: string,
  data: {
    photo?: File;
    lat?: number;
    lon?: number;
    accuracy_m?: number;
    service_code?: string;
  },
): Promise<SlotEvidenceOut> {
  const form = new FormData();
  if (data.photo) form.append('photo', data.photo);
  if (data.lat != null) form.append('lat', String(data.lat));
  if (data.lon != null) form.append('lon', String(data.lon));
  if (data.accuracy_m != null) form.append('accuracy_m', String(data.accuracy_m));
  if (data.service_code) form.append('service_code', data.service_code);
  return request<SlotEvidenceOut>(`/api/slots/${slotId}/done`, {
    method: 'POST',
    headers: { ...authHeaders('slot', slotToken) },
    body: form,
  });
}

export function notServedSlot(
  slotId: number,
  slotToken: string,
  data: { reason: string; note?: string },
): Promise<SlotOut> {
  return request<SlotOut>(`/api/slots/${slotId}/not-served`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeaders('slot', slotToken) },
    body: JSON.stringify(data),
  });
}

// ── Driver (token in path, public) ───────────────────────────
export function getDriver(machineToken: string, date?: string): Promise<DriverResponse> {
  const q = date ? `?date=${date}` : '';
  return request<DriverResponse>(`/api/driver/${machineToken}${q}`);
}

// ── Records (token in path, public) ──────────────────────────
export function getRecord(token: string): Promise<RecordOut> {
  return request<RecordOut>(`/api/records/${token}`);
}

export function verifyRecord(token: string): Promise<RecordVerify> {
  return request<RecordVerify>(`/api/records/${token}/verify`);
}

// ── Dashboard (passcode) ─────────────────────────────────────
export function getDashboardSummary(params?: {
  village?: string;
  date?: string;
  machine_id?: number;
  status?: string;
}): Promise<DashboardSummary> {
  const q = new URLSearchParams();
  if (params?.village) q.set('village', params.village);
  if (params?.date) q.set('date', params.date);
  if (params?.machine_id != null) q.set('machine_id', String(params.machine_id));
  if (params?.status) q.set('status', params.status);
  const qs = q.toString();
  return request<DashboardSummary>(`/api/dashboard/summary${qs ? '?' + qs : ''}`, {
    headers: { ...authHeaders('passcode') },
  });
}
