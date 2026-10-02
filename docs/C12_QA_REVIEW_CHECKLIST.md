# C12 — QA Review Checklist
## Pre-Activation Quality Assurance Checklist for Each Compliance Rule Record

---

## 1. Objective

Define the structured checklist that every compliance rule record must pass before it is activated in the master library (`active_flag = true`, `validation_state = VALIDATED_PRIMARY` or `VALIDATED_SECONDARY`). The checklist provides a systematic gate that prevents incomplete, incorrectly sourced, or poorly encoded rules from reaching end users.

---

## 2. Why It Matters to the Compliance Engine

Without a structured QA gate, errors in rule records reach production. A rule with a wrong due date will show the wrong deadline to every business it applies to. A rule with an unsupported penalty claim will overstate risk. A rule with an incorrect applicability expression will either miss businesses that should be alerted or flag businesses that should not be.

The QA checklist is the last line of defense before a rule becomes visible to users. It is not a formality — it is the mechanism by which the library owner can certify that a rule meets the minimum standard of accuracy.

---

## 3. Design Principles

**P1 — All MANDATORY items must PASS before activation.** No exceptions, no partial waivers. A single mandatory FAIL means the rule does not activate.

**P2 — RECOMMENDED items are reviewed and documented.** If a RECOMMENDED item cannot be satisfied, the reason must be recorded in `reviewer_notes`. It does not block activation but is flagged for follow-up.

**P3 — The checklist is completed by the QA Reviewer.** The Library Populator does not self-certify. The QA Reviewer must be different from the person who drafted the rule record.

**P4 — Checklist results are preserved.** The date of checklist completion, the reviewer's name, and the result of each item must be recorded in `reviewer_notes` before the Library Owner proceeds to activation.

**P5 — The checklist applies equally to new rules and amended rules.** When a rule is updated to create a new version (C7 versioning), the new version must pass the full QA checklist before activation, regardless of how minor the change appears.

---

## 4. How to Use This Checklist

**For each item:**
- Mark **PASS** if the item is satisfied
- Mark **FAIL** if the item is not satisfied (record the specific failure in the FAIL Notes column)
- Mark **N/A** if the item is genuinely not applicable to this rule type (e.g., "due date source confirmed" is N/A for a CONTINUOUS obligation with no due date)
- Mark **DEFER** only for RECOMMENDED items where satisfaction is planned but not yet possible

**MANDATORY items with FAIL status:** Return the rule to the Library Populator for correction. Do not activate.

**RECOMMENDED items with FAIL or DEFER status:** Record in `reviewer_notes`. Activate only after Library Owner acknowledges the gap.

---

## 5. THE QA CHECKLIST

---

### SECTION A — IDENTITY AND CODE

| # | Item | Priority | Result | Fail Notes |
|---|------|----------|--------|------------|
| A1 | `compliance_code` follows the naming pattern `{DOMAIN}_{SUBJECT}_{FREQUENCY}_{VARIANT}` | MANDATORY | | |
| A2 | `compliance_code` is unique — no other active rule in the library has the same code | MANDATORY | | |
| A3 | `title` clearly identifies the obligation without abbreviation; a non-specialist can read it and understand what is required | MANDATORY | | |
| A4 | `version_number` is set to 1 (for new rules) or correctly incremented (for amended rules) | MANDATORY | | |
| A5 | If this is a replacement for a prior rule: `predecessor_id` is correctly set to the prior rule's `compliance_id` | MANDATORY (if replacement) | | |

---

### SECTION B — LEGAL BASIS

| # | Item | Priority | Result | Fail Notes |
|---|------|----------|--------|------------|
| B1 | `governing_act` is the full official name of the Act (not abbreviated) | MANDATORY | | |
| B2 | `primary_provision_reference` is specific to the section and sub-section level. "Section 39(1)" is acceptable. "Section 39" alone is acceptable only if the full section is the provision. "The Act" or "GST Rules" alone is NOT acceptable | MANDATORY | | |
| B3 | `operative_legal_text` contains a verbatim quote from the primary source, not a paraphrase | MANDATORY | | |
| B4 | The verbatim text in `operative_legal_text` can be verified against the confirmed source document | MANDATORY | | |
| B5 | `description_plain` is written in plain language understandable to a non-legal business owner | MANDATORY | | |
| B6 | If there are provisos or exemptions in the source text, they are reflected (either in `exemption_description` or in `applicability_rule` NOT_APPLICABLE_IF nodes) | MANDATORY | | |
| B7 | `legal_basis_summary` is present and provides adequate professional context | RECOMMENDED | | |

---

### SECTION C — SOURCE QUALITY AND VERIFICATION

| # | Item | Priority | Result | Fail Notes |
|---|------|----------|--------|------------|
| C1 | The `compliance_source_link` table contains at least one source with `source_role: PRIMARY_OBLIGATION` | MANDATORY | | |
| C2 | The primary source is of qualifying type: ACT, RULES, NOTIFICATION, or GAZETTE (per C7 qualification standard) | MANDATORY | | |
| C3 | `url_verified = true` for the primary obligation source | MANDATORY | | |
| C4 | `url_verified_on` is within the last 90 days | MANDATORY | | |
| C5 | `source_confidence_level` is correctly assigned (HIGH/MEDIUM/LOW per C2 Step 9 criteria) | MANDATORY | | |
| C6 | If the due date comes from subordinate legislation (Rules/Notification), a source with `source_role: DUE_DATE_RULE` is linked | MANDATORY (if COMPUTABLE) | | |
| C7 | If penalties come from a separate provision, a source with `source_role: PENALTY_RULE` is linked | MANDATORY (if penalty record populated) | | |
| C8 | If applicability threshold comes from a notification, a source with `source_role: THRESHOLD_RULE` is linked | MANDATORY (if threshold is notification-based) | | |
| C9 | All linked sources have `is_currently_active = true` (no linked source has been superseded by a newer notification) | MANDATORY | | |
| C10 | If `portal_vs_statute_divergence` is true on any linked source, this is documented in `interpretation_notes` and reflected in the rule's display treatment | MANDATORY (if applicable) | | |

---

### SECTION D — APPLICABILITY LOGIC

| # | Item | Priority | Result | Fail Notes |
|---|------|----------|--------|------------|
| D1 | `entity_types_applicable` correctly identifies which legal entity types are subject to this obligation | MANDATORY | | |
| D2 | The `applicability_rule_expression` has been reviewed and produces the correct output for at least one obvious positive test case (a business that definitely should be APPLICABLE) | MANDATORY | | |
| D3 | The `applicability_rule_expression` has been reviewed and produces the correct output for at least one obvious negative test case (a business that definitely should be NOT_APPLICABLE) | MANDATORY | | |
| D4 | Every exemption or carve-out in the source text that affects applicability is reflected in the rule expression (as NOT_APPLICABLE_IF nodes or in `exemption_description`) | MANDATORY | | |
| D5 | All fields listed in `threshold_fields_involved` actually appear as condition fields in the `applicability_rule_expression` | MANDATORY | | |
| D6 | `requires_event_trigger` and `event_trigger_description` are correctly populated for event-based obligations | MANDATORY (if event-based) | | |
| D7 | `requires_registration_precondition` is correctly set (e.g., true for all GST obligations) | MANDATORY | | |
| D8 | `applicability_rule_summary` matches the logic in the rule expression | MANDATORY | | |
| D9 | Edge cases identified in the Rule Decomposition Worksheet are addressed in the rule expression or documented | RECOMMENDED | | |

---

### SECTION E — DUE DATE ENCODING

| # | Item | Priority | Result | Fail Notes |
|---|------|----------|--------|------------|
| E1 | `due_date_determinability` is correctly assigned per the C5 taxonomy | MANDATORY | | |
| E2 | `due_date_formula_plain` correctly describes the due date in plain language | MANDATORY | | |
| E3 | If `due_date_determinability = COMPUTABLE`, the linked `due_date_rule` record encodes the correct rule type (FIXED_ANNUAL, OFFSET_FROM_PERIOD_END, etc.) per C5 | MANDATORY | | |
| E4 | The encoded due date rule produces the correct expected due date when computed for a sample period (manually verify: run the formula mentally for one period) | MANDATORY | | |
| E5 | If `state_based_variation = true` in the due date rule, the `state_offset_rules` array is correctly populated and confirmed from sources | MANDATORY (if state variation exists) | | |
| E6 | `financial_year_dependency` and `assessment_year_dependency` are correctly set | MANDATORY | | |
| E7 | `extension_possible` is correctly set (almost always TRUE for government filings) | MANDATORY | | |
| E8 | Special cases (March override for TDS deposit, AGM-based filings) are correctly handled | MANDATORY (if applicable) | | |

---

### SECTION F — PENALTY AND SEVERITY

| # | Item | Priority | Result | Fail Notes |
|---|------|----------|--------|------------|
| F1 | `consequence_summary` is present for RETURN_FILING, TAX_PAYMENT, REGISTRATION, and GOVERNANCE obligation types | MANDATORY | | |
| F2 | Every consequence stated in `consequence_summary` is traceable to a specific statutory provision | MANDATORY | | |
| F3 | No consequence is stated that cannot be confirmed from the source (no fabricated or inferred penalties) | MANDATORY | | |
| F4 | If `prosecution_possible = true`, `prosecution_notes` includes a calibration note explaining the practical risk level (per C6 Section 4) | MANDATORY (if prosecution possible) | | |
| F5 | `base_severity_score` has been computed from the penalty record fields using the C6 scoring model, not estimated manually | MANDATORY (if penalty record exists) | | |
| F6 | `severity_band` is correctly derived from `base_severity_score` per the C6 band table | MANDATORY (if base_severity_score exists) | | |
| F7 | If any consequence field has `late_fee_confidence = LOW` or `prosecution_confidence = LOW`, this is reflected in `validation_notes` and the severity computation uses the confidence-adjusted formula | MANDATORY (if confidence is LOW) | | |
| F8 | Operational/downstream impacts (expense disallowance, blocked filings) are encoded in the correct `penalty_record` operational impact fields, not in `consequence_summary` | RECOMMENDED | | |

---

### SECTION G — LIFECYCLE AND TRUST

| # | Item | Priority | Result | Fail Notes |
|---|------|----------|--------|------------|
| G1 | `validation_state` is appropriately set for the level of confirmation achieved | MANDATORY | | |
| G2 | If `validation_state` is not `VALIDATED_PRIMARY`, `validation_notes` explains why and what remains pending | MANDATORY (if not VALIDATED_PRIMARY) | | |
| G3 | `interpretation_ambiguity_flag` is set correctly — TRUE if any ambiguity exists, not suppressed to avoid disclosure | MANDATORY | | |
| G4 | If `interpretation_ambiguity_flag = true`, `interpretation_notes` describes the ambiguity, the competing interpretations, and the adopted interpretation | MANDATORY (if flag is TRUE) | | |
| G5 | `requires_human_review` is correctly set — TRUE for FEMA, regulated sectors, complex transfer pricing, and any rule in HUMAN_REVIEW_REQUIRED state | MANDATORY | | |
| G6 | If `requires_human_review = true`, `human_review_reason` is populated with a clear explanation | MANDATORY (if TRUE) | | |
| G7 | `effective_from` is correctly set to the date this obligation has been in force | MANDATORY | | |
| G8 | `last_reviewed_at` is set to today's date (date of QA completion) | MANDATORY | | |
| G9 | `review_due_by` is set to the correct future date per the review interval guidelines | MANDATORY | | |
| G10 | `library_version` reflects the current library version number | MANDATORY | | |

---

### SECTION H — CONSISTENCY AND COHERENCE

| # | Item | Priority | Result | Fail Notes |
|---|------|----------|--------|------------|
| H1 | The rule does NOT duplicate an obligation that already exists in the library under a different `compliance_code`. (A new rule covers a genuinely distinct obligation, or is a correctly versioned replacement for an existing rule.) | MANDATORY | | |
| H2 | If this rule relates to other rules in the library (e.g., GSTR-9 depends on GSTR-3B), the dependency or cascade relationship is documented | RECOMMENDED | | |
| H3 | The `domain` is correctly assigned and matches the primary governing Act | MANDATORY | | |
| H4 | The `obligation_type` correctly reflects the nature of the required action | MANDATORY | | |
| H5 | The `frequency_type` correctly reflects the obligation cycle | MANDATORY | | |
| H6 | The `compliance_code` naming is consistent with similar rules already in the library (check domain prefix, subject naming style, frequency suffix) | MANDATORY | | |

---

### SECTION I — FINAL SIGN-OFF

| Item | Confirmed | Reviewer Notes |
|------|-----------|----------------|
| All MANDATORY items in Sections A–H are marked PASS or N/A | | |
| All FAIL items have been returned to Library Populator and corrected (if any) | | |
| All RECOMMENDED items with DEFER or FAIL are documented in `reviewer_notes` with reason | | |
| QA Reviewer name: _______________________________ | | |
| QA Review date: __________________________________ | | |
| Library Owner approval name: ____________________ | | |
| Library Owner approval date: _____________________ | | |
| Final `validation_state` assigned: _______________ | | |
| `active_flag` set to true: [ ] Yes [ ] No | | |

---

## 6. Fail Handling Procedure

**When a mandatory item FAILS:**
1. QA Reviewer documents the specific failure in the checklist notes.
2. QA Reviewer returns the rule record to the Library Populator with the failure list.
3. Library Populator addresses each failure and notifies QA Reviewer.
4. QA Reviewer re-runs only the failed items (does not need to re-run items that already PASSED in the previous round).
5. When all previously-failed mandatory items now PASS, proceed to Library Owner activation.

**When multiple rounds of correction are required:**
- Each correction cycle must be completed before re-review begins. No "fix one, review one" partial loops.
- If a rule requires more than three correction cycles, the Library Owner must be informed. Systemic issues in the population process should be addressed.

---

## 7. Domain-Specific Notes

**GST rules:** State staggering due dates require special attention (Checklist E5). The `state_offset_rules` array must be confirmed from the actual notification (not assumed from memory). For QRMP rules, state groups A and B must be verified from Notification 84/2020-CT or its successors.

**Income Tax / TDS rules:** The interaction between multiple TDS sections on the same payment type (e.g., 194Q vs. 206C(1H)) must be reflected in `interpretation_notes`. Set `interpretation_ambiguity_flag = true` where such interactions create uncertainty.

**MCA company rules:** Small company definition (₹4 Cr paid-up + ₹40 Cr turnover per 2022 amendment, confirmed in doc 24 GAP-3) affects MGT-7 vs. MGT-7A applicability. Verify this threshold is correctly encoded in all MCA company applicability rules.

**Labour law rules:** Establishment size thresholds (≥20 employees for EPF, ≥10 for ESI, ≥20 for Bonus Act) must be correctly encoded as THRESHOLD nodes with the band-field fallback for approximate employee counts.

**State-specific rules:** Rules with `jurisdiction = SPECIFIC_STATES` must have the state list confirmed from the actual governing state Act for each covered state. Rules for states not yet researched should remain `PENDING_PRIMARY_CONFIRMATION`, not `VALIDATED_PRIMARY`.

---

## 8. What Should Be Deferred

**Automated checklist tooling** (a library management application that presents this checklist interactively, records results per item, and enforces the PASS requirement before activation) is a Phase 2 library management system feature. For MVP, the checklist is applied manually.

**AI-assisted consistency checking** (automatically verifying that `threshold_fields_involved` matches the rule expression, or that the `consequence_summary` cites provisions that exist in the linked sources) is a Phase 2 tooling capability.

---

## 9. Recommended Conclusion

This checklist represents 39 structured gate items across 9 sections. When executed rigorously, it catches the most common failure modes in compliance library population: incorrect sourcing, wrong due dates, applicability expressions that don't match the source, and undisclosed ambiguities.

The checklist should not be experienced as bureaucratic friction. It is the minimum quality bar required for a product that advises businesses on legal obligations. Every item that gets marked PASS is evidence that a user of the product will receive accurate information on that dimension. Every item that gets marked FAIL before activation is a user-facing error that was caught in time.
