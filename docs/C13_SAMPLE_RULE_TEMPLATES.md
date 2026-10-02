# C13 — Sample Rule Templates
## Four Illustrative Compliance Rule Documentation Templates

---

## 1. Objective

Provide four illustrative rule documentation templates drawn from different compliance domains, obligation types, and complexity levels. Each template demonstrates how the C1 schema fields, C3 canonical sentence, C4 applicability encoding, C5 due-date encoding, and C6 consequence encoding work together for a complete rule.

These templates are documentation examples only. They are NOT final library entries. They must not be treated as ready-to-activate records. Field values shown are illustrative and are subject to primary source verification before any record based on these templates is activated.

---

## 2. Why These Four Rules

The four templates cover the breadth of the library's scope:

| Template | Rule | Why Selected |
|----------|------|-------------|
| T1 | GSTR-3B Monthly Return (GST domain) | High-volume, multi-condition, state-based variation, complex applicability |
| T2 | DPT-3 Annual Return (MCA domain) | Universal company applicability, simple fixed due date, confirmed from research (B9) |
| T3 | Payment of Bonus — Annual Payment (Labour domain) | Clear threshold-gated rule, confirmed from research (B7), high-certainty encoding |
| T4 | EPF ECR Monthly Deposit (Labour/EPF domain) | Monthly recurring, registration-preconditioned, two-part obligation (filing + payment) |

---

## 3. Template Format

Each template presents:
1. The canonical obligation sentence
2. Key field values in annotated table form
3. Applicability rule expression (documentation form per C4)
4. Due-date rule encoding (per C5)
5. Consequence summary (per C6)
6. Trust and lifecycle state at time of template creation
7. Notes on what must be verified before activation

---

## TEMPLATE T1 — GSTR-3B Monthly Return Filing (Regular Scheme, Monthly Filers)

**Compliance Code (proposed):** `GST_GSTR3B_MONTHLY_REGULAR`
**Illustration Status:** Documentation example — fields require primary source verification before activation

---

### Canonical Obligation Sentence

```
SUBJECT:     Every GST-registered business under the regular scheme
             with monthly filing frequency
MODAL:       must
ACTION:      file Form GSTR-3B (monthly summary return) and
             pay the net GST liability shown in the return
AUTHORITY:   on the GST portal (gst.gov.in)
BY WHEN:     by the 20th of the calendar month following the return period
HOW OFTEN:   every calendar month
IF:          gst_registered = true
             AND gst_scheme = REGULAR
             AND gst_filing_frequency = MONTHLY
UNLESS:      no statutory carve-out for regular monthly GSTR-3B filers
THRESHOLDS:  QRMP scheme applies to taxpayers with AATO ≤ ₹5 Cr who
             opt for quarterly — those taxpayers are a SEPARATE compliance
             record (GST_GSTR3B_QRMP_QUARTERLY)
CONSEQUENCES:
             Late fee: ₹50/day (max ₹10,000); nil return: ₹20/day (max ₹500)
             Interest: 18% p.a. on unpaid tax liability
SOURCE:      Section 39(1), CGST Act, 2017
             Rule 61(1), CGST Rules, 2017
```

---

### Key Field Values

| Field | Illustrative Value | Notes |
|-------|-------------------|-------|
| `compliance_code` | `GST_GSTR3B_MONTHLY_REGULAR` | Proposed; Library Owner confirmation required |
| `title` | GSTR-3B Monthly Return Filing — Regular Scheme | |
| `short_title` | GSTR-3B Monthly | |
| `domain` | `GST` | |
| `category` | Return Filing | |
| `obligation_type` | `RETURN_FILING` | |
| `frequency_type` | `MONTHLY` | |
| `jurisdiction` | `CENTRAL` | Central law (CGST Act); applicable across India |
| `entity_types_applicable` | `["ALL"]` | No entity type restriction in the provision |
| `governing_act` | Central Goods and Services Tax Act, 2017 | |
| `primary_provision_reference` | Section 39(1) | |
| `operative_legal_text` | "Every registered person shall furnish, for every calendar month or part thereof, a return, electronically, of outward supplies of goods or services or both effected during such month..." | Verbatim from Section 39(1) — verify from current official text |
| `requires_registration_precondition` | `true` | Requires GST registration under REGULAR scheme |
| `registration_precondition_detail` | "Active GSTIN under regular scheme with monthly filing frequency" | |
| `due_date_determinability` | `COMPUTABLE` | Fixed offset from period end |
| `due_date_formula_plain` | "20th of the calendar month immediately following the return period." | |
| `financial_year_dependency` | `false` | Monthly cycle does not depend on FY |
| `extension_possible` | `true` | CBIC regularly issues due date extensions |
| `prosecution_possible` | `false` | Routine late filing does not trigger prosecution |
| `requires_human_review` | `false` | Standard rule, well-sourced |
| `interpretation_ambiguity_flag` | `false` | Base obligation is clear; staggering applies only to QRMP, not monthly |
| `source_confidence_level` | `HIGH` (after source retrieval) | Section 39 is a primary and stable provision |

---

### Applicability Rule Expression (Documentation Form)

```
AND {
  CONDITION { field: gst_registered, operator: EQ, value: true, confidence: HIGH }
  CONDITION { field: gst_scheme, operator: EQ, value: "REGULAR", confidence: HIGH }
  CONDITION { field: gst_filing_frequency, operator: EQ, value: "MONTHLY", confidence: HIGH }
}
```

**Evaluation examples:**
- GST-registered, regular scheme, monthly → APPLICABLE (HIGH confidence)
- GST-registered, QRMP, quarterly → NOT_APPLICABLE (use GST_GSTR3B_QRMP_QUARTERLY instead)
- Not GST-registered → NOT_APPLICABLE
- gst_filing_frequency = null (unanswered) → INSUFFICIENT_DATA

---

### Due Date Rule Encoding (Documentation Form)

```
rule_type: OFFSET_FROM_PERIOD_END
period_type: CALENDAR_MONTH
offset_days: 20
state_based_variation: false
working_day_rule: NEXT_WORKING_DAY
```

**Sample computation:** For return period July 2025 → end of period: July 31, 2025 → base due date: August 20, 2025. If August 20 falls on a Sunday → next working day: August 21, 2025.

---

### Consequence Summary

"Late filing of GSTR-3B attracts a late fee of ₹50 per day (₹20 per day for nil returns), subject to a maximum of ₹10,000 per return under Section 47 of the CGST Act, 2017. Additionally, interest at 18% per annum accrues on any unpaid tax liability from the due date until actual payment under Section 50 of the CGST Act, 2017. Non-filing can result in suspension of GST registration under Section 29 of the CGST Act."

**Penalty record fields (illustrative):**
- `late_fee_per_day`: 50
- `late_fee_maximum`: 10,000
- `late_fee_nil_return_per_day`: 20
- `late_fee_nil_return_maximum`: 500
- `interest_rate_pa`: 18.00
- `interest_basis`: "on unpaid tax liability as on due date"
- `causes_registration_risk`: true
- `registration_risk_description`: "GST registration may be suspended under Section 29 for consistent non-filing"
- `base_severity_score`: ~50 (HIGH band) — to be confirmed per C6 formula

---

### Population Notes

**Before activation, confirm:**
1. Current Section 39(1) text from cbic-gst.gov.in or IndiaCode
2. Rule 61(1) CGST Rules text confirming 20th-of-month due date
3. Section 47 text for late fee amounts (confirm ₹50/day and ₹10,000 cap are still current)
4. Section 50 text for interest rate (confirm 18% p.a.)
5. Whether any notifications have modified the base 20th due date for monthly filers

---

## TEMPLATE T2 — DPT-3 Annual Return (Companies — All, Non-Government)

**Compliance Code (proposed):** `MCA_DPT3_ANNUAL`
**Illustration Status:** Documentation example — resolved as ready-to-populate per doc 23 B9; requires final source retrieval and QA

---

### Canonical Obligation Sentence

```
SUBJECT:     Every company other than a Government company
MODAL:       shall
ACTION:      file Form DPT-3 with the Registrar of Companies reporting
             details of money/loans received by the company that are not
             considered deposits (under Deposit Rules Rule 2(1)(c))
AUTHORITY:   MCA21 portal (mca.gov.in)
BY WHEN:     on or before the 30th day of June of every year
HOW OFTEN:   annually
IF:          entity_type IN [PRIVATE_LIMITED, PUBLIC_LIMITED, OPC, SECTION8_COMPANY]
UNLESS:      entity_type = GOVERNMENT_COMPANY (explicitly excluded by Rule 16A(3))
THRESHOLDS:  No size threshold — applies to ALL companies regardless of size
CONSEQUENCES:
             Non-filing: penalty under Section 450 / 451, Companies Act, 2013
             General penalty: ₹10,000 + ₹100/day for continuing default
SOURCE:      Rule 16A(3), Companies (Acceptance of Deposits) Amendment Rules, 2019
             MCA Notification dated 22.01.2019
```

---

### Key Field Values

| Field | Illustrative Value | Notes |
|-------|-------------------|-------|
| `compliance_code` | `MCA_DPT3_ANNUAL` | |
| `title` | DPT-3: Annual Return of Money Received Not Considered as Deposit | |
| `short_title` | DPT-3 Annual | |
| `domain` | `MCA_COMPANY` | |
| `category` | Disclosure | |
| `obligation_type` | `RETURN_FILING` | Disclosure/return to ROC |
| `frequency_type` | `ANNUAL` | |
| `jurisdiction` | `CENTRAL` | Companies Act — central legislation |
| `entity_types_applicable` | `["PRIVATE_LIMITED", "PUBLIC_LIMITED", "OPC", "SECTION8_COMPANY"]` | NOT LLP, NOT PROPRIETORSHIP, NOT PARTNERSHIP |
| `governing_act` | Companies Act, 2013 | |
| `primary_provision_reference` | Rule 16A(3), Companies (Acceptance of Deposits) Amendment Rules, 2019 | Rules are subordinate legislation under Companies Act — primary source |
| `exemption_description` | "Government companies are explicitly excluded per Rule 16A(3) text: 'Every company, other than Government company'" | |
| `due_date_determinability` | `COMPUTABLE` | |
| `due_date_formula_plain` | "On or before June 30 of each year, covering outstanding amounts as of March 31." | |
| `source_confidence_level` | `HIGH` (after rule retrieval) | Rule 16A(3) is direct and specific |
| `interpretation_ambiguity_flag` | `true` | NIL filing question is ambiguous (see B9) |
| `interpretation_notes` | "Rule 16A(3) requires filing 'in respect of details of money or loan received...not considered as deposits.' A strict textual reading could be interpreted to mean the obligation only arises if such amounts exist. MCA portal practice accepts NIL filings. Most practitioners recommend filing NIL. The system defaults to treating DPT-3 as APPLICABLE to all active non-government companies, with a note that NIL filing is acceptable if no reportable amounts exist." | |

---

### Applicability Rule Expression (Documentation Form)

```
AND {
  CONDITION {
    field: entity_type,
    operator: IN,
    values: ["PRIVATE_LIMITED", "PUBLIC_LIMITED", "OPC", "SECTION8_COMPANY"],
    confidence: HIGH
  }
  NOT_APPLICABLE_IF {
    conditions: [
      CONDITION { field: entity_type, operator: EQ, value: "GOVERNMENT_COMPANY" }
    ]
    reason: "Government companies explicitly excluded by Rule 16A(3)"
  }
}
```

---

### Due Date Rule Encoding

```
rule_type: FIXED_ANNUAL
fixed_day: 30
fixed_month: 6  (June)
year_context: AFTER_FY_END_YEAR
working_day_rule: NEXT_WORKING_DAY
```

**Sample computation:** For FY2024-25 (ending March 31, 2025) → due date: June 30, 2025.

---

### Consequence Summary

"Non-filing of DPT-3 attracts a general penalty under Section 450 of the Companies Act, 2013: ₹10,000 for the company and every officer in default, plus ₹100 per day for each day the default continues."

---

## TEMPLATE T3 — Statutory Bonus Payment (Payment of Bonus Act)

**Compliance Code (proposed):** `LABOUR_BONUS_PAYMENT_ANNUAL`
**Illustration Status:** Documentation example — resolved as ready-to-populate per doc 23 B7; HIGH confidence

---

### Canonical Obligation Sentence

```
SUBJECT:     Every employer covered by the Payment of Bonus Act, 1965
             (establishment employing 20 or more persons)
MODAL:       shall
ACTION:      pay annual bonus in cash to eligible employees
             (employees drawing salary/wages ≤ ₹21,000/month)
             Minimum bonus: 8.33% of salary (or ₹100, whichever higher)
             Maximum bonus: 20% of salary
             Computation basis: salary capped at ₹7,000/month or MW (whichever higher)
BY WHEN:     within eight months from the close of the accounting year
             = November 30 for standard April–March financial year businesses
HOW OFTEN:   annually
IF:          employee_count >= 20
             AND makes_salary_payments = true
UNLESS:      No obligation if employer's allocable surplus is nil (Section 10 proviso),
             BUT minimum bonus under Section 10 is payable irrespective of profit/loss
             (Section 10 itself guarantees minimum 8.33% regardless of profits)
THRESHOLDS:  Establishment employing ≥ 20 persons on any day during the accounting year
             Employee salary ≤ ₹21,000/month to be eligible for bonus
CONSEQUENCES:
             Section 28: Failure to pay bonus = offence punishable with
             imprisonment up to 6 months, or fine, or both
SOURCE:      Section 19(1)(b), Payment of Bonus Act, 1965
             Section 1(3)(b) — establishment threshold
             Section 2(13) — employee salary eligibility
             Section 10 — minimum bonus rate
             Section 28 — penalty provision
```

---

### Key Field Values

| Field | Illustrative Value | Notes |
|-------|-------------------|-------|
| `compliance_code` | `LABOUR_BONUS_PAYMENT_ANNUAL` | |
| `title` | Annual Statutory Bonus Payment to Employees | |
| `short_title` | Bonus Payment (Nov 30) | |
| `domain` | `LABOUR_BONUS` | |
| `category` | Tax Payment | (Payment obligation — to employees, not government) |
| `obligation_type` | `TAX_PAYMENT` | Closest enum; or EVENT_BASED may be discussed — but it is annual, not event-based |
| `frequency_type` | `ANNUAL` | |
| `entity_types_applicable` | `["ALL"]` | Payment of Bonus Act applies to all legal forms that constitute an "establishment" |
| `governing_act` | Payment of Bonus Act, 1965 | |
| `primary_provision_reference` | Section 19(1)(b) | |
| `operative_legal_text` | "All amounts payable to an employee by way of bonus under this Act shall be paid in cash by his employer...in any other case, within eight months from the close of the accounting year." | Verbatim from Section 19(1)(b) |
| `due_date_determinability` | `COMPUTABLE` | Fixed annual date |
| `due_date_formula_plain` | "Within eight months from the close of the accounting year. For businesses following April–March financial year: November 30 of the same year." | |
| `extension_possible` | `true` | Section 19 proviso allows government extension |
| `prosecution_possible` | `true` | Section 28 permits imprisonment |
| `source_confidence_level` | `HIGH` | Direct statute text confirmed |
| `interpretation_ambiguity_flag` | `false` | Due date is clear from statute text |

---

### Applicability Rule Expression (Documentation Form)

```
AND {
  THRESHOLD {
    field: employee_count,
    operator: GTE,
    value: 20,
    band_field: employee_count_band,
    band_values_above_threshold: ["20_49", "50_PLUS"],
    band_values_ambiguous: ["10_19"],
    confidence_if_exact: HIGH,
    confidence_if_band_above: HIGH,
    confidence_if_band_ambiguous: MEDIUM
  }
  CONDITION { field: makes_salary_payments, operator: EQ, value: true, confidence: HIGH }
}
```

**Evaluation examples:**
- 25 employees, pays salaries → APPLICABLE (HIGH)
- 15 employees, pays salaries → CHECK_THRESHOLD ("Check if you have reached 20 employees at any point in the year")
- 5 employees → NOT_APPLICABLE

---

### Due Date Rule Encoding

```
rule_type: FIXED_ANNUAL
fixed_day: 30
fixed_month: 11  (November)
year_context: AFTER_FY_END_YEAR
working_day_rule: NEXT_WORKING_DAY
```

**Sample computation:** FY2024-25 ends March 31, 2025 → bonus due by November 30, 2025.

---

### Consequence Summary

"Failure to pay statutory bonus within the required period is an offence under Section 28 of the Payment of Bonus Act, 1965, punishable with imprisonment of up to six months, or fine, or both. Prosecution is available but is typically pursued for willful non-payment rather than administrative delay. The minimum bonus of 8.33% is payable regardless of whether the establishment made a profit or loss."

---

## TEMPLATE T4 — EPF ECR Monthly Deposit

**Compliance Code (proposed):** `EPF_ECR_DEPOSIT_MONTHLY`
**Illustration Status:** Documentation example — illustrative; requires primary source verification

---

### Canonical Obligation Sentence

```
SUBJECT:     Every employer registered with EPFO
             (establishments employing 20 or more persons, or voluntarily registered)
MODAL:       must
ACTION:      submit the monthly Electronic Challan cum Return (ECR)
             reporting employee-wise PF contribution details
             AND remit the total PF contribution to EPFO
             (employer share: 12% of basic wages, employee share: 12% of basic wages,
             plus EDLI and admin charges)
AUTHORITY:   EPFO portal (epfindia.gov.in) and banking channel
BY WHEN:     on or before the 15th of the calendar month following the
             contribution month
HOW OFTEN:   every calendar month
IF:          pf_registered = true
UNLESS:      No contribution required for months where no wages are paid
THRESHOLDS:  EPF Act threshold: establishments employing ≥ 20 persons on any day.
             Basic wage cap for PF purposes: ₹15,000/month per employee
             (employer may contribute on actual salary beyond cap — at employer discretion)
CONSEQUENCES:
             Non/late deposit: interest at 12% p.a. (Paragraph 36 EPF Scheme 1952)
             Penalty: damages under Section 14B EPF Act:
             0–2 months delay: 5% p.a.; 2–4 months: 10% p.a.; >4 months: 25% p.a.
             Prosecution under Section 14(1A): imprisonment up to 3 years + fine
SOURCE:      Employees' Provident Funds and Miscellaneous Provisions Act, 1952
             EPF Scheme, 1952 — Paragraphs 32–36 (contribution rates and due dates)
             Section 14B (damages for default)
             Section 1(3)(a) (20-employee threshold)
```

---

### Key Field Values

| Field | Illustrative Value | Notes |
|-------|-------------------|-------|
| `compliance_code` | `EPF_ECR_DEPOSIT_MONTHLY` | Note: consider splitting into EPF_ECR_FILING (return) and EPF_CONTRIBUTION_DEPOSIT (payment) per P2 of C3 — one provision, two distinct obligations |
| `title` | EPF Monthly ECR Filing and Contribution Deposit | Combined here for template; consider splitting |
| `domain` | `EPF` | |
| `obligation_type` | `RETURN_FILING` | For the ECR component; `TAX_PAYMENT` for the deposit |
| `frequency_type` | `MONTHLY` | |
| `entity_types_applicable` | `["ALL"]` | EPF Act applies to all establishment types |
| `governing_act` | Employees' Provident Funds and Miscellaneous Provisions Act, 1952 | |
| `primary_provision_reference` | EPF Scheme, 1952 — Paragraph 36 (for deposit due date) | |
| `requires_registration_precondition` | `true` | Applies only to EPFO-registered establishments |
| `registration_precondition_detail` | "Requires active EPFO registration (employer PF establishment code)" | |
| `due_date_determinability` | `COMPUTABLE` | |
| `due_date_formula_plain` | "On or before the 15th of the calendar month following the month in which contributions were deducted." | |
| `prosecution_possible` | `true` | Section 14(1A) — imprisonment up to 3 years |
| `source_confidence_level` | `HIGH` (after source retrieval) | Core EPF Act provisions are stable |
| `interpretation_ambiguity_flag` | `false` | Core obligation and due date are clear |
| `requires_human_review` | `false` | Standard EPF compliance — well-understood |

---

### Applicability Rule Expression (Documentation Form)

```
AND {
  CONDITION { field: pf_registered, operator: EQ, value: true, confidence: HIGH }
}
```

**Note on pre-registration check:** A separate `EPF_REGISTRATION_MANDATORY` compliance record handles the obligation to register when the establishment first crosses the 20-employee threshold. The monthly ECR record applies only to already-registered establishments. The check for whether an unregistered establishment should register is a separate applicability rule.

---

### Due Date Rule Encoding

```
rule_type: OFFSET_FROM_PERIOD_END
period_type: CALENDAR_MONTH
offset_days: 15
state_based_variation: false
working_day_rule: NEXT_WORKING_DAY
```

**Sample computation:** For September 2025 contributions → due by October 15, 2025.

---

### Consequence Summary

"Non-payment or delayed deposit of EPF contributions attracts interest at 12% per annum under Paragraph 36 of the EPF Scheme, 1952. Additionally, damages under Section 14B are levied at a rate depending on the delay period: 5% p.a. for delay up to 2 months, 10% p.a. for delay of 2–4 months, and 25% p.a. for delays exceeding 4 months. Prosecution under Section 14(1A) is available, which may result in imprisonment for up to 3 years and fine. Prosecution is typically reserved for willful default rather than administrative delay."

---

## 5. What These Templates Must NOT Be Used For

**Do not activate these templates directly.** Each template contains illustrative field values that have not been finalized through the Phase 2 (source retrieval) and Phase 5 (domain review) steps of the C10 SOP. The following fields in particular require verification before any template-based record is activated:

- `operative_legal_text` — must be copied verbatim from the actual current source text
- `primary_provision_reference` — must be confirmed against the current in-force Act/Rules
- Penalty amounts in `penalty_record` fields — must be confirmed from current sources
- `late_fee_per_day`, `late_fee_maximum`, `interest_rate_pa` — confirm rates are current
- State groupings (T1) — confirm QRMP state groups from Notification 84/2020-CT
- `base_severity_score` — must be computed from confirmed penalty data per C6 formula

---

## 6. What Should Be Deferred

**Populating all 40–60 MVP rules** from these templates alone would be insufficient. These four templates cover GST, MCA, Labour (Bonus), and EPF. Additional templates should be developed for: TDS deposit and return, Income Tax advance payment, MCA company filings (AOC-4, MGT-7), LLP annual filings, ESI deposit, and state-specific rules. These are not created here to avoid generating what could be mistaken for validated records.

**State-specific rule templates** (PT, Shops & Establishments) should be created after Phase 2 state research is completed, as the state-specific field variations are substantial and cannot be illustrated without confirmed state source data.

---

## 7. Recommended Conclusion

These four templates demonstrate that the documentation standards defined in C1–C7 are workable for rules of varying complexity. The GSTR-3B template shows how multi-condition applicability and state-based due dates are handled. The DPT-3 template shows how a universal-applicability, fixed-date rule with a known ambiguity (NIL filing) is represented. The Bonus template shows how a threshold-gated, prosecution-risk rule is encoded cleanly. The EPF template shows how a registration-preconditioned monthly deposit rule is structured.

A Library Populator who can accurately populate these four templates, with confirmed sources, has demonstrated readiness for the full library population work.
