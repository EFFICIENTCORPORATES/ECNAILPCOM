# Document 17 — Usage Metering and Plan Limits
## Quota System, Billing Model, and Soft Paywall Design

---

## 1. THE FUNDAMENTAL QUESTION: WHAT IS A "REQUEST"?

This is the most important design decision in usage metering. The wrong definition either:
- Punishes users for normal exploration (chilling effect)
- Gets abused for free unlimited computation (revenue leakage)

**Decision: Only "evaluation operations" count toward quota.**

### COUNTED toward quota (1 unit each):
| Operation | Why counted |
|-----------|------------|
| POST /v1/projects/:id/evaluation | Primary computationally expensive operation |
| POST /v1/projects/:id/exports (any type) | Export generation triggers a fresh format render |
| POST /v1/public/demo/evaluate | Public demo call |

### NOT COUNTED toward quota:
| Operation | Why not counted |
|-----------|----------------|
| GET /v1/projects/:id/compliance | Read from already-evaluated data |
| GET /v1/projects/:id/due-dates | Read |
| GET /v1/projects/:id/heat-map | Read |
| PATCH /questionnaire/answers | Saves data, doesn't trigger computation |
| GET /v1/usage, /v1/meta, /v1/workspaces | Metadata |
| All auth endpoints | Auth operations |
| Navigation/dashboard page loads | Pure reads |
| GET /v1/projects/:id/exports/:id | Retrieval, not generation |
| Share link access (GET /share/:token) | Read-only |

**Rationale:** This model is user-friendly (explore freely), measurable (one clear operation type), and resistant to abuse (evaluation is the expensive operation). Exports are included because they trigger computation even if the output is cached — and they represent actionable value consumption.

---

## 2. FREE PLAN LIMITS (PROPOSED)

| Limit | Value | Notes |
|-------|-------|-------|
| Evaluations + Exports per day | 100 | Combined, resets UTC midnight |
| Active projects | 3 | Archived projects don't count |
| Active API keys | 3 | |
| Active share links | 10 | Per workspace |
| Public demo calls | 5/day per IP | Separate IP-level limit, not workspace |

**Why 100/day is generous for free plan:**
- A business owner with 3 businesses who re-evaluates once daily = 3 units/day
- A CA with 10 clients re-evaluating weekly = 10 units/day (well under 100)
- A developer testing the API with automated scripts = could easily hit 100, which is the intended upgrade signal

---

## 3. QUOTA STORAGE MODEL

### Efficient Counter Design

Do NOT query `COUNT(*) FROM usage_events WHERE workspace_id=X AND quota_date=TODAY` on every API request. That's too slow.

**Use a Redis counter as primary + DB for persistence:**

```
Redis key: quota:{workspace_id}:{YYYY-MM-DD}
Type: Integer counter
TTL: 25 hours (survives past midnight for late-arriving events)
Operations:
  - INCR on each countable event
  - GET before each countable event to check limit
  - SET {limit} (with NX) on first access of the day to initialize
```

**DB as persistence backup:** `usage_events` table records each event. Can be used to recompute Redis state if cache is lost or for monthly analytics queries.

### Quota Check Flow (per API request)

```python
def check_quota(workspace_id: str) -> QuotaResult:
    today = datetime.utcnow().date().isoformat()
    redis_key = f"quota:{workspace_id}:{today}"
    
    # Get current count (0 if key doesn't exist)
    current = redis.get(redis_key) or 0
    limit = workspace.daily_quota_limit  # 100 for free plan
    
    if current >= limit:
        reset_at = next_utc_midnight()
        raise QuotaExceededError(
            used=current,
            limit=limit,
            reset_at=reset_at
        )
    
    return QuotaResult(used=current, limit=limit, remaining=limit-current)

def consume_quota(workspace_id: str) -> None:
    today = datetime.utcnow().date().isoformat()
    redis_key = f"quota:{workspace_id}:{today}"
    redis.incr(redis_key)
    redis.expire(redis_key, 90000)  # 25 hours TTL
    # Also write to usage_events for persistence
    write_usage_event(workspace_id, ...)
```

---

## 4. QUOTA RESET MODEL

**Reset at UTC midnight (00:00:00 UTC).**

**Why UTC:**
- Simple, single point of truth
- Avoids timezone gaming (users can't shift to a different timezone to get an extra reset)
- Standard practice for SaaS rate limiting

**User expectation management:**
- The UI shows: "Resets at midnight UTC (5:30 AM IST)"
- The API response shows: `"resets_at": "2026-06-04T00:00:00Z"`
- Convert to IST in the UI (IST = UTC + 5:30)

---

## 5. OVER-LIMIT BEHAVIOR

**Soft block — not hard block:**

When quota is exceeded:
1. API returns HTTP 429 with `QUOTA_EXCEEDED` error code
2. Response body includes: `quota_reset_at`, `upgrade_url`, and a human-readable message
3. Read-only operations (GET requests) continue to work — user can still view their existing data
4. Only NEW evaluations and exports are blocked

**UI behavior:**
- Usage bar turns red when at 100%
- New evaluation button shows: "Daily limit reached. Resets at 5:30 AM IST. [Upgrade for unlimited →]"
- Soft messaging — no aggressive popups

**Free plan over-limit API response:**
```json
{
  "error": {
    "code": "QUOTA_EXCEEDED",
    "message": "Your daily evaluation limit (100) has been reached. Existing results are still accessible. Your quota resets at midnight UTC (5:30 AM IST).",
    "quota_used": 100,
    "quota_limit": 100,
    "quota_reset_at": "2026-06-04T00:00:00Z",
    "upgrade_url": "https://app.ecnailpcom.in/pricing"
  }
}
```

---

## 6. NEAR-LIMIT WARNINGS

| Threshold | UI Indicator | API Header |
|-----------|-------------|------------|
| < 50% used | None | `X-RateLimit-Remaining: 75` |
| 50–79% used | Subtle counter in nav | Same headers |
| 80–94% used | Amber counter + "Running low" | Same headers |
| 95–99% used | Red counter + "Almost at limit" | Same headers |
| 100% used | Red counter + upgrade CTA | 429 on next evaluation |

API headers are always present on every response regardless of threshold.

---

## 7. DEMO ENDPOINT SEPARATE QUOTA

The public demo endpoint (`POST /v1/public/demo/evaluate`) has its OWN quota:
- 5 calls per IP per day
- NOT tied to any workspace quota
- Uses Redis: `quota:demo:{ip}:{YYYY-MM-DD}` with same TTL

Authenticated users who access the demo page: their demo calls use the demo IP quota, NOT their workspace quota. Demo is always "free to try."

---

## 8. PLAN STRUCTURE (PROPOSED)

These are preliminary. Exact pricing is a business decision, not a tech decision. The system must support the plan infrastructure.

| Feature | FREE | STARTER | PRO |
|---------|------|---------|-----|
| Evaluations + Exports/day | 100 | 500 | Unlimited |
| Active Projects | 3 | 15 | Unlimited |
| API Keys | 3 | 10 | Unlimited |
| Share Links | 10 | 50 | Unlimited |
| Export Formats | JSON, CSV, Print | All | All |
| Source Attribution in Exports | ✓ | ✓ | ✓ |
| Multi-workspace member support | — | — | Phase 2 |
| Email reminders | — | ✓ | ✓ |
| Priority support | — | — | ✓ |

**Billing integration:** Placeholder only in MVP. System stores `plan_id` and `daily_quota_limit` in the `workspaces` table. Upgrading a plan = updating these fields. Actual payment processing (Razorpay/Stripe integration) is Phase 2.

---

## 9. PLAN ENFORCEMENT LOGIC

Plan limits are enforced at the application layer, not just Redis:

```python
def can_create_project(workspace) -> bool:
    active_count = count_active_projects(workspace.workspace_id)
    return active_count < workspace.max_projects

def can_create_api_key(workspace) -> bool:
    active_count = count_active_api_keys(workspace.workspace_id)
    return active_count < workspace.max_api_keys
```

When limit is hit:
```json
{
  "error": {
    "code": "PLAN_LIMIT_REACHED",
    "message": "Your free plan allows up to 3 active projects. Archive an existing project or upgrade.",
    "limit": 3,
    "current": 3,
    "upgrade_url": "/pricing"
  }
}
```

---

## 10. ABUSE PREVENTION (FREE PLAN SPECIFIC)

**Scenario 1: Multi-account abuse (creating many free accounts to get unlimited quota)**

Mitigation:
- Email verification required (prevent throwaway email spam with disposable email blocklist)
- One free workspace per email domain for business email domains (detect pattern)
- Monitor: multiple accounts from same IP on same day → flag for review

**Scenario 2: API script hammering evaluations**

Mitigation:
- Hard rate limit: max 10 evaluation calls per minute per workspace (even on paid plans)
- Hard rate limit: max 2 concurrent evaluations per workspace
- Daily quota is the binding limit for free plan

**Scenario 3: Demo endpoint scraping**

Mitigation:
- IP rate limit (5/day)
- Response truncated (max 10 items, no sources)
- hCaptcha on the web form
- Demo results not stored (no DB write, pure compute-and-return)
