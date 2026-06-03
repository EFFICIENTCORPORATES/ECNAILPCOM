# Document 14 — Authentication and Security Model
## Auth Design, API Key Lifecycle, Tenant Isolation, and Security Controls

**AUDIENCE:** Backend implementors and security reviewers. This document defines non-negotiable security requirements.

---

## 1. PASSWORD SECURITY

### Hashing Algorithm
- **Use argon2id** (not bcrypt, not SHA256, not MD5).
- Recommended parameters: memory=64MB, iterations=3, parallelism=2.
- Do not implement custom password hashing. Use the language's established argon2id library.

### Password Policy
- Minimum 8 characters.
- No maximum length restriction (to support passphrases).
- No complexity requirements (complexity rules cause weak passwords due to predictable patterns).
- Check against a common-password list at signup (e.g., top 10,000 common passwords).

### Password Reset
- Tokens: cryptographically random 32 bytes, URL-safe base64 encoded.
- Stored as SHA-256 hash in DB (not plaintext).
- Expires after 1 hour.
- One-time use: invalidated immediately on use.
- Do NOT confirm whether an email exists in the "forgot password" response.

---

## 2. SESSION MANAGEMENT (JWT)

### Access Token
- Algorithm: RS256 (asymmetric). Public key verifiable by any service.
- Lifetime: 15 minutes.
- Claims: `{sub: user_id, wid: workspace_id, role: 'OWNER', exp, iat, jti}`.
- `jti` (JWT ID): Used for revocation tracking if needed.

### Refresh Token
- 256-bit cryptographically random bytes, URL-safe base64 encoded.
- Stored as SHA-256 hash in `refresh_tokens` table.
- Lifetime: 7 days (rolling — refreshed each time it's used).
- Delivered via `HttpOnly; Secure; SameSite=Strict` cookie.
- NOT in response body or localStorage.
- Rotation: Each use of a refresh token issues a new refresh token and invalidates the old one.
- Detection of replay: If a revoked refresh token is presented, revoke ALL tokens for that user (token theft indicator).

### Token Storage (Client)
- Access token: In-memory only (JS variable). Never localStorage/sessionStorage.
- Refresh token: httpOnly cookie only. Never accessible to JavaScript.

### Session Termination
- Logout: Revoke refresh token in DB. Client clears cookie and in-memory access token.
- Password change: Revoke ALL active refresh tokens for the user.
- Account suspension: Revoke all tokens. New logins rejected.

---

## 3. API KEY MANAGEMENT

### Key Generation
```
Format: pk_live_<32_hex_random_chars>
Total length: 40 characters
Example: pk_live_a3f8c2d1e4b7a9f0c1d2e3f4a5b6c7d8

For future test/sandbox mode: pk_test_<32_hex_random_chars>
```

Generate using cryptographically secure random number generator (CSPRNG). Do not use UUID.

### Key Storage
- **NEVER store the plaintext key.**
- Store: `key_hash = SHA256(full_key_string)` in `api_keys.key_hash`.
- Store: `key_prefix = first 8 chars` in `api_keys.key_prefix` (for lookup optimization).
- Store: `key_preview = first 8 + "..." + last 4` in `api_keys.key_preview` (for display).
- The full key is shown ONCE in the API response on creation. After that, it is irrecoverable.

### Key Authentication Flow
```
1. Extract X-API-Key header value
2. Compute lookup_hash = SHA256(key_value)
3. Query: SELECT * FROM api_keys WHERE key_hash = lookup_hash AND status = 'ACTIVE'
4. If not found → 401 INVALID_API_KEY
5. If workspace is suspended → 403 WORKSPACE_SUSPENDED
6. Load workspace context from api_keys.workspace_id
7. Set user_id = null, api_key_id = key_id, role = 'API_KEY'
8. Update api_keys.last_used_at = NOW(), last_used_ip = request IP
9. Log to audit_log: action = 'api_key.used'
```

**Lookup optimization:** Index on `key_hash`. The prefix can be used as a pre-filter if performance requires (unlikely at MVP scale).

### Key Revocation
- Immediate: Set `api_keys.status = 'REVOKED'` and `revoked_at = NOW()`.
- No grace period. Revocation is instant.
- Log to audit_log: `api_key.revoked`.

### Key Rotation
- Creates new key atomically: INSERT new key, UPDATE old key status to 'ROTATED' with `rotated_to = new_key_id`.
- Old key is immediately invalid.
- Returns new full key (shown once).
- Log to audit_log: `api_key.rotated`.

### Limits
- Free plan: max 3 active keys per workspace.
- Paid plan: up to 10 keys per workspace.

---

## 4. BOT PROTECTION

### Signup and Login
- **hCaptcha or Cloudflare Turnstile** on the signup and login forms.
- Server-side validation of captcha token before processing.
- Progressive lockout: After 5 failed logins → require captcha. After 10 → lock for 15 minutes.

### Anonymous Demo Endpoint
- IP-based rate limit: 5 calls per IP per day (hard limit, no soft paywall).
- Return 429 with `retry_after` if exceeded.
- Captcha on the demo form if IP shows suspicious activity (>10 attempts across multiple days from same IP).

### API Key Creation
- Require JWT auth (not API key auth) to create API keys. Prevents automated key farming.
- Rate limit: max 3 key creation attempts per hour per user.

---

## 5. TENANT ISOLATION

### Application-Level
Every data access function MUST accept and check `workspace_id`. No "get all records" functions without tenant scope.

Pattern for every data query:
```sql
-- CORRECT:
SELECT * FROM business_profile WHERE business_id = $1 AND workspace_id = $2;

-- WRONG (never do this):
SELECT * FROM business_profile WHERE business_id = $1;
```

### Database-Level (PostgreSQL RLS)
Enable Row Level Security as defense-in-depth:

```sql
ALTER TABLE business_profile ENABLE ROW LEVEL SECURITY;
CREATE POLICY workspace_isolation ON business_profile
  USING (workspace_id = current_setting('app.current_workspace_id')::uuid);
```

Set `app.current_workspace_id` as a session variable at the start of each DB transaction.

### Cross-Tenant Leakage Prevention
- Never return 404 for resources that exist in another workspace. Return 403 (so the requester can't confirm existence).
- Never log workspace A's data in error messages surfaced to workspace B.
- Validate that all referenced IDs (project_id, instance_id, etc.) belong to the same workspace_id in multi-ID requests.

---

## 6. PUBLIC SHARE LINK SECURITY

### Token Design
- Token: 32 bytes from CSPRNG, URL-safe base64 encoded = ~43 characters.
- Example: `rANd0mT0keN123AbCdEfGhIjKlMnOpQrStUvWxYz12`
- Token space: 2^256 — brute force effectively impossible.
- Store: SHA-256 hash of token in DB. Token not in plaintext anywhere in DB.

### Access Control
- Share links reveal ONLY what the creator configured (`include_legal_name`, `include_pan_gstin`).
- By default: business identity details are hidden.
- PAN/GSTIN/CIN: NEVER included in share links unless explicitly enabled by user AND user confirms understanding.
- Share link data is always snapshot-based (MVP). Not live. The snapshot was evaluated at share creation time.

### Revocation
- Immediate on DELETE /share-links/:linkId.
- If parent project is deleted → all share links for that project are immediately revoked.
- If workspace is suspended → all share links become inaccessible.

---

## 7. AUDIT LOG REQUIREMENTS (MVP MINIMUM)

The following actions MUST be logged to `audit_log` in MVP:

| Action | Log Content |
|--------|------------|
| `user.signup` | user_id, ip, email (hashed) |
| `user.login` | user_id, ip, success/fail |
| `user.login_failed` | ip, email attempted (hashed), reason |
| `user.password_reset_requested` | user_id (if found), ip |
| `user.password_reset_completed` | user_id, ip |
| `api_key.created` | key_id, workspace_id, label, created_by |
| `api_key.revoked` | key_id, workspace_id, revoked_by |
| `api_key.rotated` | old_key_id, new_key_id, workspace_id |
| `evaluation.triggered` | project_id, workspace_id, source (UI/API), quota_units_used |
| `export.generated` | export_id, project_id, export_type |
| `share_link.created` | link_id, project_id, include_legal_name setting |
| `share_link.revoked` | link_id, project_id, revoked_by |
| `project.created` | project_id, workspace_id, created_by |
| `project.deleted` | project_id, workspace_id, deleted_by |
| `workspace.plan_changed` | workspace_id, old_plan, new_plan |

**Retention:** Audit logs are immutable append-only. Never delete audit log rows. Retain minimum 2 years.

---

## 8. RATE LIMITING

**Layer 1: Per API Key (primary for API clients)**
- 60 requests per minute (burst)
- Daily evaluation quota per workspace (see doc 17)

**Layer 2: Per IP (for public endpoints and unauthenticated access)**
- `/v1/public/demo/*`: 5 calls per IP per day
- `/v1/auth/login`: 20 attempts per IP per hour
- `/v1/auth/signup`: 5 signups per IP per hour
- `/v1/auth/forgot-password`: 5 attempts per IP per hour

**Layer 3: Per User (for authenticated UI sessions)**
- 200 requests per minute (generous — UI navigation is chatty)

**Rate limit response:** HTTP 429 with headers:
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1748947260
Retry-After: 42
```

**Implementation:** Use a token bucket or sliding window counter in Redis.

---

## 9. WHAT IS PUBLIC vs. PRIVATE

| Category | Public | Private (auth required) |
|----------|--------|------------------------|
| Marketing pages | ✓ | — |
| Pricing page | ✓ | — |
| Documentation | ✓ | — |
| API playground (authenticated) | — | ✓ |
| Demo evaluate (limited) | ✓ | — |
| Share link view | ✓ | — |
| Business profile data | — | ✓ (workspace-scoped) |
| Compliance output | — | ✓ (workspace-scoped) |
| API keys (any detail) | — | ✓ (workspace-scoped) |
| Usage data | — | ✓ (workspace-scoped) |
| Audit logs | — | ✓ (workspace-scoped) |
| Library version metadata | ✓ | — |
| Compliance master library (raw) | — | Admin-only |
| PAN/GSTIN of any business | — | Never in share links by default |

---

## 10. SECURITY HEADERS

All HTTP responses must include:
```
Strict-Transport-Security: max-age=31536000; includeSubDomains
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Content-Security-Policy: default-src 'self'; ...
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: geolocation=(), microphone=(), camera=()
```

CORS: Allow only the app's own origin. `Access-Control-Allow-Origin: https://app.ecnailpcom.in` for API. No wildcard CORS on authenticated endpoints.
