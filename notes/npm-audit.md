# Web Dependency Audit (React Router v6)

## Findings (
pm audit in web/)


pm audit reports 2 moderate severity vulnerabilities in 
eact-router / 
eact-router-dom@6.30.6:

1. **GHSA-337j-9hxr-rhxg**: Arbitrary Constructor Injection via deserializeErrors() in React Router SSR Hydration.
2. **GHSA-wrjc-x8rr-h8h6**: React Router open redirect via backslash in <Link> and useNavigate (CVE-2025-68470 bypass).

## Production vs Dev Impact

- **Production build inclusion**: 
eact-router-dom is a production client runtime dependency (bundled into the Vite SPA).
- **Exploitability in Vaari**:
  - **SSR Hydration injection**: Vaari is a pure client-side SPA built with Vite; it does not use Server-Side Rendering (SSR) or error hydration. This code path is unreachable.
  - **Open redirect**: Vaari uses only static, internal application routes (/, /record/:id, /driver, /officer, /intake, etc.). No user-controlled URLs or external redirect query parameters are passed to <Link> or useNavigate().

## Resolution Decision

- A fix is only available via 
eact-router-dom@7.18.5+, which introduces major breaking API and architecture changes.
- In accordance with the non-breaking upgrade policy, 
pm audit fix --force is not applied. Upgrading to React Router v7 is deferred to the v0.6 roadmap.
