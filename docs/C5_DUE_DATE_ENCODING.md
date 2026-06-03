# C5 — Due-Date Encoding Framework
## Complete Classification and Encoding Standard for Timing Obligations

---

## 1. Objective

Define the exhaustive classification of due-date patterns found in Indian compliance law and specify the canonical encoding structure for each pattern. Every timing obligation in the master library must be classifiable into one of the defined rule types and expressible using the corresponding encoding.

---

## 2. Why It Matters to the Compliance Engine

The due-date computation layer is the mechanism by which static master-library rules produce actual calendar dates for a specific business at a specific point in time. A due-date rule that is vaguely defined produces incorrect calendar outputs. A rule classified under the wrong type is computed via the wrong algorithm. The encoding standard here ensures that every due-date rule is both semantically correct and computationally deterministic.

---

## 3. Design Principles

**P1 — Determinism.** Given the same inputs (business profile + current date + library version), the same due date must always be produced. No randomness, no ambiguity in computation.

**P2 — Source-anchored.** Every due-date rule must cite the provision from which the timing obligation is derived. Due dates not traceable to a source are not encodeable.

**P3 — Override separation.** Statutory due dates and notification-based extensions are stored separately. The base rule is never modified for temporary extensions. Extensions are applied as overlays at computation time.

**P4 — Expressibility over approximation.** If a due date cannot be expressed precisely in the defined rule types, use `PERIOD_UNKNOWN` and note the exact statutory language — do not approximate.

---

## 4. Complete Due-Date Rule Type Classification

### Type 1: FIXED_ANNUAL

**Definition:** The due date falls on a fixed day and month in a specified calendar-year context every year. The date does not vary by the business's return period, AGM date, or any other variable.

**Year Context Options:**

| Context | Meaning | Example |
|---------|---------|---------|
| `CURRENT_FY_YEAR` | Within the financial year itself (April–March) | Advance tax Q1: June 15 of current FY |
| `AFTER_FY_END_YEAR` | In the calendar year after the FY ends (i.e., the following calendar year) | LLP Form 11: May 30 (after March FY end, so in the same calendar year as FY end) |
| `ASSESSMENT_YEAR` | In the AY year (FY+1 calendar year) | ITR: July 31 of AY (year after FY) |

**Encoding fields:**
```
rule_type: FIXED_ANNUAL
fixed_day: <1–31>
fixed_month: <1–12>
year_context: CURRENT_FY_YEAR | AFTER_FY_END_YEAR | ASSESSMENT_YEAR
```

**Computation:** Determine the correct calendar year from year_context, then construct the date from fixed_month and fixed_day. Apply working-day adjustment if applicable.

**Examples:**

| Compliance | Day | Month | Year Context |
|-----------|-----|-------|-------------|
| Advance Tax Q1 | 15 | 6 (June) | CURRENT_FY_YEAR |
| Advance Tax Q4 | 15 | 3 (March) | CURRENT_FY_YEAR |
| GSTR-4 (Composition annual) | 30 | 4 (April) | AFTER_FY_END_YEAR |
| LLP Form 11 (Annual Return) | 30 | 5 (May) | AFTER_FY_END_YEAR |
| LLP Form 8 (SAS) | 30 | 10 (October) | AFTER_FY_END_YEAR |
| ITR (non-audit) | 31 | 7 (July) | ASSESSMENT_YEAR |
| ITR (audit) | 31 | 10 (October) | ASSESSMENT_YEAR |
| Tax Audit Report | 30 | 9 (September) | ASSESSMENT_YEAR |
| DPT-3 | 30 | 6 (June) | AFTER_FY_END_YEAR |
| DIR-3 KYC | 30 | 9 (September) | AFTER_FY_END_YEAR |
| Payment of Bonus | 30 | 11 (November) | AFTER_FY_END_YEAR |
| GSTR-9 Annual Return | 31 | 12 (December) | AFTER_FY_END_YEAR |
| MSME Form I (H1: Apr-Sep) | 31 | 10 (October) | CURRENT_FY_YEAR |
| MSME Form I (H2: Oct-Mar) | 30 | 4 (April) | AFTER_FY_END_YEAR |

---

### Type 2: OFFSET_FROM_PERIOD_END

**Definition:** The due date is N calendar days after the end of a recurring period (month, quarter, or half-year).

**Encoding fields:**
```
rule_type: OFFSET_FROM_PERIOD_END
period_type: CALENDAR_MONTH | FY_QUARTER | CALENDAR_HALF_YEAR
offset_days: <positive integer>
state_based_variation: true | false
state_offset_rules: [{ states: [...], offset_days: N }, ...]  (if state_based_variation = true)
special_march_rule: { override_day: N, override_month: M }    (if March period has different rule)
working_day_rule: NEXT_WORKING_DAY | NONE
```

**Computation:** End of period + offset_days = raw due date. Apply state variation if applicable. Apply working-day adjustment. Apply special_march_rule override for March period if defined.

**Examples:**

| Compliance | Period Type | Offset | State Variation | March Override |
|-----------|-------------|--------|----------------|----------------|
| GSTR-3B Monthly (large) | CALENDAR_MONTH | 20 | None | None |
| GSTR-3B Quarterly QRMP (Group A) | FY_QUARTER | 22 days from quarter-end month | Group A states | None |
| GSTR-1 Monthly | CALENDAR_MONTH | 11 | None | None |
| GSTR-1 Quarterly (QRMP) | FY_QUARTER | 13 days from quarter-end month | None | None |
| TDS Deposit | CALENDAR_MONTH | 7 | None | Yes: April 30 for March |
| EPF ECR Deposit | CALENDAR_MONTH | 15 | None | None |
| ESI Deposit | CALENDAR_MONTH | 15 | None | None |
| CMP-08 (Composition quarterly) | FY_QUARTER | 18 days from quarter-end month | None | None |

**March override for TDS deposit:**
TDS deducted in March is due by April 30 (not March + 7 = April 7). This is encoded as a `special_march_rule` that overrides the standard offset for the March period.

```
special_march_rule: {
  override_day: 30,
  override_month: 4  (April)
}
```

---

### Type 3: OFFSET_FROM_FY_END

**Definition:** The due date is N days after the end of the financial year (March 31). Used when the timing language says "within N months of the close of the financial year."

**Encoding fields:**
```
rule_type: OFFSET_FROM_FY_END
offset_days: <positive integer>
```

**Note:** Many obligations of this type resolve to a fixed date (e.g., 183 days from March 31 = September 30). When this is the case, use FIXED_ANNUAL instead (cleaner, more robust to leap years). Use OFFSET_FROM_FY_END only when the offset is genuinely variable and not resolved to a fixed date.

**When to prefer FIXED_ANNUAL over OFFSET_FROM_FY_END:**
If the legal text says "within 6 months of close of FY" AND this always resolves to September 30 → use FIXED_ANNUAL (September 30, AFTER_FY_END_YEAR). If the offset could vary in edge cases (e.g., company with non-March FY end) → use OFFSET_FROM_FY_END.

**Example:** Company AGM — "within 6 months of close of financial year" — for standard March FY = September 30 → FIXED_ANNUAL preferred. But for a company with a non-standard FY end, OFFSET_FROM_FY_END is more accurate.

---

### Type 4: OFFSET_FROM_AGM

**Definition:** The due date is N days after the Annual General Meeting (AGM) of a company.

**Encoding fields:**
```
rule_type: OFFSET_FROM_AGM
agm_offset_days: <positive integer>
agm_deadline_as_fallback: true | false
```

**Computation:** If business has provided actual AGM date → AGM date + offset_days. If actual AGM date not provided → use AGM legal deadline (September 30 for March-FY companies) as fallback.

**Important:** If the AGM has not been held and the AGM deadline has passed, the AGM itself is overdue. The filing derived from the AGM is then computed as AGM_deadline + offset_days and will also show as overdue.

**Examples:**

| Compliance | Offset Days |
|-----------|------------|
| AOC-4 (Financial Statements) | 30 |
| MGT-7 / MGT-7A (Annual Return) | 60 |
| ADT-1 (Auditor Appointment) | 15 |

---

### Type 5: OFFSET_FROM_EVENT

**Definition:** The due date is N days after a user-specified event date. Used for event-based compliance items.

**Encoding fields:**
```
rule_type: OFFSET_FROM_EVENT
event_offset_days: <positive integer>
event_field: <name of business profile event date field>
event_description: <string: what event triggers this>
```

**Computation:** If event_date is provided → event_date + event_offset_days = due date. If event_date is not provided → `due_date_determinability: EVENT_DEPENDENT`, display prompt to user.

**Examples:**

| Compliance | Offset | Event |
|-----------|--------|-------|
| DIR-12 (Director appointment/resignation) | 30 | Date of appointment/resignation |
| PAS-3 (Share allotment) | 30 | Date of allotment |
| CHG-1 (Charge creation) | 30 | Date of charge creation |
| Form 4 LLP (Partner change) | 30 | Date of change |
| GST registration amendment | 15 | Date of change in particulars |

---

### Type 6: ADVANCE_TAX_INSTALLMENT

**Definition:** Special rule for advance tax under the Income Tax Act. Four installments per FY, each with a cumulative percentage target.

**Encoding fields:**
```
rule_type: ADVANCE_TAX_INSTALLMENT
installment_number: 1 | 2 | 3 | 4
fixed_day: 15
fixed_month: <6 | 9 | 12 | 3>
year_context: CURRENT_FY_YEAR
cumulative_target_pct: <15 | 45 | 75 | 100>
```

This type generates four separate due-date rule records, one per installment. Each record links to the same advance-tax compliance master record but produces a separate period instance per installment.

**Special case — Presumptive taxation (Section 44AD):** Single payment of 100% by March 15. Encoded as a separate compliance record with `installment_number: 1`, `cumulative_target_pct: 100`, `fixed_month: 3`.

---

### Type 7: CONTINUOUS

**Definition:** No single due date. The obligation is ongoing throughout the operation of the business.

**Encoding fields:**
```
rule_type: CONTINUOUS
```

**What this means for the compliance engine:** No period instances are generated. No calendar entry is shown. The obligation appears as a compliance list item with label "Ongoing Obligation" and `due_date_determinability: CONTINUOUS`.

**Examples:**
- Maintenance of books of account
- Display of registration certificates at premises
- Payroll record maintenance
- Any indicator-type obligation with no periodic filing

---

### Type 8: PERIOD_UNKNOWN

**Definition:** A legal timing obligation exists, but the due-date rule cannot be encoded because the timing language is delegated to future notification ("as may be prescribed") or because the primary source has not yet been retrieved.

**Encoding fields:**
```
rule_type: PERIOD_UNKNOWN
statutory_timing_language: <verbatim timing language from provision>
reason_unknown: PENDING_NOTIFICATION | PENDING_SOURCE | AMBIGUOUS_TEXT
```

**What this means for the compliance engine:** No due date is computed. The compliance appears in the list with label "Due date to be determined" and a note explaining the reason. `validation_state` must be `PARTIALLY_VALIDATED` or `PENDING_PRIMARY_CONFIRMATION`.

---

## 5. Notification Override Protocol

Notification-based extensions do not modify the base due-date rule. They are stored separately as `notification_extension` records.

**Base rule:** Always reflects the statutory or rules-based due date.
**Notification extension record:** Stores the extended date, the notification reference, the period it covers, and when the extension expires.

**Computation logic:**
```
step 1: Compute base_due_date from due_date_rule
step 2: Check for active notification_extension for (compliance_id, period, applicable_to)
step 3: If active extension found → effective_due_date = extension.extended_due_date
step 4: If no extension → effective_due_date = base_due_date
step 5: Return effective_due_date with override_active flag and notification reference
```

When an extension expires → the computation automatically reverts to the base rule. No manual action required.

---

## 6. Working-Day Adjustment Policy

When a computed due date falls on a Sunday or public holiday, the standard Indian compliance practice is that the effective due date shifts to the next working day.

**Working-day rule values:**
- `NEXT_WORKING_DAY` — shift forward to next business day (default for most GST, IT, TDS obligations)
- `NONE` — due date is fixed regardless of day (rare; only when statute explicitly states a date as final)

**Public holiday handling:** The engine requires a maintained `public_holidays` table covering central government holidays and banking holidays. This table must be updated annually. Until this table is populated, working-day adjustment should be applied conservatively (assume statutory due date stands; flag computation as advisory).

---

## 7. Due-Date Determinability States

| State | Meaning | Can Compute Due Date? |
|-------|---------|----------------------|
| `COMPUTABLE` | All required inputs are known; due date can be calculated | Yes |
| `EVENT_DEPENDENT` | Requires a user-supplied event date | Only after event date is provided |
| `AGM_DEPENDENT` | Requires actual AGM date or falls back to AGM deadline | Yes, with fallback |
| `CONTINUOUS` | No single due date; ongoing obligation | No |
| `PERIOD_UNKNOWN` | Due date rule not yet encodeable | No |

---

## 8. Financial Year and Quarter Reference Table

All period computations are anchored to the Indian financial year:

| Period | Start | End | Notes |
|--------|-------|-----|-------|
| FY2025-26 | April 1, 2025 | March 31, 2026 | — |
| FY Q1 | April 1 | June 30 | Same for all FYs |
| FY Q2 | July 1 | September 30 | — |
| FY Q3 | October 1 | December 31 | — |
| FY Q4 | January 1 | March 31 | — |
| AY for FY2025-26 | April 1, 2026 | March 31, 2027 | AY = FY + 1 year |

---

## 9. What Should Be Deferred

- State-specific due date variations (e.g., Professional Tax payment frequencies by state) are deferred to Phase 2 population.
- Calendar half-year computations for state-specific returns are deferred.
- Non-standard financial year handling (companies with non-March FY end) is deferred to Phase 2.
