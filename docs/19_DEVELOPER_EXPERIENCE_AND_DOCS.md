# Document 19 — Developer Experience and Documentation
## API Docs Structure, Playground Design, and First-Success Path

---

## 1. DEVELOPER EXPERIENCE PRINCIPLES

**DX-1: Time to first successful API call ≤ 5 minutes.**
The developer should be able to sign up, get an API key, copy a curl command, and get a real response in under 5 minutes.

**DX-2: Every endpoint has a working example.**
No endpoint in the reference should lack a request/response example. No placeholders like `{your_token_here}` without clear explanation.

**DX-3: OpenAPI spec is the single source of truth for the API reference.**
The OpenAPI 3.1 spec is generated from (or validated against) the actual implementation. Docs are never manually written prose that drifts from actual behavior.

**DX-4: Errors should be self-explanatory.**
A developer hitting a 400 error should not need to consult docs to understand what went wrong. The `details` array explains precisely which field failed and why.

**DX-5: Public docs, no login wall.**
All documentation is public. No signup required to read docs. Authenticated playground is available post-signup.

---

## 2. DOCUMENTATION SITE STRUCTURE

URL base: `https://docs.ecnailpcom.in` or `https://app.ecnailpcom.in/docs`

### Sidebar Navigation

```
Getting Started
  ├── Overview
  ├── Quickstart (5-minute guide)
  ├── Authentication
  └── Rate Limits & Quotas

Core Concepts
  ├── How Compliance Evaluation Works
  ├── Financial Year Context
  ├── Applicability Status Explained
  ├── Severity Scoring
  └── Source Attribution

API Reference
  ├── Auth
  ├── Workspaces
  ├── Projects
  ├── Questionnaire
  ├── Evaluation
  ├── Compliance Items
  ├── Due Dates
  ├── Heat Map
  ├── Exports
  ├── Share Links
  ├── API Keys
  ├── Usage
  └── Public / Meta

Guides
  ├── Create a Business Profile via API
  ├── Get All Overdue Compliance Items
  ├── Track Compliance Completion
  ├── Export Compliance Data
  ├── Using Share Links

Error Reference
  └── Complete Error Code List

Versioning & Changelog
  ├── API Versioning Policy
  └── Changelog

Libraries & SDKs (Phase 2)
```

---

## 3. QUICKSTART GUIDE — EXACT CONTENT

The Quickstart must work end-to-end for a developer who just signed up.

```markdown
# Quickstart: Your First Compliance Profile in 5 Minutes

## Step 1: Get Your API Key
Sign up at app.ecnailpcom.in → Dashboard → API Keys → Create Key.
Copy your key — it is shown once.

## Step 2: Create a Business Profile
```bash
curl -X POST https://api.ecnailpcom.in/v1/projects \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "project_name": "My Test Business",
    "entity_type": "PRIVATE_LIMITED"
  }'
```
Save the `project_id` from the response.

## Step 3: Submit Business Details
```bash
curl -X PUT https://api.ecnailpcom.in/v1/projects/PROJECT_ID/questionnaire/answers \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "entity_type": "PRIVATE_LIMITED",
    "principal_state": "MH",
    "activity_type": "SERVICE",
    "gst_registered": true,
    "gst_scheme": "REGULAR",
    "gst_filing_frequency": "MONTHLY",
    "annual_turnover_estimated": 15000000,
    "employee_count_band": "10_19",
    "makes_salary_payments": true
  }'
```

## Step 4: Run Compliance Evaluation
This uses 1 of your 100 daily evaluations.
```bash
curl -X POST https://api.ecnailpcom.in/v1/projects/PROJECT_ID/evaluation \
  -H "X-API-Key: YOUR_API_KEY"
```

## Step 5: Get Overdue Items
```bash
curl "https://api.ecnailpcom.in/v1/projects/PROJECT_ID/compliance?status=OVERDUE" \
  -H "X-API-Key: YOUR_API_KEY"
```

🎉 That's it. You now have a fully classified compliance profile with source-backed due dates.

Next steps:
- [Get the full due-date schedule →]
- [View severity scores and penalty summaries →]
- [Export as JSON or CSV →]
```

---

## 4. OPENAPI SPEC

The system must maintain a valid OpenAPI 3.1 specification at:
```
https://api.ecnailpcom.in/v1/openapi.json  (machine-readable)
https://api.ecnailpcom.in/v1/openapi.yaml  (human-readable)
```

**What the OpenAPI spec must include:**
- All endpoint definitions with request/response schemas
- All enum values
- All error response shapes
- Rate-limit header descriptions
- Authentication security schemes (bearer + apiKey)
- Example values for every request and response field

**How to maintain it:**
The spec should be generated from code annotations (not manually written). Implementation teams should use a framework that generates OpenAPI spec from route/schema definitions. The generated spec is then used to render documentation.

**Rendered docs:** Use Redoc or Scalar (open source, clean rendering) to render the OpenAPI spec as the API Reference section. This ensures docs are always in sync with the spec.

---

## 5. CODE SAMPLES IN THREE LANGUAGES

Every major operation in the docs must show examples in:

### cURL (always first)
```bash
curl -X POST https://api.ecnailpcom.in/v1/projects/uuid/evaluation \
  -H "X-API-Key: pk_live_yourkey" \
  -H "Content-Type: application/json"
```

### JavaScript (fetch / native)
```javascript
const response = await fetch(
  'https://api.ecnailpcom.in/v1/projects/uuid/evaluation',
  {
    method: 'POST',
    headers: {
      'X-API-Key': 'pk_live_yourkey',
      'Content-Type': 'application/json'
    }
  }
);
const result = await response.json();
console.log(result.summary.overdue);
```

### Python (requests)
```python
import requests

response = requests.post(
    'https://api.ecnailpcom.in/v1/projects/uuid/evaluation',
    headers={
        'X-API-Key': 'pk_live_yourkey',
        'Content-Type': 'application/json'
    }
)
data = response.json()
print(f"Overdue: {data['summary']['overdue']}")
```

---

## 6. API PLAYGROUND

### Pre-login Playground (Public Demo Console)
- At `/demo` page: a limited interactive form that calls `/v1/public/demo/evaluate`
- Shows real response in a formatted JSON viewer
- Rate limited: 5 calls per IP per day
- Does NOT expose full source details or full item list

### Post-login Playground (Authenticated)
- At `/docs/playground` or within the docs site
- Uses the logged-in user's actual API key (auto-injected, not shown in the UI)
- Can make real calls against the user's own workspace
- Shows request builder UI + formatted response viewer
- Request logs shown for debugging
- "Try it" buttons on every API reference endpoint that opens the request in the playground

**Implementation approach:** The playground can be as simple as an in-browser request builder that constructs and sends the API call. No complex tooling needed.

---

## 7. WHAT MUST BE IN DOCS AT LAUNCH

**Required at launch (no exceptions):**
- Overview page: what the API does, base URL, versioning note
- Authentication page: JWT vs API key, how to get a key, Bearer format
- Rate limits page: what counts, how limits work, headers, over-limit response
- API reference: all MVP endpoints with request/response examples
- Quickstart: working 5-step guide (tested and verified to work)
- Error codes: complete list with descriptions

**Deferred to Phase 2:**
- SDK libraries (Python, JavaScript)
- Webhook documentation
- Integration guides (Tally, Zoho Books, etc.)
- Video tutorials

---

## 8. FIRST API SUCCESS PATH (CRITICAL METRIC)

The system should track: "Did the user make a successful API call within 24 hours of getting their API key?"

This is tracked via `api_keys.last_used_at`. When this transitions from null to a non-null value for the first time, it triggers:
1. Mark `step_first_api_call = true` in `onboarding_progress`
2. Optionally: In-app celebration / confetti moment the next time user logs in to the UI
3. Analytics event: `developer_first_api_call`

This metric is one of the most important product health indicators for developer adoption.
