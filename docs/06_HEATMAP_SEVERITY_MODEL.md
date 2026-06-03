# Document 06 — Heat Map and Severity Model
## Penalty Criticality Scoring Framework

---

## 1. DESIGN INTENT

The heat map is the product's most immediately actionable view.
A business owner should be able to look at it and instantly know:
- Which obligations are most dangerous to miss
- Which are currently overdue
- Which are coming up dangerously soon

The heat map must answer: **"What should I worry about MOST, RIGHT NOW?"**

---

## 2. TWO-COMPONENT SEVERITY MODEL

Severity has two distinct components that must be kept separate and combined:

### Component A: BASE SEVERITY (Inherent severity of the compliance itself)

This is static. It is the severity of the compliance assuming it is exactly on its due date.
It reflects: how bad is it if this is missed at all?

This is stored in `penalty_record.computed_base_score` (0–100).

### Component B: TIME ESCALATION (Dynamic, based on how overdue it currently is)

This is dynamic. It reflects: given that this is already late, how much worse is it now?

This is computed at runtime when generating the heat map view.

### Combined Score

```
combined_score = min(100, base_score + time_escalation_score(overdue_days))
```

---

## 3. BASE SEVERITY SCORING (0–100)

Base score is computed from the penalty record using a weighted factor model.

### Factor 1: Prosecution / Imprisonment Risk (Max 30 points)

| Condition | Points |
|-----------|--------|
| Imprisonment possible (specified in Act) | 25–30 pts |
| Prosecution possible but imprisonment not specified | 15–20 pts |
| No prosecution risk | 0 pts |

**Reference compliances at max end:**
- Failure to maintain books (IT Act Sec 271A): prosecution possible → 20 pts
- TDS non-compliance (IT Act Sec 276B): prosecution + rigorous imprisonment → 28 pts
- GST invoice fraud (CGST Act Sec 132): prosecution + imprisonment → 28+ pts

### Factor 2: Financial Penalty Magnitude (Max 25 points)

| Penalty Range | Points |
|--------------|--------|
| Flat penalty > ₹1 lakh | 20–25 pts |
| Flat penalty ₹25,000–₹1 lakh | 14–19 pts |
| Flat penalty ₹5,000–₹25,000 | 8–13 pts |
| Flat penalty < ₹5,000 | 3–7 pts |
| No flat penalty | 0 pts |

### Factor 3: Recurring Daily/Monthly Fee or Interest Exposure (Max 20 points)

| Rate | Points |
|------|--------|
| Daily late fee + interest rate ≥ 18% p.a. combined | 16–20 pts |
| Daily late fee + interest 10–18% p.a. combined | 10–15 pts |
| Daily late fee only (no interest), moderate | 5–9 pts |
| No recurring fee/interest | 0 pts |

**Note:** This factor is highest for TDS non-deposit (1.5%/month interest, which is 18% p.a. + 30% expense disallowance). GST delayed payment (18% p.a. interest) also scores high.

### Factor 4: Compliance Cascade Impact (Max 15 points)

Blocks other filings, causes disallowance, or has downstream business impact.

| Condition | Points |
|-----------|--------|
| Blocks other government filings (e.g., GSTR-2B mismatch, MCA strike-off) | 12–15 pts |
| Causes tax disallowance of business expense | 10–12 pts |
| Causes audit qualification or regulatory action | 8–10 pts |
| Causes difficulty in obtaining government certificates | 5–7 pts |
| No cascade impact | 0 pts |

**Reference:** TDS non-deduction causes 30% disallowance of the related expense (IT Act Sec 40(a)(ia)) → 12 pts. Not filing GSTR-1 blocks ITC for the recipient → 12 pts.

### Factor 5: Registration / Business Disability (Max 10 points)

| Condition | Points |
|-----------|--------|
| Risk of registration cancellation or suspension | 8–10 pts |
| Restricted from making certain business transactions | 5–7 pts |
| Debarment from government contracts/tenders | 5–6 pts |
| No business disability | 0 pts |

**Reference:** GST registration can be suspended for non-filing of returns → 8 pts.

---

### Base Score Examples for Common Compliances

| Compliance | F1 | F2 | F3 | F4 | F5 | Base Score | Band |
|-----------|----|----|----|----|-----|-----------|------|
| TDS non-deposit | 28 | 18 | 18 | 12 | 0 | 76 | **SEVERE** |
| GSTR-3B late payment | 0 | 12 | 18 | 12 | 8 | 50 | **HIGH** |
| GSTR-1 not filed | 0 | 10 | 8 | 15 | 8 | 41 | **HIGH** |
| ITR not filed | 15 | 20 | 12 | 8 | 5 | 60 | **SEVERE** |
| EPF not deposited | 10 | 15 | 14 | 5 | 5 | 49 | **HIGH** |
| MCA AOC-4 late | 0 | 10 | 8 | 8 | 8 | 34 | **MODERATE** |
| GSTR-9 late | 0 | 8 | 8 | 5 | 0 | 21 | **MODERATE** |
| Shops registration | 8 | 12 | 0 | 3 | 5 | 28 | **MODERATE** |
| LLP Form 11 late | 0 | 8 | 5 | 3 | 3 | 19 | **LOW** |
| Books not maintained | 20 | 12 | 0 | 8 | 0 | 40 | **HIGH** |
| DIR-3 KYC missed | 5 | 10 | 8 | 10 | 8 | 41 | **HIGH** |

*All scores above are illustrative estimates for the architecture document. Actual scores must be computed from confirmed penalty provisions via proper source verification.*

---

## 4. SEVERITY BANDS

| Band | Combined Score | Color | Hex Code |
|------|--------------|-------|----------|
| CRITICAL | 80–100 | Dark Red | `#B71C1C` |
| SEVERE | 60–79 | Red | `#D32F2F` |
| HIGH | 40–59 | Deep Orange | `#E64A19` |
| MODERATE | 20–39 | Amber | `#F9A825` |
| LOW | 0–19 | Green | `#388E3C` |

---

## 5. TIME ESCALATION FORMULA

The time escalation adds urgency based on how overdue the compliance currently is.

```
time_escalation_score(overdue_days):
  if overdue_days <= 0:      return 0          # Not overdue
  if overdue_days <= 7:      return 5           # Very recently overdue
  if overdue_days <= 30:     return 10          # 1 month
  if overdue_days <= 60:     return 15          # 2 months
  if overdue_days <= 90:     return 20          # 3 months
  if overdue_days <= 180:    return 25          # 6 months
  if overdue_days > 180:     return 30          # Severely overdue
```

**Combined score examples:**
- GSTR-1 base=41 (HIGH), overdue 45 days → 41+15 = 56 → still HIGH (just)
- TDS deposit base=76 (SEVERE), overdue 45 days → 76+15 = 91 → **CRITICAL**
- ITR base=60 (SEVERE), overdue 10 months → 60+30 = 90 → **CRITICAL**

This escalation makes a HIGH compliance that's 6 months overdue become CRITICAL,
which correctly reflects the real-world risk.

---

## 6. STATUS-BASED COLOR CODING IN CALENDAR/CHECKLIST VIEWS

In addition to the severity band colors (used in heat map), the calendar and checklist views
need status-based coloring:

| Status | Color | Hex | Condition |
|--------|-------|-----|-----------|
| Completed | Grey/Green | `#4CAF50` | User has marked as done |
| Not Yet Open | Light Blue | `#B0BEC5` | Filing window not yet open |
| Upcoming | Blue | `#1565C0` | Due in > 30 days |
| Due Soon | Amber | `#FF8F00` | Due in 8–30 days |
| Due Very Soon | Orange | `#E65100` | Due in ≤ 7 days |
| Overdue — Low | Yellow | `#F9A825` | Overdue, combined score < 20 |
| Overdue — Moderate | Orange | `#FF6D00` | Overdue, combined score 20–39 |
| Overdue — High | Deep Orange | `#E64A19` | Overdue, combined score 40–59 |
| Overdue — Severe | Red | `#D32F2F` | Overdue, combined score 60–79 |
| Overdue — Critical | Dark Red | `#B71C1C` | Overdue, combined score 80–100 |

---

## 7. HEAT MAP GRID DESIGN (UI RECOMMENDATION)

The heat map grid should be organized as:

**X-axis (columns):** Compliance domains
(GST, Income Tax, TDS, MCA/LLP, EPF/ESI, Labour, Establishments, Records)

**Y-axis (rows):** Time urgency
(Critical Overdue, Severely Overdue, High Overdue, Moderate Overdue, Due Very Soon, Due Soon, Upcoming, Future)

**Cell color:** Combined severity score → band color

Each cell shows: count of obligations in that category/urgency combination.
Clicking a cell shows the list of specific obligations.

This design gives the user a two-dimensional view:
- "Which domain has the most critical risk?" (column)
- "What's most urgently overdue?" (row)

---

## 8. APPLICABILITY STATUS MAPPING TO HEAT MAP

Not all compliances should appear on the heat map with severity colors. Here is how to handle them:

| Applicability Status | Heat Map Treatment |
|---------------------|-------------------|
| APPLICABLE | Full severity color based on score |
| LIKELY_APPLICABLE | Show with amber border + "Confirm applicability" tag |
| CHECK_THRESHOLD | Show greyed with "Check threshold" tag |
| EVENT_TRIGGERED | Show only if event date provided; else grey |
| STATE_SPECIFIC | Show with state flag; severity for that state |
| RECOMMENDED | Show in a separate "Recommended" section, not main heat map |
| NOT_APPLICABLE | Do not show |
| INSUFFICIENT_DATA | Show in "Needs More Info" section |
| HUMAN_REVIEW_REQUIRED | Show with professional review flag, not heat map |

---

## 9. ESTIMATED FINANCIAL EXPOSURE CALCULATION

Where possible, the system should compute an estimated financial exposure for overdue items:

```
For late GST filing:
  late_fee_accrued = min(late_fee_per_day × overdue_days, late_fee_maximum)

For delayed GST payment:
  interest_accrued = gst_payable × (interest_rate_pa / 365) × overdue_days
  (Requires user to input approximate GST payable amount)

For delayed TDS deposit:
  interest = tds_amount × 1.5% × months_delayed
  (Requires user to have entered TDS deducted amount)
```

Where input data is insufficient for exact calculation:
- Show the per-day rate and total overdue days
- Show "Estimated minimum exposure: ₹X (based on late fee only)"
- Mark it as an estimate, not a precise calculation

---

## 10. SEVERITY MODEL — IMPORTANT CAVEATS

1. **This model is for prioritization, not legal quantification.** It should not be presented as "you owe exactly ₹X in penalties." It is a risk prioritization tool.

2. **Base scores must be verified against actual current penalty provisions.** The illustrative scores in Section 3 above must be replaced with scores computed from properly sourced `penalty_record` entries.

3. **Prosecution risk scoring is conservative.** Many provisions allow prosecution theoretically but in practice prosecution is rare for delays vs. outright evasion. The system must capture `prosecution_notes` explaining the practical risk level, not just the statutory possibility.

4. **Interest-based scores require the amount involved.** If the user hasn't entered their GST liability or TDS deducted amount, interest exposure can't be computed precisely. The system must flag this as "exposure depends on amount — enter payable amount for accurate estimate."

5. **Severity bands may need recalibration after user testing.** The 0–100 scale with these thresholds is a starting proposal. The product team should validate that users find the relative prioritization intuitive.
