# C1 — Canonical Compliance Item Schema
## Complete Field-Level Definition of a Master Library Rule Record

---

## 1. Objective

Define every field that constitutes a compliance rule in the master library — its purpose, governing constraints, data type, and whether it belongs to the master layer (static, shared) or the instance layer (computed, per-business).

This schema is the formal specification from which the database tables (defined in Part A doc 04) derive their meaning. The tables define structure; this document defines governance and semantics.

---

## 2. Why It Matters to the Compliance Engine

An incomplete or inconsistently populated rule record produces unreliable applicability determinations, wrong due dates, inaccurate severity scores, or unsupported claims shown to users. Every field in the schema exists for a specific purpose. Populating a field incorrectly is as harmful as leaving it empty.

---

## 3. Design Principles

- Every mandatory field must have a value before a rule enters the active library.
- Optional fields are optional because the information may not exist for all rules — not because they are unimportant.
- Conditional fields apply only under specified conditions.
- Master-layer fields describe the law. Instance-layer fields describe a business's specific situation.
- No prose descriptions may substitute for structured fields. Prose belongs in `description_plain` and `notes` fields only as supplementary context.

---

## 4. Schema Definition

The schema is organized into seven groups: Identity, Classification, Legal Basis, Obligation Logic, Timing/Recurrence, Consequence, and Lifecycle/Trust.

---

### GROUP 1 — IDENTITY FIELDS

| Field | Purpose | Mandatory | Type | Layer |
|-------|---------|-----------|------|-------|
| `compliance_id` | Immutable unique identifier for this rule. Never reused, never changed. | Mandatory | UUID | Master |
| `compliance_code` | Human-readable stable code following the naming convention `{DOMAIN}_{SUBJECT}_{FREQUENCY}_{VARIANT}`. Example: `GST_GSTR3B_MONTHLY_REGULAR`. Used for referencing across documents and in exports. Once assigned and activated, this code must not change. | Mandatory | String, pattern: `[A-Z][A-Z0-9_]{4,49}` | Master |
| `title` | Full display title of the compliance obligation as it will appear to users. Must be descriptive and precise, not abbreviated. | Mandatory | String, max 200 chars | Master |
| `short_title` | Abbreviated title for calendar, heat map tile, and compact views. Must be self-explanatory in context. | Optional | String, max 60 chars | Master |
| `version_number` | Integer starting at 1. Incremented each time a substantive field is changed. | Mandatory | Integer ≥ 1 | Master |
| `predecessor_id` | If this rule supersedes a prior version, the `compliance_id` of the superseded rule. | Conditional: required if this is a replacement | UUID or null | Master |

---

### GROUP 2 — CLASSIFICATION FIELDS

| Field | Purpose | Mandatory | Type | Layer |
|-------|---------|-----------|------|-------|
| `domain` | Top-level compliance domain. Drives dashboard grouping and domain-level filtering. Valid values defined in the domain taxonomy (see C11). | Mandatory | Enum | Master |
| `category` | Functional category within the domain. Example: "Return Filing", "Tax Payment", "Registration". | Mandatory | Enum | Master |
| `subcategory` | More granular classification. Example: "Monthly Returns", "Event-Based Filings". | Optional | String | Master |
| `obligation_type` | The nature of the required action. Drives how the system presents and tracks the obligation. Valid values: REGISTRATION, RETURN_FILING, TAX_PAYMENT, RECORD_KEEPING, GOVERNANCE, EVENT_BASED, AUDIT, DISCLOSURE, RENEWAL, CERTIFICATE, INDICATOR. | Mandatory | Enum | Master |
| `frequency_type` | How often this obligation recurs. Valid values: ONE_TIME, MONTHLY, QUARTERLY, HALF_YEARLY, ANNUAL, EVENT_BASED, CONTINUOUS, AS_APPLICABLE. | Mandatory | Enum | Master |
| `jurisdiction` | Whether this obligation arises from a central law, state law, or specific state. Valid values: CENTRAL, ALL_STATES, SPECIFIC_STATES. | Mandatory | Enum | Master |
| `applicable_states` | For SPECIFIC_STATES jurisdiction: list of ISO 3166-2:IN state codes. Empty for CENTRAL or ALL_STATES. | Conditional: required if jurisdiction = SPECIFIC_STATES | Array of state codes | Master |

---

### GROUP 3 — LEGAL BASIS FIELDS

| Field | Purpose | Mandatory | Type | Layer |
|-------|---------|-----------|------|-------|
| `governing_act` | Full name of the primary Act from which the obligation arises. Example: "Central Goods and Services Tax Act, 2017". | Mandatory | String | Master |
| `governing_act_short` | Common abbreviation. Example: "CGST Act". | Optional | String | Master |
| `primary_provision_reference` | The section, sub-section, rule, or regulation that directly creates the obligation. Must be specific. "Section 39" is acceptable. "The Act" is not. | Mandatory | String | Master |
| `secondary_provision_references` | Rules, regulations, or notifications that supplement the primary provision. Stored as an array of strings. | Optional | Array of strings | Master |
| `operative_legal_text` | The key operative sentence or clause from the primary provision, quoted verbatim. This is used to verify the rule's legal basis and is shown in source attribution. | Mandatory | String, quoted verbatim | Master |
| `description_plain` | Plain-language explanation of the obligation for non-legal readers. Written as: "What is required", not a legal summary. | Mandatory | String | Master |
| `legal_basis_summary` | Brief legal explanation for professional users. May reference provisions, exceptions, and cross-references. One paragraph maximum. | Optional | String | Master |

---

### GROUP 4 — APPLICABILITY AND TRIGGER FIELDS

| Field | Purpose | Mandatory | Type | Layer |
|-------|---------|-----------|------|-------|
| `entity_types_applicable` | Which legal entity types this obligation may apply to. Use `["ALL"]` if no entity-type restriction. Valid values: PROPRIETORSHIP, PARTNERSHIP, LLP, PRIVATE_LIMITED, PUBLIC_LIMITED, OPC, SECTION8_COMPANY, ALL. | Mandatory | Array of enum values | Master |
| `activity_types_applicable` | Which business activity types this obligation may apply to. Valid values: SERVICE, TRADING, MANUFACTURING, MIXED, ALL. | Optional; defaults to ALL | Array of enum values | Master |
| `applicability_rule_id` | Reference to the structured rule expression (in the applicability_rule table) that encodes the programmatic evaluation logic. | Mandatory | UUID reference | Master |
| `applicability_rule_summary` | Human-readable summary of the applicability logic. Example: "Applies to all GST-registered businesses under regular scheme with monthly filing frequency." Must match the programmatic rule. | Mandatory | String | Master |
| `exemption_description` | Description of legal exemptions or carve-outs. Example: "Government companies are excluded per Rule 16A(3)." Populate when a legal exemption exists. | Conditional: required if exemptions exist | String | Master |
| `threshold_fields_involved` | List of business profile field names that are used in applicability evaluation. Helps identify which business facts must be collected to evaluate this rule. Example: `["employee_count", "annual_turnover_estimated", "gst_registered"]`. | Mandatory | Array of field name strings | Master |
| `requires_event_trigger` | Whether this obligation is only triggered by a specific business event (change of director, allotment of shares, etc.). | Mandatory | Boolean | Master |
| `event_trigger_description` | If requires_event_trigger = true: description of the triggering event. Example: "Appointment of a new director." | Conditional | String | Master |
| `industry_specific_flag` | Whether this obligation applies only to a specific industry or sector. | Mandatory | Boolean | Master |
| `industry_notes` | If industry_specific_flag = true: describe the industry scope. | Conditional | String | Master |
| `requires_registration_precondition` | Whether a prior registration (GST, PF, ESI, etc.) is required before this obligation arises. Example: GSTR-3B only applies if GST-registered. | Mandatory | Boolean | Master |
| `registration_precondition_detail` | Which registration is required. Example: "Requires active GST registration under regular scheme." | Conditional | String | Master |

---

### GROUP 5 — TIMING AND RECURRENCE FIELDS

| Field | Purpose | Mandatory | Type | Layer |
|-------|---------|-----------|------|-------|
| `due_date_rule_id` | Reference to the structured due-date rule record. If null, the obligation is CONTINUOUS (no computable due date) or EVENT_BASED with a pending event. | Conditional | UUID reference or null | Master |
| `due_date_determinability` | Whether the due date can be computed from the rule alone. Valid values: COMPUTABLE (can compute), EVENT_DEPENDENT (requires user-supplied event date), CONTINUOUS (no single due date), PERIOD_UNKNOWN (rule exists but due date formula not yet encoded). | Mandatory | Enum | Master |
| `due_date_formula_plain` | Plain-language description of how the due date is derived. Example: "20th of the calendar month following the return period." | Mandatory | String | Master |
| `financial_year_dependency` | Whether the due date is anchored to the Indian financial year (April–March). | Mandatory | Boolean | Master |
| `assessment_year_dependency` | Whether the due date is expressed in Assessment Year terms (relevant for income tax items). | Mandatory | Boolean | Master |
| `extension_possible` | Whether the government can extend this due date via notification or circular. | Mandatory | Boolean | Master |
| `extension_history_note` | Narrative note on historical extension patterns. Example: "CBDT has extended ITR due dates in multiple years via circular." Informs users to verify current extensions. | Optional | String | Master |

---

### GROUP 6 — CONSEQUENCE AND SEVERITY FIELDS

| Field | Purpose | Mandatory | Type | Layer |
|-------|---------|-----------|------|-------|
| `penalty_record_id` | Reference to the structured penalty record. | Conditional: required for all RETURN_FILING, TAX_PAYMENT, REGISTRATION obligations | UUID reference | Master |
| `consequence_summary` | One or two sentence plain-language description of consequences. Example: "Late filing attracts ₹50/day fee (max ₹10,000) plus 18% annual interest on unpaid tax." | Mandatory for non-INDICATOR types | String | Master |
| `base_severity_score` | Pre-computed severity score 0–100 based on the penalty record. Stored for performance. Recomputed when penalty record changes. | Mandatory for obligations with a penalty record | Integer 0–100 | Master |
| `severity_band` | Derived band: LOW, MODERATE, HIGH, SEVERE, CRITICAL. | Mandatory for obligations with a penalty record | Enum | Master |
| `prosecution_possible` | Whether the governing statute permits prosecution for non-compliance. | Mandatory | Boolean | Master |
| `requires_professional_review_for_consequence` | Whether the consequence interpretation requires a CA or legal professional's review. Set true for ambiguous penalty provisions. | Mandatory | Boolean | Master |

---

### GROUP 7 — LIFECYCLE, TRUST, AND VERSION FIELDS

| Field | Purpose | Mandatory | Type | Layer |
|-------|---------|-----------|------|-------|
| `validation_state` | The trust/confidence state of this rule record. Full taxonomy defined in C8. | Mandatory | Enum | Master |
| `validation_notes` | Explanation of why this validation state was assigned. Required when state is not VALIDATED_PRIMARY. | Conditional | String | Master |
| `source_confidence_level` | Overall confidence in the primary source: HIGH, MEDIUM, LOW. | Mandatory | Enum | Master |
| `interpretation_ambiguity_flag` | Whether there is unresolved interpretive ambiguity in this rule. | Mandatory | Boolean | Master |
| `interpretation_notes` | If interpretation_ambiguity_flag = true: describe the ambiguity, competing interpretations, and the adopted interpretation. | Conditional | String | Master |
| `requires_human_review` | Whether a professional reviewer must assess this rule before it is shown to users. | Mandatory | Boolean | Master |
| `human_review_reason` | Reason human review is required. Required when requires_human_review = true. | Conditional | String | Master |
| `reviewer_notes` | Internal notes from the last reviewer. May include questions, caveats, or cross-references. | Optional | String | Master |
| `active_flag` | Whether this rule is part of the active library. False for archived/superseded/deferred rules. | Mandatory | Boolean | Master |
| `effective_from` | Date from which this rule version applies. | Mandatory | Date | Master |
| `effective_to` | Date after which this rule is no longer operative. Null if still active. | Optional | Date or null | Master |
| `last_reviewed_at` | Timestamp of the last substantive review. | Mandatory | Timestamp | Master |
| `review_due_by` | Date by which the next review should be completed. Computed as last_reviewed_at + max_review_interval (default 90 days; 30 days for rate/threshold rules). | Mandatory | Date | Master |
| `library_version` | The library version at which this rule was introduced or last substantively modified. | Mandatory | String | Master |
| `created_at` | Creation timestamp. Immutable. | Mandatory | Timestamp | Master |
| `updated_at` | Last update timestamp. Auto-set on any write. | Mandatory | Timestamp | Master |

---

## 5. Field Population Rules

### Mandatory vs. Optional — Strict Enforcement
A rule record may only enter `active_flag = true` if ALL mandatory fields are populated. A rule with any mandatory field left blank must remain in `validation_state = DRAFT` and must not be shown to users.

### Prose vs. Structure
Prose fields (`description_plain`, `legal_basis_summary`, `consequence_summary`) are supplementary. They provide human-readable context but must not be the only representation of logic that the system evaluates. The applicability_rule_id and due_date_rule_id references contain the machine-evaluable logic. Both must exist.

### Immutable Fields
`compliance_id`, `compliance_code`, `created_at`, and `operative_legal_text` are immutable once a rule is activated. Changes to these require creating a new rule version with a new `compliance_id` and setting `predecessor_id` to point to the old record.

---

## 6. Edge Cases

**Rule with no penalty:** INDICATOR and RECORD_KEEPING obligations may have no direct statutory penalty in the primary source. In these cases, `penalty_record_id` is null, `consequence_summary` describes the indirect risk, and `base_severity_score` is computed from the indirect risk factors only. Do not fabricate a penalty.

**Rule applicable to only one state:** Set `jurisdiction = SPECIFIC_STATES` and `applicable_states = ["MH"]`. All applicability logic still applies; the state check is one condition in the rule expression.

**Rule that is INDICATOR type:** `due_date_determinability = CONTINUOUS` and `due_date_rule_id = null`. No period instances are generated. The obligation appears in the compliance list as an awareness item without a calendar due date.

---

## 7. Deferred Fields

The following fields are defined in the schema for future use but are NOT required for MVP population:

- `related_compliance_ids`: Array of compliance_ids that are logically connected (e.g., GSTR-9 depends on GSTR-3B). Useful for cascade logic but not required for initial library.
- `evidence_document_expectation`: What the business should retain as evidence of compliance (e.g., "ARN from GST portal", "Challan receipt"). Phase 2 feature for evidence tracking.
- `self_service_guide_url`: Link to official government guide for self-filing. Phase 2 enhancement.
