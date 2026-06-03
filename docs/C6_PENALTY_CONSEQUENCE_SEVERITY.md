# C6 — Penalty, Consequence, and Severity Encoding Framework
## Consequence Data Model and Risk Scoring Standard

---

## 1. Objective

Define how the legal consequences of non-compliance are represented in the master library, how they are converted into structured data, and how that data drives the severity scoring system that powers the risk heat map.

Ensure that the framework prevents overstating risk where source support is weak, while accurately representing the full statutory consequence where primary sources confirm it.

---

## 2. Why It Matters to the Compliance Engine

The severity score is what makes the heat map meaningful. A compliance system that shows the same urgency for a ₹200/day late fee as it does for a provision that allows prosecution and imprisonment has failed its user. Conversely, a system that downplays a prosecution-risk provision because "prosecution is rare in practice" has fabricated a risk reduction not supported by the statute.

The penalty data model must be both accurate and calibrated — reflecting what the law actually says, neither more nor less.

---

## 3. Design Principles

**P1 — Statute-only consequences.** Only consequences directly stated in the governing statute, rules, or notification are recorded as confirmed consequences. Do not infer consequences.

**P2 — Distinguish types.** Late fees, interest, flat penalties, and prosecution risks are distinct consequence types. They must not be conflated into a single severity assessment.

**P3 — No fabricated risk escalation.** If the statute sets a maximum late fee of ₹10,000 regardless of delay duration, the system must not imply that penalties keep rising indefinitely.

**P4 — Indirect/operational consequences are secondary.** Consequences like "blocked from filing connected forms" or "expense disallowance" are real and important, but they are inferred operational impacts — not direct statutory penalties. They must be flagged as `consequence_type: OPERATIONAL_IMPACT` not `STATUTORY_PENALTY`.

**P5 — Uncertainty is declared, not hidden.** Where the penalty amount is variable, discretionary, or dependent on facts the system doesn't know (e.g., the amount of tax evaded), the consequence is recorded with its formula and noted as not precisely quantifiable.

---

## 4. Consequence Data Model

Each compliance rule with a penalty connects to a `penalty_record` containing the following structured fields:

---

### Consequence Group 1: Late Fee

A fixed per-day fee for delayed filing, specified in the statute.

| Field | Type | Notes |
|-------|------|-------|
| `late_fee_per_day` | Decimal (₹) | Per-day late fee amount. Example: ₹50/day |
| `late_fee_maximum` | Decimal (₹) | Statutory cap on total late fee. Example: ₹10,000 |
| `late_fee_nil_return_per_day` | Decimal (₹) | Reduced rate for nil returns where statute specifies |
| `late_fee_nil_return_maximum` | Decimal (₹) | Cap for nil return late fee |
| `late_fee_source_reference` | String | Exact provision reference. Example: "Section 47(1), CGST Act, 2017" |
| `late_fee_confidence` | Enum: HIGH/MEDIUM/LOW | Confidence that this rate is current and correctly sourced |

**Important:** If the statute specifies a per-day fee but with a maximum cap, the late fee accrual stops at the cap. The system must never display an accumulating fee beyond the statutory maximum.

---

### Consequence Group 2: Interest

Interest on outstanding tax, contribution, or dues — typically continues to accrue until payment.

| Field | Type | Notes |
|-------|------|-------|
| `interest_rate_pa` | Decimal (%) | Annual interest rate. Example: 18.00 for 18% p.a. |
| `interest_basis` | String | What the interest applies to. Example: "on unpaid tax liability" |
| `interest_from_when` | Enum | PAYMENT_DUE_DATE (from when tax was due) or DEDUCTION_DATE (for TDS) |
| `interest_until_when` | Enum | ACTUAL_PAYMENT or ASSESSMENT |
| `interest_source_reference` | String | Provision reference |
| `interest_confidence` | Enum | HIGH/MEDIUM/LOW |

**Note:** Interest unlike late fee typically has no cap and continues to accrue until payment. This makes it a more severe long-term risk than a capped late fee.

---

### Consequence Group 3: Flat Monetary Penalty

A fixed or variable penalty (distinct from late fees and interest) imposed by the statute.

| Field | Type | Notes |
|-------|------|-------|
| `flat_penalty_minimum` | Decimal (₹) | Minimum penalty under the provision |
| `flat_penalty_maximum` | Decimal (₹) | Maximum penalty under the provision |
| `flat_penalty_fixed` | Decimal (₹) | If exact fixed amount (not variable), record here |
| `flat_penalty_formula_notes` | String | If formula-based (e.g., "penalty equal to tax evaded"), describe the formula |
| `flat_penalty_source_reference` | String | Provision reference |
| `flat_penalty_confidence` | Enum | HIGH/MEDIUM/LOW |

---

### Consequence Group 4: Prosecution and Imprisonment

| Field | Type | Notes |
|-------|------|-------|
| `prosecution_possible` | Boolean | Whether prosecution is permitted under the statute |
| `imprisonment_possible` | Boolean | Whether imprisonment is a possible outcome |
| `imprisonment_minimum_months` | Integer | Minimum term if imprisonment specified |
| `imprisonment_maximum_months` | Integer | Maximum term if imprisonment specified |
| `imprisonment_type` | Enum: SIMPLE / RIGOROUS / EITHER | From the statutory language |
| `prosecution_notes` | String | Important context. Example: "Prosecution is available for willful evasion; routine delay typically results only in penalty." Must include a candid note on practical risk level where known. |
| `prosecution_source_reference` | String | Provision reference |
| `prosecution_confidence` | Enum | HIGH/MEDIUM/LOW |

**Mandatory note for prosecution fields:** Where the statute allows prosecution but practical prosecution is rare (e.g., routine late filing without evasion), the `prosecution_notes` field MUST include a calibration note. Example: "Prosecution under Section 276B (TDS non-deposit) is available but is typically reserved for willful default with evidence of intent to evade. Routine late deposits generally attract interest and penalty only." This prevents the system from overstating risk to users.

---

### Consequence Group 5: Operational / Downstream Impacts

These are real consequences but are inferred operational impacts, not direct statutory penalties. They must be flagged as such.

| Field | Type | Notes |
|-------|------|-------|
| `causes_expense_disallowance` | Boolean | Example: TDS non-deduction → 30% expense disallowance under Section 40(a)(ia) |
| `disallowance_description` | String | Describe what expense is disallowed and under which provision |
| `blocks_connected_filings` | Boolean | Example: Delayed GSTR-1 affects recipient's ITC |
| `blocks_description` | String | Describe what filings are blocked |
| `causes_registration_risk` | Boolean | Example: Non-filing can lead to GST registration cancellation/suspension |
| `registration_risk_description` | String | Describe the registration consequence and provision |
| `operational_impact_confidence` | Enum | HIGH/MEDIUM/LOW — confidence in the operational impact claim |

---

## 5. Severity Scoring Model

The base severity score (0–100) is computed from the above fields using a weighted factor model. This model is already defined in Part A doc 06. Part C formalizes the relationship between the penalty data model and the score computation.

### Factor Weights

| Factor | Source Fields | Max Points |
|--------|-------------|-----------|
| Prosecution/imprisonment risk | `prosecution_possible`, `imprisonment_possible`, `imprisonment_maximum_months` | 30 |
| Flat monetary penalty magnitude | `flat_penalty_maximum` or `flat_penalty_fixed` | 25 |
| Recurring fee/interest exposure | `late_fee_per_day` + `interest_rate_pa` combined | 20 |
| Cascading operational impact | `causes_expense_disallowance`, `blocks_connected_filings`, `causes_registration_risk` | 15 |
| Business/registration disability | `causes_registration_risk`, `registration_risk_description` | 10 |

### Scoring Logic (Illustrative, Non-Executable)

```
FACTOR 1 — Prosecution/imprisonment:
  imprisonment_possible = true AND imprisonment_maximum_months >= 12 → 25–30 pts
  imprisonment_possible = true AND imprisonment_maximum_months < 12  → 20–24 pts
  prosecution_possible = true AND imprisonment_possible = false      → 15–19 pts
  prosecution_possible = false                                       → 0 pts

FACTOR 2 — Flat penalty:
  flat_penalty_maximum > 100,000 (₹1L)   → 20–25 pts
  flat_penalty_maximum 25,001–100,000     → 14–19 pts
  flat_penalty_maximum 5,001–25,000       → 8–13 pts
  flat_penalty_maximum ≤ 5,000            → 3–7 pts
  No flat penalty                         → 0 pts

FACTOR 3 — Recurring exposure:
  (late_fee_per_day * 30) + (interest_rate_pa/12 * hypothetical_liability):
  High exposure (>18% equivalent annual rate) → 16–20 pts
  Medium exposure (8–18%)                      → 10–15 pts
  Low exposure (<8%)                           → 5–9 pts
  No recurring fee/interest                    → 0 pts

FACTOR 4 — Cascading impact:
  causes_expense_disallowance = true         → +10–12 pts
  blocks_connected_filings = true            → +12–15 pts
  Either one                                 → use higher
  Neither                                    → 0 pts

FACTOR 5 — Business disability:
  causes_registration_risk = true            → 8–10 pts
  blocks business transactions               → 5–7 pts
  None                                       → 0 pts

BASE SCORE = sum of factors, capped at 100
```

### Confidence Adjustment

If `source_confidence_level = LOW` for any consequence field, reduce the contribution of that factor by 50%. This prevents low-confidence consequence data from producing artificially high severity scores.

If `prosecution_confidence = LOW` → treat prosecution_possible as effectively false for scoring purposes and add interpretation note.

### Severity Bands

| Score | Band |
|-------|------|
| 0–19 | LOW |
| 20–39 | MODERATE |
| 40–59 | HIGH |
| 60–79 | SEVERE |
| 80–100 | CRITICAL |

---

## 6. Dynamic Severity (Time-Based Escalation)

The base severity is inherent to the rule. The dynamic severity reflects current lateness. This is computed at the instance layer (not stored in the penalty record).

**Time Escalation Table:**

| Overdue Duration | Additional Points |
|-----------------|------------------|
| Not overdue | 0 |
| 1–7 days | +5 |
| 8–30 days | +10 |
| 31–60 days | +15 |
| 61–90 days | +20 |
| 91–180 days | +25 |
| > 180 days | +30 |

**Combined Score = min(100, base_score + time_escalation)**

This ensures that a MODERATE obligation that is severely overdue escalates to HIGH or SEVERE, while a LOW obligation that is slightly late remains low priority.

---

## 7. What Must Not Be Done

**Do not fabricate continuing penalties beyond the statutory cap.** If the statute caps a late fee at ₹10,000 regardless of duration, the heat map must NOT imply exponentially growing risk. Show the cap clearly.

**Do not import risk from professional commentary without statutory basis.** If a professional blog says "non-filing can result in massive penalties," this does not constitute a consequence unless the provision specifying those penalties is identified and sourced.

**Do not conflate administrative difficulty with statutory penalty.** "It is difficult to revive a cancelled GST registration" is an operational observation — it is not a statutory penalty. It may be noted in `registration_risk_description` but should not add to the STATUTORY consequence score.

---

## 8. What Should Be Deferred

- Computing actual financial exposure (₹ amounts) based on user-specific tax liability requires the user to provide additional inputs (amount of tax payable, TDS deducted, etc.). This is a Phase 2 enhancement.
- State-specific penalty provisions (e.g., state Shops & Establishments fines) are deferred to Phase 2 state-specific rule population.
