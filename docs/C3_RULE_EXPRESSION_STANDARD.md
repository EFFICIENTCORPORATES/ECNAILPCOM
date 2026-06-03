# C3 — Rule Expression Standard
## Canonical Pattern for Expressing Every Compliance Obligation

---

## 1. Objective

Ensure that every compliance obligation in the master library is decomposable into a canonical expression pattern that captures the complete logic of the obligation in a structured, evaluable, and auditable form.

No obligation should be stored as prose alone. Every obligation must be expressible in the canonical form defined here.

---

## 2. Why It Matters to the Compliance Engine

An obligation stored only as a prose description can be read by humans but cannot be evaluated by the applicability engine, cannot produce computed due dates, and cannot drive severity scoring. The rule expression standard ensures that every piece of legal logic that matters to the system's behavior is represented in a structured, machine-usable form — while prose fields remain as supplementary context.

---

## 3. Design Principles

**P1 — Atomic obligations.** Each rule record represents one atomic obligation: one action, one due date cycle, one set of consequences. Composite obligations (file AND pay) must be split.

**P2 — The canonical sentence.** Every rule must be expressible as: *"[WHO] must [DO WHAT] [BY WHEN] [HOW OFTEN] [IF conditions] [UNLESS exemptions] [OR ELSE consequences] [PER source]."* If any component cannot be expressed, it must be flagged as `PENDING` in the relevant field.

**P3 — Structure over prose.** The structured expression is authoritative. Prose descriptions are secondary aids. If they conflict, investigate and correct the structured expression — do not override structure with prose.

**P4 — Completeness is mandatory.** A partially expressed rule is more dangerous than an absent rule, because it appears valid but produces incorrect outputs.

---

## 4. The Canonical Obligation Sentence

Every compliance obligation should be expressible as:

```
[SUBJECT] [MODAL] [ACTION]
  [INSTRUMENT / AUTHORITY]
  [BY WHEN / DUE DATE]
  [HOW OFTEN]
  [IF (conditions)]
  [UNLESS (exemptions / carve-outs)]
  [SUBJECT TO (thresholds)]
  [CONSEQUENCES IF NOT DONE]
  [SOURCE]
```

**Worked example — GSTR-3B Monthly:**

```
SUBJECT:     Every GST-registered business under the regular scheme
             with monthly filing frequency
MODAL:       must
ACTION:      file Form GSTR-3B (summary return) and pay tax liability
AUTHORITY:   on the GST portal (gst.gov.in)
BY WHEN:     by the 20th of the month following the return period
             (state-specific: 22nd or 24th for QRMP taxpayers)
HOW OFTEN:   every calendar month
IF:          GST registration is active
             AND scheme is REGULAR
             AND filing frequency is MONTHLY
UNLESS:      no applicable statutory exemption for this obligation
THRESHOLDS:  turnover > ₹5 Cr = mandatory monthly; ≤ ₹5 Cr = QRMP eligible
CONSEQUENCES:
             Late fee: ₹50/day (max ₹10,000) — Section 47 CGST Act
             Interest: 18% p.a. on unpaid liability — Section 50 CGST Act
SOURCE:      Section 39, CGST Act, 2017 + Rule 61(1), CGST Rules, 2017
```

---

## 5. Component-Level Specification

### WHO Component

Expressed via:
- `entity_types_applicable` (entity type filter)
- `applicability_rule.rule_expression` conditions on: `gst_registered`, `employee_count`, `has_manufacturing`, etc.
- `registration_precondition_detail` (prior registration required)
- `entity_types_applicable = ["ALL"]` when no entity-type restriction exists

**Rule:** If the legal subject is "every person" → `["ALL"]`. If "every company" → `["PRIVATE_LIMITED", "PUBLIC_LIMITED", "OPC", "SECTION8_COMPANY"]`. If "every employer" under EPF → add employee threshold condition. Never assume entity scope beyond what the provision states.

### MODAL Component

Only mandatory obligations are included in the active master library. Permissive provisions (`may`, `can opt to`) are represented as `obligation_type: INDICATOR` or `applicability_status: RECOMMENDED` — never as `APPLICABLE` in the evaluation engine.

### ACTION Component

Expressed via `obligation_type` enum + `description_plain`. The action must be specific enough that a user understands exactly what must be done.

### BY WHEN Component

Expressed via the `due_date_rule` record. See C5 for the complete due-date encoding standard.

If BY WHEN cannot be determined from the current source, set `due_date_determinability: PERIOD_UNKNOWN`.

### HOW OFTEN Component

Expressed via `frequency_type` enum: MONTHLY, QUARTERLY, HALF_YEARLY, ANNUAL, ONE_TIME, EVENT_BASED, CONTINUOUS.

### IF Component (Triggering Conditions)

Expressed via the `applicability_rule.rule_expression` using structured condition nodes.

For each condition in the IF clause:
- Map to a business profile field
- Choose the correct node type (CONDITION, THRESHOLD, STATE_SPECIFIC, EVENT_TRIGGERED)
- Assign the correct confidence contribution

### UNLESS Component (Exemptions)

Expressed via NOT_APPLICABLE_IF nodes in the rule expression, or via `exemption_description` for conditions that cannot be programmatically evaluated (e.g., exemptions requiring human review of fact patterns).

### SUBJECT TO Component (Thresholds)

Expressed via THRESHOLD nodes in the rule expression. Use the `if_field_is_band` / `band_values_ambiguous` construct for turnover bands.

### CONSEQUENCES Component

Expressed via the `penalty_record` linked to this rule. Plain description in `consequence_summary`. See C6 for the complete consequence encoding standard.

### SOURCE Component

Expressed via the source link records in `compliance_source_link`. The primary obligation source carries `source_role: PRIMARY_OBLIGATION`. See C7 for the complete source provenance standard.

---

## 6. The Rule Decomposition Template

Before encoding a new rule, the populator must complete this decomposition template:

```
RULE DECOMPOSITION WORKSHEET
─────────────────────────────────────────────────────────────────

Rule under analysis:
  Act/Source: ________________________________________________
  Provision: ________________________________________________
  Version date: _____________________________________________

Component Extraction:
  WHO must comply?
    └─ Entity types: _______________________________________
    └─ Registration/status required: ________________________
    └─ Size/threshold: _____________________________________

  WHAT action is required?
    └─ Obligation type: ____________________________________
    └─ Specific action: ____________________________________
    └─ To which authority/portal: __________________________

  BY WHEN?
    └─ Timing language (verbatim): _________________________
    └─ Due date rule type: _________________________________
    └─ Due date formula: ___________________________________

  HOW OFTEN?
    └─ Frequency type: ____________________________________

  IF (conditions that must be true)?
    └─ Condition 1: _______________________________________
    └─ Business profile field: ____________________________
    └─ Condition 2: _______________________________________
    └─ Business profile field: ____________________________

  UNLESS (exemptions)?
    └─ Exemption 1: _______________________________________
    └─ Source for exemption: ______________________________

  SUBJECT TO (thresholds)?
    └─ Threshold: _________________________________________
    └─ Threshold field: ___________________________________
    └─ Threshold direction (above/below): __________________

  CONSEQUENCES?
    └─ Late fee: __________________________________________
    └─ Interest: __________________________________________
    └─ Penalty: ___________________________________________
    └─ Prosecution: _______________________________________
    └─ Source for consequences: ___________________________

  SOURCE QUALITY?
    └─ Confidence level: __________________________________
    └─ Ambiguity? (describe): _____________________________

Decomposition complete? [ ] Yes  [ ] No — pending: __________
```

---

## 7. What Cannot Be Expressed in This Pattern

Some obligations resist the canonical sentence because:

**a. The due date depends on an unknown event:** Use `due_date_determinability: EVENT_DEPENDENT` and prompt the user to provide the event date. The rule expression itself remains complete; the instance-level computation is pending.

**b. The obligation is continuous with no periodic cycle:** Use `frequency_type: CONTINUOUS` and `obligation_type: RECORD_KEEPING` or `INDICATOR`. No due date is generated. The obligation appears in the compliance list as an ongoing requirement.

**c. The obligation is an awareness indicator only:** Use `obligation_type: INDICATOR`. No action is tracked; no completion status is generated. The system shows the indicator as an informational item.

**d. Applicability requires professional judgment:** Use `requires_human_review: true` and set `applicability_status: HUMAN_REVIEW_REQUIRED` as the default output. Do not attempt to encode a rule expression that would produce a definitive APPLICABLE determination.

---

## 8. Edge Cases

**Multiple thresholds in the same rule:** A rule may have both an entity size threshold (≥20 employees) AND a salary threshold (employee earns ≤ ₹21,000). Both must be encoded. The entity threshold controls whether the establishment is covered. The salary threshold controls which employees within that establishment are eligible. These may require two distinct rule expressions: one for establishment applicability, one for employee-level eligibility.

**Rule that varies by state:** A Shops & Establishments registration is state-specific. The same canonical pattern applies, but the WHO includes a state check via the STATE_SPECIFIC node. The due-date rule may also vary by state. If variation is significant, create separate rule records per state rather than a single rule with complex state branches.

**Rule that has changed over time:** The current rule record represents the current version. The prior version is archived with `active_flag: false`. If a business needs to know what applied to them two years ago (for historical compliance review), the archived version is consulted. The canonical expression standard applies to both past and present versions independently.
