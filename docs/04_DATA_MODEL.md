# Document 04 — Data Model
## Database Schema Design for the Compliance Knowledge System

---

## DESIGN PHILOSOPHY

### Static Master Data vs. Computed Instance Data

**Static master data** (the compliance library) lives in tables that are edited only when laws/notifications change.
- `compliance_master`
- `source_master`
- `compliance_source_link`
- `applicability_rule`
- `due_date_rule`
- `penalty_record`

**Instance data** (per business, per period) is computed from master data + business profile.
- `business_profile`
- `business_compliance_output`
- `computed_due_date`

This separation is architecturally critical. If a due date notification is updated in master data,
the instance outputs for all affected businesses can be recomputed automatically.

---

## TABLE 1 — compliance_master

The central record of every compliance obligation in the system.

```sql
compliance_master {

  -- Identity
  compliance_id           UUID PRIMARY KEY
  compliance_code         VARCHAR(50) UNIQUE NOT NULL
                          -- e.g., "GST_GSTR1_MONTHLY", "IT_TDS_DEPOSIT_MONTHLY",
                          --       "MCA_AOC4_ANNUAL", "EPF_ECR_MONTHLY"
  title                   VARCHAR(200) NOT NULL
  short_title             VARCHAR(100)
  
  -- Domain Classification
  domain                  ENUM (
                            'GST', 'INCOME_TAX', 'TDS', 'TCS',
                            'MCA_COMPANY', 'MCA_LLP', 'SECRETARIAL',
                            'EPF', 'ESI', 'PROFESSIONAL_TAX',
                            'SHOPS_ESTABLISHMENTS', 'FACTORIES',
                            'LABOUR_BONUS', 'LABOUR_GRATUITY',
                            'LABOUR_MINIMUM_WAGES', 'LABOUR_CONTRACT',
                            'FSSAI', 'MSME', 'CUSTOMS_IEC',
                            'ENVIRONMENT', 'BOOKS_RECORDS',
                            'AUDIT_STATUTORY', 'AUDIT_TAX',
                            'ADVANCE_TAX', 'OTHER'
                          )
  category                VARCHAR(100)
                          -- e.g., "Return Filing", "Tax Payment", "Registration",
                          --       "Governance", "Record Keeping", "Event-Based"
  subcategory             VARCHAR(100)
  
  -- Obligation Type
  obligation_type         ENUM (
                            'REGISTRATION',       -- one-time or renewal
                            'RETURN_FILING',      -- periodic government return
                            'TAX_PAYMENT',        -- tax/fee payment to government
                            'RECORD_KEEPING',     -- maintain registers/books
                            'GOVERNANCE',         -- meeting, resolution, approval
                            'EVENT_BASED',        -- triggered by specific event
                            'AUDIT',              -- audit or certification
                            'DISCLOSURE',         -- public disclosure requirement
                            'RENEWAL',            -- periodic renewal of license
                            'CERTIFICATE',        -- issuance of certificate to party
                            'INDICATOR'           -- flag only, no specific filing
                          )
  
  -- Frequency
  frequency_type          ENUM (
                            'ONE_TIME',
                            'MONTHLY',
                            'QUARTERLY',
                            'HALF_YEARLY',
                            'ANNUAL',
                            'EVENT_BASED',
                            'CONTINUOUS',         -- ongoing obligation, no single due date
                            'AS_APPLICABLE'
                          )
  
  -- Applicability Scope
  entity_types_applicable JSONB
                          -- Array: ["PROPRIETORSHIP","PARTNERSHIP","LLP",
                          --         "PRIVATE_LIMITED","PUBLIC_LIMITED","OPC","ALL"]
  
  activity_types_applicable JSONB
                          -- Array: ["SERVICE","TRADING","MANUFACTURING","MIXED","ALL"]
  
  geography_scope         ENUM ('CENTRAL', 'ALL_STATES', 'SPECIFIC_STATE', 'SPECIFIC_STATES')
  
  state_codes             TEXT[]
                          -- If geography_scope = SPECIFIC_STATE(S), list state codes
  
  -- Description
  description_plain       TEXT
                          -- Human-readable explanation of what this compliance is
  
  legal_basis_summary     TEXT
                          -- One-paragraph summary of the legal basis
  
  -- Applicability Logic
  applicability_rule_id   UUID FK -> applicability_rule.rule_id
                          -- Structured rule expression for programmatic evaluation
  
  -- Due Date
  due_date_rule_id        UUID FK -> due_date_rule.rule_id
                          -- If null, compliance is continuous or event-dependent
  
  -- Penalty / Criticality
  penalty_record_id       UUID FK -> penalty_record.penalty_id
  
  base_severity_score     SMALLINT (0-100)
                          -- Inherent severity; computed from penalty record
  severity_band           ENUM ('LOW','MODERATE','HIGH','SEVERE','CRITICAL')
  
  -- Dependencies
  depends_on_compliance   UUID[]
                          -- Compliance IDs that must be done before this one
                          -- e.g., GSTR-9 depends on GSTR-3B
  cascades_to_compliance  UUID[]
                          -- Compliance IDs that are affected if this is late
  
  -- State of Knowledge
  requires_human_review   BOOLEAN DEFAULT FALSE
                          -- True if professional judgment needed to determine applicability
  requires_threshold_check BOOLEAN DEFAULT FALSE
                          -- True if applicability depends on threshold to be verified
  state_specific_notes    TEXT
                          -- Notes on state-specific variations
  
  -- Versioning / Quality
  active_flag             BOOLEAN DEFAULT TRUE
  effective_from          DATE NOT NULL
  effective_to            DATE
                          -- Null if still active
  superseded_by           UUID FK -> compliance_master.compliance_id
  last_reviewed_at        TIMESTAMPTZ
  review_due_by           DATE
                          -- Max 90 days from last_reviewed_at
  
  created_at              TIMESTAMPTZ DEFAULT NOW()
  updated_at              TIMESTAMPTZ DEFAULT NOW()
}
```

---

## TABLE 2 — source_master

See [docs/03_SOURCE_STRATEGY.md](03_SOURCE_STRATEGY.md) for full field definitions.

```sql
source_master {
  source_id               UUID PRIMARY KEY
  source_code             VARCHAR(100) UNIQUE
  source_type             ENUM ('ACT','RULES','NOTIFICATION','CIRCULAR','GAZETTE',
                                'OFFICIAL_FAQ','PORTAL_GUIDANCE','PROFESSIONAL_BODY',
                                'OPERATIONAL_PRACTICE')
  source_priority         ENUM ('PRIMARY_STATUTE','SUBORDINATE_LEGISLATION',
                                'OFFICIAL_PORTAL','SECONDARY')
  is_primary_source       BOOLEAN
  authority               VARCHAR(200)
  act_name                VARCHAR(300)
  act_short_name          VARCHAR(100)
  section_rule_reference  VARCHAR(500)
  notification_number     VARCHAR(200)
  circular_number         VARCHAR(200)
  notification_date       DATE
  gazette_reference       VARCHAR(200)
  official_url            TEXT
  url_verified            BOOLEAN DEFAULT FALSE
  portal_url              TEXT
  version_effective_from  DATE
  version_effective_to    DATE
  is_currently_active     BOOLEAN DEFAULT TRUE
  superseded_by           UUID FK -> source_master.source_id
  supersedes              UUID FK -> source_master.source_id
  jurisdiction            ENUM ('CENTRAL','STATE','UT','SPECIFIC_STATE')
  jurisdiction_state      CHAR(2)
  portal_vs_statute_divergence  BOOLEAN DEFAULT FALSE
  portal_vs_statute_note        TEXT
  confidence_level        ENUM ('HIGH','MEDIUM','LOW')
  last_verified_on        DATE
  verified_by             VARCHAR(100)
  source_notes            TEXT
  created_at              TIMESTAMPTZ DEFAULT NOW()
  updated_at              TIMESTAMPTZ DEFAULT NOW()
}
```

---

## TABLE 3 — compliance_source_link

```sql
compliance_source_link {
  link_id                 UUID PRIMARY KEY
  compliance_id           UUID FK -> compliance_master.compliance_id
  source_id               UUID FK -> source_master.source_id
  source_role             ENUM ('PRIMARY_OBLIGATION','DUE_DATE_RULE',
                                'DUE_DATE_EXTENSION_OVERRIDE','PENALTY_RULE',
                                'THRESHOLD_RULE','RATE_RULE','OPERATIONAL_GUIDE',
                                'INTERPRETATION')
  is_currently_operative  BOOLEAN DEFAULT TRUE
  effective_from          DATE
  effective_to            DATE
  relevance_note          TEXT
  
  UNIQUE (compliance_id, source_id, source_role, effective_from)
}
```

---

## TABLE 4 — applicability_rule

Stores the structured rule expression used to evaluate whether a compliance applies
to a given business profile.

```sql
applicability_rule {
  rule_id                 UUID PRIMARY KEY
  rule_code               VARCHAR(100) UNIQUE
  rule_version            INTEGER DEFAULT 1
  
  -- The rule expression (see applicability_rule.schema.json)
  rule_expression         JSONB NOT NULL
  
  -- What entity/activity/threshold combinations this rule handles
  entity_types_handled    TEXT[]
  activity_types_handled  TEXT[]
  threshold_fields_used   TEXT[]
                          -- e.g., ["annual_turnover","employee_count","gst_registered"]
  
  expected_output_status  TEXT[]
                          -- Possible outputs this rule can produce
  
  needs_manual_override_flag BOOLEAN DEFAULT FALSE
  
  -- Human-readable version for debugging
  rule_description        TEXT
  
  confidence_output       ENUM ('HIGH','MEDIUM','LOW')
                          -- Max confidence this rule can produce given its completeness
  
  effective_from          DATE
  effective_to            DATE
  is_active               BOOLEAN DEFAULT TRUE
  created_at              TIMESTAMPTZ DEFAULT NOW()
  updated_at              TIMESTAMPTZ DEFAULT NOW()
}
```

---

## TABLE 5 — due_date_rule

Stores the computable due date formula for each recurring compliance.
See [docs/05_DUE_DATE_ENGINE.md](05_DUE_DATE_ENGINE.md) for full rule type definitions.

```sql
due_date_rule {
  rule_id                 UUID PRIMARY KEY
  rule_code               VARCHAR(100) UNIQUE
  rule_version            INTEGER DEFAULT 1
  
  -- Rule type drives which computation algorithm is used
  rule_type               ENUM (
                            'FIXED_ANNUAL',             -- Same day every year
                            'FIXED_IN_AY',              -- Fixed in Assessment Year
                            'OFFSET_FROM_PERIOD_END',   -- Nth day after period end
                            'OFFSET_FROM_FY_END',       -- Nth day after FY end
                            'OFFSET_FROM_AGM',          -- Nth day after AGM
                            'OFFSET_FROM_EVENT',        -- Nth day after event
                            'ADVANCE_TAX_INSTALLMENT',  -- Special advance tax rule
                            'REGISTRATION_RELATIVE',    -- Relative to reg date
                            'CONTINUOUS',               -- No single due date
                            'CUSTOM_EXPRESSION'         -- Complex rule in JSON
                          )
  
  frequency               ENUM ('ONE_TIME','MONTHLY','QUARTERLY','HALF_YEARLY',
                                'ANNUAL','EVENT_BASED','CONTINUOUS')
  
  -- For FIXED_ANNUAL
  fixed_day               SMALLINT    -- 1-31
  fixed_month             SMALLINT    -- 1-12
  
  -- For FIXED_IN_AY
  ay_fixed_day            SMALLINT
  ay_fixed_month          SMALLINT    -- Month in AY calendar
  
  -- For OFFSET_FROM_PERIOD_END
  period_type             ENUM ('CALENDAR_MONTH','FY_QUARTER','CALENDAR_QUARTER',
                                'HALF_YEAR','FINANCIAL_YEAR','CALENDAR_YEAR')
  offset_days             SMALLINT    -- Days after period end
  
  -- For quarterly, which quarters apply
  applicable_quarters     SMALLINT[]  -- [1,2,3,4] or subset
  
  -- For OFFSET_FROM_FY_END
  fy_end_offset_days      SMALLINT
  
  -- State-based variations (JSON array of {states: [...], offset_days: N})
  state_based_variation   BOOLEAN DEFAULT FALSE
  state_offset_rules      JSONB
  
  -- Working day adjustment
  working_day_rule        ENUM ('NONE','NEXT_WORKING_DAY','PREV_WORKING_DAY')
  
  -- Notification override support
  notification_override_possible  BOOLEAN DEFAULT TRUE
  active_override_source_id       UUID FK -> source_master.source_id
                                  -- If a notification is currently extending/changing date
  active_override_due_date        DATE
                                  -- The actual date per current override (if active)
  active_override_expires         DATE
  
  -- Human-readable description of the rule
  rule_description        TEXT
  rule_notes              TEXT        -- Edge cases, caveats
  
  -- Versioning
  effective_from          DATE
  effective_to            DATE
  superseded_by           UUID FK -> due_date_rule.rule_id
  is_active               BOOLEAN DEFAULT TRUE
  
  created_at              TIMESTAMPTZ DEFAULT NOW()
  updated_at              TIMESTAMPTZ DEFAULT NOW()
}
```

---

## TABLE 6 — penalty_record

```sql
penalty_record {
  penalty_id              UUID PRIMARY KEY
  compliance_id           UUID FK -> compliance_master.compliance_id
  
  -- Late Fee (statutory, per day or per filing)
  late_fee_per_day        NUMERIC(12,2)     -- ₹ per day
  late_fee_maximum        NUMERIC(12,2)     -- Cap on late fee
  late_fee_nil_return     NUMERIC(12,2)     -- Reduced rate for nil returns
  late_fee_nil_max        NUMERIC(12,2)
  late_fee_formula_notes  TEXT
  late_fee_source_id      UUID FK -> source_master.source_id
  
  -- Interest
  interest_rate_pa        NUMERIC(6,4)      -- % per annum
  interest_basis          TEXT              -- "on tax due", "on unpaid liability", etc.
  interest_source_id      UUID FK -> source_master.source_id
  
  -- Flat Penalty (min/max/fixed)
  flat_penalty_min        NUMERIC(12,2)
  flat_penalty_max        NUMERIC(12,2)
  flat_penalty_fixed      NUMERIC(12,2)     -- If exact fixed amount
  flat_penalty_formula    TEXT
  flat_penalty_source_id  UUID FK -> source_master.source_id
  
  -- Prosecution Risk
  prosecution_possible    BOOLEAN DEFAULT FALSE
  imprisonment_possible   BOOLEAN DEFAULT FALSE
  imprisonment_min_months SMALLINT
  imprisonment_max_months SMALLINT
  prosecution_notes       TEXT
  prosecution_source_id   UUID FK -> source_master.source_id
  
  -- Business/Compliance Impact
  causes_tax_disallowance     BOOLEAN DEFAULT FALSE
  disallowance_description    TEXT
  blocks_other_filings        BOOLEAN DEFAULT FALSE
  blocks_description          TEXT
  causes_registration_issue   BOOLEAN DEFAULT FALSE
  registration_impact_notes   TEXT
  
  -- Derived severity (computed from fields above; stored for performance)
  computed_base_score         SMALLINT (0-100)
  computed_severity_band      ENUM ('LOW','MODERATE','HIGH','SEVERE','CRITICAL')
  
  -- Source
  general_penalty_source_id   UUID FK -> source_master.source_id
  
  penalty_notes               TEXT
  
  effective_from              DATE
  effective_to                DATE
  is_active                   BOOLEAN DEFAULT TRUE
  created_at                  TIMESTAMPTZ DEFAULT NOW()
  updated_at                  TIMESTAMPTZ DEFAULT NOW()
}
```

---

## TABLE 7 — business_profile

The normalized representation of a business captured through the questionnaire.

```sql
business_profile {
  business_id             UUID PRIMARY KEY
  
  -- Owner / user link
  user_id                 UUID FK -> users.user_id
  profile_name            VARCHAR(200)   -- Display name
  
  -- Entity Identity
  entity_type             ENUM ('PROPRIETORSHIP','PARTNERSHIP','LLP',
                                'PRIVATE_LIMITED','PUBLIC_LIMITED','OPC',
                                'SECTION8_COMPANY','TRUST','OTHER')
  legal_name              VARCHAR(300)
  brand_name              VARCHAR(300)
  pan                     VARCHAR(10)
  
  -- Registration Details
  incorporation_date      DATE
  commencement_date       DATE
  cin_or_llpin            VARCHAR(25)    -- CIN for companies, LLPIN for LLP
  gstin                   VARCHAR(15)
  
  -- Financial Year
  fy_end_month            SMALLINT DEFAULT 3   -- 3 = March (standard Indian FY)
  
  -- Geography
  principal_state         CHAR(2)        -- ISO state code, e.g., "MH"
  number_of_states        SMALLINT
  state_codes_present     TEXT[]
  
  -- Activity
  activity_type           ENUM ('SERVICE','TRADING','MANUFACTURING','MIXED')
  sector                  VARCHAR(100)
  is_regulated_sector     BOOLEAN DEFAULT FALSE
  regulated_sector_name   VARCHAR(200)
  
  has_manufacturing       BOOLEAN DEFAULT FALSE
  uses_power_in_mfg       BOOLEAN DEFAULT FALSE
  has_food_business       BOOLEAN DEFAULT FALSE
  has_import_export       BOOLEAN DEFAULT FALSE
  has_ecommerce           BOOLEAN DEFAULT FALSE
  has_hazardous_material  BOOLEAN DEFAULT FALSE
  
  -- Ownership / Governance
  num_directors_or_partners SMALLINT
  has_foreign_director_partner BOOLEAN DEFAULT FALSE
  has_foreign_ownership   BOOLEAN DEFAULT FALSE
  paid_up_capital         NUMERIC(15,2)
  lp_contribution         NUMERIC(15,2)  -- For LLP
  has_appointed_auditor   BOOLEAN DEFAULT FALSE
  
  -- Tax Profile
  pan_obtained            BOOLEAN DEFAULT FALSE
  tan_obtained            BOOLEAN DEFAULT FALSE
  gst_registered          BOOLEAN DEFAULT FALSE
  gst_scheme              ENUM ('REGULAR','COMPOSITION','NOT_REGISTERED')
  gst_filing_frequency    ENUM ('MONTHLY','QUARTERLY')   -- For GSTR-3B / GSTR-1
  
  annual_turnover_current NUMERIC(15,2)  -- Actual if known
  annual_turnover_estimated NUMERIC(15,2) -- Estimated for current year
  turnover_band           ENUM ('BELOW_20L','20L_40L','40L_1CR','1CR_5CR',
                                '5CR_10CR','ABOVE_10CR')
  
  has_interstate_supply   BOOLEAN DEFAULT FALSE
  has_exports             BOOLEAN DEFAULT FALSE
  has_imports             BOOLEAN DEFAULT FALSE
  einvoicing_applicable   BOOLEAN
  
  -- TDS Profile
  makes_salary_payments   BOOLEAN DEFAULT FALSE
  makes_contractor_payments BOOLEAN DEFAULT FALSE
  makes_professional_fee_payments BOOLEAN DEFAULT FALSE
  makes_rent_payments     BOOLEAN DEFAULT FALSE
  tan_required_flag       BOOLEAN
  
  -- Employment Profile
  employee_count          SMALLINT
  employee_count_band     ENUM ('ZERO','1_9','10_19','20_49','50_PLUS')
  contract_worker_count   SMALLINT
  pf_registered           BOOLEAN DEFAULT FALSE
  esi_registered          BOOLEAN DEFAULT FALSE
  has_female_employees    BOOLEAN DEFAULT FALSE
  approximate_avg_salary  NUMERIC(10,2)
  
  -- Premises / Operations
  premise_type            TEXT[]    -- ["OFFICE","FACTORY","WAREHOUSE","SHOP"]
  num_locations           SMALLINT
  shops_est_registration  BOOLEAN DEFAULT FALSE
  factory_registration    BOOLEAN DEFAULT FALSE
  fssai_license           BOOLEAN DEFAULT FALSE
  
  -- Financial Reporting
  books_maintained        BOOLEAN DEFAULT FALSE
  audited_accounts_done   BOOLEAN DEFAULT FALSE
  statutory_audit_done    BOOLEAN DEFAULT FALSE
  tax_audit_done          BOOLEAN DEFAULT FALSE
  
  -- Pending Event-Based Changes
  has_pending_director_changes   BOOLEAN DEFAULT FALSE
  has_pending_office_changes     BOOLEAN DEFAULT FALSE
  has_pending_capital_changes    BOOLEAN DEFAULT FALSE
  has_started_exports_recently   BOOLEAN DEFAULT FALSE
  
  -- Profile Quality
  profile_completeness_pct SMALLINT      -- 0-100
  last_answered_at         TIMESTAMPTZ
  
  created_at              TIMESTAMPTZ DEFAULT NOW()
  updated_at              TIMESTAMPTZ DEFAULT NOW()
}
```

---

## TABLE 8 — business_compliance_output

The computed applicability and due date output for a specific business and compliance item.
This is re-derived whenever the business profile or master data changes.

```sql
business_compliance_output {
  output_id               UUID PRIMARY KEY
  business_id             UUID FK -> business_profile.business_id
  compliance_id           UUID FK -> compliance_master.compliance_id
  
  -- Applicability Decision
  applicability_status    ENUM (
                            'APPLICABLE',
                            'LIKELY_APPLICABLE',
                            'CHECK_THRESHOLD',
                            'EVENT_TRIGGERED',
                            'STATE_SPECIFIC',
                            'RECOMMENDED',
                            'NOT_APPLICABLE',
                            'INSUFFICIENT_DATA',
                            'HUMAN_REVIEW_REQUIRED',
                            'FUTURE_TRIGGER'
                          )
  applicability_confidence ENUM ('HIGH','MEDIUM','LOW')
  why_it_applies          TEXT
  why_it_may_not_apply    TEXT
  missing_inputs          TEXT[]        -- Fields that would improve the decision
  threshold_basis         TEXT          -- Which threshold drove the decision
  state_dependency_basis  TEXT
  human_verification_required BOOLEAN DEFAULT FALSE
  
  -- Due Date (latest / current period)
  current_period_start    DATE
  current_period_end      DATE
  filing_window_opens     DATE
  computed_due_date       DATE          -- The actual computed due date
  financial_year_label    VARCHAR(20)   -- "FY2025-26"
  period_label            VARCHAR(50)   -- "June 2025", "Q1 FY2025-26", etc.
  
  -- Status
  is_overdue              BOOLEAN
  overdue_days            SMALLINT
  due_in_days             SMALLINT      -- Positive = days remaining, null if overdue
  
  next_due_date           DATE          -- Next period's due date
  next_period_label       VARCHAR(50)
  
  -- Severity (at time of computation)
  base_severity_score     SMALLINT
  dynamic_severity_score  SMALLINT      -- Base + lateness escalation
  combined_severity_score SMALLINT
  severity_band           ENUM ('LOW','MODERATE','HIGH','SEVERE','CRITICAL')
  color_code              VARCHAR(7)    -- Hex color e.g., "#D32F2F"
  
  -- Source snapshot
  source_snapshot_version VARCHAR(50)   -- Version of master data used
  
  -- Computation metadata
  generated_at            TIMESTAMPTZ DEFAULT NOW()
  is_stale                BOOLEAN DEFAULT FALSE  -- True if master data updated since
  stale_since             TIMESTAMPTZ
}
```

---

## TABLE 9 — notification_extension

Stores due date extensions from government notifications, allowing override of base rules.

```sql
notification_extension {
  extension_id            UUID PRIMARY KEY
  compliance_id           UUID FK -> compliance_master.compliance_id
  source_id               UUID FK -> source_master.source_id   -- The notification
  
  extended_due_date       DATE
  original_due_date       DATE
  period_affected         VARCHAR(100)    -- e.g., "March 2021 GSTR-3B"
  period_start            DATE
  period_end              DATE
  
  applicable_to           TEXT            -- Which taxpayers this applies to
  conditions              TEXT
  is_currently_active     BOOLEAN DEFAULT TRUE
  expires_after           DATE            -- When this extension itself expires
  
  notes                   TEXT
  created_at              TIMESTAMPTZ DEFAULT NOW()
}
```

---

## KEY DESIGN DECISIONS

### Decision D1: JSONB for Rule Expressions

Applicability rules and due date state variations are stored as JSONB.
This enables:
- Querying rules from the database without code changes
- Updating rules without a code deployment
- Version-controlled rule history

### Decision D2: Computed Severity Is Stored, Not Only Calculated

`computed_base_score` in `penalty_record` and `combined_severity_score` in `business_compliance_output` are stored even though they could be recalculated. This is for:
- Dashboard performance (avoid full recompute on every page load)
- Historical audit trail of what severity was shown at what time
- Stale flag to trigger recomputation when source data changes

### Decision D3: Separation of State Data

State-specific compliances (Professional Tax, Shops & Establishments, Factories) are stored as
individual compliance records with `geography_scope = SPECIFIC_STATE` and the relevant state codes.
This means 10 states × 5 state-specific compliances = 50 separate compliance records, each with
their own source links. This is verbose but necessary for correctness.

### Decision D4: Compliance "Indicator" Type

Some compliance records have `obligation_type = INDICATOR`. These are not actionable filings.
They are awareness flags: "MSME threshold likely crossed — consider Udyam registration" or
"e-invoicing threshold appears to be crossed — verify IRP registration."
They show up in the dashboard but don't generate calendar due dates.

### Decision D5: Due Date Rule vs. Notification Extension

Base due date rules are stable (set by the Act or Rules).
Notification extensions are time-limited overrides.
They must never be merged. A `notification_extension` record linked to a base `due_date_rule`
is the correct model. This allows the system to correctly revert to base rules when extensions expire.
