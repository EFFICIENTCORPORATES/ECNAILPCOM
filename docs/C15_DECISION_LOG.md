# C15 — Decision Log
## Residual Design Questions, Open Items, and Unresolved Decisions Requiring Review

---

## 1. Objective

Record all design decisions, residual ambiguities, and unresolved questions that emerged during Part C documentation and have not been fully resolved by C1–C14. Each item is categorized by domain, assessed for urgency and impact, and assigned a recommended resolution path.

This document is the institutional memory of what the design team knew, what it decided, and what it left open. Future contributors must read this document before making decisions in the areas it covers, to avoid unknowingly reversing or contradicting prior decisions.

---

## 2. Format

Each item follows this structure:
- **Item ID:** Stable reference code (e.g., DL-001)
- **Domain:** Which area of the system this affects
- **Status:** OPEN | RESOLVED | DEFERRED | SUPERSEDED
- **Impact:** CRITICAL | HIGH | MEDIUM | LOW
- **Decision Made (if any):** What was decided, and when
- **What Remains Open:** What still needs resolution
- **Recommended Resolution Path:** Steps to resolve
- **Target Phase:** MVP / Phase 2 / No deadline

---

## 3. ACTIVE OPEN ITEMS

---

### DL-001: GSTR-3B QRMP State Groups — Verification Required Before Activation

**Domain:** GST — Due Date Rule
**Status:** OPEN
**Impact:** CRITICAL

**Background:** The QRMP quarterly GSTR-3B compliance record (`GST_GSTR3B_QRMP_QUARTERLY`) requires a `state_offset_rules` array encoding which states are in Group A (22nd due date) and Group B (24th due date). The state groupings were established by Notification No. 84/2020-Central Tax dated 10.11.2020. The state groups as of August 2025 are documented in doc 23 B1. However, the following remain open:

1. Any amendment notification between Notification 84/2020-CT and June 2026 that may have altered the state groupings.
2. The author's knowledge cutoff is August 2025 — anything issued between August 2025 and June 2026 is unknown.

**Decision Made:** The GSTR-3B Monthly Regular record (all states = 20th) CAN be activated immediately. The GSTR-3B QRMP Quarterly record must NOT be activated until the state group verification is complete.

**What Remains Open:** Retrieve Notification 84/2020-CT from cbic.gov.in, confirm the exact state lists, and search for any amendment notifications issued after August 2023.

**Recommended Resolution Path:**
1. Access cbic.gov.in notifications section.
2. Retrieve Notification 84/2020-CT — read the state group lists in the notification text.
3. Search for all Central Tax notifications issued between 84/2020-CT and the current date that reference QRMP or GSTR-3B due dates.
4. Update the `state_offset_rules` in the due_date_rule record after confirmation.

**Target Phase:** MVP — CRITICAL BLOCKER for QRMP record

---

### DL-002: E-Invoicing Threshold — Post-August 2025 Status Unknown

**Domain:** GST — Applicability Rule
**Status:** OPEN
**Impact:** CRITICAL

**Background:** The e-invoicing applicability threshold was confirmed at ₹5 Cr AATO as of August 2025 (doc 23 B2). The GST Council had discussed further reduction to ₹1 Cr, but no notification was confirmed as of the author's knowledge cutoff. Current status as of June 2026 is unknown.

**Decision Made:** Populate the indicator record using ₹5 Cr as the threshold. Set `review_due_by` to 30 days from activation (not the standard 90 days) to force an immediate re-verification.

**What Remains Open:** Retrieve the current active e-invoicing threshold notification from cbic-gst.gov.in before activation. If the threshold has been reduced below ₹5 Cr, the applicability rule must be updated before the record goes live.

**Recommended Resolution Path:**
1. Access cbic-gst.gov.in notifications section.
2. Search for the most recent notification setting the e-invoicing threshold (look for notification series modifying Rule 48(4) CGST Rules or the original Notif. 13/2020-CT).
3. Confirm the current threshold value.
4. Update the THRESHOLD node in the applicability rule with the confirmed current threshold.
5. Link the notification as source with `source_role: THRESHOLD_RULE`.

**Target Phase:** MVP — CRITICAL BLOCKER for e-invoicing indicator record

---

### DL-003: ESI Return — Statute/Portal Divergence Unresolved

**Domain:** ESI — Due Date Rule and Obligation Type
**Status:** OPEN
**Impact:** CRITICAL for ESI return record; NON-BLOCKING for ESI contribution deposit

**Background:** Rule 26 of ESI (Central) Rules, 1950 requires a half-yearly return (Form 5) due by November 11 and May 11. However, ESIC's current portal practice requires monthly electronic submission of contribution and wage data. Whether Rule 26 has been formally amended to reflect monthly requirements, or whether an official ESIC circular has retired Form 5, is not confirmed (doc 23 B5). This is a genuine statute/portal divergence per C7 guidelines.

**Decision Made:** The ESI contribution deposit record (`ESI_CONTRIBUTION_DEPOSIT_MONTHLY`) is unaffected and can be populated immediately — the 15th-of-month payment due date is clear and stable. The ESI return record's due date and filing cycle are the blocked items.

**What Remains Open:**
1. Current text of Rule 26, ESI (Central) Rules, 1950 — from Ministry of Labour & Employment website.
2. Any official ESIC circular replacing or retiring Form 5.
3. Current ESIC portal (esic.gov.in) employer compliance requirements.

**Recommended Resolution Path:**
1. Retrieve Rule 26 text from official source.
2. Search ESIC website for circulars regarding Form 5 filing requirements.
3. If Rule 26 is unchanged and Form 5 still exists: encode as half-yearly with `portal_vs_statute_divergence: true` and display BOTH requirements.
4. If Rule 26 has been amended: encode per the amended requirement.

**Recommended interim approach:** Enter the ESI return compliance record with `validation_state: PARTIALLY_VALIDATED`, `requires_human_review: true`, `portal_vs_statute_divergence: true`, and `due_date_determinability: PERIOD_UNKNOWN` until research is complete.

**Target Phase:** MVP — CRITICAL BLOCKER for ESI return due date only

---

### DL-004: GSTR-9 Small Taxpayer Exemption — Annual Notification Check

**Domain:** GST — Applicability Rule
**Status:** OPEN
**Impact:** HIGH

**Background:** Section 44 CGST Act empowers CBIC to exempt small taxpayers from GSTR-9. CBIC has historically exempted AATO ≤ ₹2 Cr taxpayers via year-specific notifications. The exemption for FY2022-23 is confirmed (Notification 10/2023-CT). Exemptions for FY2023-24 and FY2024-25 are not confirmed from the author's knowledge (doc 23 B3).

**Decision Made:** Populate the GSTR-9 base record as APPLICABLE to all registered regular-scheme taxpayers. Add a `CHECK_THRESHOLD` flag for AATO ≤ ₹2 Cr businesses: "Likely exempt — verify current FY notification." Add the FY2022-23 exemption as a `notification_extension` record.

**What Remains Open:** Whether CBIC issued exemption notifications for FY2023-24 and FY2024-25. These must be researched and, if found, added as `notification_extension` records.

**Recommended Resolution Path:**
1. Access cbic-gst.gov.in — search for GSTR-9 annual return exemption notifications for FY2023-24 and FY2024-25.
2. If found: add as `notification_extension` records linked to `GST_GSTR9_ANNUAL`.
3. If not found: the base rule (APPLICABLE to all) stands; update the CHECK_THRESHOLD note to explain no exemption was found for those years.

**Target Phase:** MVP (base rule); FY-specific exemptions ongoing annual maintenance

---

### DL-005: Small Company Definition — Threshold Confirmation for MGT-7A Applicability

**Domain:** MCA Company — Applicability Rule
**Status:** OPEN
**Impact:** CRITICAL (per doc 24 GAP-3)

**Background:** The small company definition under Section 2(85) Companies Act 2013 was last amended in 2022: ₹4 Cr paid-up capital AND ₹40 Cr turnover. This distinction is critical for MGT-7 (large companies) vs. MGT-7A (small companies and OPCs). The current thresholds are confirmed from the 2022 amendment, but any post-August 2025 change is unknown.

**Decision Made:** The applicability rules for `MCA_MGT7_ANNUAL` and `MCA_MGT7A_ANNUAL` must use the ₹4 Cr / ₹40 Cr threshold per MCA Notification S.O. 1178(E) dated 15.03.2022.

**What Remains Open:** Whether any further amendment to the small company definition has been issued post-August 2025. Must be confirmed from mca.gov.in before activation.

**Recommended Resolution Path:**
1. Access mca.gov.in company law section.
2. Confirm current Section 2(85) definition.
3. Search for any amendment notification post-S.O. 1178(E) dated 15.03.2022.
4. Update applicability rules with confirmed current thresholds.

**Target Phase:** MVP — CRITICAL for MGT-7 vs. MGT-7A distinction

---

### DL-006: Obligation Type for Labour Payment Obligations

**Domain:** Data Dictionary — Enum Design
**Status:** OPEN
**Impact:** MEDIUM

**Background:** The Payment of Bonus Act obligation is a payment to employees, not a payment to the government. The closest `obligation_type` enum value is `TAX_PAYMENT`, but this is technically a misnomer. Similarly, gratuity payment and minimum wages payment are employer-to-employee obligations, not tax/government payments.

**What Was Considered:** Adding a new `obligation_type` value of `LABOUR_PAYMENT` to the enum. This would require a schema change and a migration if any records already use `TAX_PAYMENT` for labour obligations.

**What Remains Open:**
1. Should `obligation_type` include `LABOUR_PAYMENT` as a distinct value for employer-to-employee statutory payments?
2. Or should the current `TAX_PAYMENT` value be used with the understanding that it covers all mandatory periodic payments (including labour statutory payments)?

**Design recommendation:** Add `LABOUR_PAYMENT` as a new enum value. The semantic distinction matters for product features: a `TAX_PAYMENT` item may show a government payment portal link; a `LABOUR_PAYMENT` item would show payroll action guidance. Using `TAX_PAYMENT` for both conflates two different workflow types.

**Required Action:** Library Owner decision. If `LABOUR_PAYMENT` is added to the enum, update the data dictionary (C11) and the JSON schema (`compliance_master.schema.json`). If `TAX_PAYMENT` is retained as the value, add an explicit note to C11 that `TAX_PAYMENT` covers all mandatory periodic payments including labour statutory payments.

**Target Phase:** Must be resolved before any labour domain rules are activated

---

### DL-007: DIR-3 KYC — FIXED_ANNUAL Year Context Definition

**Domain:** MCA Company / LLP — Due Date Rule
**Status:** RESOLVED (with documentation note)
**Impact:** LOW

**Background:** Doc 24 GAP-6 corrected the due date encoding for DIR-3 KYC. The date is September 30 of the current financial year end year, not the Assessment Year. The `year_context` enum in C5 does not explicitly include a `CURRENT_FY_END_YEAR` value — it uses `CURRENT_FY_YEAR` and `AFTER_FY_END_YEAR`.

**Decision Made:** September 30 for DIR-3 KYC falls within the same calendar year as the FY end (March 31, 2026 → September 30, 2026). This is `CURRENT_FY_YEAR` context, not `AFTER_FY_END_YEAR` (which would be the following calendar year). The distinction: for March-FY businesses, `CURRENT_FY_YEAR` means "the calendar year April–March" and September 30 falls within this window. Encode as `FIXED_ANNUAL`, `fixed_day: 30`, `fixed_month: 9`, `year_context: CURRENT_FY_YEAR`.

**Remaining Note:** The due_date_rule schema and the doc 05 FIXED_ANNUAL table should be annotated to make the `CURRENT_FY_YEAR` vs `AFTER_FY_END_YEAR` distinction explicit for months September–March (which can fall in either context depending on interpretation). A comment in the due_date_rule `rule_notes` field for DIR-3 KYC should state: "September 30 is within the FY that ends March 31 of the same calendar year. year_context = CURRENT_FY_YEAR (not AFTER_FY_END_YEAR)."

**Status:** RESOLVED — use `CURRENT_FY_YEAR` with the above annotation.

---

### DL-008: EPF/ESI Registration Obligation — Threshold vs. Voluntary Registration

**Domain:** EPF / ESI — Applicability Rule
**Status:** OPEN
**Impact:** MEDIUM

**Background:** EPF registration becomes mandatory when an establishment crosses 20 employees. ESI registration becomes mandatory when an establishment crosses 10 employees. However, establishments below these thresholds may voluntarily register. Once voluntarily registered, all monthly compliance obligations apply regardless of employee count.

**What Remains Open:** The applicability rule for EPF monthly compliance is straightforward for registered establishments (`pf_registered = true`). But the applicability rule for the REGISTRATION obligation is:
- Mandatory if employee_count ≥ 20 (or crosses 20 at any point)
- Recommended / advisory if employee_count < 20 but business may benefit from voluntary registration

**Design question:** Should the EPF Registration compliance record show as APPLICABLE (mandatory) for ≥20 employees and RECOMMENDED for 10–19 employees? Or should it show as CHECK_THRESHOLD for all bands below 20?

**Recommended approach:** Show as APPLICABLE (mandatory) for `employee_count_band IN ["20_49", "50_PLUS"]`. Show as CHECK_THRESHOLD for `employee_count_band = "10_19"` with message "You may be approaching the mandatory EPF registration threshold of 20 employees." Show as NOT_APPLICABLE for `employee_count_band IN ["ZERO", "1_9"]`. Do not show RECOMMENDED for voluntary registration — that introduces false urgency.

**Required Action:** Library Owner and Domain Reviewer alignment on whether to show voluntary registration as a compliance item at all for sub-threshold businesses. Decision must be documented before EPF Registration record is activated.

**Target Phase:** MVP

---

### DL-009: Consequences of Missed Due Date vs. Missed Obligation Entirely

**Domain:** Penalty / Consequence Model — Display
**Status:** OPEN
**Impact:** MEDIUM

**Background:** The current severity model computes `base_severity_score` based on statutory penalties for non-compliance. However, there is a distinction between:
(a) Filing late (but filing) — attracts late fees and interest but satisfies the obligation eventually
(b) Never filing at all — may attract higher penalties, prosecution, or registration cancellation

The current model does not distinguish these two scenarios. The `time_escalation_score` escalates the dynamic severity as time passes, but does not explicitly model the transition from "late filing" consequences to "never filed" consequences.

**What Remains Open:** Should the penalty record distinguish `consequence_if_late` (filed after due date but before some threshold) from `consequence_if_entirely_defaulted` (never filed)?

**Design recommendation:** For most obligations, the `base_severity_score` reflects the worst-case statutory consequence (never filed / sustained default). The `consequence_summary` should note both: "Filing after the due date attracts [X late fee/interest]. Continued non-filing beyond [Y days/period] may result in [Z registration action/prosecution]." The time escalation model handles urgency escalation; the base score handles the inherent risk.

No new fields are required. The `prosecution_notes` field and `registration_risk_description` should be used to capture the "beyond late" consequences. This is a content quality discipline, not a schema change.

**Target Phase:** Resolve before GSTR-3B, GSTR-1, TDS deposit records are finalized

---

### DL-010: Section 43B(h) and MSME Form I — Cross-Domain Linkage

**Domain:** Income Tax / MCA — Rule Dependency
**Status:** OPEN
**Impact:** HIGH

**Background:** Section 43B(h) (IT domain — income tax disallowance for delayed MSME payments) and MSME Form I (MCA domain — reporting of overdue MSME supplier payments) both arise from the same underlying fact: delayed payment to MSME suppliers. They are two different legal obligations from two different laws but with the same trigger.

**Decision Made:** They are separate compliance records in separate domains. `IT_MSME_PAYMENT_43B_H_INDICATOR` covers the income tax risk; `MCA_MSME_FORM_I` covers the company reporting obligation.

**What Remains Open:** How should the UI surface this relationship? A business that sees both items in their compliance list may not understand they both relate to MSME supplier payment timing. The `depends_on_compliance` and `cascades_to_compliance` arrays on the schema exist for this purpose, but the nature of the relationship here is "related context" rather than a strict dependency.

**Recommended Resolution:** Use the `description_plain` field of each record to explicitly cross-reference the other. For `MCA_MSME_FORM_I`: include a note "Also see: IT_MSME_PAYMENT_43B_H_INDICATOR for the income tax implications of the same delayed payments." For `IT_MSME_PAYMENT_43B_H_INDICATOR`: "Also see: MCA_MSME_FORM_I for companies' reporting obligation on delayed MSME payments."

Additionally, consider adding a `related_compliance_ids` array (currently a deferred field per C1 Section 7) to formally link these two records. The Library Owner should decide whether to advance this deferred field to MVP use.

**Target Phase:** Phase 2 (for related_compliance_ids); MVP (for cross-reference in description_plain)

---

### DL-011: Professional Tax — State Completeness for Phase 2

**Domain:** Professional Tax — Scope
**Status:** DEFERRED
**Impact:** MEDIUM

**Background:** Professional Tax is confirmed to apply in approximately 14 states (doc 23 B6). PT slabs and registration thresholds are state-specific and change via state budget amendments. For MVP, PT records carry `requires_human_review: true` and `STATE_SPECIFIC` applicability.

**Decision Made (doc 23 B6):** For MVP, enter PT records for the top 5 commercial states (Maharashtra, Karnataka, West Bengal, Tamil Nadu, Telangana) as `PARTIALLY_VALIDATED` with `requires_human_review: true`. Do not populate state-specific slabs until Phase 2.

**What Remains Open (for Phase 2):**
1. Exact current PT slabs for each confirmed state — retrieved from state Finance Department websites.
2. PT status for uncertain states: Goa, Kerala, Madhya Pradesh, Chhattisgarh.
3. PT payment frequency (monthly vs. annual) per state.

**Target Phase:** Phase 2 — explicit deferral confirmed

---

### DL-012: Advance Tax — Presumptive Taxation Section 44AD Variant

**Domain:** Advance Tax — Rule Variant
**Status:** OPEN
**Impact:** MEDIUM

**Background:** Businesses under presumptive taxation (Section 44AD) pay 100% of advance tax as a single installment by March 15 (instead of four installments). This requires a separate advance tax record: `IT_ADVANCE_TAX_44AD_SINGLE_PAYMENT`.

**Decision Made:** Four standard advance tax records will be created for non-presumptive taxpayers. A separate record for Section 44AD presumptive taxpayers is needed.

**What Remains Open:** The applicability condition for the 44AD variant requires a field in the business profile: `uses_presumptive_taxation = true` or equivalent. This field is not currently in the business_profile schema in doc 04.

**Required Action:** Confirm with the questionnaire/profile design owner (doc 07) whether a `uses_presumptive_taxation` field (or `gst_scheme` equivalent for income tax) should be added to `business_profile`. Once confirmed, create the applicability rule for the 44AD variant.

**Target Phase:** MVP (both records should ideally be in MVP — advance tax affects every income-earning business)

---

### DL-013: Company Governance — Board Meetings and AGM Obligations

**Domain:** MCA Company — Governance
**Status:** OPEN
**Impact:** MEDIUM

**Background:** Companies Act requires every company to hold a minimum number of board meetings (4 per year for most companies, with gap between consecutive meetings not exceeding 120 days), and an AGM annually. These are GOVERNANCE-type obligations. They have no form filing directly (the filing is in the minutes/registers), but some have associated filings (e.g., MGT-15 for AGM notice, which is only for listed companies).

**What Remains Open:** Whether GOVERNANCE obligations like "minimum board meetings" should be in the compliance library with `obligation_type: GOVERNANCE` and `frequency_type: QUARTERLY` (for the 4-meetings-per-year obligation), or whether they are out of scope for MVP.

**Design consideration:** GOVERNANCE items like board meetings and AGM have no direct due date form submission — they are internal governance obligations. The compliance engine cannot track whether a meeting was actually held. Including them as INDICATOR types may be appropriate for awareness, but they cannot be marked "completed" in the same way a GST return can.

**Recommended approach:** Include as `obligation_type: INDICATOR` records for MVP (awareness only). Flag for Phase 2 where evidence attachment (uploading minutes) may enable tracking.

**Required Action:** Library Owner decision on whether governance INDICATOR records are in MVP scope.

**Target Phase:** MVP decision needed; population likely Phase 2

---

### DL-014: Notification Extension Records — When to Create vs. When to Update Rule

**Domain:** Data Model — Notification vs. Rule Update
**Status:** OPEN (clarification needed)
**Impact:** MEDIUM

**Background:** C5 and C7 establish that: (a) temporary extensions of due dates are stored as `notification_extension` records, NOT as rule updates; (b) permanent changes to due dates require a new rule version. The distinction between "temporary" and "permanent" is important but not always obvious.

**Example ambiguity:** What if CBIC has extended GSTR-9 due dates for three consecutive years (FY2020-21, FY2021-22, FY2022-23)? Each year was technically a "temporary" extension. But a pattern of three consecutive extensions might be treated practically as a de facto permanent due date change. Does the third consecutive extension require a rule version update or another notification_extension record?

**Decision Made (established principle):** The legal basis governs, not the practical pattern. If the extension is issued via a temporary notification exercising the Commissioner's power to extend under Section 44 (not a permanent amendment to the due date rule in Rules), it is a `notification_extension` record, regardless of how many times it has been issued. The base rule retains the statutory due date; each extension overlays it.

**What Remains Open:** This principle needs to be explicitly communicated to Library Populators. The C10 SOP and C7 should be cross-referenced to ensure Library Populators know the test: "Is this issued under permanent rulemaking power (Rule amendment → new rule version) or temporary extension power (notification under Section/Rule power to extend → notification_extension record)?"

**Required Action:** Add a cross-reference note in the C10 SOP Phase 8 (maintenance) section and in C7 Section 8. This is a documentation clarification, not a design change.

**Target Phase:** Pre-population (before first notification_extension records are created)

---

### DL-015: source_confidence_level for Rules Confirmed Post-Author Cutoff

**Domain:** Trust Model — Source Confidence Assignment
**Status:** OPEN
**Impact:** LOW-MEDIUM

**Background:** Several rules depend on information that must be verified against notifications issued after August 2025 (the author's knowledge cutoff). For rules like the e-invoicing threshold (B2), the GSTR-9 FY-specific exemption (B3), and the GSTR-3B QRMP state groups (B1), the Library Populator must retrieve and confirm current notifications.

**What Remains Open:** What `source_confidence_level` should be assigned when the Library Populator retrieves the current notification and it matches what was expected? This is straightforwardly HIGH. But what if the Library Populator cannot access the official website, or the notification text is ambiguous? Guidance is needed for these edge cases.

**Resolution:** Already embedded in C2 Step 9 and C7 source qualification standard. HIGH requires confirmed, official, read-in-full. MEDIUM requires strong likelihood but some uncertainty. If the Library Populator cannot access the official source, the level is at most MEDIUM. This does not require any new documentation — it requires Library Populators to apply C2 Step 9 consistently and not assign HIGH as a default.

**Status:** The principle is resolved. The remaining open item is enforcement through training and QA review.

---

## 4. RESOLVED ITEMS (for reference)

| ID | Item | Resolution | Phase |
|----|------|-----------|-------|
| DL-007 | DIR-3 KYC year context | Use CURRENT_FY_YEAR for September 30 | Resolved |

---

## 5. ITEMS REQUIRING PRODUCT / LEGAL TEAM REVIEW

The following items cannot be resolved by the documentation team alone and require input from the product owner, legal reviewer, or business stakeholder:

| ID | Item | Who Needs to Decide | Urgency |
|----|------|---------------------|---------|
| DL-006 | Add LABOUR_PAYMENT enum value | Library Owner + Product Owner | Before labour rules activated |
| DL-008 | Voluntary EPF/ESI registration display treatment | Library Owner + Product Owner | MVP |
| DL-009 | Late vs. never-filed consequence modeling | Library Owner | MVP |
| DL-010 | Related compliance IDs for MSME cross-reference | Library Owner | Phase 2 |
| DL-012 | Presumptive taxation profile field | Library Owner + Questionnaire Owner | MVP |
| DL-013 | Board meeting / AGM governance obligations — scope decision | Product Owner | MVP or Phase 2 decision |
| DL-014 | Notification extension vs. rule version clarification | Library Owner | Pre-population |

---

## 6. Items Requiring Source Research (Pending)

| ID | Item | Blocked On | Phase |
|----|------|-----------|-------|
| DL-001 | QRMP state groups | Notification 84/2020-CT retrieval + post-Aug 2025 amendments | MVP |
| DL-002 | E-invoicing threshold | Current CBIC notification retrieval | MVP |
| DL-003 | ESI return statute/portal divergence | Rule 26 ESI Rules text + ESIC circular | MVP |
| DL-004 | GSTR-9 FY-specific exemptions FY23-24, FY24-25 | CBIC notification retrieval | MVP |
| DL-005 | Small company definition post-Aug 2025 | MCA.gov.in confirmation | MVP |
| DL-011 | PT state slabs for 5 priority states | State government Finance Dept websites | Phase 2 |

---

## 7. Index of All Part C Design Decisions

The following decisions are embedded across the C1–C14 documents and are summarized here for quick reference:

| Decision | Location | Summary |
|----------|----------|---------|
| Nine validation states | C8 Section 4 | Full state taxonomy with engine behavior |
| Three-layer architecture | C9 Section 4 | Master / Profile / Instance separation |
| Two-person review rule | C10 Section 4 | Drafter may not self-certify |
| Immutable identity fields | C1 Section 5, C11 | compliance_id, compliance_code, operative_legal_text |
| 90-day review for threshold rules | C1 Section 4 Group 7 | review_due_by computation |
| Notification extension ≠ rule version | C5 Section 5, C7 Section 8 | Temporary extensions → notification_extension; permanent changes → new rule version |
| Source confidence governs severity | C6 Section 5 | LOW confidence → 50% reduction in factor contribution |
| NOT_APPLICABLE records not shown | C4 Section 6 | NOT_APPLICABLE items hidden or in collapsed section |
| Four-stage mapping procedure | C9 Section 5 | Applicability → Due Date → Severity → Storage |
| Tier 1 library of 20 rules | C14 Section 6 | MVP target library with TDS/GST/IT/EPF/MCA priorities |

---

## 8. Recommended Conclusion

This decision log records 15 open items as of the completion of Part C documentation. Of these:

- **6 items** require source research (DL-001 through DL-005, DL-011) — these are information gaps, not design gaps. They are resolvable by accessing official government websites.
- **7 items** require product or legal team decisions (DL-006 through DL-010, DL-013, DL-014) — these involve design choices where the documentation team has made recommendations but cannot make the final call.
- **2 items** are effectively resolved with documentation notes (DL-007, DL-015).

None of the open items block ALL library population. Items DL-001, DL-002, DL-003, DL-005 are blockers for their specific rule records only. All other Tier 1 rules (see C14) can proceed to population immediately, subject to their own source retrieval steps.

The decision log should be revisited at least once before the first Tier 1 rules are activated, and after every subsequent batch activation, to close out resolved items and add newly discovered open items.
