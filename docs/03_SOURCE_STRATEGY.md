# Document 03 — Source Strategy
## Legal/Regulatory Source Hierarchy, Acquisition, and Metadata Model

---

## 1. CORE PRINCIPLE

Every compliance record in this system must be traceable to a source.
A source is not a blog, not an explainer, not a CA newsletter.

A source is one of:
1. An Act of Parliament or State Legislature
2. Rules made under that Act
3. A Notification issued under statutory authority
4. A Circular or Instruction issued by the competent authority
5. An official government portal page or official help document (for operational filing procedures)

If none of the above is available and a compliance is widely known in practice, it must be
marked as `SOURCE_TYPE: OPERATIONAL_PRACTICE` with confidence LOW until a primary source is located.

---

## 2. SOURCE HIERARCHY

### Priority 1 — Primary Statute (HIGHEST AUTHORITY)

| Level | What it covers | Example |
|-------|---------------|---------|
| 1a | Central Act / State Act | CGST Act 2017, Companies Act 2013, IT Act 1961, EPF Act 1952 |
| 1b | Rules under Act | CGST Rules 2017, LLP Rules 2009, IT Rules 1962 |
| 1c | Schedule / Form attached to Act or Rules | Schedule I of CGST Act (exempt supplies), Form 3CD of IT Rules |

**How to use:** Section + Sub-section + Proviso references must be captured precisely. "Section 47" is insufficient. "Section 47(1) of CGST Act, 2017" is correct.

### Priority 2 — Subordinate Legislation (HIGH AUTHORITY)

| Level | What it covers | Example |
|-------|---------------|---------|
| 2a | Gazette Notification under statutory power | Notification No. 82/2020-Central Tax dt. 10.11.2020 (QRMP) |
| 2b | Official Circular from competent authority | CBDT Circular No. 15/2021 |
| 2c | Official Trade Notice / Instruction | DGFT Trade Notice |
| 2d | Official FAQ issued by competent authority | CBIC FAQs on GST (only if issued officially and dated) |

**How to use:** Full notification number, date, and issuing authority must be captured. Cross-check whether notification is still in force (not superseded).

### Priority 3 — Official Portal/Filing Guidance (MEDIUM AUTHORITY)

| Level | What it covers | Example |
|-------|---------------|---------|
| 3a | Official ministry/department portal help pages | incometax.gov.in help, MCA21 user manual |
| 3b | Official advisory/instruction sheets | GST portal tutorial, EPFO user guide |
| 3c | Official professional body guidance | ICAI guidance notes where endorsed by statute |

**How to use:** These can supplement law/rule understanding, especially for filing procedures. Must never override Priority 1 or 2.

### Priority 4 — Secondary/Professional Commentary (LOW AUTHORITY — must be explicitly marked)

| Level | What it covers |
|-------|---------------|
| 4a | ICAI publications (non-endorsed, educational) |
| 4b | High-court / tribunal decisions (persuasive, not binding unless SC) |
| 4c | Leading professional commentary (Taxmann, CCH, Padhuka, etc.) |

**Must be flagged as:** `source_priority: SECONDARY` + `is_primary_source: false`

**Never to be used as sole source for:**
- Due date rules
- Penalty rates
- Applicability thresholds

---

## 3. SOURCE CONFLICT RESOLUTION POLICY

Conflicts arise frequently in Indian compliance because:
- Portal practice may differ from statutory language
- Notifications may partially override the Act
- CBDT/CBIC may issue clarifications that are operationally binding but technically subordinate to the Act
- State laws may overlap with central laws

### Conflict Resolution Rules:

**Rule C1:** When a Notification issued under the Act modifies a due date set in the Rules, the Notification governs (it is subordinate legislation exercising delegated authority).

**Rule C2:** When a Circular contradicts the Act or Rules, the Act/Rules govern. The Circular may still be operationally followed by the department, and this divergence must be captured explicitly in the `portal_vs_statute_conflict_note` field.

**Rule C3:** When a more recent Notification supersedes an older one, store both. Mark the older one as `superseded_by: [new_notification_id]` and set `effective_to: [date of supersession]`.

**Rule C4:** When a portal instruction differs from the statutory rule (common in MCA and GST), store BOTH in the source record and flag the compliance as having `portal_vs_statute_divergence: true` with `compliance_notes` explaining the divergence.

**Rule C5:** For due dates that have been extended multiple times via sequential notifications (common during Covid and GST stabilization), store each notification as a separate source record linked to the compliance with a `source_role: DUE_DATE_EXTENSION_OVERRIDE` tag and explicit effective dates.

**Rule C6:** State-specific laws always override central laws for state-level obligations (e.g., Shops and Establishments, Professional Tax, Factory Act). State laws cannot override central laws for GST, income tax, EPF, ESI.

---

## 4. SOURCE METADATA MODEL

Each source stored in the system must carry the following fields.

```
SOURCE RECORD
─────────────

source_id               UUID, primary key
source_code             Short stable code, e.g. "CGST_ACT_2017_SEC47"
source_type             Enum: ACT | RULES | NOTIFICATION | CIRCULAR | GAZETTE | 
                               OFFICIAL_FAQ | PORTAL_GUIDANCE | PROFESSIONAL_BODY | 
                               OPERATIONAL_PRACTICE
source_priority         Enum: PRIMARY_STATUTE | SUBORDINATE_LEGISLATION | 
                               OFFICIAL_PORTAL | SECONDARY
is_primary_source       Boolean: true if Priority 1 or 2
authority               Name of issuing authority
                        e.g., "Ministry of Finance, Department of Revenue"
                        e.g., "Central Board of Indirect Taxes and Customs (CBIC)"
                        e.g., "Ministry of Corporate Affairs (MCA)"
                        e.g., "Central Board of Direct Taxes (CBDT)"
                        e.g., "EPFO (Employees' Provident Fund Organisation)"
                        e.g., "Government of Maharashtra"

act_name                Full name of the Act (if applicable)
                        e.g., "Central Goods and Services Tax Act, 2017"

act_short_name          Abbreviated name
                        e.g., "CGST Act"

section_rule_reference  Section/Rule/Regulation reference
                        e.g., "Section 47(1)"
                        e.g., "Rule 61(1)"
                        e.g., "Regulation 10(3)"

notification_number     For notifications: full notification reference
                        e.g., "Notification No. 82/2020-Central Tax"

circular_number         For circulars: full circular reference

notification_date       Date of notification/circular/gazette (ISO 8601)
gazette_reference       Gazette of India reference if applicable

official_url            Official URL to source text
                        e.g., "https://cbic-gst.gov.in/..."
                        NOTE: Must be verified as an active, official URL.
                        Flag as url_verified: false if not confirmed.

portal_url              If portal filing guidance differs, URL of portal help page

version_effective_from  Date from which this source version applies
version_effective_to    Date until which this version applies (null if still active)
is_currently_active     Boolean

superseded_by           source_id of the superseding source (if applicable)
supersedes              source_id of the source this one supersedes (if applicable)

jurisdiction            Enum: CENTRAL | STATE | UT | SPECIFIC_STATE
jurisdiction_state      ISO state code (if state-specific), e.g., "MH" for Maharashtra

portal_vs_statute_divergence  Boolean: true if portal practice differs from statute
portal_vs_statute_note        Text: explain the divergence

confidence_level        Enum: HIGH | MEDIUM | LOW
                        HIGH = confirmed, active, directly stated in source
                        MEDIUM = inferred from source, confirmed practice
                        LOW = secondary source or operationally followed but unclear basis

last_verified_on        Date on which this source was last verified as active/accurate
verified_by             Who/what verified (manual / automated / professional_review)

source_notes            Free text for nuances, edge cases, conflicting interpretations
```

---

## 5. COMPLIANCE-SOURCE LINKAGE TABLE

Each compliance can have multiple sources (the primary Act section + the Rule + notification overrides).

```
COMPLIANCE_SOURCE_LINK
──────────────────────

link_id                 UUID
compliance_id           FK to compliance master
source_id               FK to source record

source_role             Enum:
                        PRIMARY_OBLIGATION — defines the obligation itself
                        DUE_DATE_RULE — sets the due date
                        DUE_DATE_EXTENSION_OVERRIDE — extends/changes due date temporarily
                        PENALTY_RULE — sets the penalty
                        THRESHOLD_RULE — sets applicability threshold
                        RATE_RULE — sets rates (GST rates, TDS rates, etc.)
                        OPERATIONAL_GUIDE — portal/operational procedure
                        INTERPRETATION — clarification circular/FAQ

is_currently_operative  Boolean: is this source-link currently applicable?

effective_from          Date this source link became applicable
effective_to            Date this source link ceased/expires

relevance_note          Short note on what this source establishes for this compliance
```

---

## 6. SOURCE ACQUISITION STRATEGY

### Phase 1 — Foundation (before any record is entered)

For each compliance domain, the following must be done **manually**:

1. Read the full text of the primary Act section(s)
2. Read the relevant Rules
3. Identify all currently active Notifications (check CBIC/MCA/CBDT websites for the latest)
4. Note the exact current thresholds, rates, and due dates from official sources
5. Note any superseded notifications (for versioning)
6. Record the official URL for each source
7. Assign a `last_verified_on` date

### Phase 2 — Source Validation

Before populating a compliance record, every source link must be verified:
- Is the URL still active?
- Is the notification still in force (not superseded by a more recent one)?
- Is the threshold/rate still current?
- Has the Finance Act or any amendment Act changed anything?

### Phase 3 — Ongoing Maintenance

The compliance library is **not static**. Indian compliance changes frequently:
- CBIC issues notifications for due date changes
- Finance Bills amend the IT Act every year
- MCA issues circulars for extended filing deadlines
- GST Council decisions translate into notifications

The system must have a `last_reviewed_at` field on every compliance record. Records older than 90 days should trigger a review flag.

### Source Acquisition Anti-Patterns (WHAT TO AVOID)

| Anti-pattern | Why it's wrong |
|--------------|---------------|
| Using ClearTax/TaxGuru/IndiaFilings as source | These are SEO blogs; they often contain errors or outdated information; they are not authoritative |
| Using CA firm website explanations as source | Not authoritative; may contain commercial bias |
| Using news articles about compliance changes | May be misquoting the notification; go to the original notification |
| Copying WhatsApp CA group forwards | Obviously not a valid source |
| Using older ICAI study material | May be outdated; rates and thresholds change every Finance Act |
| Assuming a "common knowledge" rule without finding its statutory basis | Very dangerous; may be a practice that has no solid legal basis |

---

## 7. SOURCE TRACEABILITY IN USER-FACING OUTPUTS

When the system shows a compliance obligation to a user, it must be able to display:

1. The primary Act and section: e.g., "As per Section 47(1) of the CGST Act, 2017"
2. The relevant Rule: e.g., "Read with Rule 61(1) of the CGST Rules, 2017"
3. The current notification if a notification modifies the due date: e.g., "As modified by Notification No. XX/20XX-Central Tax dated DD/MM/YYYY"
4. A link to the official source: the gst.gov.in or CBIC page where this notification lives
5. Last verified date: so users know how recent the information is

This traceability is a non-negotiable design requirement. It distinguishes this system from generic compliance blogs.
