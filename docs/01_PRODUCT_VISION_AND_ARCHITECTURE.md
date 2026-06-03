# Document 01 — Product Vision and System Architecture
## ECNAILPCOM: Indian Business Compliance Intelligence System

---

## 1. DEEP RESTATEMENT OF THE PRODUCT GOAL

What we are building is not a checklist application. It is a **compliance knowledge graph engine** that:

1. Takes a structured description of a business as input (entity type, turnover, employee count, state presence, activity type, GST scheme, registration status, and other signals).
2. Runs that profile through a rule-based applicability engine that evaluates each compliance obligation against the business's characteristics.
3. Produces a ranked, source-backed list of compliance obligations that apply — or likely apply — to that business, with a calculated applicability confidence.
4. Computes **actual calendar due dates** for every applicable recurring compliance, using the current date, current Indian financial year, and encoded due-date rules.
5. Surfaces those obligations through multiple views: checklist, calendar, dashboard, and heat map.
6. Exposes, for every obligation, the exact legal provision, rule, notification, or official source behind it.
7. Flags delayed/overdue obligations with a severity score that reflects the real-world financial, legal, and business consequences of non-compliance.

The system is intended to work correctly without a professional advisor's intervention for the large majority of routine business compliance scenarios, while clearly flagging cases where human professional review is genuinely needed.

It is **not** a generic reminder app. Every single piece of compliance intelligence stored in this system must be traceable to a legal or regulatory source.

---

## 2. PROBLEM DECOMPOSITION — SYSTEM LAYERS

The system divides cleanly into eight distinct logical layers. These layers are partially independent (different teams can work on them simultaneously) but have well-defined data dependencies.

---

### LAYER 1 — USER INPUT LAYER

**Purpose:** Capture a normalized, structured business profile.

**Inputs:**
- Questionnaire answers from the business owner/accountant
- Progressive disclosure: later questions depend on earlier answers
- Optional: pre-population from MCA/GST public data if GSTIN or CIN is provided

**Outputs:**
- A `BusinessProfile` record with normalized fields
- A set of derived boolean/threshold flags used by the applicability engine

**Key Design Constraint:**
The questionnaire must be adaptive. Asking a proprietorship about board meetings is wasted UX. The question flow must prune itself based on entity type, activity, and earlier answers.

**See:** [docs/07_QUESTIONNAIRE_DESIGN.md](07_QUESTIONNAIRE_DESIGN.md)

---

### LAYER 2 — ENTITY CLASSIFICATION LAYER

**Purpose:** Translate raw business inputs into a compliance-relevant entity profile.

**Inputs:** `BusinessProfile` from Layer 1

**Outputs:**
- `EntityClass` — one of: PROPRIETORSHIP, PARTNERSHIP, LLP, PRIVATE_LIMITED, PUBLIC_LIMITED, OPC
- `ActivityClass` — one of: SERVICE, TRADING, MANUFACTURING, MIXED
- `TurnoverBand` — threshold bracket
- `EmployeeCountBand` — threshold bracket
- `GeographyProfile` — principal state, multi-state flag
- `GSTProfile` — scheme, registration status
- `TaxProfile` — audit applicability flag, advance tax flag
- `LabourProfile` — EPF/ESI triggers
- `EstablishmentProfile` — shop, factory, food, export triggers
- Set of derived boolean flags: `has_employees`, `makes_interstate_supply`, `has_manufacturing`, `is_gst_registered`, etc.

**Why this layer matters:**
Many compliances are triggered by combinations of factors, not single factors. A company that has 18 employees (below EPF threshold of 20) but has voluntarily registered for EPF is still under EPF obligations. The classification layer must encode such nuance.

---

### LAYER 3 — APPLICABILITY / RULES LAYER

**Purpose:** Evaluate, for each compliance in the master library, whether it applies to a given business profile.

**Inputs:**
- `EntityClassification` from Layer 2
- `ComplianceMasterLibrary` from Layer 4

**Outputs:**
- `ApplicabilityDecision` per compliance-business pair:
  - `applicability_status` (see applicability taxonomy in [docs/08_APPLICABILITY_MODEL.md](08_APPLICABILITY_MODEL.md))
  - `applicability_confidence` (HIGH / MEDIUM / LOW)
  - `why_it_applies` (human-readable reasoning)
  - `why_it_may_not_apply` (edge cases or missing data)
  - `missing_inputs` (what additional data would improve confidence)

**Key Design Constraint:**
Rules should be stored as structured expressions (JSON conditions), not as hardcoded logic. This allows the rule library to be updated without code changes.

**See:** [docs/08_APPLICABILITY_MODEL.md](08_APPLICABILITY_MODEL.md)

---

### LAYER 4 — COMPLIANCE LIBRARY LAYER

**Purpose:** Store the master knowledge base of all compliance obligations.

**Contents:**
- Compliance master records (static, source-backed, versioned)
- Due date rule records (computable formulas)
- Penalty/criticality records (static scores per compliance)
- Applicability rule records (structured conditions)
- Source records (legal/regulatory citations)

**Key Design Constraint:**
This is the most important layer. Every record must have a source. The library is maintained separately from any business instance. It is updated as laws change, notifications are issued, and due dates are revised.

**See:** [docs/04_DATA_MODEL.md](04_DATA_MODEL.md)

---

### LAYER 5 — DUE DATE COMPUTATION LAYER

**Purpose:** For each applicable compliance for a specific business, compute actual calendar dates.

**Inputs:**
- `ComplianceMasterRecord` with encoded due date rule
- Current date
- Current financial year
- Business-specific parameters (registration date, state, GST scheme, filing frequency, etc.)

**Outputs per compliance per period:**
- `current_period_start`
- `current_period_end`
- `filing_window_opens`
- `filing_window_closes` (actual due date)
- `is_overdue` (bool)
- `overdue_days` (int)
- `due_in_days` (int)
- `next_due_date` (for future periods)
- `overdue_flag` (bool)
- `financial_year_label` (e.g., "FY2025-26")
- `assessment_year_label` (where applicable, e.g., "AY2026-27")

**Key Design Constraint:**
Due date computation must be deterministic given the inputs. The same inputs must always produce the same output. Notification-based extensions must be stored as overrides in the library, not in ad-hoc code.

**See:** [docs/05_DUE_DATE_ENGINE.md](05_DUE_DATE_ENGINE.md)

---

### LAYER 6 — PENALTY / CRITICALITY LAYER

**Purpose:** Assign a severity score to each applicable overdue compliance.

**Inputs:**
- `PenaltyRecord` from compliance master
- `overdue_days` from Layer 5
- `amount_involved` where applicable (for interest calculations)

**Outputs:**
- `base_severity_score` (0–100, inherent)
- `dynamic_severity_score` (0–100, adjusted for current lateness)
- `combined_severity_score` (0–100)
- `severity_band` (LOW / MODERATE / HIGH / SEVERE / CRITICAL)
- `color_code` (hex color for UI heat map)
- `estimated_late_fee` (₹ amount if calculable)
- `estimated_interest` (₹ amount if calculable)
- `prosecution_risk_flag`

**See:** [docs/06_HEATMAP_SEVERITY_MODEL.md](06_HEATMAP_SEVERITY_MODEL.md)

---

### LAYER 7 — SOURCE TRACKING LAYER

**Purpose:** Maintain a fully source-attributed knowledge base, with versioning and conflict tracking.

**Contents:**
- Source master records (each law, rule, notification, circular)
- Compliance-source linkage (which source supports which compliance)
- Supersession / version history
- Conflict records (statute vs portal practice divergence)

**Key Design Constraint:**
Sources should be records, not free-text fields. Every source should have a type, authority, act/rule reference, and URL. When a notification supersedes an earlier one, the supersession relationship should be explicitly stored.

**See:** [docs/03_SOURCE_STRATEGY.md](03_SOURCE_STRATEGY.md)

---

### LAYER 8 — UI / API CONSUMPTION LAYER

**Purpose:** Present compliance intelligence to users in actionable formats.

**Views:**
1. **Checklist View** — all applicable compliances grouped by domain, filterable by status
2. **Calendar View** — due dates plotted on a monthly/annual timeline
3. **Dashboard View** — summary stats, upcoming obligations, overdue alerts
4. **Heat Map View** — severity grid or matrix showing critical obligations prominently
5. **Compliance Detail View** — full source attribution, due date logic, penalty summary

**This layer has not been designed yet.** It is intentionally deferred. The purpose of this planning phase is to get Layers 1–7 right first.

---

## 3. DESIGN PHILOSOPHY — CRITICAL PRINCIPLES

### 3.1 Source-First, Not Content-First

Every compliance record starts from a source. We identify the legal provision first, then encode the compliance details. We do NOT start from "what does a CA typically remind clients of" and then find a law to justify it.

### 3.2 Computable Due Dates, Not Labels

Every recurring compliance must have an encoded due date rule that the engine can evaluate programmatically. "Monthly" is not sufficient. The rule must specify: what period it applies to, what day/offset it falls on, what triggers it, and what adjustments apply.

### 3.3 Applicability Has Confidence Levels

Nothing is binary. A compliance can be APPLICABLE, LIKELY_APPLICABLE, CHECK_THRESHOLD, STATE_SPECIFIC, EVENT_TRIGGERED, or NOT_APPLICABLE. Confidence is tracked separately. Ambiguous cases are surfaced, not silently decided.

### 3.4 Penalties Are Structured, Not Freetext

Penalty consequences must be stored as structured fields, not prose paragraphs. This allows the severity scoring engine to compute heat map values from them.

### 3.5 The Library Is Separate from Business Instances

The compliance master library is static (versioned) knowledge. A business's compliance output is a computed view derived from the library applied to their profile. If the library is updated (e.g., a new circular extends a due date), all businesses' outputs can be re-derived.

### 3.6 Notification Overrides Are First-Class

Indian compliance is characterized by frequent notification-based due date extensions. The system must store these as versioned overrides, not as edits to base rules. This ensures auditability and allows rollback when extensions expire.

---

## 4. FINANCIAL YEAR HANDLING

All compliance logic must be grounded in the Indian financial year context.

| Concept | Definition |
|---------|-----------|
| Financial Year (FY) | April 1 to March 31 |
| FY Label | FY2025-26 = April 1 2025 to March 31 2026 |
| Assessment Year (AY) | For income tax: AY = FY + 1 year |
| AY Label | AY2026-27 corresponds to FY2025-26 income |
| FY Quarter Q1 | April 1 – June 30 |
| FY Quarter Q2 | July 1 – September 30 |
| FY Quarter Q3 | October 1 – December 31 |
| FY Quarter Q4 | January 1 – March 31 |
| GST Calendar Month | Calendar month (Jan–Dec) |
| MCA AGM Deadline | September 30 (for March FY companies) |

The engine must know the current date and derive:
- Current FY (e.g., "FY2025-26")
- Current FY quarter (Q1/Q2/Q3/Q4)
- Current AY (e.g., "AY2026-27")
- Days remaining in current FY
- Days since FY start

---

## 5. WHAT THIS SYSTEM IS NOT

- It is not a legal advice platform. It surfaces legal obligations, not legal advice.
- It is not a CA substitute for complex transactions. It flags professional review needs.
- It is not a filing portal. It does not file anything on behalf of users.
- It is not a blanket reminder tool. Every item it shows must be legally grounded.
- It is not an SEO-driven compliance blog. Content quality standards are legal-grade.
