# Part C — Master Compliance Library Design Pack
## Index and Reader Guide

**Status:** Documentation phase only. No code has been written or authorized.

**Purpose of Part C:**
To convert the validated legal understanding from Part A and Part B into a disciplined, formal, implementation-ready specification for the master compliance library. Part C is the bridge between "we understand the law" and "the system can safely store, evaluate, version, and operationalize the law."

**What Part C is NOT:**
- Not a coding specification
- Not a database migration
- Not an API definition
- Not a deployment guide
- Not a UI specification

**What Part C IS:**
- A formal field-level schema for compliance rules
- A legal-to-data translation methodology
- A rule expression standard
- An applicability encoding framework
- A due-date encoding framework
- A consequence/penalty encoding framework
- A source provenance and versioning protocol
- A validation-state model for trust and uncertainty
- A master-to-instance mapping standard
- A population SOP with QA checklist
- Sample documentation templates (illustrative only)
- A population priority framework
- A decision log for residual open items

---

## Document Map

| File | Section | Purpose |
|------|---------|---------|
| [C1_CANONICAL_SCHEMA.md](C1_CANONICAL_SCHEMA.md) | C1 | Complete field-level definition of a compliance rule record |
| [C2_LEGAL_TO_DATA_TRANSLATION.md](C2_LEGAL_TO_DATA_TRANSLATION.md) | C2 | Method for converting legal text to structured rule data |
| [C3_RULE_EXPRESSION_STANDARD.md](C3_RULE_EXPRESSION_STANDARD.md) | C3 | Canonical pattern for expressing every obligation |
| [C4_APPLICABILITY_ENCODING.md](C4_APPLICABILITY_ENCODING.md) | C4 | How applicability logic is represented and evaluated |
| [C5_DUE_DATE_ENCODING.md](C5_DUE_DATE_ENCODING.md) | C5 | Complete due-date classification and encoding standard |
| [C6_PENALTY_CONSEQUENCE_SEVERITY.md](C6_PENALTY_CONSEQUENCE_SEVERITY.md) | C6 | Consequence data model and severity scoring framework |
| [C7_SOURCE_PROVENANCE_VERSIONING.md](C7_SOURCE_PROVENANCE_VERSIONING.md) | C7 | Source citation standards, versioning, and conflict handling |
| [C8_VALIDATION_STATE_MODEL.md](C8_VALIDATION_STATE_MODEL.md) | C8 | Trust states, ambiguity states, and activation rules |
| [C9_MASTER_VS_INSTANCE_MAPPING.md](C9_MASTER_VS_INSTANCE_MAPPING.md) | C9 | How a generic rule becomes a business-specific obligation |
| [C10_LIBRARY_POPULATION_SOP.md](C10_LIBRARY_POPULATION_SOP.md) | C10 | Step-by-step standard operating procedure for adding rules |
| [C11_DATA_DICTIONARY.md](C11_DATA_DICTIONARY.md) | C11 | Field-level governance and definitions |
| [C12_QA_REVIEW_CHECKLIST.md](C12_QA_REVIEW_CHECKLIST.md) | C12 | Pre-activation review checklist per rule |
| [C13_SAMPLE_RULE_TEMPLATES.md](C13_SAMPLE_RULE_TEMPLATES.md) | C13 | Four illustrative rule templates (documentation only) |
| [C14_POPULATION_PRIORITY_FRAMEWORK.md](C14_POPULATION_PRIORITY_FRAMEWORK.md) | C14 | Framework for sequencing library population |
| [C15_DECISION_LOG.md](C15_DECISION_LOG.md) | C15 | Log of residual design questions requiring resolution |

---

## Foundation References (Part A and B)

Part C builds on these documents. Do not read Part C in isolation.

| Reference | What Part C relies on |
|-----------|----------------------|
| [docs/04_DATA_MODEL.md](04_DATA_MODEL.md) | Database schema for compliance_master, penalty_record, due_date_rule, source_master |
| [docs/05_DUE_DATE_ENGINE.md](05_DUE_DATE_ENGINE.md) | Due date rule type taxonomy |
| [docs/06_HEATMAP_SEVERITY_MODEL.md](06_HEATMAP_SEVERITY_MODEL.md) | Severity scoring framework |
| [docs/07_QUESTIONNAIRE_DESIGN.md](07_QUESTIONNAIRE_DESIGN.md) | Business profile input fields |
| [docs/08_APPLICABILITY_MODEL.md](08_APPLICABILITY_MODEL.md) | Applicability status taxonomy and rule expression nodes |
| [docs/03_SOURCE_STRATEGY.md](03_SOURCE_STRATEGY.md) | Source hierarchy and conflict policy |
| [docs/23_LEGAL_RESEARCH_B1_B10.md](23_LEGAL_RESEARCH_B1_B10.md) | B1–B10 resolution and ready-to-populate determinations |
| [docs/24_ADDITIONAL_COMPLIANCE_GAPS.md](24_ADDITIONAL_COMPLIANCE_GAPS.md) | New items surfaced in legal research |

---

## Key Governing Principles

**P1 — No legal certainty beyond source support.** If a rule is not supported by a confirmed primary source, the validation state must reflect this. Never label a rule as validated when it is not.

**P2 — Master library is read-only for end users.** Business-specific determinations are computed instances. The master library records the law; the instance layer records what the law means for a particular business.

**P3 — Every field must have a governance owner.** No field in the master library should be updateable without a defined authority, review path, and version record.

**P4 — Ambiguity is a first-class data state.** Ambiguous rules are not "bad" rules that need to be fixed — they are a valid category that must be represented honestly and shown to users with appropriate context.

**P5 — Historical records are immutable.** When a rule is amended or superseded, the old version is archived — never deleted. This preserves legal traceability.

**P6 — No silent assumptions.** If a threshold, condition, or due date is assumed without direct source confirmation, the assumption must be recorded as an `interpretation_note` and the validation state must not be `VALIDATED_PRIMARY`.

---

## Definition of Done for Part C

Part C is complete when:
- [x] All 15 sections are formally documented
- [x] No production code has been written
- [x] No implementation drift has occurred
- [ ] Sample templates have been reviewed against Part B legal research findings
- [ ] Residual open items in C15 have been reviewed by the product/legal team
- [ ] Population SOP has been read and accepted by whoever will populate the library
