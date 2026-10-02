# C9 — Master-to-Instance Mapping Standard
## How a Generic Compliance Rule Becomes a Business-Specific Obligation

---

## 1. Objective

Define the formal boundary between the master library layer and the instance layer, specify the mapping procedure by which a generic compliance rule is evaluated against a specific business profile to produce a business-specific compliance obligation, and establish the data structures that record the result of that mapping.

---

## 2. Why It Matters to the Compliance Engine

The master library records what the law says. The instance layer records what the law means for a particular business. These are fundamentally different things. A rule that says "every employer of 20 or more persons must pay bonus by November 30" exists in the master library as a generic obligation. Whether it applies to "ABC Pvt Ltd, a 25-employee technology company in Bengaluru" is an instance-level determination that requires evaluating the rule against that specific business profile.

If this separation is not maintained rigorously:

- Changes to the law (master layer) cannot be automatically propagated to all affected businesses.
- Business-specific outputs cannot be regenerated cleanly when a business updates its profile.
- Audit trails become muddled — it becomes unclear whether a change in a compliance output was caused by a change in the law or a change in the business's facts.
- The system cannot correctly serve thousands of businesses from a single shared library.

The master-to-instance mapping standard is what makes the compliance engine scalable, maintainable, and auditable.

---

## 3. Design Principles

**P1 — The master library has no knowledge of individual businesses.** No field in the master library records a specific business's name, registration number, or profile. The master library records the law; the instance layer records what the law means for a business.

**P2 — The instance layer has no knowledge of law.** Instance records do not store legal text, provision references, or source citations. They store computation outputs. The legal basis for a determination is traced by looking up the master rule that produced the instance.

**P3 — Instances are disposable and recomputable.** Every instance record is derived data. If the master library changes (a new notification, an amended rule) or the business profile changes (new employee hired, GST registration obtained), all affected instance records can be discarded and recomputed. No instance record contains data that cannot be regenerated from its inputs.

**P4 — One master rule → zero or more instances per business.** A rule may produce no instance for a business (because it does not apply), one instance (for annual or one-time obligations), or multiple instances per year (for monthly or quarterly obligations). The instance count is driven by the rule's `frequency_type` and the business's applicable period.

**P5 — The instance records the determination, not the logic.** An instance record says "GSTR-3B Monthly is APPLICABLE to Business X for July 2025 with due date August 20, 2025 and severity HIGH." It does not re-store the applicability rule expression or the due date formula. Those live in the master layer and are referenced by foreign key.

---

## 4. The Three-Layer Architecture (Recap and Formalization)

This was introduced in C4 (Three-Layer Separation). C9 formalizes the mapping procedure between the layers.

```
LAYER 1 — MASTER LIBRARY (shared, static until law changes)
  Contents: compliance_master, applicability_rule, due_date_rule, penalty_record, source_master
  Answers: "What does the law require, of whom, by when, with what consequences?"
  Changes when: Law changes, new notification, library population decisions

LAYER 2 — BUSINESS PROFILE (per-business, changes when business facts change)
  Contents: business_profile fields
  Answers: "What are the facts about THIS specific business?"
  Changes when: Business updates profile (new employees, new registration, etc.)

LAYER 3 — COMPLIANCE INSTANCE (per-business per-period, derived)
  Contents: business_compliance_output, computed_due_date
  Answers: "Does THIS law apply to THIS business for THIS period?"
  Changes when: Layer 1 changes (master library update) OR Layer 2 changes (profile update)
```

The mapping procedure takes Layer 1 + Layer 2 as inputs and produces Layer 3 as output.

---

## 5. The Mapping Procedure

The mapping procedure runs once per (business, compliance_rule) pair, per period. The procedure has four stages:

---

### Stage 1: Applicability Evaluation

**Input:** The `applicability_rule.rule_expression` from the master library + the `business_profile` of the specific business.

**Process:** The rule expression is evaluated against the business profile using the node evaluation algorithm defined in C4 (Section 5) and doc 08 (Section 5).

**Output:** An `applicability_status` value (APPLICABLE, LIKELY_APPLICABLE, CHECK_THRESHOLD, EVENT_TRIGGERED, STATE_SPECIFIC, NOT_APPLICABLE, INSUFFICIENT_DATA, HUMAN_REVIEW_REQUIRED, FUTURE_TRIGGER) and an `applicability_confidence` level (HIGH, MEDIUM, LOW), plus a human-readable `why_it_applies` explanation.

**Instance fields populated at this stage:**
- `applicability_status`
- `applicability_confidence`
- `why_it_applies`
- `why_it_may_not_apply`
- `missing_inputs` (list of profile fields that would improve confidence)
- `threshold_basis`
- `state_dependency_basis`
- `human_verification_required`

**Termination conditions:**
- If `applicability_status = NOT_APPLICABLE` → no further stages run; no instance record is created (or an archived NOT_APPLICABLE record is maintained for audit purposes).
- If `applicability_status = INSUFFICIENT_DATA` → stages 2 and 3 are skipped; the instance is created in a "pending more info" state.
- If `applicability_status = HUMAN_REVIEW_REQUIRED` → stage 2 proceeds with provisional due dates only; stage 3 is skipped.

---

### Stage 2: Due Date Computation

**Runs when:** `applicability_status` is APPLICABLE, LIKELY_APPLICABLE, CHECK_THRESHOLD, or EVENT_TRIGGERED.

**Input:** The `due_date_rule` record referenced by the master compliance rule + the current date + the business profile (for AGM date, event dates, financial year start) + any active `notification_extension` records.

**Process:** The due-date computation algorithm (defined in C5 and doc 05) is applied:

```
Step 1: Identify the rule_type (FIXED_ANNUAL, OFFSET_FROM_PERIOD_END, etc.)
Step 2: Apply the appropriate computation formula for that rule_type
Step 3: Apply state-based variation if state_based_variation = true
         (using principal_state from business profile)
Step 4: Apply working-day adjustment if working_day_rule = NEXT_WORKING_DAY
Step 5: Check for active notification_extension records for this compliance + period
Step 6: If active extension found → effective_due_date = extension.extended_due_date
Step 7: If no extension → effective_due_date = computed base due date
Step 8: Compute current period label, next period, and days-until/days-overdue
```

**Output fields populated at this stage:**
- `current_period_start`, `current_period_end`
- `filing_window_opens`
- `computed_due_date`
- `financial_year_label`
- `period_label`
- `is_overdue`, `overdue_days`, `due_in_days`
- `next_due_date`, `next_period_label`

**Determinability states:**
- `COMPUTABLE` → all above fields are populated with definitive values
- `EVENT_DEPENDENT` → `computed_due_date` is null; `why_it_applies` prompts for event date
- `AGM_DEPENDENT` → computed using AGM fallback date; flagged as provisional
- `CONTINUOUS` → `computed_due_date` is null; `period_label` = "Ongoing"
- `PERIOD_UNKNOWN` → `computed_due_date` is null; `period_label` = "Due date to be determined"

---

### Stage 3: Severity Computation

**Runs when:** `applicability_status` is APPLICABLE or LIKELY_APPLICABLE AND the compliance rule has a linked `penalty_record`.

**Input:** The `penalty_record` linked to the master compliance rule + `overdue_days` from Stage 2 + `source_confidence_level` from the master rule.

**Process:**
```
Step 1: Retrieve base_severity_score from penalty_record.computed_base_score
        (pre-computed from penalty fields per C6 scoring model)
Step 2: Retrieve overdue_days from Stage 2 output
Step 3: Apply time escalation: escalation_points = time_escalation_score(overdue_days)
Step 4: Apply confidence adjustment:
        if source_confidence_level = LOW → reduce base_severity by 50%
Step 5: combined_score = min(100, adjusted_base + escalation_points)
Step 6: Assign severity_band from combined_score (per C6 severity bands)
Step 7: Assign color_code from severity_band (per doc 06 color table)
```

**Output fields populated at this stage:**
- `base_severity_score`
- `dynamic_severity_score`
- `combined_severity_score`
- `severity_band`
- `color_code`

---

### Stage 4: Instance Record Creation and Storage

**When:** All applicable stages are complete.

The result of Stages 1–3 is persisted as a `business_compliance_output` record (per doc 04 Table 8). The `source_snapshot_version` field records the library version number at the time of computation, allowing detection of stale outputs.

**Staleness detection:** The `is_stale` flag on the instance record is set to `true` whenever:
- The master compliance rule it references is updated
- The due_date_rule or penalty_record linked to it changes
- An active notification_extension is added or expires
- The business profile is updated in a way that affects applicability conditions

When `is_stale = true`, the instance must be recomputed before it is shown to the user.

---

## 6. Master-to-Instance Cardinality Reference

| Frequency Type | Instances Per Business Per Year | Notes |
|---------------|--------------------------------|-------|
| ONE_TIME | 1 (in the year first applicable) | Registration, first filings |
| CONTINUOUS | 0 (no period instances) | Shows as ongoing item without due date |
| MONTHLY | 12 (one per calendar month) | Each month's return/payment |
| QUARTERLY | 4 (Q1–Q4 of FY) | Each quarter |
| HALF_YEARLY | 2 (H1 Apr–Sep, H2 Oct–Mar) | ESI return, MSME Form I |
| ANNUAL | 1 (one per FY) | ITR, GSTR-9, AOC-4, etc. |
| EVENT_BASED | 0 (until event occurs); 1 per event occurrence | Director changes, share allotments |
| AS_APPLICABLE | Varies | Sector-specific; determined per business profile |

For rules of type ADVANCE_TAX_INSTALLMENT, four instances are created per year (Q1–Q4 installments), each as a separate output record pointing to the same master rule but a different due-date sub-rule record.

---

## 7. Change Propagation Policy

When the master library changes, affected instance records must be recomputed. The following events trigger propagation:

| Event | Records Affected | Propagation Action |
|-------|-----------------|-------------------|
| Master rule `active_flag` set to `false` (superseded) | All instances referencing this rule | Mark all as stale; remove from active view after recomputation |
| Due-date rule updated (new notification changes deadline) | All instances for affected compliance in affected periods | Recompute due dates for all businesses in affected periods |
| Notification extension added | All instances for affected compliance in affected period | Recompute effective due date with extension |
| Notification extension expires | All instances for affected compliance in affected period | Recompute effective due date reverting to base |
| Penalty record updated | All instances for affected compliance | Recompute severity scores |
| Business profile field updated | All instances for business where that field is a condition | Reapply applicability evaluation; recompute due dates if needed |
| New master rule activated | All businesses → check if new rule applies | Run applicability evaluation for new rule against all profiles |

**Propagation is not retroactive for past periods.** If the GSTR-3B due date for March 2025 was shown as March 20 and is now extended to March 31 by a new notification, the March 2025 instance is updated. But if a business's compliance status for March 2025 was already marked as completed (manually), that completion record is preserved — the due date update only affects uncompleted instances.

---

## 8. The Instance Record as an Audit Snapshot

The `source_snapshot_version` field on every instance record records the library version under which the instance was computed. This allows the system to answer: "What was the user shown about this obligation on March 15, 2025?" — even if the library has been updated since.

This has two practical implications:

**For product integrity:** If a notification is entered into the library after a period has passed (e.g., a due date extension notification is added retroactively), the old instance record shows what the user would have seen before the notification was entered. This is important for explaining historical user behavior.

**For legal defensibility:** If a user claims they complied on time based on what the system showed them, the `source_snapshot_version` allows reconstruction of exactly what due date the system computed for them on any given date.

Instance records must never be deleted. They may be archived after a retention period (e.g., 7 years for Indian tax records) but must not be purged while the associated compliance period is within the statutory limitation period.

---

## 9. Edge Cases

**Business profile changes after compliance period ends:** If a business changes its `gst_registered` status from true to false after the GSTR-3B period has already passed, the historical instances for that period retain their original `applicability_status = APPLICABLE` determination. The de-registration only affects future periods.

**Rule that applies for only part of a period:** If a business crossed the EPF threshold (≥20 employees) mid-month, the EPF compliance applies from the month of crossing. The instance for the month of crossing should be created with a note in `why_it_applies` explaining the mid-period applicability start. Future instances are unaffected.

**Rule with AGM-dependent due date and AGM not yet held:** The instance is created with `due_date_determinability = AGM_DEPENDENT` and `computed_due_date` set to the AGM deadline (September 30) as the fallback. Once the actual AGM date is provided, the instance is updated with the precise due date. Both the fallback due date and the actual due date are preserved in the instance record.

**Business with multiple states and a state-specific rule:** For Professional Tax (state-specific), an instance is created per state where the business has presence. Each instance references the applicable state-specific master rule for that state. The aggregated view shows one PT item per applicable state. This is correct behavior, not duplication.

---

## 10. What Should Be Deferred

**Real-time propagation** — triggering instance recomputation automatically the moment a master rule changes — requires an event-driven messaging architecture. For MVP, propagation is batch-triggered (e.g., nightly) and instance records carry the `is_stale` flag to indicate they need recomputation.

**Cross-business analytics using instance data** — identifying which segment of businesses is affected by a specific rule change — is a Phase 2 operational feature.

**Historical compliance gap analysis** — comparing what the system showed vs. what the user actually filed, for periods prior to the user's onboarding — requires the user to provide their actual filing history. This is a Phase 2 feature.

---

## 11. Recommended Conclusion

The master-to-instance mapping standard establishes a clean, computationally deterministic pipeline from a generic legal rule to a business-specific compliance obligation. The key discipline is architectural: master data records the law, instance data records what the law means for a business, and the two layers must never be merged.

For every compliance period, for every applicable rule, for every business: the system can produce a fresh, auditable, traceable determination. When the law changes or the business changes, the affected instances are invalidated and recomputed. This separation is what makes the compliance engine reliable at scale.
