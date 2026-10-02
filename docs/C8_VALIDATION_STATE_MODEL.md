# C8 — Validation State Model
## Trust States, Ambiguity States, and Activation Rules for Compliance Rule Records

---

## 1. Objective

Define the complete taxonomy of validation states that a compliance rule record may occupy at any point in its lifecycle, specify the conditions under which a record transitions between states, and establish rules that govern what the compliance engine may do with records in each state.

The validation state is the single most important trust signal in the master library. It tells the engine — and ultimately the user — how much confidence to place in the rule's legal accuracy.

---

## 2. Why It Matters to the Compliance Engine

A compliance product that shows inaccurate legal obligations to businesses causes real harm: missed filings, incorrect due dates, overstated risk, and misplaced user trust. The validation state model prevents this by ensuring that every rule in the system carries an explicit, honest declaration of how well it is supported by verified primary sources.

The validation state is not cosmetic metadata. It directly controls:

- Whether a rule may be shown to users as an active compliance item
- What confidence indicators and disclaimers accompany the display
- Whether due dates and severity scores computed from the rule are shown as definitive or provisional
- When human review is required before a rule is activated
- Which rules are flagged for urgent re-verification

Without a rigorous validation state model, a single poorly sourced rule can produce incorrect guidance to thousands of businesses simultaneously.

---

## 3. Design Principles

**P1 — Validation state is mandatory.** Every rule record must carry a validation state. There is no default of "assumed valid." The default state for a newly created record is `DRAFT`.

**P2 — State determines engine behavior, not just display.** Validation state is not a label for human readers. It is a control signal that the engine evaluates before computing outputs.

**P3 — Downward transitions are permitted; upward transitions require work.** A validated rule can be demoted (e.g., back to PARTIALLY_VALIDATED if its source URL stops working or a new conflicting source is found). A rule can only be promoted to a higher state after the documented requirements for that state are met.

**P4 — Ambiguity is a valid terminal state.** A rule that is legally ambiguous does not become clearer by ignoring the ambiguity. `CONFLICTING_SOURCES` and `PARTIALLY_VALIDATED` are stable operational states, not error conditions requiring immediate correction.

**P5 — Historical validation records are immutable.** When a rule transitions from one state to another, the old state and the reason for transition must be preserved. Rules must not be silently re-labeled.

---

## 4. Complete Validation State Taxonomy

---

### State 1: DRAFT

**Definition:** The rule record has been created but the mandatory fields have not been fully populated or the primary source has not been identified and confirmed.

**Engine behavior:** Record is invisible to all user-facing outputs. Not included in any applicability evaluation, due-date computation, or severity scoring. Exists only in the internal library management interface.

**Conditions to enter DRAFT:** Any newly created record starts here. A record that fails a QA gate is demoted here.

**Conditions to leave DRAFT:** All mandatory fields are populated AND a primary source has been identified (even if not yet fully verified). Record moves to `PENDING_PRIMARY_CONFIRMATION`.

**What must be true:** No mandatory field is blank. `compliance_code`, `title`, `domain`, `obligation_type`, `frequency_type`, `governing_act`, `primary_provision_reference`, and `description_plain` must all have values before the record leaves DRAFT.

---

### State 2: PENDING_PRIMARY_CONFIRMATION

**Definition:** The rule's obligation, applicability, and timing have been described, and a probable primary source has been identified, but the source text has not yet been retrieved and read in full from an official channel.

**Engine behavior:** Record is invisible to user-facing outputs. Internal use only. May be referenced in documentation but not shown to end users.

**When to assign:**
- The compliance obligation is well-known but the specific provision reference has not yet been confirmed from the official text.
- The source URL has been recorded but `url_verified` is `false`.
- The rule was entered using secondary source knowledge (professional commentary, practitioner notes) and the primary Act/Rule text has not yet been retrieved.

**What is needed to leave this state:** The primary source text must be retrieved, read, and confirmed as accurate. `url_verified` must be set to `true`. `source_confidence_level` must be elevated to at least MEDIUM. Move to `PARTIALLY_VALIDATED` or `VALIDATED_PRIMARY` depending on how fully the rule can be confirmed from the source.

**Example:** A rule for Shops & Establishments registration in a new state is entered with the Act name known but the registration threshold not yet confirmed from the state government website.

---

### State 3: PARTIALLY_VALIDATED

**Definition:** The primary source has been identified and confirmed, and the core obligation is correctly captured, but one or more of the following remain unresolved: (a) the due date is not fully encoded, (b) the penalty provisions are not yet sourced, (c) an applicability threshold is known but the exact notification setting the threshold has not been retrieved, or (d) the rule has known gaps that are documented.

**Engine behavior:** Record MAY be shown to users, but ONLY with an explicit disclaimer. Applicability may be evaluated. Due dates may be shown if the `due_date_determinability` field indicates `COMPUTABLE` or `EVENT_DEPENDENT`. Penalty-based severity scoring is suppressed if the penalty record is incomplete.

**Typical display treatment:** Shown with a "Source partially verified — exercise caution" indicator. If the due date component is validated but the penalty is not, the due date is shown and the severity band is shown as provisional.

**When to assign:**
- The obligation and due date are confirmed from primary sources but the penalty provisions require separate research.
- The base rule is confirmed but FY-specific notifications (e.g., GSTR-9 small-taxpayer exemption) have not yet been checked for the current year.
- State-specific thresholds (e.g., Professional Tax slabs) are known to exist but the current schedule has not been retrieved.

**What is needed to leave this state:** All pending gaps must be resolved and the full rule record passes the QA checklist defined in C12.

---

### State 4: VALIDATED_PRIMARY

**Definition:** The rule record is fully populated from confirmed primary sources (Acts, Rules, Notifications). All mandatory fields are complete. The source text has been retrieved and read. The `operative_legal_text` field contains a verbatim quote from the confirmed source. `url_verified = true`. The QA checklist has been completed.

**Engine behavior:** Full activation. Record is shown to users with normal confidence display. Applicability evaluation runs at full confidence. Due dates, severity scores, and consequence summaries are shown without disclaimers (beyond normal professional-review caveats).

**Conditions to enter VALIDATED_PRIMARY:**
- All fields in the C1 schema are populated where mandatory
- `source_confidence_level = HIGH`
- `url_verified = true` and `url_verified_on` is within the last 90 days
- `operative_legal_text` is populated with verbatim quoted text from the confirmed source
- QA checklist (C12) has been completed and signed off
- `requires_human_review = false` OR, if `true`, human review has been completed and documented in `reviewer_notes`

**Review cadence:** VALIDATED_PRIMARY rules require re-verification within 90 days for rate/threshold provisions, and within 180 days for stable statutory provisions.

**Demotion triggers:** The rule is demoted from VALIDATED_PRIMARY if:
- The source URL becomes dead or the source document is superseded
- A contradictory notification or amendment is found
- The library review reveals that the `operative_legal_text` does not match the current in-force provision
- A user or professional reviewer raises a substantiated concern

---

### State 5: VALIDATED_SECONDARY

**Definition:** The rule record is well-described and the obligation is commercially well-known, but the primary Act or Rule text has not been retrieved directly. The rule is supported by one or more secondary sources (ICAI guidance, official FAQ, or professional body publication) with HIGH or MEDIUM confidence.

**Engine behavior:** Shown to users, but with a visible secondary-source indicator: "This obligation is well-established in practice. Primary statutory source is pending verification." Due dates and penalties are shown as provisional if they are drawn from secondary sources. Severity scores use a confidence-adjusted computation (see C6, confidence adjustment rules).

**When to assign:** Rarely — only for obligations that are operationally well-established but where the exact statutory provision is difficult to retrieve (e.g., some state-level Shops & Establishments variations, some sector-specific requirements). This state is intended as a temporary staging ground, not a permanent destination.

**What is needed to leave this state:** Retrieve and confirm the primary source. Move to VALIDATED_PRIMARY or PARTIALLY_VALIDATED.

**Strict limit:** No more than 15% of the active library should be in VALIDATED_SECONDARY at any time. Exceeding this limit indicates the library population process is cutting corners on source verification.

---

### State 6: CONFLICTING_SOURCES

**Definition:** Two or more sources have been retrieved that appear to create different requirements for the same obligation — different due dates, different thresholds, or conflicting applicability — and the conflict cannot be resolved by the source hierarchy rules defined in C7.

**Engine behavior:** Record is shown to users with an explicit conflict warning: "We have found conflicting information about this obligation. Please consult a professional for current requirements." Applicability is shown at LOW confidence. Due dates and severity are shown as provisional with a disclaimer.

**When to assign:** After the conflict resolution procedure in C7 has been applied (hierarchy analysis, apparent vs. real conflict determination) and the conflict remains unresolved.

**What must be documented:** The `interpretation_notes` field must contain: (a) a description of the conflict, (b) which sources conflict, (c) what resolution was attempted, and (d) why the conflict cannot be resolved. The competing sources must both be linked in `compliance_source_link`.

**Resolution path:** Escalate to legal or professional review. If professional review resolves the conflict, move to `PARTIALLY_VALIDATED` or `VALIDATED_PRIMARY`. If professional review confirms the conflict is genuine and ongoing (e.g., a circular that arguably contradicts the Act), the record may remain in `CONFLICTING_SOURCES` with a note explaining the ongoing uncertainty. `requires_human_review` must be `true` while in this state.

---

### State 7: HUMAN_REVIEW_REQUIRED

**Definition:** The rule record is structurally complete and source-supported, but the interpretation of the obligation — or a key aspect of it — requires professional judgment that a rule expression cannot reliably provide.

**Engine behavior:** Shown to users with a prominent "Professional review recommended" flag. The system displays the obligation's title, general description, and the reason professional review is needed — but does not show computed applicability status, due dates, or severity scores as definitive.

**Common triggers:**
- Foreign ownership / FDI compliance under FEMA
- Complex transfer pricing obligations
- Regulated sector obligations (banking, insurance, NBFC)
- Provisions with extensively debated interpretations (e.g., whether a specific payment is TDS-liable)
- State-level obligations where the state's current enforcement position is unclear

**What must be documented:** The `human_review_reason` field must contain a plain-language explanation of what professional review is needed for and why the rule engine cannot make the determination.

**This state is a valid terminal operational state.** A rule in `HUMAN_REVIEW_REQUIRED` is not defective — it is correctly and honestly calibrated. Attempting to encode such rules as if they were machine-evaluable would be more harmful than flagging them.

---

### State 8: SUPERSEDED

**Definition:** This rule record has been replaced by a newer version of the rule. The new version carries a `predecessor_id` pointing to this record. This record's `active_flag` is `false` and `effective_to` is set.

**Engine behavior:** Invisible to current-period compliance evaluation. Accessible via version history for audit trail purposes. Historical compliance period instances that reference this rule retain their references — the system does not retroactively update historical computations.

**When to assign:** When a legal amendment changes the rule's terms, applicability, due date, or penalties. See C7 (versioning protocol) for the full procedure.

**Preservation:** Superseded records are never deleted. They are archived with all their source links and original field values intact.

---

### State 9: DEFERRED

**Definition:** The rule is known to exist and is legally valid, but a deliberate product decision has been made not to include it in the active library yet. This is distinct from PENDING_PRIMARY_CONFIRMATION (which means the source work is incomplete) — DEFERRED means the source work may be complete but the rule is out of scope for the current library population phase.

**Engine behavior:** Invisible to user-facing outputs. Logged in the library management interface as deferred, with the reason.

**When to assign:** When the MVP scope decision (doc 09 / doc 21) has explicitly deferred a domain or rule type (e.g., state PT slabs, TCS obligations, complex transfer pricing rules).

**Required documentation:** The `validation_notes` field must state: (a) what the rule covers, (b) why it is deferred, and (c) which phase it is targeted for.

---

## 5. State Transition Map

```
DRAFT
  └─→ PENDING_PRIMARY_CONFIRMATION  [when: all mandatory identity fields populated]
         └─→ PARTIALLY_VALIDATED      [when: primary source retrieved and confirmed; gaps remain]
         └─→ VALIDATED_PRIMARY        [when: all fields complete, QA passed, source confirmed]
         └─→ CONFLICTING_SOURCES      [when: conflicting sources found during research]
         └─→ DEFERRED                 [when: scope decision defers this rule]

PARTIALLY_VALIDATED
  └─→ VALIDATED_PRIMARY              [when: all gaps resolved, QA checklist complete]
  └─→ VALIDATED_SECONDARY            [when: primary source remains unavailable but secondary is HIGH quality]
  └─→ CONFLICTING_SOURCES            [when: new conflicting source discovered]
  └─→ HUMAN_REVIEW_REQUIRED          [when: interpretation complexity identified]
  └─→ DRAFT                          [when: QA gate fails and record must be reworked]

VALIDATED_PRIMARY
  └─→ SUPERSEDED                     [when: amendment or new version replaces this rule]
  └─→ CONFLICTING_SOURCES            [when: contradictory notification discovered post-validation]
  └─→ PARTIALLY_VALIDATED            [when: a component (e.g., source URL) becomes unverifiable]

VALIDATED_SECONDARY
  └─→ VALIDATED_PRIMARY              [when: primary source retrieved and confirmed]
  └─→ PARTIALLY_VALIDATED            [when: partial primary confirmation achieved]
  └─→ DEFERRED                       [when: scope deprioritizes the rule]

CONFLICTING_SOURCES
  └─→ VALIDATED_PRIMARY              [when: professional review resolves the conflict]
  └─→ PARTIALLY_VALIDATED            [when: conflict partially resolved]
  └─→ HUMAN_REVIEW_REQUIRED          [when: conflict persists and requires ongoing professional guidance]

HUMAN_REVIEW_REQUIRED
  └─→ VALIDATED_PRIMARY              [when: professional review completes and rule is encodeable]
  └─→ DEFERRED                       [when: professional review concludes rule is out of current scope]

SUPERSEDED and DEFERRED are terminal states (no forward transitions)
```

---

## 6. Validation State and User-Facing Display

| Validation State | Shown to Users? | How Displayed |
|-----------------|----------------|---------------|
| `DRAFT` | No | Internal only |
| `PENDING_PRIMARY_CONFIRMATION` | No | Internal only |
| `PARTIALLY_VALIDATED` | Yes, with caution | Shown with "Source partially verified" tag; severity provisional |
| `VALIDATED_PRIMARY` | Yes, fully | Normal display; full confidence |
| `VALIDATED_SECONDARY` | Yes, with note | "Well-established practice; primary source verification pending" |
| `CONFLICTING_SOURCES` | Yes, with warning | "Conflicting information found — consult a professional" |
| `HUMAN_REVIEW_REQUIRED` | Yes, with flag | "Professional review recommended"; no definitive due dates |
| `SUPERSEDED` | No (current); Yes (history) | Accessible via compliance history; not shown in active view |
| `DEFERRED` | No | Internal only |

---

## 7. Edge Cases

**Rule that was VALIDATED_PRIMARY but source notification is superseded:** When the system detects (via periodic re-verification) that the primary notification has been superseded by a newer notification, the rule must be demoted to `PARTIALLY_VALIDATED`. A task must be created to retrieve the new notification and update the rule. If the superseding notification is retrieved and confirms the same rule, the rule is re-validated. If it changes the rule, a new record version is created per the C7 versioning protocol.

**Rule where the governing Act is stable but the threshold is notification-based:** For rules like e-invoicing (where the Act is stable but the AATO threshold is set by a periodically amended notification), the `validation_state` reflects the notification status. If the threshold notification is current and verified, the state is `VALIDATED_PRIMARY`. If the notification's currency is uncertain (e.g., post the author's knowledge cutoff as in B2), the state is `PARTIALLY_VALIDATED` with the note explaining what needs to be checked.

**Rule with multiple sources at different validation levels:** A rule may have a `PRIMARY_OBLIGATION` source at HIGH confidence and a `PENALTY_RULE` source at MEDIUM confidence (because the penalty provision was read in secondary sources but not yet retrieved from the Act). In this case, the overall `validation_state` is `PARTIALLY_VALIDATED` and the `source_confidence_level` is `MEDIUM`. The penalty scoring reflects the MEDIUM confidence adjustment per C6.

**New Act provisions with no implementation track record:** When the Finance Act introduces a new provision effective from a future date (e.g., Section 43B(h) effective FY2023-24), the rule can be populated immediately as `VALIDATED_PRIMARY` if the Finance Act text is retrieved. The novelty of the provision does not reduce validation state — what matters is source support, not enforcement history.

---

## 8. What Should Be Deferred

**Automated validation state transitions** — detecting when a source URL becomes dead, when a notification is superseded, or when a threshold changes — require background monitoring infrastructure. This is a Phase 2 operational enhancement. For MVP, validation state transitions are managed manually during periodic review cycles.

**Confidence scoring automation** — computing `source_confidence_level` from the combination of source roles and URL verification status automatically — is a Phase 2 library management feature.

**User-visible validation metadata** — showing users which specific provision supports a rule — is a planned feature. For MVP, the display focuses on the plain-language description and consequence summary. Source attribution depth (e.g., clickable provision links) is Phase 2.

---

## 9. Recommended Conclusion

The validation state model establishes nine distinct states that collectively represent the full range of trust levels a compliance rule record may occupy. The design is asymmetric by intention: it is easier to demote a rule (when uncertainty increases) than to promote it (which requires specific documented evidence). This asymmetry protects users from being shown inaccurate compliance guidance.

The two states that deserve the most operational discipline are `DRAFT` (rules must not linger here without active work) and `PARTIALLY_VALIDATED` (rules here are shown to users and must carry accurate partial-confidence indicators). The `VALIDATED_PRIMARY` state is the target for all production-quality rules and requires the full QA process defined in C12 before it can be assigned.

`HUMAN_REVIEW_REQUIRED` and `CONFLICTING_SOURCES` are legitimate, stable operating states — not error conditions. The system is more honest and more useful when it admits uncertainty than when it forces a false determination.
