# Document 22 — SaaS Clarification Questions and Inconsistencies
## Open Questions Before Implementation Begins

---

## SECTION A — INCONSISTENCIES AND ARCHITECTURAL FLAGS

These are real issues in the combined Part A + Part B specification that need resolution before implementation.

---

### INCONSISTENCY I1: Part A `business_compliance_output` Table vs. Tracker Requirement

**Problem:**
Part A (doc 04) defined `business_compliance_output` as one row per compliance per business. But the compliance tracker requirement (Q-A3) and recurring compliance reality demand one row per compliance per PERIOD per business (e.g., GSTR-3B for May AND GSTR-3B for June are separate trackable items).

**Resolution proposed in doc 11:**
Replace `business_compliance_output` with `compliance_period_instance` (defined in doc 11, Extension B1). This table has a UNIQUE constraint on `(business_id, compliance_id, period_start)`.

**Decision needed:** Confirm this replacement is accepted and there is no architectural reason to retain the original single-row design.

---

### INCONSISTENCY I2: How Many Periods to Pre-Generate per FY

When an evaluation runs, the engine generates `compliance_period_instance` rows. For how many periods should it generate?

**Options:**
- (a) All periods in the CURRENT financial year only (April–March)
- (b) Current FY + 3 months into next FY (for long-advance planning)
- (c) On-demand: only generate the current period + past overdue periods

**Problem with (a):** If the user evaluates in January 2026, they won't see February and March due dates until those periods "open." But these are predictable and should be shown.

**Problem with (c):** Users can't plan ahead.

**Recommendation:** Option (a) with the following: for the current FY, generate ALL period instances April–March. Additionally, pre-generate the first 1 month of the NEXT FY so calendar continuity is preserved at FY end.

**Decision needed:** Confirm this approach.

---

### INCONSISTENCY I3: Evaluation Quota When Profile is Unchanged

**Problem:** If a user clicks "Re-evaluate" without changing any questionnaire answers AND the library version hasn't changed since last evaluation, should this cost a quota unit?

**Arguments for charging:** The computation still runs.
**Arguments against charging:** Wasted quota; user experience frustration; encourages users to change fake answers to avoid the charge.

**Recommendation:** If `last_evaluation_library_version == current_library_version` AND no questionnaire changes since last evaluation: return the cached evaluation result at 0 quota cost with header `X-Cache: HIT` and `X-Cache-Reason: no_changes`.

**Decision needed:** Accept this caching rule?

---

### INCONSISTENCY I4: Share Link — Snapshot vs. Live

Part B (doc 18) decided: share links are snapshot-based. But the product spec also says the system must allow users to "update answers over time and regenerate outputs."

**Resulting question:** When a user re-evaluates their project and creates a NEW share link, is the NEW share link always based on the LATEST evaluation? Or can a user choose which snapshot to share?

**Recommendation:** By default, a new share link attaches to the LATEST evaluation. Allow user to optionally specify `?evaluation_id=uuid` to share a specific earlier snapshot. This allows "sharing last month's report" specifically.

**Decision needed:** Accept this, or simplify to "always latest evaluation only"?

---

### INCONSISTENCY I5: Demo — Real Computation vs. Sample Data

The product spec says "try before signup." Two possible implementations:

**(a) Real computation:** The demo uses the actual compliance engine with the submitted 6-field mini-profile. Computationally honest but requires engine access from an unauthenticated endpoint.

**(b) Curated sample responses:** Prepared JSON responses for common demo inputs. Fast, safe, but less impressive and could be "gamed" (the response doesn't really reflect the input).

**Recommendation:** Real computation (option a). It is more impressive and honest. Security is handled by rate limiting + result truncation. The demo never stores any data and computes on-the-fly.

**Decision needed:** Confirm real computation for demo.

---

### INCONSISTENCY I6: Financial Year Context When User Crosses April 1

The evaluation runs on the current FY. If a user creates a project in March 2026 and evaluates it, all period instances are for FY2025-26. On April 2, 2026, the current FY becomes FY2026-27.

**Behavior question:** Should old FY2025-26 data remain visible? Should a new evaluation automatically generate FY2026-27 periods?

**Recommendation:**
- Old FY periods remain visible with their original tracking status (so the user can see what was completed last FY)
- On the first evaluation AFTER the FY changes, generate new FY periods AND preserve old FY history
- Dashboard default shows CURRENT FY; user can toggle to previous FY
- Period instances from old FY: `tracking_status` becomes read-only (cannot be modified)

**Decision needed:** Confirm this FY transition behavior.

---

## SECTION B — CLARIFICATION QUESTIONS (MUST ANSWER BEFORE IMPLEMENTATION)

---

**Q1. Can one user manage multiple businesses at MVP?**

Context: Q-C5 said "multi-business data model ready, CA portfolio UI deferred." But does the free plan allow up to 3 projects (each being a different business), or is it truly 1 project per user at MVP?

**Recommendation:** Allow up to 3 projects on free plan. This covers: owner who has multiple businesses, CA who tests with 2–3 client profiles. The CA portfolio VIEW is deferred, but the underlying multi-project capability is present.

**Your decision:**

---

**Q2. Does UI-triggered evaluation count toward request quota?**

Context: The user triggers "Re-evaluate" in the browser dashboard. Does this consume 1 of the 100 daily quota units?

**Recommendation:** YES. Both UI and API evaluations consume quota. The quota is workspace-level, not API-key-level. This is simpler and fairer.

**Your decision:**

---

**Q3. Does the public demo use real computation or sample/pre-baked responses?**

Context: Inconsistency I5 above. Recommendation is real computation.

**Your decision:**

---

**Q4. Are exports snapshot-based (CONFIRMED) — but what happens when the snapshot is > 30 days old?**

Context: The download URL expires after 24 hours. After that, the user must regenerate the export (costing 1 quota unit). Is this acceptable? Or should we keep the snapshot data available for regeneration on-demand without quota cost?

**Recommendation:** The underlying export data (library version, evaluation snapshot) should be stored in DB for 30 days. Regenerating the DOWNLOAD URL from an existing snapshot should cost 0 quota. Generating a brand new export from a NEW evaluation costs 1 quota.

**Your decision:**

---

**Q5. Are in-app reminders/alerts (badges + banners) in MVP or later?**

Context: The product is due-date driven. Should the dashboard show overdue items prominently (Yes — already designed) and should it also show "GSTR-1 is due tomorrow" as an active push notification? Or just the passive count?

**Recommendation:**
- **MVP:** In-app visual indicators ONLY (red badges, overdue banners, due-soon counts). No push notifications.
- **Phase 2:** Email reminders, configurable thresholds.

**Your decision:**

---

**Q6. Should API responses include FULL source details or only source references?**

Context: Every API compliance item has a `source_summary` field. Should it include:
- (a) Full source data: act name, section, rule, notification number, official URL, last verified date — embedded in every compliance item response
- (b) Source reference only: `source_id` + `primary_act` + `authority` — consumer must call a separate `/source` endpoint for details

**Recommendation:** Include full source summary inline in every compliance item (option a). Source data is small in size. Making developers do a second call for source info reduces adoption. Option (b) was designed for this product exactly for the purpose of showing source provenance.

**Your decision:**

---

**Q7. Is pricing/billing integration MVP or placeholder only?**

Context: The system stores `plan_id` and `daily_quota_limit` in workspaces. Is actual payment processing (Razorpay/Stripe/etc.) required on launch day, or is it acceptable to launch with:
- Free plan only initially
- "Upgrade" button that shows interest form / waitlist
- Paid plans manually provisioned by admin

**Recommendation:** Launch with free plan + interest form for paid plans. Real payment integration is Phase 2. Ensure the plan infrastructure in DB is designed to support it when added.

**Your decision:**

---

**Q8. Are public docs and playground available before login (no signup wall)?**

Context: All documentation should be public. But should the interactive API playground (authenticated, using real API key) require signup?

**Recommendation:** 
- Docs: 100% public, no login required
- Public demo console at /demo: public, IP rate limited
- Authenticated playground (using real workspace API key): requires signup
- OpenAPI spec JSON/YAML: public

**Your decision:**

---

**Q9. Is multi-client CA/consultant workflow MVP or later?**

Context: Already answered as "later for UI." But clarify: if a CA creates 3 projects (3 different clients) under 1 workspace on the free plan, is that supported? Or must CAs sign up separately for each client?

**Recommendation:** 3 projects per workspace on free plan. A CA can use these for 3 clients. They don't need separate accounts. When they need more clients, they upgrade. This is the natural upgrade trigger for the CA segment.

**Your decision:**

---

**Q10. Is historical recomputation required when library/source versions change?**

Context: If CBIC issues a notification extending GSTR-3B due date and we update the library, should ALL existing `compliance_period_instance` rows be recomputed? Or just flagged as stale?

**Recommendation:** Flag as stale (set `evaluation_is_stale = true` on all affected business_profiles). Do NOT auto-recompute. Recomputation happens on next user-triggered evaluation. This avoids a thundering herd and ensures the user actively sees the change.

The exception: if a notification changes a past due date (extension was retroactive), the system should show a notification on the dashboard: "The due date for GSTR-3B March 2026 was extended to April 30 per Notification XX. Re-evaluate to update your records."

**Your decision:**

---

**Q11. What is the product name? (Blocking for implementation)**

Context: "ECNAILPCOM" is a code name / repository identifier. The product needs a real brand name for:
- Homepage copy and hero text
- Email addresses (no-reply@[domain])
- Documentation URLs
- Error message text
- Legal pages

**Your decision:**

---

**Q12. What is the tech stack? (Partially blocking for implementation)**

Context: Part A and Part B are technology-agnostic by design. However, implementation needs to choose:
- Backend language/framework
- Frontend framework
- Database (recommended: PostgreSQL — confirmed in doc 04)
- Cache/queue (recommended: Redis for quotas)
- File storage (S3 or equivalent)
- Email service (SendGrid / AWS SES / Postmark)
- Hosting/cloud provider

The compliance intelligence design works with any reasonable stack. The architecture (RLS, JSONB, cursor pagination, structured logs) is specifically designed for PostgreSQL + any web backend.

**Your decision:**

---

## SECTION C — SUMMARY OF OPEN DECISIONS

| # | Question | Recommendation | Blocking Implementation? |
|---|---------|---------------|--------------------------|
| I1 | `business_compliance_output` → `compliance_period_instance` replacement | Accept | YES — schema design |
| I2 | FY period generation scope | Current FY + 1 month next FY | YES — evaluation engine |
| I3 | Zero-quota cache on unchanged re-evaluation | Accept | NO — can add later |
| I4 | Share link snapshot choice | Latest by default; allow specific evaluation_id | NO — can simplify to latest only for MVP |
| I5 | Demo: real computation | Yes — real computation | YES — demo implementation |
| I6 | FY transition behavior | Preserve old FY, generate new FY on first post-April eval | YES — evaluation engine |
| Q1 | Multiple projects on free plan | Up to 3 | YES — plan limits |
| Q2 | UI evaluations count toward quota | YES | YES — metering |
| Q3 | Demo real vs. sample | Real computation | YES — demo |
| Q4 | Export re-download quota | Re-download from existing snapshot = 0 quota | NO — can simplify |
| Q5 | In-app reminders MVP | Passive indicators only in MVP | NO |
| Q6 | Full source in API response | YES, inline | YES — API response shape |
| Q7 | Billing integration MVP | Placeholder only | YES — affects paid plan feature set |
| Q8 | Docs public before login | YES, docs always public | YES — routing/auth |
| Q9 | CA multi-client MVP | 3 projects on free = OK for CAs | YES — plan limits |
| Q10 | Stale recomputation | Flag, don't auto-recompute | YES — library update flow |
| Q11 | Product name | ❓ REQUIRED | YES — blocks content |
| Q12 | Tech stack | ❓ REQUIRED | YES — blocks implementation |
