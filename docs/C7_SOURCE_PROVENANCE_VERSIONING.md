# C7 — Source Provenance, Citation, and Versioning Protocol
## Standard for Source Attribution, Trust Hierarchy, and Amendment History

---

## 1. Objective

Define the complete metadata standard for source attachment to compliance rules, including what qualifies as a valid primary source, how multiple sources are handled, how conflicting sources are recorded, how amended law creates version history, and how the system preserves historical traceability.

---

## 2. Design Principles

**P1 — One source record per legal instrument.** A single Act section is one source record. A notification is one source record. An amendment to that Act section is a new source record, linked to the original via supersession chain.

**P2 — No merged sources.** Two separate legal instruments (e.g., an Act section and a notification modifying its timeline) must never be combined into one source record. They are stored separately and linked to the rule at different `source_role` levels.

**P3 — Supersession is explicit, not silent.** When a newer notification replaces an older one, the old source record is updated with `superseded_by` pointing to the new record, and `is_currently_active` is set to false. The old record is never deleted.

**P4 — Portal guidance is supplementary, not primary.** Official portal instructions (gst.gov.in, mca.gov.in) may supplement but never override the primary statute or rules.

**P5 — URL verification is a required step.** Every source record must have its `official_url` verified as a live, official URL before the rule enters the active library. Dead URLs reduce the product's credibility.

---

## 3. Source Qualification Standard

### What qualifies as a PRIMARY source

| Type | Examples |
|------|---------|
| Act of Parliament / State Legislature | CGST Act 2017, Companies Act 2013, EPF Act 1952, Payment of Bonus Act 1965 |
| Statutory Rules under an Act | CGST Rules 2017, LLP Rules 2009, Companies (Acceptance of Deposits) Rules 2014 |
| Statutory Notification issued under express legislative power | Notification No. 84/2020-Central Tax dated 10.11.2020 |
| Official Gazette publication of a statute or amendment | Finance Act 2023 (Gazette of India, Extraordinary) |

### What qualifies as a SECONDARY source

| Type | When Used | Confidence Cap |
|------|----------|---------------|
| Official Circular from a competent authority | CBDT Circular, CBIC Trade Circular, MCA General Circular | HIGH if from competent authority; MEDIUM if interpretive |
| Official FAQ issued by Ministry/CBIC/CBDT | Must be an officially issued and dated document | MEDIUM |
| Official portal guidance page | gst.gov.in help, MCA21 user manual | MEDIUM for procedural; LOW for substantive |
| ICAI/ICSI guidance (endorsed) | Endorsed by or under statutory obligation | MEDIUM |

### What DOES NOT qualify as a source

- Blogs, articles, or explainers from any source
- CA/law firm website summaries
- News articles about compliance changes
- WhatsApp forwards or professional group summaries
- Unattributed online summaries

---

## 4. Source Record Fields

Each source record contains:

| Field | Description |
|-------|------------|
| `source_id` | Immutable UUID |
| `source_code` | Stable code. Pattern: `{ACT_SHORT}_{PROVISION}`. Example: `CGST_ACT_S39`, `CGST_RULES_R61_1` |
| `source_type` | ACT \| RULES \| NOTIFICATION \| CIRCULAR \| GAZETTE \| OFFICIAL_FAQ \| PORTAL_GUIDANCE |
| `source_priority` | PRIMARY_STATUTE \| SUBORDINATE_LEGISLATION \| OFFICIAL_PORTAL \| SECONDARY |
| `is_primary_source` | Boolean. True for Acts, Rules, Notifications, Gazette entries. |
| `authority` | Full name of issuing authority. Example: "Central Board of Indirect Taxes and Customs (CBIC)" |
| `act_name` | Full Act name (for Acts and Rules). |
| `section_rule_reference` | Exact provision reference. Must be specific: "Section 39(1)" not "Section 39" if sub-section matters. |
| `notification_number` | For notifications: full number. Example: "Notification No. 84/2020-Central Tax" |
| `notification_date` | Date of notification/circular/gazette in ISO format |
| `official_url` | URL to the actual source text on an official government website |
| `url_verified` | Boolean. Must be true before rule is activated. |
| `url_verified_on` | Date of URL verification |
| `version_effective_from` | Date this source version became operative |
| `version_effective_to` | Date this source version was superseded or expired. Null if still active. |
| `is_currently_active` | Boolean |
| `superseded_by` | source_id of the replacing source record (if this has been superseded) |
| `supersedes` | source_id of the source this record replaces (if this is a replacement) |
| `jurisdiction` | CENTRAL \| STATE \| SPECIFIC_STATE |
| `jurisdiction_state` | State code if SPECIFIC_STATE |
| `portal_vs_statute_divergence` | Boolean. True if portal practice deviates from statute. |
| `portal_vs_statute_note` | Description of the divergence. Required if above = true. |
| `confidence_level` | HIGH \| MEDIUM \| LOW |
| `last_verified_on` | Date of last content verification |
| `source_notes` | Nuances, edge cases, pending questions about this source |

---

## 5. Source-Rule Linkage

Each compliance rule is linked to one or more sources via the `compliance_source_link` table. The link carries a `source_role` that clarifies what aspect of the rule this source establishes.

### Source Role Taxonomy

| Role | Meaning | Example |
|------|---------|---------|
| `PRIMARY_OBLIGATION` | Establishes the obligation itself | Section 39 CGST Act → creates the GSTR-3B obligation |
| `DUE_DATE_RULE` | Specifies the due date | Rule 61(1) CGST Rules → establishes 20th-of-month rule |
| `DUE_DATE_EXTENSION_OVERRIDE` | Temporarily extends the due date | CBIC Notification extending GSTR-3B deadline |
| `PENALTY_RULE` | Establishes the consequence | Section 47 CGST Act → ₹50/day late fee |
| `THRESHOLD_RULE` | Establishes a triggering threshold | Notification setting e-invoicing at ₹5 Cr |
| `APPLICABILITY_RULE` | Establishes who must comply | Section 1(3) Bonus Act → ≥20 employees |
| `EXEMPTION_RULE` | Establishes an exemption | CBIC Notification exempting ≤₹2 Cr from GSTR-9 |
| `RATE_RULE` | Establishes a rate (TDS rate, interest rate) | CBDT notification specifying TDS rate |
| `OPERATIONAL_GUIDE` | Portal/procedural guidance supplementing the statutory rule | GST portal help on GSTR-3B filing procedure |
| `INTERPRETATION` | Official clarification or FAQ that interprets an ambiguous provision | CBIC Circular clarifying 194Q/206C(1H) interaction |

---

## 6. Multiple Sources on a Single Rule

Most compliance rules require 2–4 source links. The required sources for a complete rule:

| Source Role | Required? |
|------------|----------|
| PRIMARY_OBLIGATION | Always required |
| DUE_DATE_RULE | Required for rules with COMPUTABLE due dates |
| PENALTY_RULE | Required for all non-INDICATOR, non-RECORD_KEEPING obligations |
| THRESHOLD_RULE | Required when thresholds set by subordinate legislation |
| APPLICABILITY_RULE | Required when applicability depends on subordinate legislation |

Optional but recommended:
- OPERATIONAL_GUIDE: Helps users navigate filing
- INTERPRETATION: Resolves documented ambiguity

---

## 7. Handling Conflicting Sources

When two sources appear to create different rules for the same obligation:

**Step 1: Establish hierarchy.** Apply the source hierarchy (doc 03, Section 2):
- Act > Rules > Notification > Circular > Portal
- More recent within same level > older
- Central law > State law for central obligations

**Step 2: Determine if conflict is real or apparent.**
- Apparent conflict: A notification may *appear* to contradict the Act but actually exercises delegated authority granted by the Act (e.g., CBIC extending a due date set in Rules). This is not a conflict — the notification is the operative rule.
- Real conflict: The Act says X and a circular says Y, but the circular lacks authority to override the Act. The Act governs.

**Step 3: Record the conflict.**
Set `portal_vs_statute_divergence: true` on the relevant source record and document the conflict in `portal_vs_statute_note`. Record both sources in the compliance_source_link table. Do NOT silently choose one.

**Step 4: Set validation state.**
If the conflict cannot be resolved by the hierarchy analysis, set `validation_state: CONFLICTING_SOURCES` on the rule. The rule remains in the library with this state — it may be shown to users with a warning.

---

## 8. Versioning Protocol

### When a rule changes due to a legal amendment

1. Set `effective_to` on the current rule version to the date the amendment takes effect.
2. Set `active_flag: false` on the current version.
3. Create a new rule record (new `compliance_id`) with the updated content.
4. Set `predecessor_id` on the new record pointing to the old record.
5. Set `effective_from` on the new record to the amendment effective date.
6. Create a new source record for the amending Act/Notification.
7. Link the new source to the new rule record with the appropriate `source_role`.

**Never edit the operative_legal_text, compliance_code, or primary_provision_reference of an active rule.** These fields describe the rule as it was — changing them destroys the historical record.

### When a notification temporarily extends a due date

Do NOT create a new rule version. Create a `notification_extension` record:
```
notification_extension {
  compliance_id: <the affected compliance>
  source_id: <the extension notification source record>
  extended_due_date: <the new due date>
  original_due_date: <what the base rule would have produced>
  period_affected: <e.g., "GSTR-3B for March 2021">
  period_start: <start of affected period>
  period_end: <end of affected period>
  applicable_to: <which taxpayers, if not all>
  is_currently_active: <true during the extension>
  expires_after: <the last date the extension applies>
}
```

When the extension expires, `is_currently_active` is set to false and the computation reverts to the base rule automatically.

### Library Version Record

Each change to the compliance library (adding new rules, modifying rules, adding notifications) should be captured in the `library_meta` table with a version increment and release notes describing what changed. This allows exports to reference a specific library version and enables historical reconstruction.

---

## 9. Source Verification SOP

Before any source is marked as a valid, verified source:

1. **Retrieve the actual document text** — not a summary, not a commentary.
2. **Confirm the document is from an official channel** — .gov.in domain, official Gazette, or Ministry website.
3. **Confirm the document is currently in force** — check for supersession notices, amendment Acts, or revocation circulars.
4. **Verify the URL** — navigate to the URL and confirm the document loads.
5. **Record `url_verified: true` and `url_verified_on: [today]`.**
6. **Set `last_verified_on: [today]`.**

Source verification must be repeated every 90 days for threshold/rate sources, every 180 days for stable statutory provisions.
