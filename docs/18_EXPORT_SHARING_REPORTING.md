# Document 18 — Export, Sharing, and Reporting
## Export Formats, Share Link Architecture, and Report Design

---

## 1. DESIGN PRINCIPLE: ALL EXPORTS ARE SNAPSHOT-BASED

**Decision:** Exports capture the compliance state at the time of generation. They are not live.

**Rationale:**
- A shared report should reflect what was true when it was created, not a different state when the recipient opens it a week later
- Exports are used as records for CA review, internal governance, or filing reminders — they need to be stable
- "Live" shared reports create confusion when due dates change due to re-evaluation

**Every export includes (mandatory metadata header):**
```
Generated At: June 3, 2026, 10:15 AM IST
Business Profile: Acme Technologies Pvt Ltd
Entity Type: Private Limited Company | State: Maharashtra
Financial Year: FY2025-26 | As of: June 3, 2026
Library Version: v1.2.0 (last updated May 28, 2026)
Compliance Source: Primary statutory sources (CGST Act, IT Act, Companies Act, etc.)
DISCLAIMER: This report is for informational purposes only. Not legal advice. Verify due dates on official government portals before filing. [Full disclaimer text]
```

---

## 2. EXPORT TYPES — MVP

### Type 1: JSON Export

**Purpose:** Machine-readable full compliance output for developer/integrator consumption.

**Content structure:**
```json
{
  "export_metadata": {
    "export_id": "uuid",
    "export_type": "JSON",
    "format_version": "1.0",
    "generated_at": "2026-06-03T10:15:00Z",
    "library_version": "v1.2.0",
    "project_id": "uuid",
    "project_name": "Acme Technologies Pvt Ltd",
    "financial_year": "FY2025-26",
    "current_date": "2026-06-03",
    "disclaimer": "..."
  },
  "entity_classification": {
    "entity_type": "PRIVATE_LIMITED",
    "activity_type": "SERVICE",
    "turnover_band": "5CR_10CR",
    "gst_scheme": "REGULAR",
    "employee_count_band": "10_19",
    "principal_state": "MH"
  },
  "summary": {
    "total_applicable": 45,
    "overdue": 3,
    "due_within_7_days": 2,
    "due_within_30_days": 8,
    "completed": 12
  },
  "compliance_items": [
    {
      "compliance_code": "GST_GSTR3B_MONTHLY_REGULAR",
      "title": "GSTR-3B Monthly Return Filing",
      "domain": "GST",
      "period_label": "May 2026",
      "effective_due_date": "2026-06-20",
      "is_overdue": true,
      "overdue_days": 3,
      "severity_band": "HIGH",
      "combined_severity_score": 65,
      "tracking_status": "PENDING",
      "applicability_status": "APPLICABLE",
      "applicability_confidence": "HIGH",
      "why_it_applies": "GST registered regular taxpayer with monthly filing",
      "source": {
        "primary_act": "Central Goods and Services Tax Act, 2017",
        "primary_section": "Section 39",
        "primary_rule": "Rule 61(1), CGST Rules 2017",
        "authority": "CBIC",
        "official_url": "https://cbic-gst.gov.in/...",
        "last_verified": "2026-05-15",
        "confidence": "HIGH"
      }
    }
  ]
}
```

**Source inclusion:** Included in JSON export by default. Configurable via `?include_sources=false`.
**Delivery:** Download URL valid 24 hours. Stored in file storage (S3/equivalent) temporarily.

### Type 2: CSV Export

**Purpose:** Spreadsheet-friendly compliance schedule.

**Columns:**
```
Compliance Code | Title | Domain | Period | Due Date | Overdue Days | Severity | Status | Applicability | Primary Source | Source Authority | Last Verified | Why It Applies
```

**Two CSV files in one ZIP:**
1. `compliance_list.csv` — All applicable items (one row per period instance)
2. `due_date_schedule.csv` — Sorted by due date, calendar-style view

**Source URLs:** Included as a column. Truncated if very long.

### Type 3: Print Report (HTML → Print)

**Purpose:** Professional-looking document for CA review, internal governance, printing.

**Format:** Styled HTML page rendered by the browser's print function. No PDF generation library dependency in MVP (avoid headless Chrome complexity).

**Page structure:**
1. **Cover section:** Business name, entity type, state, FY, generated date, library version, disclaimer
2. **Executive Summary:** Summary card counts, critical items highlighted
3. **Critical Items (severity SEVERE + CRITICAL):** Detailed cards with penalty info
4. **Full Compliance Schedule:** Grouped by domain, then by period
5. **Source References:** Appendix listing all primary sources cited

**Print CSS:** `@media print` styles with page breaks at section boundaries. Logo at header. Page numbers in footer.

---

## 3. SHARE LINKS — DETAILED DESIGN

### Share Link Access Flow

```
User visits: https://app.ecnailpcom.in/share/rANd0mT0keN123

Server:
1. Extract token from URL
2. Compute token_hash = SHA256(token)
3. Query: SELECT * FROM share_links WHERE token_hash = ? AND status = 'ACTIVE'
4. If not found or revoked → 404 "This link has expired or been revoked"
5. If expires_at < NOW() → 404 "This link has expired"
6. Load snapshot data from the evaluation referenced by snapshot_evaluation_id
7. Apply include_legal_name and include_pan_gstin filters
8. Increment access_count, update last_accessed_at
9. Return rendered report page (HTML for browser, or JSON for API consumers)
```

### What Share Links Expose by Default

| Data | Shared by Default | User Configurable |
|------|------------------|--------------------|
| Compliance items (titles, domains, due dates) | ✓ | — |
| Severity scores and colors | ✓ | — |
| Source citations | ✓ | — |
| Business legal name | ✗ | Enable if needed |
| PAN, GSTIN, CIN | ✗ | Enable (with warning) |
| Financial turnover band | ✗ | Not configurable — never in share link |
| Employee count | ✗ | Not configurable — never in share link |

**Rationale:** Compliance output is the value — sensitive business details should not be exposed in a shareable URL by default.

### Share Link Page (Public View)

```
┌─────────────────────────────────────────────────────────────────┐
│  Compliance Report [Optional: Business Name]
│  Financial Year: FY2025-26
│  Report Date: June 3, 2026
│  ⚠ This report was generated using source-backed compliance data.
│    For the most current information, verify on official portals.
│
│  SUMMARY
│  ────────
│  45 applicable compliances identified
│  🔴 3 overdue   🟠 8 due soon   ✅ 12 completed
│
│  CRITICAL / SEVERE ITEMS (top 5)
│  ────────────────────────────────
│  [OVERDUE] GSTR-3B May 2026 — Due Jun 20 — 3 days late
│  ...
│
│  [View full report] (shows full compliance list)
│
│  Source: ecnailpcom.in | Report created by workspace owner
│  Want your own compliance profile? → Get started free
└─────────────────────────────────────────────────────────────────┘
```

The share page always shows the "Get started free" CTA — this is a key acquisition channel.

---

## 4. EXPORT STORAGE ARCHITECTURE

**Storage:** Cloud object storage (S3 or equivalent). Never serve export files directly from the application server.

**File lifecycle:**
1. Export created: File generated and uploaded to `exports/{workspace_id}/{export_id}/{export_type}.{ext}`
2. Download URL: Pre-signed URL with 24-hour expiry
3. After 30 days: File purged from storage, download_url marked expired
4. If project deleted: Files purged after 7 days

**Why not store indefinitely:** Storage cost; compliance data is periodically outdated anyway (new FY, new evaluations).

---

## 5. EXPORT QUOTA ACCOUNTING

Each export generation = 1 quota unit (see doc 17).

Exception: Print Report (Type 3) uses the SAME export record as the most recently generated full report snapshot. It does NOT count as a new quota unit if the underlying data hasn't changed since the last export. Implementation note: compare `evaluated_at` of the requested export against the last export. If same evaluation, serve cached HTML render without consuming quota.

---

## 6. WHAT MUST BE IN EXPORT METADATA (NON-NEGOTIABLE)

All three export types MUST include:
- `disclaimer` text (full text, not just a link)
- `generated_at` timestamp in ISO 8601 + human-readable IST
- `library_version` — which version of the compliance library produced this output
- `last_library_update` date — so reader knows how recent the data is
- `financial_year_label`
- `current_date` at time of evaluation
- **Source provenance per compliance item** — at minimum: act name, section, authority, last_verified date

This is non-negotiable. An export without this information is not a credible compliance document.
