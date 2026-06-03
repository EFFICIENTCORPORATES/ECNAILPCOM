# Document 21 — MVP vs. v1 Hardening vs. Later Phase
## What Gets Built When

**PHILOSOPHY:** MVP is not the smallest thing imaginable. It is the smallest complete product that delivers real, reliable value to a real user. A compliance product with unreliable due dates or missing source attribution is not a minimum viable product — it's a liability.

---

## MVP — DAY 1 LAUNCH REQUIREMENTS

Everything in this section must be complete and tested before the product launches publicly.

### Auth & Identity
- [x] Email/password signup with argon2id hashing
- [x] Email verification (with 24-hour grace period before gating)
- [x] Login, logout, forgot-password, reset-password
- [x] JWT access token + httpOnly refresh cookie
- [x] hCaptcha on signup and login
- [x] Auto-workspace creation on signup
- [x] Progressive login lockout (after 10 failures)

### Workspace & Tenancy
- [x] Single workspace per user (auto-created)
- [x] workspace_members table with OWNER role (infrastructure for Phase 2 roles)
- [x] Row-level security on all tenant tables
- [x] Workspace-scoped queries everywhere

### API Keys
- [x] Create API key (shown once, stored as hash)
- [x] List keys (preview only)
- [x] Revoke key
- [x] Rotate key
- [x] API key authentication (X-API-Key header)
- [x] Rate limit headers on all responses

### Projects / Business Profiles
- [x] Create project (minimum: name + entity_type)
- [x] List, view, update projects
- [x] Soft delete / archive
- [x] Clone project
- [x] Multi-project support (up to 3 on free plan)

### Questionnaire
- [x] GET questionnaire schema with current answers merged
- [x] PUT (replace all answers) and PATCH (partial update)
- [x] Adaptive questionnaire (depends_on logic in schema)
- [x] Completeness percentage computation
- [x] Validate-without-saving endpoint

### Compliance Evaluation Engine (wraps Part A)
- [x] POST evaluation (synchronous, returns summary)
- [x] GET latest evaluation
- [x] Stale detection (library version comparison)
- [x] compliance_period_instance rows generated for all applicable periods of current FY
- [x] Applicability rule evaluation
- [x] Due date computation (all rule types from doc 05)
- [x] Severity scoring (base + dynamic)
- [x] Part A compliance library populated for all MVP domains (doc 09 list)

### Compliance Tracking (Q-A3)
- [x] PATCH compliance status (mark done, add date, add notes, completed_by)
- [x] Tracking status included in all compliance responses

### Dashboard & Views
- [x] Dashboard home (summary cards, upcoming items widget, usage counter)
- [x] Projects list page
- [x] Project overview page
- [x] Compliance list with filters: Status + Domain + Severity + Search
- [x] Due date timeline (list view, month-grouped)
- [x] Heat map grid view
- [x] Compliance detail page with full source attribution
- [x] Onboarding checklist (DB-backed, 9 steps)

### Exports
- [x] JSON export (full compliance output with sources)
- [x] CSV export (compliance schedule)
- [x] Print report (HTML print-optimized view)
- [x] All exports: snapshot-based with metadata header + disclaimer

### Share Links
- [x] Create share link (token generated once, stored as hash)
- [x] List share links
- [x] Revoke share link
- [x] Public share link view page (no login required)
- [x] Configuration: include/exclude legal name

### API Product
- [x] All endpoint families from doc 13 implemented
- [x] Consistent error response format
- [x] Rate limit headers on all responses
- [x] Request validation (strict, with field-level error details)
- [x] Pagination on list endpoints
- [x] Idempotency-Key support on create endpoints
- [x] OpenAPI 3.1 spec generated from implementation

### Usage Metering
- [x] Redis-based quota counter
- [x] usage_events DB persistence
- [x] 100 evaluations+exports/day on free plan
- [x] Quota check before every evaluation/export
- [x] Near-limit UI warnings (50%, 80%, 95%, 100%)
- [x] Friendly over-limit response (not hard block, read operations still work)
- [x] UTC midnight reset

### Public Surface
- [x] Homepage (value prop, how it works, compliance domains, pricing link, developer CTA)
- [x] Pricing page (plan comparison, FAQ)
- [x] Demo page (6-field form, 10-item response, IP rate limited)
- [x] Login, Signup pages
- [x] Privacy Policy (text from lawyer required)
- [x] Terms of Service (text from lawyer required)

### Documentation
- [x] Overview
- [x] Authentication
- [x] Rate Limits
- [x] API Reference (all MVP endpoints)
- [x] Quickstart (5-minute working guide)
- [x] Error codes
- [x] OpenAPI spec publicly served

### Security
- [x] argon2id passwords
- [x] API keys stored as SHA-256 hash only
- [x] Tenant isolation (workspace_id check on every query)
- [x] RLS on all tenant tables
- [x] Security headers (HSTS, CSP, X-Content-Type-Options, etc.)
- [x] audit_log for all sensitive actions
- [x] Bot protection (hCaptcha) on auth and demo endpoints

### Observability
- [x] Structured JSON application logs
- [x] Health/readiness endpoints
- [x] Basic error tracking (Sentry or equivalent)
- [x] Uptime monitoring

---

## V1 HARDENING — WITHIN 60 DAYS OF LAUNCH

These are not MVP requirements but should be done shortly after launch to address known gaps and early user feedback.

- [ ] Email notifications: welcome email, email verification reminder, password reset
- [ ] In-app notification system (bell icon): overdue items, stale profile warnings
- [ ] Due date calendar grid view (traditional monthly calendar)
- [ ] Compliance item bulk actions (mark multiple as done)
- [ ] Export history with download link refresh (re-generate expired download URLs)
- [ ] API pagination improvements (filtering on more fields)
- [ ] Questionnaire: save-and-continue with progress indicator
- [ ] Rate limit: per-endpoint tightening based on real usage data
- [ ] Performance: evaluation result caching (if same profile + library version → serve cached)
- [ ] Admin tooling: basic DB-based user lookup for customer support
- [ ] Compliance library: B1–B10 legal research items fully resolved and records verified
- [ ] Source URL verification: automated check that all official_url values return 200
- [ ] Changelog page: record library updates with notes on what changed

---

## PHASE 2 — 3–6 MONTHS POST-LAUNCH

These require additional product investment and will be driven by user feedback.

### Collaboration & Multi-User
- Workspace member invites (email-based)
- ADMIN and ANALYST roles with different permissions
- Project-level assignments ("assigned to")
- Comments on compliance items
- Activity feed per project

### CA/Consultant Workflow
- Client list view (portfolio view across all projects in workspace)
- Batch export (export all client reports at once)
- Client-specific share link with custom branding option
- CSV upload for batch client profile creation

### Billing Integration
- Razorpay or Stripe integration for paid plan subscriptions
- Webhook for payment events
- Invoice generation
- Plan downgrade/upgrade flows with proration

### Reminders & Notifications
- Email reminders: "GSTR-3B is due in 3 days" (configurable: 7 days, 3 days, 1 day before)
- Reminder configuration per compliance type
- Digest email: weekly compliance summary

### Webhooks
- Register webhook URLs per workspace
- Events: `evaluation.completed`, `compliance.overdue_started`, `compliance.completed`
- Retry logic for failed webhook deliveries

### Advanced Analytics
- Export usage analytics to workspace owner
- Historical overdue trend (how many items were overdue last month vs this month)
- Compliance health score per project

### Technical
- Async evaluation (for future larger compliance libraries)
- Compliance library import admin UI
- Automated notification monitoring (detect new CBIC/MCA circulars — semi-automated)
- OpenAPI SDK generation (Python + JavaScript official SDKs)

---

## PHASE 3 — 6+ MONTHS (FUTURE EXPANSION)

- Full CA-mode product (separate UX layer on top of same API)
- Sector-specific compliance modules (FEMA/FDI, Factories full state coverage, SEBI)
- Third-party integrations (Tally, Zoho Books, QuickBooks India)
- AI-assisted compliance query ("What does missing my GSTR-3B filing mean for my input tax credit?")
- Compliance training content embedded in detail views
- White-label API for accounting software companies
- Multi-country expansion (Bangladesh, Sri Lanka — similar needs)

---

## WHAT EXPLICITLY DOES NOT GO IN MVP

| Feature | Reason for deferral |
|---------|---------------------|
| Workspace member invites | Single-user is the Day 1 use case (Q-C5) |
| Billing integration (Razorpay/Stripe) | Plan infrastructure exists; payment processing is Phase 2 |
| Email reminders | In-app is sufficient for MVP; email requires email deliverability infrastructure |
| Webhooks | No known need at MVP stage |
| Calendar grid view | Timeline list view covers the need; grid is a UX enhancement |
| Revision history/diff | Useful but not critical; audit_log gives basic trail |
| AI suggestions | Requires a different product capability layer |
| Admin panel | Direct DB access is sufficient for MVP at small scale |
| Native mobile apps | Web-first is correct; mobile is Phase 3 |
| SSO/Google login | Nice to have; email/password is sufficient for now |
| FEMA/FDI compliance module | High complexity, high professional review rate; Phase 3 |
