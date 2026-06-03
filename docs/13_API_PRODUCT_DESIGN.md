# Document 13 — API Product Design
## Complete REST API Endpoint Reference and Design Contract

**AUDIENCE:** This document is the primary spec for backend API implementors and frontend teams.
Any AI writing API code must implement these contracts exactly as defined here.

---

## 1. API FUNDAMENTALS

### Base URL
```
Production:   https://api.ecnailpcom.in/v1
Staging:      https://api-staging.ecnailpcom.in/v1
```

### Protocol
- HTTPS only. No HTTP redirects for API calls — reject with 400.
- JSON request/response bodies with `Content-Type: application/json`.
- UTF-8 encoding throughout.

### Versioning Strategy
- **URL-based versioning:** `/v1/`, `/v2/` etc.
- `v1` is the initial version and must be stable once launched.
- Breaking changes require a new version number.
- **Breaking change definition:** Any change that removes a field, changes a field's type, renames a field, or removes an endpoint.
- **Non-breaking changes** (can be done without version bump): Adding new optional fields to responses, adding new optional query parameters, adding new endpoints.
- At least 6 months deprecation notice before removing a version in production.
- Responses include `X-API-Version: 1` header on all responses.

### Request ID
Every request receives a unique `X-Request-ID` header in the response (UUID v4). Include this in all logs. If the client provides `X-Request-ID` in the request, echo it back. This enables support ticket debugging.

---

## 2. AUTHENTICATION MODEL

Two authentication mechanisms. Both produce the same access context (workspace_id + user/key identity):

### Mechanism A: JWT Bearer Token (for UI / session-based clients)
```
Authorization: Bearer <jwt_access_token>
```
- Access token: 15-minute lifetime, RS256 signed
- Refresh token: 7-day lifetime, stored in httpOnly cookie
- Claims: `{sub: user_id, workspace_id, role, exp, iat, jti}`
- When access token expires, client uses refresh token to get new pair
- Full details in [doc 14](14_AUTHENTICATION_AND_SECURITY.md)

### Mechanism B: API Key Header (for programmatic/developer access)
```
X-API-Key: pk_live_a3f8c2d1e4b7a9f0c1d2e3f4a5b6c7d8
```
- Long-lived until revoked
- Derives workspace context from key record
- Rate limited per key (see doc 17)
- Full details in [doc 14](14_AUTHENTICATION_AND_SECURITY.md)

**Endpoints that support both mechanisms:** All `/v1/*` endpoints except `/v1/auth/*`.
**Endpoints that require JWT only:** `/v1/auth/*` flows, workspace member management (Phase 2).
**Endpoints that require API key only:** None — API keys can do anything a logged-in OWNER/ADMIN can do (minus purely account-management actions like password change).

---

## 3. ERROR RESPONSE FORMAT

All errors return a consistent JSON envelope:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "The request contains invalid fields.",
    "request_id": "req_abc123",
    "details": [
      {
        "field": "questionnaire.entity_type",
        "issue": "must be one of: PROPRIETORSHIP, PARTNERSHIP, LLP, PRIVATE_LIMITED, PUBLIC_LIMITED, OPC"
      }
    ]
  }
}
```

### Error Code Taxonomy

| HTTP Status | Code | When Used |
|------------|------|----------|
| 400 | `VALIDATION_ERROR` | Request body fails schema validation |
| 400 | `INVALID_PARAMETER` | Query param or path param invalid |
| 401 | `UNAUTHORIZED` | No auth token/key provided |
| 401 | `INVALID_TOKEN` | Token is malformed or expired |
| 401 | `INVALID_API_KEY` | API key not found or revoked |
| 403 | `FORBIDDEN` | Auth valid but insufficient permission |
| 403 | `WORKSPACE_SUSPENDED` | Workspace is suspended |
| 404 | `NOT_FOUND` | Resource does not exist (or belongs to another workspace) |
| 409 | `CONFLICT` | Create request conflicts with existing resource (e.g., duplicate slug) |
| 422 | `EVALUATION_FAILED` | Evaluation triggered but engine returned error |
| 422 | `INSUFFICIENT_PROFILE_DATA` | Profile too incomplete to evaluate |
| 429 | `QUOTA_EXCEEDED` | Daily evaluation quota reached |
| 429 | `RATE_LIMITED` | Too many requests in short window |
| 500 | `INTERNAL_ERROR` | Unexpected server error |
| 503 | `SERVICE_UNAVAILABLE` | Planned maintenance or temporary outage |

**Note for implementors:** Never return 404 for auth reasons (don't confirm resource existence to unauthorized callers). Return 403 FORBIDDEN instead, except for public endpoints.

### Rate Limit Headers (on all responses)
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 73
X-RateLimit-Reset: 1748947200    (UTC epoch for next reset)
X-RateLimit-Window: daily
```

---

## 4. PAGINATION

List endpoints use **cursor-based pagination** (not page numbers):

```json
{
  "data": [...],
  "pagination": {
    "has_more": true,
    "next_cursor": "eyJpZCI6InV1aWQiLCJjcmVhdGVkX2F0IjoiMjAyNi0wNi0wMyJ9",
    "count": 20,
    "total_count": 47
  }
}
```

Default page size: 20. Max: 100.
Pass `?cursor=<next_cursor>&limit=20` for subsequent pages.

---

## 5. ENDPOINT FAMILIES

---

### FAMILY A: Authentication `/v1/auth`

These endpoints do not require authentication. They establish identity.

#### POST /v1/auth/signup
Create a new user account. Automatically creates a workspace.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "minimum 8 chars",
  "full_name": "Rajan Mehta",
  "self_identified_role": "BUSINESS_OWNER",
  "timezone": "Asia/Kolkata"
}
```

**Response 201:**
```json
{
  "user": { "user_id": "uuid", "email": "user@example.com", "email_verified": false },
  "workspace": { "workspace_id": "uuid", "name": "Rajan Mehta's Workspace" },
  "tokens": { "access_token": "jwt...", "expires_in": 900 },
  "onboarding_path": "BUSINESS_USER"   // or "DEVELOPER"
}
```

**Side effects:** Send email verification email. Create workspace. Create onboarding_progress record. Log `user.signup` audit event.

#### POST /v1/auth/login
```json
{ "email": "user@example.com", "password": "..." }
```
Response: same as signup tokens. Sets httpOnly refresh cookie.

#### POST /v1/auth/refresh
Uses httpOnly refresh cookie. No body. Returns new access token.

#### POST /v1/auth/logout
Invalidates refresh token. Clears cookie.

#### POST /v1/auth/forgot-password
```json
{ "email": "user@example.com" }
```
Always returns 200 (don't confirm email existence to prevent enumeration).

#### POST /v1/auth/reset-password
```json
{ "token": "reset_token_from_email", "new_password": "..." }
```

#### POST /v1/auth/verify-email
```json
{ "token": "verify_token_from_email" }
```

#### GET /v1/auth/me
Returns current user + workspace context.

---

### FAMILY B: Workspaces `/v1/workspaces`

#### GET /v1/workspaces
List workspaces the current user belongs to.

#### GET /v1/workspaces/:workspaceId
Get workspace details.

#### PATCH /v1/workspaces/:workspaceId
Update workspace name/settings. OWNER/ADMIN only.

#### GET /v1/workspaces/:workspaceId/usage
Get usage summary for this workspace (today's quota, monthly summary).

---

### FAMILY C: Projects `/v1/projects`

All project endpoints are scoped to the authenticated user's active workspace.

#### POST /v1/projects
Create a new project.

**Request:**
```json
{
  "project_name": "Acme Technologies Pvt Ltd",
  "entity_type": "PRIVATE_LIMITED",
  "legal_name": "Acme Technologies Private Limited"
}
```

**Response 201:**
```json
{
  "project_id": "uuid",
  "project_name": "Acme Technologies Pvt Ltd",
  "project_status": "ACTIVE",
  "questionnaire_completeness_pct": 5,
  "evaluation_is_stale": true,
  "created_at": "2026-06-03T10:00:00Z"
}
```

**Idempotency:** Support `Idempotency-Key` header for this endpoint. If a request with the same idempotency key was processed within 24 hours, return the original response.

#### GET /v1/projects
List projects in active workspace.

**Query params:**
- `status=ACTIVE|ARCHIVED` (default: ACTIVE)
- `limit=20&cursor=...`
- `search=acme` (searches project_name and legal_name)

#### GET /v1/projects/:projectId
Get full project details including questionnaire completeness and evaluation status.

#### PATCH /v1/projects/:projectId
Update project metadata (name, notes). Does NOT trigger re-evaluation.

#### DELETE /v1/projects/:projectId
Soft delete. OWNER/ADMIN only.

#### POST /v1/projects/:projectId/clone
Clone project (copy profile, reset evaluation state). Returns new project_id.

---

### FAMILY D: Questionnaire `/v1/projects/:id/questionnaire`

#### GET /v1/projects/:projectId/questionnaire/schema
Returns the full questionnaire schema with current project's answers merged in.

**Response:**
```json
{
  "schema_version": "1.0",
  "domains": [
    {
      "domain_id": "A",
      "domain_title": "Business Identity",
      "questions": [
        {
          "question_id": "A1",
          "question_text": "What type of legal entity is your business?",
          "field_name": "entity_type",
          "type": "SINGLE_SELECT",
          "required": true,
          "options": [
            {"value": "PROPRIETORSHIP", "label": "Sole Proprietorship"},
            {"value": "LLP", "label": "Limited Liability Partnership (LLP)"},
            ...
          ],
          "current_answer": "PRIVATE_LIMITED",
          "visible": true,
          "depends_on": null
        }
      ]
    }
  ],
  "completeness_pct": 65,
  "missing_required": ["B3", "D1"]
}
```

**Note:** The `depends_on` field enables frontend adaptive questionnaire logic. If `entity_type != COMPANY`, question E4 about paid-up capital should be hidden.

#### PUT /v1/projects/:projectId/questionnaire/answers
Replace ALL answers (full questionnaire submission).

**Request:**
```json
{
  "entity_type": "PRIVATE_LIMITED",
  "incorporation_date": "2022-04-15",
  "principal_state": "MH",
  "activity_type": "SERVICE",
  "annual_turnover_estimated": 15000000,
  "gst_registered": true,
  "gst_scheme": "REGULAR",
  "gst_filing_frequency": "MONTHLY",
  ...
}
```

**Response 200:** Updated project summary with new completeness %.
**Side effect:** Sets `evaluation_is_stale = true` but does NOT auto-trigger evaluation.

#### PATCH /v1/projects/:projectId/questionnaire/answers
Partial update — only send changed fields.

#### POST /v1/projects/:projectId/questionnaire/validate
Validate answers without saving. Returns validation errors and computed warnings.

---

### FAMILY E: Compliance Evaluation `/v1/projects/:id/evaluation`

**This is the primary billable action. Each call costs 1 quota unit.**

#### POST /v1/projects/:projectId/evaluation
Trigger compliance evaluation. Synchronous in MVP.

**Request:** `{}` (empty body — uses the project's current questionnaire answers)

**Response 200:**
```json
{
  "evaluation_id": "uuid",
  "project_id": "uuid",
  "evaluated_at": "2026-06-03T10:15:00Z",
  "financial_year_label": "FY2025-26",
  "assessment_year_label": "AY2026-27",
  "current_date": "2026-06-03",
  "library_version": "v1.2.0",
  "library_last_updated": "2026-05-28",
  
  "entity_classification": {
    "entity_type": "PRIVATE_LIMITED",
    "activity_type": "SERVICE",
    "turnover_band": "5CR_10CR",
    "gst_scheme": "REGULAR",
    "gst_filing_frequency": "MONTHLY",
    "employee_count_band": "10_19",
    "principal_state": "MH",
    "state_name": "Maharashtra"
  },
  
  "summary": {
    "total_evaluated": 68,
    "applicable": 45,
    "likely_applicable": 5,
    "check_threshold": 4,
    "event_triggered": 6,
    "state_specific": 3,
    "not_applicable": 5,
    "insufficient_data": 0,
    "human_review_required": 2,
    
    "overdue": 3,
    "due_within_7_days": 2,
    "due_within_30_days": 8,
    
    "critical_count": 1,
    "severe_count": 2,
    "high_count": 8,
    "moderate_count": 12,
    "low_count": 22
  },
  
  "warnings": [
    {
      "warning_type": "THRESHOLD_NEAR",
      "message": "Your turnover band (₹5Cr–₹10Cr) means e-invoicing applies. Confirm if IRP registration is complete.",
      "compliance_code": "GST_EINVOICING_INDICATOR"
    }
  ],
  
  "disclaimer": "This compliance assessment is for informational purposes only...",
  
  "quota": {
    "used_today": 12,
    "limit_today": 100,
    "remaining_today": 88,
    "resets_at": "2026-06-04T00:00:00Z"
  }
}
```

**Note:** The full list of compliance_period_instances is NOT in this response envelope. Use the `/compliance` family endpoints to retrieve the detailed list. This keeps the evaluation response lightweight.

**Async migration path:** When/if async is needed, add `evaluation_status: "PENDING"|"COMPLETE"|"FAILED"` and `job_id` fields. Clients polling for async jobs use `GET /v1/projects/:id/evaluation/latest`. This is backward-compatible.

#### GET /v1/projects/:projectId/evaluation/latest
Get the most recent evaluation result (without triggering a new one).

#### GET /v1/projects/:projectId/evaluation/summary
Compact summary widget data (counts only, no line items). Does not count toward quota.

---

### FAMILY F: Compliance Items `/v1/projects/:id/compliance`

These are READ-ONLY endpoints. They do not cost quota units.

#### GET /v1/projects/:projectId/compliance
List all compliance period instances for the project.

**Query params:**
- `status=OVERDUE|DUE_SOON|UPCOMING|COMPLETED` (multi-select: `?status=OVERDUE&status=DUE_SOON`)
- `domain=GST|INCOME_TAX|TDS|MCA_COMPANY|EPF|ESI|...`
- `frequency=MONTHLY|QUARTERLY|ANNUAL|EVENT_BASED`
- `severity=CRITICAL|SEVERE|HIGH|MODERATE|LOW`
- `applicability=APPLICABLE|LIKELY_APPLICABLE|...`
- `period_label=May+2026`
- `search=GSTR` (searches compliance title and code)
- `sort=due_date|severity|domain` (default: due_date ASC)
- `limit=20&cursor=...`

**Response item shape:**
```json
{
  "instance_id": "uuid",
  "compliance_id": "uuid",
  "compliance_code": "GST_GSTR3B_MONTHLY_REGULAR",
  "title": "GSTR-3B Monthly Return Filing",
  "short_title": "GSTR-3B",
  "domain": "GST",
  "frequency_type": "MONTHLY",
  
  "applicability_status": "APPLICABLE",
  "applicability_confidence": "HIGH",
  "why_it_applies": "GST registered, regular scheme, monthly filing frequency",
  
  "period_label": "May 2026",
  "period_start": "2026-05-01",
  "period_end": "2026-05-31",
  "effective_due_date": "2026-06-20",
  "override_active": false,
  
  "is_overdue": true,
  "overdue_days": 3,
  "due_in_days": null,
  "financial_year_label": "FY2025-26",
  
  "combined_severity_score": 65,
  "severity_band": "SEVERE",
  "color_code": "#D32F2F",
  
  "tracking_status": "PENDING",
  "completed_on": null,
  "completed_by": null,
  "completion_notes": null,
  
  "source_summary": {
    "primary_act": "CGST Act, 2017",
    "primary_section": "Section 39",
    "source_authority": "CBIC",
    "last_verified": "2026-05-15",
    "confidence": "HIGH"
  }
}
```

#### GET /v1/projects/:projectId/compliance/:instanceId
Single compliance instance with full detail including full source tree and why_it_applies reasoning.

#### PATCH /v1/projects/:projectId/compliance/:instanceId/status
Update tracking status (mark as done, add notes).

**Request:**
```json
{
  "tracking_status": "COMPLETED",
  "completed_on": "2026-06-18",
  "completion_notes": "Filed GSTR-3B on June 18. ARN: AA12345678"
}
```

**Validation rules:**
- `completed_on` must not be in the future
- `tracking_status` can only be set to `COMPLETED` or `SKIPPED` via API (not `PENDING` or `NOT_APPLICABLE_THIS_PERIOD`)
- Once marked `COMPLETED`, can be reverted to `PENDING` only by OWNER/ADMIN

---

### FAMILY G: Due Date Schedule `/v1/projects/:id/due-dates`

These are read-only, no quota cost.

#### GET /v1/projects/:projectId/due-dates
Returns the full due-date schedule for the current FY.

**Query params:**
- `year=FY2025-26` (default: current FY)
- `from_date=2026-06-01&to_date=2026-06-30` (date range filter)
- `frequency=MONTHLY|QUARTERLY|...`
- `domain=GST|TDS|...`
- `status=OVERDUE|DUE_SOON|UPCOMING|COMPLETED`

**Response:** Grouped by month or flat list (controlled by `?group_by=month`).

#### GET /v1/projects/:projectId/due-dates/upcoming
Next N upcoming due dates (default: 10).
**Query params:** `?limit=10&days_ahead=30`

#### GET /v1/projects/:projectId/due-dates/overdue
All currently overdue items, sorted by severity DESC.

---

### FAMILY H: Heat Map `/v1/projects/:id/heat-map`

No quota cost.

#### GET /v1/projects/:projectId/heat-map
Returns the data needed to render the heat map grid.

**Response:**
```json
{
  "grid": {
    "domains": ["GST", "INCOME_TAX", "TDS", "MCA_COMPANY", "EPF", "ESI"],
    "urgency_tiers": ["CRITICAL_OVERDUE", "SEVERELY_OVERDUE", "HIGH_OVERDUE", "DUE_VERY_SOON", "DUE_SOON", "UPCOMING"],
    "cells": [
      {
        "domain": "GST",
        "urgency_tier": "HIGH_OVERDUE",
        "count": 2,
        "max_severity_band": "HIGH",
        "color_code": "#E64A19",
        "compliance_instance_ids": ["uuid1", "uuid2"]
      }
    ]
  },
  "top_critical_items": [
    // Top 5 most critical items for quick display
  ]
}
```

---

### FAMILY I: Exports `/v1/projects/:id/exports`

**POST to create an export costs 1 quota unit.**

#### POST /v1/projects/:projectId/exports
Create an export.

**Request:**
```json
{
  "export_type": "JSON",
  "options": {
    "include_sources": true,
    "include_not_applicable": false,
    "period_filter": "FY2025-26"
  }
}
```

**Response 202:** (async generation)
```json
{
  "export_id": "uuid",
  "status": "GENERATING",
  "estimated_ready_in_seconds": 5
}
```

**Response after polling GET:**
```json
{
  "export_id": "uuid",
  "status": "READY",
  "export_type": "JSON",
  "download_url": "https://...",
  "download_expires_at": "2026-06-04T10:15:00Z",
  "file_size_bytes": 42500,
  "generated_at": "2026-06-03T10:15:02Z",
  "library_version": "v1.2.0"
}
```

#### GET /v1/projects/:projectId/exports
List export history for this project.

#### GET /v1/projects/:projectId/exports/:exportId
Get export status and download URL.

---

### FAMILY J: Share Links `/v1/projects/:id/share-links`

#### POST /v1/projects/:projectId/share-links
Create a shareable link.

**Request:**
```json
{
  "label": "Q1 FY2025-26 Report for CA",
  "include_legal_name": false,
  "expires_in_days": 30
}
```

**Response:**
```json
{
  "link_id": "uuid",
  "share_url": "https://app.ecnailpcom.in/share/rANd0mT0keN123",
  "token_preview": "rANd0mT...",
  "expires_at": "2026-07-03T00:00:00Z",
  "created_at": "2026-06-03T10:15:00Z"
}
```

**The full token is shown ONCE in the response.** Store share_url immediately.

#### GET /v1/projects/:projectId/share-links
List active share links.

#### DELETE /v1/projects/:projectId/share-links/:linkId
Revoke a share link immediately.

---

### FAMILY K: API Key Management `/v1/api-keys`

#### POST /v1/api-keys
Create a new API key for the active workspace.

**Request:**
```json
{ "label": "Production Server" }
```

**Response 201:** Full key shown ONCE.
```json
{
  "key_id": "uuid",
  "label": "Production Server",
  "api_key": "pk_live_a3f8c2d1e4b7a9f0c1d2e3f4a5b6c7d8",
  "key_preview": "pk_live_a3f8...c7d8",
  "created_at": "2026-06-03T10:15:00Z",
  "warning": "Store this key securely. It will not be shown again."
}
```

#### GET /v1/api-keys
List API keys (show key_preview only, never full key).

#### DELETE /v1/api-keys/:keyId
Revoke key immediately.

#### POST /v1/api-keys/:keyId/rotate
Revoke old key and create new one atomically. Returns new key ONCE.

#### GET /v1/api-keys/:keyId/usage
Usage statistics for this key.

---

### FAMILY L: Usage `/v1/usage`

No quota cost.

#### GET /v1/usage/today
Today's quota usage for the workspace.

**Response:**
```json
{
  "date": "2026-06-03",
  "quota_limit": 100,
  "quota_used": 12,
  "quota_remaining": 88,
  "resets_at": "2026-06-04T00:00:00Z",
  "breakdown": {
    "evaluations": 10,
    "exports": 2
  },
  "plan": "FREE",
  "upgrade_url": "/pricing"
}
```

#### GET /v1/usage/history
Usage history by day.

---

### FAMILY M: Public Endpoints `/v1/public`

No authentication required. IP-based rate limiting enforced.

#### POST /v1/public/demo/evaluate
Anonymous demo evaluation. Rate-limited per IP.

**Request:** Limited profile (5–6 fields only):
```json
{
  "entity_type": "PRIVATE_LIMITED",
  "principal_state": "MH",
  "gst_registered": true,
  "gst_scheme": "REGULAR",
  "annual_turnover_band": "1CR_5CR",
  "employee_count_band": "10_19"
}
```

**Response:** Truncated result (max 10 compliance items, no detailed sources, no tracking).

**Rate limit:** 5 demo calls per IP per day. Response includes demo disclaimer.

#### GET /v1/public/share/:shareToken
Access a shared report.

**Response:** Full compliance snapshot for that share link (respects `include_legal_name` and `include_pan_gstin` flags).

---

### FAMILY N: Metadata `/v1/meta`

No authentication required. No quota cost.

#### GET /v1/meta/financial-year
```json
{
  "current_date": "2026-06-03",
  "current_fy": "FY2025-26",
  "current_ay": "AY2026-27",
  "fy_start": "2025-04-01",
  "fy_end": "2026-03-31",
  "current_fy_quarter": 1,
  "quarter_label": "Q1 FY2026-27"
}
```

#### GET /v1/meta/compliance-domains
List of all compliance domains in the library.

#### GET /v1/meta/library-version
```json
{
  "current_version": "v1.2.0",
  "released_at": "2026-05-28T00:00:00Z",
  "num_compliance_records": 94,
  "num_sources": 187
}
```

---

## 6. IDEMPOTENCY DESIGN

Endpoints that create resources support the `Idempotency-Key` header:
- POST /v1/projects
- POST /v1/projects/:id/evaluation
- POST /v1/api-keys

If a request with the same `Idempotency-Key` was processed within 24 hours:
- Return the original response with HTTP 200 (not 201)
- Add `X-Idempotent-Replayed: true` header

Store idempotency keys in a cache (Redis) with 24-hour TTL.

---

## 7. REQUEST VALIDATION STYLE

Use strict schema validation on all request bodies:
- Unknown fields → 400 VALIDATION_ERROR (fail fast, don't silently ignore)
- Missing required fields → 400 with `details` listing each missing field
- Enum violation → 400 with the valid values listed
- Date format violation → 400 with expected format

Validation should happen before any DB write, not after partial writes.
