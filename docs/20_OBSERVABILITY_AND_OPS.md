# Document 20 — Observability and Internal Operations
## Logging, Metrics, Alerting, and Product Analytics Design

---

## 1. STRUCTURED APPLICATION LOGGING

Every server-side log entry must be structured JSON. No plain text log lines.

**Minimum fields on every log entry:**
```json
{
  "timestamp": "2026-06-03T10:15:00.123Z",
  "level": "INFO",
  "request_id": "req_abc123xyz",
  "service": "api",
  "endpoint": "POST /v1/projects/:id/evaluation",
  "user_id": "uuid",
  "workspace_id": "uuid",
  "api_key_id": "uuid",
  "ip_address": "203.0.113.42",
  "duration_ms": 284,
  "status_code": 200,
  "message": "Evaluation completed successfully",
  "quota_units_used": 1,
  "quota_remaining": 87
}
```

**Log levels:**
- `DEBUG`: Verbose internal state (disabled in production by default)
- `INFO`: Normal operations (requests, evaluations, exports)
- `WARN`: Non-critical issues (near quota limit, deprecated endpoint used)
- `ERROR`: Application errors that need investigation (evaluation engine failure, DB error)
- `CRITICAL`: System-level failures requiring immediate attention

**Never log in application logs:**
- Full API keys (even in `X-API-Key` header)
- Passwords or password hashes
- Session tokens or refresh tokens
- PAN, GSTIN, or sensitive business identity fields

---

## 2. AUDIT LOG (DB-BACKED)

The `audit_log` table (defined in doc 12) is the source of truth for:
- Who did what, when, from where
- All key lifecycle events
- All evaluation and export events

This is separate from application logs. Audit logs must:
- Be append-only (no update/delete permissions on this table even for admins)
- Survive even if application logs are rotated
- Be queryable per workspace for user-facing audit history (Phase 2)

**Minimum retention:** 2 years.

---

## 3. HEALTH AND READINESS ENDPOINTS

```
GET /health          → 200 {"status": "ok", "version": "1.2.0"}
GET /health/ready    → 200 if DB + Redis connections are healthy
GET /health/live     → 200 if process is running (used by container orchestrator)
```

These endpoints must be unauthenticated and excluded from rate limiting.

---

## 4. KEY METRICS TO TRACK

### Product / Business Metrics

| Metric | Why It Matters |
|--------|---------------|
| `signups_per_day` | Growth rate |
| `activation_rate` | % of signups who complete first evaluation (target: > 60%) |
| `evaluations_per_day` | Core engagement metric |
| `daily_active_workspaces` | Real engagement |
| `quota_hit_rate` | % of free users hitting 100/day limit — upgrade signal |
| `api_key_adoption_rate` | % of users who create and use an API key |
| `first_api_call_within_24h` | Developer activation rate |
| `export_rate` | % of users who export after evaluating |
| `share_link_creation_rate` | Virality/referral signal |
| `free_to_paid_conversion` | Revenue metric |
| `projects_per_workspace` | Power user signal |

### Technical / Reliability Metrics

| Metric | Alert Threshold |
|--------|----------------|
| `api_p95_latency_ms` | Alert if > 2000ms |
| `api_error_rate` | Alert if 5xx rate > 1% |
| `evaluation_failure_rate` | Alert if > 0.5% |
| `db_connection_pool_saturation` | Alert if > 80% |
| `redis_memory_usage` | Alert if > 75% |
| `quota_check_latency_ms` | Alert if p99 > 20ms |
| `failed_login_spike` | Alert if > 50/minute per IP |

### Security Metrics

| Metric | Alert Threshold |
|--------|----------------|
| `failed_logins_per_hour` | Alert if > 100 across all IPs |
| `revoked_key_usage_attempts` | Alert on any (indicates compromised key usage) |
| `demo_quota_exhaustions_per_ip` | Alert if > 20 unique IPs/hour at limit (scraping pattern) |
| `cross_workspace_access_attempts` | Alert on any (should never happen if correctly implemented) |

---

## 5. OBSERVABILITY STACK RECOMMENDATION

**For MVP (simple, low-cost):**
- Application logs: stdout → log aggregation (Loki / Papertrail / CloudWatch)
- Metrics: Prometheus-compatible metrics endpoint + Grafana dashboard
- Alerting: PagerDuty or simple email alerts via alertmanager
- Error tracking: Sentry (free tier sufficient for MVP)
- Uptime monitoring: UptimeRobot or Betterstack (free tier)

**Do not invest in complex observability infrastructure before product-market fit.**

---

## 6. INTERNAL OPS CONSIDERATIONS

### Compliance Library Updates

When a new compliance library version is released (via Git push to the compliance library repo):
1. An import script runs: reads new/updated compliance records from Git-tracked files
2. Validates: every record must have at least one source link with a primary source
3. Inserts/updates `compliance_master`, `source_master`, `due_date_rule`, `penalty_record` records
4. Updates `library_meta` with new version number and release date
5. Sets `evaluation_is_stale = true` on ALL `business_profile` records (forcing re-evaluation on next access)

**Important:** Step 5 does NOT automatically re-evaluate all businesses. Re-evaluation happens lazily when a user next accesses their dashboard or explicitly triggers it. This prevents a thundering herd when a library update touches many records.

### Stale Evaluation Detection

When a user accesses their project:
1. Check `business_profile.last_evaluation_library_version`
2. Compare against `library_meta.current_version`
3. If different: show banner "Compliance library updated on [date]. Re-evaluate to get the latest results."
4. Banner has a [Re-evaluate Now] button

### Admin Tooling (Phase 2)

MVP does not require a full admin panel. For MVP, direct DB access by the engineering team is acceptable for:
- Investigating user issues
- Manually updating plan limits
- Reviewing audit logs for abuse

Phase 2 admin panel should have:
- User and workspace management
- Library management UI
- Usage analytics dashboard
- Abuse review queue

---

## 7. ACTIVATION FUNNEL TRACKING

Track these events in the analytics system (one event per occurrence per user):

| Event Name | When Fired |
|-----------|-----------|
| `user.signed_up` | New account created |
| `user.email_verified` | Email verified |
| `user.first_project_created` | First project created |
| `user.questionnaire_50pct` | Profile reaches 50% completeness |
| `user.first_evaluation` | First evaluation completed |
| `user.first_overdue_viewed` | User views an overdue item detail |
| `user.first_completion_marked` | First compliance marked as done |
| `user.api_key_created` | API key created |
| `developer.first_api_call` | API key first used |
| `user.first_export` | First export completed |
| `user.first_share_link` | First share link created |
| `user.quota_50pct` | Used 50 of 100 daily evaluations |
| `user.quota_exceeded` | Hit daily limit for first time |
| `user.plan_upgraded` | Plan upgraded (Phase 2) |

**Where to store:** Analytics events table in DB (simple append log) for MVP. Can migrate to dedicated analytics system (Segment, PostHog, or Mixpanel) in Phase 2.

---

## 8. DATA PRIVACY AND RETENTION

| Data Type | Retention |
|-----------|----------|
| User passwords | Stored as hash; no retention of plaintext ever |
| Business profile answers | As long as workspace is active; purge 90 days after deletion |
| Compliance period instances | As long as project is active; 90 days after project deletion |
| Exports | 30 days after generation |
| Audit logs | 2 years minimum |
| Usage events | 1 year for analytics; raw events purged after 90 days |
| Refresh tokens | 7 days (auto-expire) |
| Share link snapshots | Until link is revoked or project deleted |

**GDPR/IT Act consideration:** Business owners' data is sensitive. The privacy policy must clearly state what is collected, how long it's retained, and how to request deletion. Implement a data deletion API (POST /v1/users/me/delete-data) in Phase 1 or Phase 2.
