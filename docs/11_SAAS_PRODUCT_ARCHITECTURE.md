# Document 11 — SaaS Product Architecture
## From Compliance Engine to Full SaaS Platform

**STATUS:** Part A (docs 01–10, schema/) is FROZEN BASELINE. This document builds on top of it.
**TECH LEAD NOTE:** Any AI implementing this product must read docs 01–10 before reading Part B (docs 11–22).

---

## 1. DEEP RESTATEMENT OF THE SAAS PRODUCT GOAL

The compliance intelligence engine defined in Part A is the **brain**. Part B defines the **body** — everything required to make that brain accessible, accountable, monetizable, and maintainable as a production SaaS.

The product transforms into a platform with three distinct interaction modes:

**Mode 1 — Self-Serve Business User (MVP Day 1)**
A business owner or founder creates an account, describes their business through a guided questionnaire, and receives a fully classified, source-backed compliance profile. They see actual due dates, overdue items, risk severity, and can track completion across periods. This is the primary Day 1 user.

**Mode 2 — Consultant / CA Workflow (Data model ready; UI deferred to Phase 2)**
A professional user manages multiple client businesses under one account. The data model supports this from Day 1. The UI for CA-specific portfolio views is deferred but the underlying multi-project structure enables it without a schema change later.

**Mode 3 — Developer / API Integration (MVP Day 1)**
A developer receives a workspace API key, reads the documentation, submits a business profile via REST API, and receives structured JSON compliance output. This enables embedding compliance intelligence in ERPs, accountant dashboards, or workflow tools.

**Core promise of the platform:**
- Every compliance output is traceable to a primary legal source
- Every due date is computed, not guessed
- Every severity score is structured, not subjective
- Every output carries a disclaimer, a confidence level, and a last-verified date
- The compliance library is version-controlled and separately maintainable from business instances

---

## 2. PRODUCT MODULE MAP

The SaaS consists of the following product modules. Each module maps to one or more docs in this series.

| Module | Responsibility | Doc Reference |
|--------|---------------|---------------|
| Auth & Identity | User signup, login, session, API keys | doc 14 |
| Workspace & Tenancy | Multi-tenant isolation, roles, data scoping | doc 12 |
| Project / Business Profile | Business questionnaire, classification, storage | doc 12 + Part A doc 04 |
| Compliance Evaluation Engine | Applicability, due dates, penalties (from Part A) | Part A docs 01–10 |
| Compliance Tracker | Marking completion, status per period | doc 12 (schema extension) |
| Dashboard & Views | UI surfaces, heat map, calendar, list | doc 16 |
| Export & Sharing | JSON/CSV/print exports, share links | doc 18 |
| REST API | Endpoint families, auth, versioning, error handling | doc 13 |
| Usage Metering | Quota tracking, free plan, soft paywall | doc 17 |
| Onboarding | New user flows, guided setup | doc 15 |
| Developer Experience | Docs, API playground, quickstarts | doc 19 |
| Observability & Ops | Logging, metrics, admin visibility | doc 20 |
| Public Surface | Homepage, pricing, demo, docs pre-login | doc 16 section 1 |

---

## 3. CRITICAL PART B EXTENSIONS TO PART A DATA MODEL

Part B introduces three structural extensions to the Part A schema that must be reflected in implementation. These are not contradictions — they are refinements required by the compliance tracker requirement (Q-A3) and the SaaS tenancy layer.

### Extension B1 — Compliance Period Instances (REQUIRED)

**Problem with Part A `business_compliance_output` table:**
It models ONE output record per compliance per business (the "current period"). But a compliance tracker needs one record per compliance per PERIOD per business. GSTR-3B for May and GSTR-3B for June are separate trackable items.

**Resolution: Replace `business_compliance_output` with `compliance_period_instance`**

```sql
compliance_period_instance {
  instance_id             UUID PRIMARY KEY
  business_id             UUID FK -> business_profile.business_id
  compliance_id           UUID FK -> compliance_master.compliance_id
  workspace_id            UUID FK -> workspaces.workspace_id  -- for tenant isolation
  
  -- Period
  period_label            VARCHAR(50)     -- "May 2026", "Q1 FY2026-27", "FY2025-26"
  period_start            DATE
  period_end              DATE
  
  -- Applicability (from evaluation)
  applicability_status    ENUM (same taxonomy as Part A doc 08)
  applicability_confidence ENUM
  why_it_applies          TEXT
  missing_inputs          TEXT[]
  
  -- Computed Due Date
  filing_window_opens     DATE
  computed_due_date       DATE
  override_active         BOOLEAN DEFAULT FALSE
  override_source_id      UUID FK -> source_master.source_id
  effective_due_date      DATE    -- = computed_due_date or override if active
  financial_year_label    VARCHAR(20)
  
  -- Status at computation time
  is_overdue              BOOLEAN
  overdue_days            SMALLINT
  due_in_days             SMALLINT
  base_severity_score     SMALLINT
  dynamic_severity_score  SMALLINT
  combined_severity_score SMALLINT
  severity_band           ENUM
  color_code              VARCHAR(7)
  
  -- TRACKER FIELDS (Q-A3 requirement)
  tracking_status         ENUM ('PENDING','COMPLETED','SKIPPED','NOT_APPLICABLE_THIS_PERIOD')
  completed_on            DATE
  completed_by            UUID FK -> users.user_id
  completion_notes        TEXT
  
  -- Library version at evaluation time
  library_version         VARCHAR(20)
  evaluated_at            TIMESTAMPTZ
  is_stale                BOOLEAN DEFAULT FALSE

  created_at              TIMESTAMPTZ DEFAULT NOW()
  updated_at              TIMESTAMPTZ DEFAULT NOW()
  
  UNIQUE (business_id, compliance_id, period_start)
}
```

### Extension B2 — SaaS Tenancy Tables (REQUIRED)

New tables layered on top of Part A's `business_profile`:

```
users
workspaces
workspace_members
api_keys
usage_events
onboarding_progress
share_links
exports
audit_log
```

Full schema in [doc 12](12_TENANT_USER_WORKSPACE_MODEL.md).

### Extension B3 — Workspace FK on business_profile (REQUIRED)

The Part A `business_profile` table must gain a `workspace_id` column:
```sql
ALTER TABLE business_profile ADD COLUMN workspace_id UUID NOT NULL REFERENCES workspaces(workspace_id);
CREATE INDEX idx_business_profile_workspace ON business_profile(workspace_id);
```

This enables workspace-scoped queries and row-level security policies.

---

## 4. PART A / PART B COMPATIBILITY CHECK

| Part A Design Decision | Part B Impact | Resolution |
|------------------------|--------------|------------|
| `business_compliance_output` single-row per compliance | Tracker needs per-period rows | Replaced with `compliance_period_instance` (Extension B1 above) |
| No tenancy layer in Part A tables | SaaS needs workspace isolation | `workspace_id` FK added to `business_profile` and `compliance_period_instance` |
| Library is static master data | SaaS needs versioning for snapshots | Add `library_version` tag to source records; exports capture version at snapshot time |
| Disclaimer requirement (Q-A1) | Every API response and UI view needs disclaimer | Disclaimer field in evaluation response envelope; not on each line item |
| Multi-project for individual users allowed | Part A data model already supports it | No conflict — `business_profile` has 1:many with workspace |

**No fundamental conflicts found.** The Part A design is forward-compatible with the SaaS layer.

---

## 5. LIBRARY VERSION CONCEPT

Part A stores compliance records with `effective_from` and `last_reviewed_at`. For export snapshots and API responses, a `library_version` tag is needed.

**Implementation:** A `library_meta` table with one active row:
```sql
library_meta {
  version           VARCHAR(20) PRIMARY KEY   -- e.g., "v1.2.0"
  released_at       TIMESTAMPTZ
  release_notes     TEXT
  num_compliance_records INTEGER
  num_sources         INTEGER
  is_current          BOOLEAN DEFAULT TRUE
}
```

When a compliance library update is released (via Git-tracked import), increment the version. All `compliance_period_instance` records capture the `library_version` at evaluation time. Exports include this version in their metadata header.

---

## 6. SYNCHRONOUS vs. ASYNC EVALUATION

**For MVP: Synchronous evaluation.**

The compliance engine runs entirely in-process:
1. Load business profile
2. Load applicable compliance master records
3. Evaluate applicability rules (JSON expression tree evaluation)
4. Compute due dates for all applicable compliances and all periods of current FY
5. Compute severity scores
6. Persist `compliance_period_instance` rows
7. Return evaluation result

**Estimated computation time:** For a typical business with ~50 applicable compliances × 12 monthly periods + quarterly + annual items ≈ 200–400 period instance rows to compute. This should complete in < 500ms on any reasonable server.

**When to switch to async:** If computation exceeds 2 seconds (e.g., if future scope adds 500+ compliance items or complex rule chains). At that point, POST /evaluation returns a `job_id` and results are polled via GET /evaluation/:jobId. Design the API response envelope to support this migration without breaking changes (see doc 13).

---

## 7. DISCLAIMER ARCHITECTURE

Per Q-A1, every compliance output must carry:
- Source provenance (compliance-level)
- Last verified date (compliance-level)
- Confidence level (compliance-level)
- Standard disclaimer (evaluation-level, once per response)

**Disclaimer text (standardized):**
> "This compliance assessment is generated for informational and planning purposes only. It is not legal advice and does not substitute for consultation with a qualified Chartered Accountant, Company Secretary, or legal professional. Due dates, thresholds, and rules are subject to change via government notifications and circulars. Always verify current due dates on official government portals before filing. [Product Name] does not accept liability for any penalties or losses arising from reliance on this output."

This text is stored in a `system_config` table (not hardcoded) so it can be updated without a code deployment.
