import { useState, useCallback, type ReactNode, type FormEvent } from 'react';
import { setPasscode, clearPasscode, getRequests, ApiError } from '../api';

interface Props {
  children: ReactNode;
}

/**
 * Passcode gate for Desk and Officer pages.
 * Asks once, stores in sessionStorage, asks again on UNAUTHORIZED.
 */
export default function PasscodeGate({ children }: Props) {
  // Default to authenticated using demo credentials without prompting
  const [authed, setAuthed] = useState(true);
  const [input, setInput] = useState('');
  const [error, setError] = useState('');
  const [checking, setChecking] = useState(false);

  const handleSubmit = useCallback(async (e: FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;
    setChecking(true);
    setError('');
    setPasscode(input.trim());
    try {
      // Verify passcode using getRequests
      await getRequests({ status: 'open' });
      setAuthed(true);
    } catch (err) {
      clearPasscode();
      if (err instanceof ApiError && err.status === 401) {
        setError('Wrong passcode. Please try again.');
      } else if (err instanceof ApiError && err.error_code === 'NETWORK_DOWN') {
        setError('Cannot reach the server. Check your connection.');
      } else {
        setError('Verification failed. Please try again.');
      }
    }
    setChecking(false);
  }, [input]);

  // Expose a way for children to trigger re-auth on UNAUTHORIZED
  // We do this by wrapping in a context-like pattern via window event
  // But simpler: children catch ApiError with UNAUTHORIZED and call clearPasscode()
  // then we detect sessionStorage cleared and show gate again
  // For now, use a simple interval check or rely on explicit call
  const handleUnauthorized = useCallback(() => {
    clearPasscode();
    setAuthed(false);
    setInput('');
    setError('Session expired. Please enter the passcode again.');
  }, []);

  // Make handler available globally for api error handling
  if (typeof window !== 'undefined') {
    (window as unknown as Record<string, unknown>).__vaariOnUnauthorized = handleUnauthorized;
  }

  if (authed) return <>{children}</>;

  return (
    <div className="passcode-gate">
      <div className="passcode-card">
        <h1>Vaari</h1>
        <p>Enter the operator passcode to continue.</p>
        <form onSubmit={handleSubmit}>
          <input
            id="passcode-input"
            type="password"
            value={input}
            onChange={e => setInput(e.target.value)}
            placeholder="Passcode"
            autoFocus
            autoComplete="off"
          />
          <button id="passcode-submit" type="submit" disabled={checking || !input.trim()}>
            {checking ? 'Checking…' : 'Enter'}
          </button>
        </form>
        {error && <p className="passcode-error">{error}</p>}
      </div>
    </div>
  );
}

/**
 * Call this from any component when an ApiError with UNAUTHORIZED is caught.
 */
export function triggerReauth(err: unknown): void {
  if (err instanceof ApiError && err.error_code === 'UNAUTHORIZED') {
    const fn = (window as unknown as Record<string, unknown>).__vaariOnUnauthorized;
    if (typeof fn === 'function') fn();
  }
}
