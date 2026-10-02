# C10 — Library Population Standard Operating Procedure
## Step-by-Step SOP for Adding and Maintaining Compliance Rules in the Master Library

---

## 1. Objective

Define the authoritative standard operating procedure (SOP) for every act of adding, modifying, reviewing, or retiring a rule in the master compliance library. This SOP governs the human process behind library population — who does what, in what sequence, using what tools, and with what sign-off.

This document does not define how the rule is encoded (that is C1–C7). It defines how the process of adding a rule to the library is managed.

---

## 2. Why It Matters to the Compliance Engine

The compliance library is the legal brain of the product. Its accuracy directly determines whether thousands of businesses receive correct or incorrect compliance guidance. A library with no population discipline will accumulate errors: incorrectly sourced rules, incomplete records shown as validated, superseded provisions treated as current, and encoding inconsistencies between rules entered by different people at different times.

This SOP imposes the structural rigor that prevents these failure modes. Every rule must pass through defined gates. No rule enters the active library by bypassing these gates.

---

## 3. Design Principles

**P1 — No rule is self-certifying.** The person who researches and drafts a rule may not be the same person who validates and approves it. Two-person review is required for any rule reaching `VALIDATED_PRIMARY` status.

**P2 — The SOP applies uniformly.** There is no fast path for "obvious" or "well-known" rules. GSTR-3B is just as subject to this process as a niche state labour law provision. Obviousness is not a substitute for source verification.

**P3 — Blocked rules are not silently abandoned.** If a rule cannot be fully validated (e.g., source cannot be retrieved), it is recorded in the library in a `PENDING_PRIMARY_CONFIRMATION` or `DEFERRED` state with an explanation. Nothing is dropped silently.

**P4 — The SOP is a living document.** As the population process matures and the library grows, this SOP may be refined. Version this document. All changes must be reviewed by the library owner.

**P5 — All work is traceable.** Every step in this SOP produces an artifact (a record, a note, a checklist entry) that is retained. If a rule is challenged, the entire work trail must be reconstructable from the library's internal records.

---

## 4. Roles and Responsibilities

| Role | Responsibility |
|------|---------------|
| **Library Populator** | Researches the legal provision, retrieves source text, drafts the rule record fields per C1–C7, and submits for review. May be a compliance analyst, CA, or trained researcher. |
| **Domain Reviewer** | Reviews the populated rule for legal accuracy, source quality, and field correctness. Must have domain expertise in the relevant compliance area (e.g., a GST expert reviews GST rules). May not be the same person as the Library Populator for the same rule. |
| **Library Owner** | Final approval authority for activating a rule into the library. Responsible for overall library coherence, versioning discipline, and escalation of unresolved items. |
| **QA Reviewer** | Applies the QA checklist (C12) as a structured gate check. May be the Domain Reviewer performing the checklist, or a separate person doing a final structured pass. |

For small teams, one person may hold multiple roles — but the rule that the drafter may not self-approve always stands. A Library Populator may also be the Domain Reviewer for a different rule (not one they drafted).

---

## 5. The Population Procedure — Eight Phases

---

### Phase 1: Rule Selection and Assignment

**Purpose:** Decide which rule is being added and assign it to a Library Populator.

**Inputs:** The population priority framework (C14) determines which rules are scheduled for population. The library owner maintains a queue.

**Steps:**
1. Library owner selects the next rule to populate from the priority queue (per C14).
2. Library owner assigns the rule to a Library Populator.
3. Library owner records the assignment in the library management log with: rule description, domain, assigned to, and target date.
4. Library Populator acknowledges the assignment and begins work.

**Output:** A work order entry in the library log with the rule identified, assigned, and dated.

---

### Phase 2: Legal Research and Source Retrieval

**Purpose:** Locate and confirm the primary source for the rule.

This phase follows the C2 Translation Procedure (Steps 1–3) and the C7 Source Qualification Standard.

**Steps:**
1. Library Populator identifies the governing Act and the specific provision reference.
2. Library Populator retrieves the actual provision text from the official source (not from a blog, commentary, or memory). The source must be from the official government website (.gov.in domain, Ministry website, or official Gazette).
3. Library Populator records the `official_url`, verifies it loads correctly, and records `url_verified: true` with `url_verified_on` as today's date.
4. Library Populator assesses the source confidence level (HIGH / MEDIUM / LOW per C2 Step 9).
5. Library Populator identifies any subordinate legislation (Rules, Notifications) that supplement or modify the primary provision.
6. Library Populator retrieves all required supplementary sources (due date rule, penalty rule, applicability threshold, if these come from separate instruments).

**Disqualifying condition:** If the primary source cannot be retrieved from an official channel after reasonable effort (see C2 Section 4, Step 1 disqualifying condition), the Library Populator records the rule as `validation_state: PENDING_PRIMARY_CONFIRMATION`, documents what was searched and not found, and escalates to the Library Owner for a decision on whether to defer or continue effort.

**Output:** Source records drafted in `source_master` with all required fields populated. `url_verified` confirmed.

---

### Phase 3: Rule Decomposition

**Purpose:** Fully decompose the legal provision into its logical components before encoding any fields.

This phase uses the C3 Rule Decomposition Worksheet.

**Steps:**
1. Library Populator completes the Rule Decomposition Worksheet for the obligation:
   - WHO must comply (entity types, registration, size threshold)
   - WHAT action is required (obligation type, specific action, authority)
   - BY WHEN (timing language verbatim; due date rule type)
   - HOW OFTEN (frequency type)
   - IF conditions (triggering conditions + business profile field mapping)
   - UNLESS exemptions (with source for each)
   - SUBJECT TO thresholds
   - CONSEQUENCES (types and amounts per C6)
   - SOURCE QUALITY (confidence, ambiguity notes)
2. Library Populator confirms every component has been addressed. If any component is unknown, it is flagged explicitly (e.g., "PENALTY: source not yet retrieved, will enter as PARTIALLY_VALIDATED").
3. Library Populator verifies the canonical obligation sentence (C3 Section 4) can be written for this rule. If it cannot, the reason is documented and the limitation is recorded in `interpretation_notes`.

**Output:** Completed Rule Decomposition Worksheet. The worksheet itself is not stored in the database but must be referenced in `reviewer_notes` or retained in a linked document.

---

### Phase 4: Field Encoding

**Purpose:** Translate the decomposed rule into structured field values per the C1 schema.

**Steps:**
1. Library Populator creates a new rule record in the library management interface with `validation_state: DRAFT`.
2. Library Populator populates fields in the order defined in C2 Step 10:
   - Identity fields (compliance_code, title, version_number)
   - Classification fields (domain, category, obligation_type, frequency_type, jurisdiction)
   - Legal basis fields (governing_act, primary_provision_reference, operative_legal_text, description_plain)
   - Applicability and trigger fields (entity_types_applicable, applicability_rule_id, threshold_fields_involved, etc.)
   - Timing fields (due_date_rule_id, due_date_determinability, due_date_formula_plain)
   - Consequence fields (penalty_record_id, consequence_summary, base_severity_score, severity_band)
   - Lifecycle/trust fields (validation_state, source_confidence_level, interpretation_ambiguity_flag, etc.)
3. Library Populator links all source records to the compliance rule record via `compliance_source_link` with appropriate `source_role` values per C7.
4. Library Populator populates the linked `applicability_rule.rule_expression` per C4 node types.
5. Library Populator populates the linked `due_date_rule` record per C5 rule types.
6. Library Populator populates the linked `penalty_record` per C6 consequence data model.
7. Library Populator records `validation_state: PENDING_PRIMARY_CONFIRMATION` once all known fields are populated.
8. Library Populator completes any `interpretation_notes` for ambiguous elements.

**Output:** A rule record with all knowable fields populated, source links attached, and validation state set appropriately. The record is NOT yet in PARTIALLY_VALIDATED or VALIDATED_PRIMARY state.

**Compliance_code assignment discipline:** The Library Populator proposes a `compliance_code` following the pattern `{DOMAIN}_{SUBJECT}_{FREQUENCY}_{VARIANT}`. The Library Owner reviews and confirms the code before it is locked. Once a rule is activated, the code is immutable.

---

### Phase 5: Domain Review

**Purpose:** Expert review of the rule's legal accuracy by a Domain Reviewer.

**Steps:**
1. Library Populator submits the draft record to the assigned Domain Reviewer with: the draft rule record, the source documents retrieved, and the completed Rule Decomposition Worksheet.
2. Domain Reviewer independently reads the source text (not relying solely on the Library Populator's extraction).
3. Domain Reviewer checks each of the following:
   - Is the `operative_legal_text` correctly quoted verbatim from the primary source?
   - Is the `primary_provision_reference` exact and correctly cited?
   - Are the WHO / WHAT / BY WHEN / IF / UNLESS components correctly encoded?
   - Is the `applicability_rule_expression` logically correct — does it evaluate correctly for an obvious positive case and an obvious negative case?
   - Is the `due_date_formula_plain` correct in plain language?
   - Are the penalty/consequence fields correctly drawn from the statute, without fabrication or extrapolation?
   - Are any exemptions or carve-outs that exist in the statute correctly reflected?
   - Is the `source_confidence_level` assigned correctly?
4. Domain Reviewer records findings in `reviewer_notes`.
5. If corrections are required: Domain Reviewer returns to Library Populator with specific corrections. Library Populator makes corrections and resubmits.
6. If the record is satisfactory: Domain Reviewer endorses it for QA review.

**Typical domain assignments:**
- GST rules → GST domain reviewer
- Income Tax / TDS rules → income tax domain reviewer
- MCA/LLP rules → company law domain reviewer
- Labour law rules → labour law domain reviewer (Payment of Bonus, EPF, ESI, Gratuity)

**Output:** Domain-reviewed and endorsed rule record, ready for QA checklist.

---

### Phase 6: QA Checklist Execution

**Purpose:** Structured gate check using the QA Checklist defined in C12.

**Steps:**
1. QA Reviewer applies every item in the C12 checklist to the rule record.
2. QA Reviewer marks each checklist item as PASS, FAIL, or N/A.
3. If any mandatory item FAILS, the rule record is returned to the Library Populator with the specific failures noted. The Library Populator corrects and resubmits for QA.
4. If all mandatory items PASS, the QA Reviewer records the checklist completion in `reviewer_notes` with the date and their name.

**Output:** Completed QA checklist documented in the rule record. All mandatory QA items PASS.

---

### Phase 7: Library Owner Activation

**Purpose:** Final approval and state transition to VALIDATED_PRIMARY (or PARTIALLY_VALIDATED).

**Steps:**
1. Library Owner reviews the Domain Reviewer endorsement and QA checklist completion.
2. Library Owner confirms that:
   - The `compliance_code` is correctly formed and unique.
   - The rule fits correctly within the library's taxonomy (no duplicates, no overlap with existing rules).
   - The `library_version` field is correctly set to the current library version.
3. Library Owner transitions `validation_state` to `VALIDATED_PRIMARY` (if all sources are confirmed) or `PARTIALLY_VALIDATED` (if documented gaps remain).
4. Library Owner sets `active_flag: true`.
5. Library Owner sets `effective_from` to the date the rule becomes operative in the library.
6. Library Owner records in the `library_meta` table: version number, date, description of what was added.

**Output:** Rule is now active in the library. Instance computation for affected businesses can begin.

---

### Phase 8: Post-Activation Maintenance

**Purpose:** Ongoing review, update, and versioning of active rules.

**Steps and schedule:**
1. **Periodic re-verification:** Every rule in the library must have `review_due_by` set. This is automatically computed as `last_reviewed_at + 90 days` for rate/threshold rules, and `last_reviewed_at + 180 days` for stable statutory provisions. Rules past their `review_due_by` date generate a review alert.

2. **Rate/threshold changes:** When a notification changes a threshold, rate, or due date (common for GST, TDS rates):
   - If the change is a temporary extension (notification_extension): Create a new `notification_extension` record. Do NOT create a new rule version.
   - If the change is a permanent amendment to the rule's terms: Create a new rule record version per C7 versioning protocol.

3. **Amendment-triggered versioning:** When an Act, Rules, or permanent notification changes the rule's obligation, applicability, or consequence:
   - Follow C7 versioning protocol: set `effective_to` on current version, create new version, link via `predecessor_id`.
   - The Domain Reviewer and Library Owner must approve the new version.

4. **Correction of discovered errors:** If an error is found in an active rule:
   - If the error is in a non-immutable field (e.g., `description_plain`, `consequence_summary`): correct the field, increment `version_number`, record the correction in `reviewer_notes`.
   - If the error is in an immutable field (`compliance_code`, `compliance_id`, `operative_legal_text`): this requires creating a new rule version. The old version is marked SUPERSEDED.
   - All corrections require Domain Reviewer and Library Owner approval.

5. **Deactivation of rules that no longer apply:** When a compliance obligation is abolished or no longer relevant:
   - Set `active_flag: false` and `effective_to` on the current rule version.
   - Record the deactivation source (the amendment Act or notification) as a new source record linked to the rule.
   - Do NOT delete the record.

---

## 6. Population Throughput Expectations

Library population is time-intensive when done correctly. The following estimates are based on the steps above:

| Rule Type | Estimated Populator Time | Estimated Review Time | Total Cycle Time |
|-----------|--------------------------|----------------------|-----------------|
| Simple annual filing (stable Act) | 2–3 hours | 1–2 hours | 1–2 days |
| Monthly/quarterly GST return | 3–4 hours (staggered state data) | 2–3 hours | 2–3 days |
| State-specific rule (one state) | 2–3 hours per state | 1–2 hours | 1–2 days |
| Event-based corporate filing | 2 hours | 1 hour | 1 day |
| Complex threshold rule (turnover-based) | 3–5 hours | 2–4 hours | 2–3 days |
| Rule with statute/portal divergence | 4–6 hours (research intensive) | 3–4 hours | 3–5 days |

These estimates assume the primary source is locatable. Rules where the primary source requires extended research (e.g., certain state-level notifications) may take significantly longer.

**Realistic MVP library target:** 40–60 rules, at average 1.5 working days per rule with review = approximately 60–90 working days of total effort for initial library population.

---

## 7. Exception Handling

**What to do when the official source URL is dead:**
1. Search for the document on alternative official channels (National Legislation website, IndiaCode, official Ministry archive).
2. If found on an alternative official URL, record the new URL and set `url_verified: true`.
3. If not found: Set `url_verified: false`, record the search history in `source_notes`, and set `validation_state: PARTIALLY_VALIDATED` (not VALIDATED_PRIMARY — a rule without a verifiable live URL does not meet VALIDATED_PRIMARY criteria).

**What to do when two domain reviewers disagree:**
1. Escalate to Library Owner.
2. Library Owner may seek an independent third opinion (from a CA firm or legal practitioner).
3. If disagreement persists, record both interpretations in `interpretation_notes`, set `interpretation_ambiguity_flag: true`, and assign `validation_state: HUMAN_REVIEW_REQUIRED`.
4. Do not force a resolution that neither reviewer is confident in.

**What to do when a new notification changes a rule shortly after it was activated:**
1. Treat as any other amendment: follow Phase 8 (maintenance) steps.
2. If the notification was issued but the system has not yet updated and a business has already been shown the wrong due date:
   - Update the rule and add a `notification_extension` record.
   - Set `is_stale: true` on all affected instance records.
   - Recompute affected instances before the next time the business views their compliance dashboard.

---

## 8. What Should Be Deferred

**Automated SOP workflows** (task assignment, checklist submission, review routing via software) are a Phase 2 library management infrastructure item. For MVP, the SOP is executed manually using the tools available (document sharing, spreadsheets for tracking, direct database entry).

**Machine-assisted source retrieval** (automated fetching of source documents from government websites) is a Phase 2 technical capability. For MVP, all source retrieval is manual.

**SLA enforcement and escalation automation** (automatically flagging overdue review tasks) is a Phase 2 operational feature. For MVP, the Library Owner monitors the population queue manually.

---

## 9. Recommended Conclusion

This SOP defines eight phases that every compliance rule must pass through before entering the active library. The process is deliberately thorough because the consequence of error — incorrect compliance guidance to businesses — is serious.

The two most important gates are Phase 2 (source retrieval — no rule enters the library without its primary source text being read) and Phase 5 (domain review — no rule is self-certified). These two gates alone prevent the most common failure modes in compliance product libraries.

The SOP should be treated as a living document. As the library grows and the team gains experience, certain steps may be streamlined without compromising accuracy. Any such changes must be reviewed, documented, and approved by the Library Owner.
