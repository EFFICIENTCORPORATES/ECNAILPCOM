# Document 10 — Clarification Questions and Open Issues
## Questions That Must Be Answered Before Implementation Begins

---

## SECTION A — PRODUCT SCOPE AND BUSINESS DECISIONS

These are questions about what the product should and should not do.
Answers determine MVP scope, legal risk posture, and UI design decisions.

---

**Q-A1. What is the legal / liability posture of the product?**

The system will tell business owners "GSTR-3B is due on June 20."
If that date is wrong (because a notification extended it and we haven't updated), the business owner may incur a late fee they would not have incurred if they had checked directly.

**Options:**
- (a) Product carries standard "for informational purposes only" disclaimer with strong encouragement to verify due dates on official portals
- (b) Product makes a stronger commitment to accuracy and has a verification workflow and update SLA
- (c) Somewhere between the above

**Why this matters:** This decision affects how the product phrases outputs, whether it shows "verify on portal" prompts, and whether you need a CMS-style internal team to monitor notification changes.

---

**Q-A2. Will this be a self-serve product or will it be supported by CA/compliance professionals?**

**Option A — Pure SaaS, no professional:** Business owner sets up their own profile, sees their compliance list, acts on it themselves.

**Option B — CA-assisted:** A CA or compliance professional sets up the client's profile, reviews the outputs, and takes action on their behalf. Product is a tool for professionals.

**Option C — Hybrid:** Self-serve for basic items (GST returns, TDS reminders), CA-flagged for complex items.

**Why this matters:** Changes the questionnaire UX design, the language used in outputs, the level of legal caution in disclaimers, and how HUMAN_REVIEW_REQUIRED items are surfaced.

---

**Q-A3. Will the product support marking compliances as "filed/done"?**

If yes, the system needs:
- A completion status field per compliance per period
- A mechanism to record who marked it done and when
- Optionally: attachment upload for filed returns/receipts
- A way to distinguish "marked done" from "we confirmed it via API" (rare, but worth planning for)

**Why this matters:** Without this, the system only shows due dates and severity. With this, it becomes a proper compliance tracker. This is a significant feature scope difference.

---

**Q-A4. Should the system try to pre-populate business profile data from government databases?**

For example:
- Enter GSTIN → auto-fill entity type, principal state, registration date, scheme, filing frequency
- Enter CIN → auto-fill company details from MCA public data

**Feasibility note:** GSTIN data is partially public (the GST search API at gst.gov.in returns basic details). MCA public data is available but not via a simple API.

**Decision needed:** Should this be built, and if so, is it MVP or Phase 2?

---

**Q-A5. How should the system handle mid-year threshold crossings?**

Example: A business starts the year with ₹3 Cr turnover expectation (below e-invoicing threshold of ₹5 Cr). In Q2, actual turnover trajectory suggests they'll cross ₹5 Cr.

**Options:**
- (a) System uses estimated turnover entered at profile setup; user must update manually
- (b) System prompts user quarterly: "Has your turnover crossed [threshold]?"
- (c) System shows FUTURE_TRIGGER statuses for near-threshold businesses proactively

**Why this matters:** Many compliance thresholds are crossed mid-year and the penalty for non-compliance starts from the crossing date, not the end of year.

---

**Q-A6. What is the monetization model, and does it affect compliance domain access?**

For example:
- Free tier: GST + IT basics only
- Paid tier: All domains including Labour, MCA, EPF/ESI
- Enterprise tier: Multi-company / multi-branch management

**Why this matters:** The architecture must support domain-gating or feature flags if different tiers have different compliance coverage.

---

## SECTION B — LEGAL/COMPLIANCE ACCURACY QUESTIONS

These questions require legal confirmation from a qualified professional.
They should NOT be answered casually from blogs or memory.

---

**Q-B1. What is the precise current list of GSTR-3B state groups for the 20th/22nd/24th staggering?**

In this document, we have noted that states are divided into groups for GSTR-3B due dates.
The exact grouping is defined in CBIC Central Tax notifications and has been revised over time.

**Action required:** Retrieve the current active CBIC notification(s) that define the state groupings. Record the notification numbers and the exact state lists. This is required before encoding the due_date_rule for GSTR-3B.

---

**Q-B2. Has the e-invoicing threshold been revised again recently? What is the current threshold?**

As of our knowledge base, the e-invoicing threshold has been progressively reduced:
- Started at ₹500 Cr → ₹100 Cr → ₹50 Cr → ₹20 Cr → ₹10 Cr → ₹5 Cr

**Action required:** Confirm the current threshold from the latest CBIC notification. This determines which businesses we flag for e-invoicing applicability.

---

**Q-B3. For GSTR-9: when the annual return is due for small taxpayers (turnover ≤ ₹2 Cr), is it optional or mandatory?**

There have been notifications making GSTR-9 optional/exempted for small taxpayers in past years.
The current status of this needs to be confirmed.

**Action required:** Check the latest notification on GSTR-9 filing obligation for taxpayers with annual aggregate turnover ≤ ₹2 Cr.

---

**Q-B4. What is the current precise threshold for GSTR-9C (reconciliation statement)?**

We have stated ₹5 Cr turnover triggers GSTR-9C. This needs current verification.

**Action required:** Confirm from the latest CBIC notification or circular.

---

**Q-B5. For ESI: what is the current status of the "half-yearly return" (Form 5-IE) requirement?**

The ESI portal has evolved and some sources suggest that the traditional Form 5-IE half-yearly return has been replaced by monthly online contribution submissions. The exact current compliance requirement needs verification.

**Action required:** Check ESIC website and regulations for current return filing requirements.

---

**Q-B6. For Professional Tax: which states currently levy PT and what are their current thresholds?**

Our document lists approximately 15 states with PT. Some states have changed their PT rules recently.

**Action required:** Produce a verified current list of states with PT, their governing Acts, and current thresholds before populating PT compliance records.

---

**Q-B7. For the Bonus Act: is the 8-month deadline (November 30) correctly stated?**

We have stated: bonus must be paid within 8 months of financial year end = November 30.
This needs to be confirmed against the current text of the Payment of Bonus Act.

**Action required:** Confirm the exact deadline from the Act text, including any extensions granted historically.

---

**Q-B8. For MSME Form I: what is the exact current scope?**

Who must file MSME Form I? Is it all companies/LLPs that have dues outstanding > 45 days to MSME suppliers, or is there a size/registration threshold?

**Action required:** Confirm from the MCA notification that introduced Form I and any subsequent clarifications.

---

**Q-B9. For DPT-3: does it apply to ALL companies (including those that have not taken any deposits), or only companies that have accepted deposits / outstanding loans?**

There has been ambiguity about whether DPT-3 is a universal annual filing or only if money has been received.

**Action required:** Confirm from MCA notification/circular whether DPT-3 is mandatory for all companies or only those with outstanding receipts.

---

**Q-B10. For DIR-3 KYC: does it apply to all directors of all companies, including dormant directors?**

**Action required:** Confirm applicability scope from the Companies (Appointment and Qualification of Directors) Rules.

---

## SECTION C — DATA ARCHITECTURE DECISIONS

---

**Q-C1. What database technology will be used?**

The data model described in this document is designed for a relational database with JSONB support (i.e., PostgreSQL). If a different database is chosen, the JSONB-based rule expressions will need to be stored differently.

**Preferred recommendation:** PostgreSQL. Its JSONB support, row-level security, and maturity make it the right choice for this schema.

**Decision needed:** Confirm PostgreSQL or explain if another DB is required.

---

**Q-C2. How will the compliance library be maintained? Who edits it?**

The compliance master library (`compliance_master`, `source_master`, `due_date_rule`, etc.) is source-controlled knowledge. It must be updated when:
- CBIC issues a new notification
- Finance Act amends the IT Act
- MCA extends a filing deadline

**Options:**
- (a) Direct database edits by an admin user through a backend CMS panel
- (b) Git-tracked JSON/YAML files that are imported into the database on deployment
- (c) A combination: JSON files for initial population, database for runtime overrides like notification extensions

**Why this matters:** Option (b) is strongly recommended — it provides version control, audit trail, and rollback capability for the compliance library, which is critical for a legally-sensitive product.

---

**Q-C3. How should notification extensions be discovered and applied?**

When CBIC issues a new notification extending GSTR-3B due date by 2 weeks, how does that extension get into the system?

**Options:**
- (a) Manual: a compliance team reads the notification and creates a `notification_extension` record
- (b) Semi-automated: a monitoring workflow alerts the team to check for new notifications; team creates the record
- (c) Automated: scrape official portals for new notifications (technically complex, legally sensitive)

**Recommendation:** Option (b) for MVP. Option (c) as a future enhancement. Manual option (a) is too unreliable for a legally-sensitive product.

---

**Q-C4. How should the "completed" status of a compliance be tracked?**

If a business marks GSTR-3B for May 2025 as "Filed on June 18, 2025", does the system:
- (a) Just record "filed — yes/no"
- (b) Record "filed on [date]" (allowing calculation of whether it was filed on time or late)
- (c) Record "filed on [date] + acknowledgment number"

Option (b) or (c) is strongly recommended. Knowing the filing date allows calculation of actual late fee exposure (if filed after due date) vs. estimated exposure.

---

**Q-C5. Should the system support multiple businesses per user?**

Example: A CA managing 50 clients, each of which is a separate business.

**If yes:** The data model is ready for this (business_profile has a user_id FK). But the UI and the output views need a "portfolio view" design.

**Decision needed:** Is this a Day 1 requirement or Phase 2?

---

**Q-C6. Should the system support different financial year endings?**

Most Indian businesses have March 31 FY end. But some regulated entities (banks, insurance companies) may have different FY endings.

**Recommendation for MVP:** Assume March 31 FY end for all businesses. Add `fy_end_month` field to the profile but only validate March for MVP. This field is already in the schema.

---

## SECTION D — AMBIGUITIES IN THE PRODUCT DEFINITION

These are architectural or definitional gaps in the original product brief that need resolution.

---

**Q-D1. How should the system treat "registrations already obtained" vs. "registrations not yet obtained but required"?**

Example: A business says GST registration is required (based on turnover + interstate supply), but the user says "not registered yet."

Should the system:
- (a) Show GST filing compliances as NOT_APPLICABLE (since they can't file without being registered) and flag registration as the urgent first step
- (b) Show both: "GST Registration — OVERDUE" AND all GST filing items as "Pending Registration" with deferred due dates
- (c) Show registration as critical and filing items as blocked

**Recommendation:** Option (b) — show registration as the critical first item with its own penalty indicator (unregistered supply has heavy penalties under CGST Sec 122), then show filing obligations as "Applicable once registered."

---

**Q-D2. How precise should the turnover-based due date adjustments be?**

GSTR-3B has two different due dates depending on turnover:
- Monthly filing: 20th/22nd/24th
- Quarterly filing (QRMP): 22nd/24th of month after quarter-end

A business might change their filing frequency during the year (QRMP opt-in/opt-out windows: 1st Nov to 30th Nov for Jan–Mar quarter; 1st May to 31st May for Jul-Sep quarter).

Should the system support mid-year frequency changes? Or assume one frequency per FY?

**Recommendation for MVP:** One frequency per FY, captured in `gst_filing_frequency`. Add a note that QRMP opt-in/opt-out exists but don't model the transition mid-year in MVP.

---

**Q-D3. How should presumptive taxation (Sec 44AD/44ADA) be handled?**

Businesses that opt for presumptive taxation are exempt from maintaining detailed books (within limits). Their ITR is simpler. Some TDS rules still apply.

Should the system:
- (a) Ask "Are you filing under presumptive taxation?" and simplify the output accordingly
- (b) Show all compliance items but flag "Presumptive taxation may simplify your books/audit obligations — verify with your CA"
- (c) Treat presumptive taxation as an INDICATOR flag only and not adjust output

**Recommendation:** Option (a) — if the user is on presumptive taxation, it affects the books/audit compliance status directly and the advance tax rule. Ask the question, use it to adjust output.

---

**Q-D4. For "event-based" compliances, should the system prompt for historical events?**

Example: "Have any of your directors changed in the last 6 months?"
If yes and no filing was made, the filing is now overdue — this needs to surface immediately.

Current questionnaire design asks about "pending changes" (forward-looking), but overdue event-based filings from the past are equally important.

**Recommendation:** Ask BOTH: "Are any changes pending?" and "Have any changes occurred in the last 6 months that may not have been filed?" Then compute overdue status from user-entered event date.

---

**Q-D5. Should the heat map be pre-loaded with default severity scores, or should it require full profile completion before showing anything?**

A user who has only answered "Private Limited Company" and "GST Registered" should see:
- (a) A partial heat map with the compliances that are confirmed applicable
- (b) A message: "Complete your profile to see your compliance heat map"
- (c) A template heat map with greyed-out items for unknowns and colored items for confirmed ones

**Recommendation:** Option (c) — the partial profile should show APPLICABLE items in their true colors and INSUFFICIENT_DATA items in grey with an "Answer more questions to reveal" indicator.

---

## SECTION E — SPECIFIC TECHNICAL AMBIGUITIES

**Q-E1. Will the due date engine need to handle budget session amendments in real-time?**

The Union Budget (presented in February) sometimes changes IT Act provisions effective April 1 of the same year. This means a compliance rule active from April 1 must be pre-loaded before April 1, even though the Finance Bill may not have received Presidential assent yet.

**Decision needed:** How to handle provisionally-announced but not-yet-enacted changes?

**Recommendation:** Do not activate Finance Bill changes until the Finance Act receives Presidential assent. Show a "Budget proposal: [description] — not yet enacted" note for pending changes.

---

**Q-E2. How will the system handle state/UT reorganizations or jurisdictional changes?**

E.g., J&K was bifurcated into two UTs. Certain state-level laws changed applicability.
If such changes occur, compliance records for affected states need updates.

**Recommendation:** State codes should be stored as ISO India state codes (ISO 3166-2:IN). Store change history in a `state_master` table if needed.

---

**Q-E3. Should the system flag "first year" businesses differently?**

A company incorporated in July 2025 may have:
- First AGM deadline of April 2026 (9 months from first FY end of March 2026)
- No advance tax obligation for the first quarter if turnover is uncertain
- Different first-return rules for GST

**Decision needed:** Should the system have "first year" logic for entities incorporated in the current FY?

**Recommendation:** Yes — add a `first_fy_flag` computed from incorporation date. Apply first-year rule variants where the law explicitly provides them (e.g., AGM timing, first ITR).

---

## SUMMARY CHECKLIST OF DECISIONS NEEDED

| # | Decision | Priority |
|---|---------|---------|
| A1 | Legal liability posture / disclaimer strategy | HIGH — affects launch |
| A2 | Self-serve vs. CA-assisted product design | HIGH — affects UX architecture |
| A3 | "Mark as done" tracking feature | HIGH — core feature scope |
| A4 | GSTIN/CIN pre-population | MEDIUM — MVP or Phase 2? |
| A5 | Mid-year threshold crossing handling | MEDIUM |
| A6 | Monetization model and tier structure | HIGH — architecture implications |
| B1–B10 | Legal confirmations from primary sources | CRITICAL — must be done before library population |
| C1 | Database technology (PostgreSQL?) | HIGH — affects implementation |
| C2 | Compliance library maintenance mechanism | HIGH — affects operational model |
| C3 | Notification extension discovery process | HIGH — affects compliance accuracy SLA |
| C4 | Completion status tracking depth | MEDIUM |
| C5 | Multi-business (CA portfolio) support | HIGH — Day 1 or Phase 2? |
| D1 | Unregistered but should-be-registered scenario | HIGH — common case |
| D2 | QRMP mid-year change handling | LOW — defer to Phase 2 |
| D3 | Presumptive taxation questionnaire | MEDIUM |
| D4 | Historical event-based compliance check | HIGH — affects overdue detection |
| D5 | Partial-profile heat map behavior | MEDIUM — UX decision |
| E1 | Budget session amendment handling | MEDIUM |
| E3 | First-year business handling | HIGH — very common case |
