# Document 05 — Due Date Engine
## Framework for Computing Actual Due Dates

---

## 1. CORE REQUIREMENT

The system must not show "Monthly" as a due date. It must show "20 June 2025".
It must know whether that date is in the past (overdue) or future (upcoming).
It must compute how many days remain or how many days are overdue.

This document defines the complete framework for encoding and computing due dates.

---

## 2. FINANCIAL YEAR CONTEXT

Every computation requires a FY context. The engine must always know:

```
current_date          = today's date (real-time)
current_fy_start      = April 1 of current FY
current_fy_end        = March 31 of current FY + 1 year
current_fy_label      = "FY{YYYY}-{YY}"   e.g., "FY2025-26"
current_ay_label      = "AY{YYYY}-{YY}"   e.g., "AY2026-27"
current_fy_quarter    = 1/2/3/4

FY Quarter mapping:
  Q1 = April 1   – June 30      (months 4, 5, 6)
  Q2 = July 1    – September 30 (months 7, 8, 9)
  Q3 = October 1 – December 31  (months 10, 11, 12)
  Q4 = January 1 – March 31     (months 1, 2, 3)
```

---

## 3. DUE DATE RULE TYPES

### TYPE 1: FIXED_ANNUAL

**Definition:** A single fixed date in the calendar year (not assessment year).

**Parameters:**
- `fixed_day`: day of month (1–31)
- `fixed_month`: month (1–12)

**Examples:**
| Compliance | Day | Month | Notes |
|-----------|-----|-------|-------|
| Advance Tax Q1 | 15 | 6 (June) | June 15 of current FY |
| Advance Tax Q2 | 15 | 9 (Sep) | Sep 15 of current FY |
| Advance Tax Q3 | 15 | 12 (Dec) | Dec 15 of current FY |
| Advance Tax Q4 | 15 | 3 (Mar) | March 15 of current FY |
| GSTR-4 (Composition annual) | 30 | 4 (Apr) | April 30 after FY end |
| LLP Form 11 (Annual Return) | 30 | 5 (May) | May 30 after FY end |
| LLP Form 8 (SAS) | 30 | 10 (Oct) | Oct 30 (6 months from FY end + 30 days) |

**Computation algorithm:**
```
due_date = DATE(current_fy_end_year, fixed_month, fixed_day)
# Adjust to next year if fixed_month is post-FY-end and this is for next year's filing
# For GSTR-4: April 30 of NEXT calendar year after FY end
# For Form 11: May 30 of NEXT calendar year after FY end
```

---

### TYPE 2: FIXED_IN_AY (Fixed in Assessment Year)

**Definition:** A fixed date, but anchored to the Assessment Year (FY+1).

**Parameters:**
- `ay_fixed_day`: day of month
- `ay_fixed_month`: month in AY calendar

**Examples:**
| Compliance | Day | Month | AY Interpretation |
|-----------|-----|-------|------------------|
| ITR filing (non-audit) | 31 | 7 (July) | July 31 of AY (FY2025-26 → July 31, 2026) |
| ITR filing (audit) | 31 | 10 (Oct) | Oct 31 of AY |
| Tax Audit Report | 30 | 9 (Sep) | Sep 30 of AY |
| ITR with TP | 30 | 11 (Nov) | Nov 30 of AY |

**Computation algorithm:**
```
ay_year = current_fy_end_year + 1
due_date = DATE(ay_year, ay_fixed_month, ay_fixed_day)
```

---

### TYPE 3: OFFSET_FROM_PERIOD_END

**Definition:** Due date is N days after the end of a recurring period (month, quarter, etc.).

**Parameters:**
- `period_type`: CALENDAR_MONTH | FY_QUARTER | HALF_YEAR
- `offset_days`: number of days after period end
- `state_based_variation`: boolean
- `state_offset_rules`: JSON array

**Examples:**
| Compliance | Period | Offset | Adjusted |
|-----------|--------|--------|---------|
| GSTR-3B (Group A states) | Calendar month | 20 days | 20th of following month |
| GSTR-3B (Group B states) | Calendar month | 22 days | 22nd of following month |
| GSTR-3B (Group C states) | Calendar month | 24 days | 24th of following month |
| GSTR-1 (monthly) | Calendar month | 11 days | 11th of following month |
| GSTR-1 (quarterly QRMP) | FY quarter | 13 days | 13th of following month after quarter |
| TDS deposit (non-Mar) | Calendar month | 7 days | 7th of following month |
| TDS deposit (March) | Special | — | Fixed April 30 (override rule) |
| EPF/ECR deposit | Calendar month | 15 days | 15th of following month |
| ESI deposit | Calendar month | 15 days | 15th of following month |
| CMP-08 (Composition quarterly) | FY quarter | 18 days | 18th of following month after quarter |
| TDS quarterly return Q1 | FY quarter (Apr-Jun) | Fixed | 31st July |
| TDS quarterly return Q2 | FY quarter (Jul-Sep) | Fixed | 31st October |
| TDS quarterly return Q3 | FY quarter (Oct-Dec) | Fixed | 31st January |
| TDS quarterly return Q4 | FY quarter (Jan-Mar) | Fixed | 31st May |
| DPT-3 | Annual (FY end) | 90 days from FY end | June 30 |

**Computation algorithm:**
```
period_end = end_of_period(current_period, period_type)
base_due = period_end + offset_days

# Apply state variation if applicable
if state_based_variation and business.state in state_offset_rules:
    adjusted_offset = state_offset_rules[business.state].offset_days
    base_due = period_end + adjusted_offset

# Apply working day adjustment
if working_day_rule == 'NEXT_WORKING_DAY' and is_holiday_or_weekend(base_due):
    due_date = next_working_day(base_due)
else:
    due_date = base_due
```

---

### TYPE 4: OFFSET_FROM_FY_END

**Definition:** Due date is N days after end of financial year (March 31).

**Examples:**
| Compliance | Offset | Resulting Date |
|-----------|--------|---------------|
| GSTR-9 / GSTR-9C | ~275 days | December 31 of AY year |
| DIR-3 KYC | ~183 days | September 30 |
| MSME Form I (H2: Oct-Mar) | 30 days | April 30 |
| Company AGM (deadline) | 183 days | September 30 |

**Note:** Many of these are more naturally modeled as FIXED_IN_AY or FIXED_ANNUAL since the actual date resolves to a fixed calendar date. Use OFFSET_FROM_FY_END only when the rule is genuinely stated as "within N days of FY end."

---

### TYPE 5: OFFSET_FROM_AGM

**Definition:** Due date is N days after the Annual General Meeting (AGM).

**Important:** The AGM itself has a due date (September 30 for March-ending companies). The derived compliance due date must be computed from the actual AGM date if known, OR from the AGM deadline if actual date is unknown.

**Examples:**
| Compliance | Offset | Source |
|-----------|--------|--------|
| AOC-4 filing | 30 days | Companies Act Sec 137 |
| MGT-7 / MGT-7A filing | 60 days | Companies Act Sec 92 |
| ADT-1 (auditor) | 15 days | Companies Act Sec 139 |

**Computation algorithm:**
```
agm_date = business.actual_agm_date if known, else agm_deadline
due_date = agm_date + offset_days

# If AGM not yet held and current date < AGM deadline:
#   Show "Pending: AGM first, then N days"
# If AGM deadline passed and no AGM held:
#   AGM itself is overdue; this filing is also overdue from AGM deadline + N days
```

**User Data Required:** The business must provide their AGM date (or it defaults to the legal deadline).

---

### TYPE 6: OFFSET_FROM_EVENT

**Definition:** Due date is N days after a user-specified event.

**Examples:**
| Compliance | Event | Offset | Source |
|-----------|-------|--------|--------|
| DIR-12 (director change) | Date of appointment/resignation | 30 days | Companies Act |
| PAS-3 (share allotment) | Date of allotment | 30 days | Companies Act Sec 39 |
| CHG-1 (charge creation) | Date of charge creation | 30 days | Companies Act Sec 77 |
| Form 4 LLP (partner change) | Date of change | 30 days | LLP Rules |
| GST registration amendment | Date of change in particulars | 15 days | CGST Act Sec 28 |

**Computation algorithm:**
```
if event_date is provided:
    due_date = event_date + offset_days
    if current_date > due_date:
        is_overdue = True
        overdue_days = (current_date - due_date).days
else:
    applicability_status = 'EVENT_TRIGGERED'
    due_date = None
    show_message = "Provide event date to compute due date"
```

---

### TYPE 7: ADVANCE_TAX_INSTALLMENT

A special rule for advance tax — four installments per FY.

```
Installment 1: June 15 of FY   → 15% cumulative
Installment 2: Sep 15 of FY    → 45% cumulative
Installment 3: Dec 15 of FY    → 75% cumulative
Installment 4: Mar 15 of FY    → 100% cumulative
```

The engine generates four separate due date records per FY for this compliance.

---

### TYPE 8: CONTINUOUS

Compliance has no single due date. It is an ongoing obligation.

**Examples:**
- Maintenance of books of account
- Wage register maintenance
- Display of registration certificates

**Behavior:** No due date computed. These appear in checklist view as "Ongoing" with a check for completion status.

---

## 4. PERIOD GENERATION

For recurring compliances, the engine must generate all applicable periods for the current FY and flag each as:
- Filed/Completed (if user marks it)
- Upcoming (due date in future)
- Due Soon (due date within 30 days)
- Overdue (due date has passed)

**Monthly compliance period generation example (GSTR-3B):**

```
For FY2025-26:
  Period 1: Apr 2025 → Due: May 20, 2025
  Period 2: May 2025 → Due: Jun 20, 2025
  Period 3: Jun 2025 → Due: Jul 20, 2025
  Period 4: Jul 2025 → Due: Aug 20, 2025
  Period 5: Aug 2025 → Due: Sep 20, 2025
  Period 6: Sep 2025 → Due: Oct 20, 2025
  Period 7: Oct 2025 → Due: Nov 20, 2025
  Period 8: Nov 2025 → Due: Dec 20, 2025
  Period 9: Dec 2025 → Due: Jan 20, 2026
  Period 10: Jan 2026 → Due: Feb 20, 2026
  Period 11: Feb 2026 → Due: Mar 20, 2026
  Period 12: Mar 2026 → Due: Apr 20, 2026
```

As of June 3, 2026:
- Periods 1–11: Should be completed; flag each as overdue if not marked done
- Period 12: April 20 is past → overdue if not marked done

---

## 5. OVERDUE AND DUE-SOON COMPUTATION

```
Given: computed_due_date, current_date

if current_date > computed_due_date:
    is_overdue = True
    overdue_days = (current_date - computed_due_date).days
    due_in_days = -(overdue_days)   # negative = overdue
else:
    is_overdue = False
    overdue_days = 0
    due_in_days = (computed_due_date - current_date).days

is_due_soon = (not is_overdue) and (due_in_days <= 30)
is_due_very_soon = (not is_overdue) and (due_in_days <= 7)
is_critical_overdue = is_overdue and (overdue_days > 90)
```

---

## 6. NOTIFICATION OVERRIDE HANDLING

When a government notification extends a due date:

1. A new `notification_extension` record is created in the database.
2. The extension is linked to the relevant `compliance_id` and `period_affected`.
3. The due date engine checks for active extensions before returning a due date:

```
def compute_due_date(compliance_id, period, business_state):
    base_rule = get_due_date_rule(compliance_id)
    base_due = compute_from_rule(base_rule, period, business_state)
    
    # Check for active notification override for this period
    extension = get_active_extension(compliance_id, period)
    if extension:
        effective_due = extension.extended_due_date
        override_active = True
        override_source = extension.source_id
    else:
        effective_due = base_due
        override_active = False
    
    return {
        "due_date": effective_due,
        "base_due_date": base_due,
        "override_active": override_active,
        "override_source": override_source
    }
```

---

## 7. WHAT CAN BE COMPUTED RELIABLY vs. WHAT NEEDS VERIFICATION

### Highly Reliable (encode and compute)

- GST return due dates (GSTR-1, GSTR-3B, GSTR-9, GSTR-4, CMP-08)
- TDS deposit due dates
- TDS quarterly return due dates
- Advance tax installment dates
- ITR filing due dates
- Tax audit report due dates
- EPF/ESI deposit due dates
- LLP Form 8 and Form 11
- MCA AOC-4, MGT-7 (once AGM date is known)
- LLP annual return (Form 11)

### Needs "Verify Latest Notification" Flag

- Any due date that has historically been extended via CBDT/CBIC notifications
- GSTR-9 / GSTR-9C annual returns (frequently extended historically)
- ITR due dates (extended via CBDT circular in multiple years)
- MCA annual filing deadlines (extended via MCA circulars during Covid)

For these, compute the statutory due date, AND display: "Check for any CBDT/CBIC extension notification applicable for this period."

### Cannot Be Computed (event-based, show prompt)

- Director changes, share allotments, charge creation
- Company name change
- LLP partner changes
- GST registration amendment

For these: show the applicable compliance rule, ask user to input the event date, then compute the due date from the event.

### Cannot Be Computed (state-specific, show flag)

- Professional Tax (varies by state, slab, and employer type)
- Shops & Establishments registration/renewal (state-specific timelines)
- Factory compliance (state-specific forms and cycles)

For these: flag as `STATE_SPECIFIC` and provide the state-specific rule if it has been encoded.

---

## 8. FINANCIAL YEAR LABEL GENERATION

```
current_year = current_date.year
current_month = current_date.month

if current_month >= 4:  # April or later: we are in FY that started this year
    fy_start_year = current_year
    fy_end_year = current_year + 1
else:  # Jan-March: we are still in FY that started last year
    fy_start_year = current_year - 1
    fy_end_year = current_year

fy_label = f"FY{fy_start_year}-{str(fy_end_year)[-2:]}"
# e.g., "FY2025-26"

ay_label = f"AY{fy_end_year}-{str(fy_end_year + 1)[-2:]}"
# e.g., "AY2026-27"
```

---

## 9. WORKING DAYS AND HOLIDAYS

Indian compliance due dates are adjusted when they fall on a Sunday or public holiday in some (not all) cases. The rule is not uniform:

- **GST:** If due date falls on a public holiday or Sunday, the effective due date is the next working day (CBIC practice, reflected in notifications)
- **TDS:** If due date falls on a holiday, next working day applies
- **MCA:** Similar practice
- **Income Tax:** Explicit provision in IT Act Sec 10(4) for adjustments

The engine must maintain a **public holiday calendar** (central government holidays + banking holidays) to enable this adjustment. This is a data maintenance requirement:
- Store holidays per year in a `public_holidays` table
- Apply `next_working_day()` adjustment when `working_day_rule = NEXT_WORKING_DAY`

**NOTE:** The holiday calendar is a separate data maintenance concern and must be updated annually.
