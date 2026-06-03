# Document 12 — Tenant, User, Workspace, and Project Model
## Multi-Tenancy Design and Role/Permission Framework

**CONTEXT:** This document defines the SaaS tenancy layer that sits above the Part A compliance engine.
The compliance library (Part A docs 01–10) is global, not tenant-specific.
Everything in this document is per-tenant (workspace-scoped).

---

## 1. ENTITY HIERARCHY

```
User
 └── belongs to one or more Workspaces (via WorkspaceMember)
      └── Workspace contains Projects (BusinessProfiles)
           └── Project contains CompliancePeriodInstances
           └── Project contains Exports
           └── Project contains ShareLinks
      └── Workspace owns ApiKeys
      └── Workspace has UsageEvents
      └── Workspace has AuditLogs
```

**Day 1 simplified reality:**
- 1 user = 1 workspace (auto-created on signup)
- 1 workspace = N projects (multiple businesses the owner manages)
- Single user access (no workspace collaboration in Day 1 UI)
- Data model fully supports multi-member workspaces for Phase 2

---

## 2. DATABASE TABLES

### users

```sql
users {
  user_id             UUID PRIMARY KEY DEFAULT gen_random_uuid()
  email               VARCHAR(254) UNIQUE NOT NULL
  email_verified      BOOLEAN DEFAULT FALSE
  email_verified_at   TIMESTAMPTZ
  
  password_hash       TEXT NOT NULL           -- argon2id hash, never store plaintext
  
  full_name           VARCHAR(200)
  display_name        VARCHAR(100)
  phone               VARCHAR(15)             -- optional, for future 2FA/reminders
  
  -- Account state
  account_status      ENUM ('ACTIVE','SUSPENDED','DELETED') DEFAULT 'ACTIVE'
  deleted_at          TIMESTAMPTZ
  
  -- Preferences
  timezone            VARCHAR(50) DEFAULT 'Asia/Kolkata'
  preferred_language  VARCHAR(10) DEFAULT 'en'
  
  -- Session / auth tracking
  last_login_at       TIMESTAMPTZ
  last_login_ip       INET
  failed_login_count  SMALLINT DEFAULT 0
  locked_until        TIMESTAMPTZ
  
  -- Onboarding
  onboarding_completed_at  TIMESTAMPTZ
  self_identified_role     ENUM ('BUSINESS_OWNER','CA_CONSULTANT','DEVELOPER','OTHER')
  
  created_at          TIMESTAMPTZ DEFAULT NOW()
  updated_at          TIMESTAMPTZ DEFAULT NOW()
}
```

**Notes for implementors:**
- `password_hash`: Use argon2id with appropriate memory/time cost. Never bcrypt for new implementations.
- `email`: lowercase-normalize before storing and querying.
- `failed_login_count`: Reset on successful login. Lock after 10 failures for 15 minutes.
- `self_identified_role`: Captured at signup; drives onboarding fork (Business User vs Developer path).

### workspaces

```sql
workspaces {
  workspace_id        UUID PRIMARY KEY DEFAULT gen_random_uuid()
  name                VARCHAR(200) NOT NULL
  slug                VARCHAR(100) UNIQUE     -- URL-safe identifier, e.g., "acme-corp"
  
  -- Ownership
  owner_user_id       UUID NOT NULL FK -> users.user_id
  
  -- Plan
  plan_id             VARCHAR(50) DEFAULT 'FREE'
                      -- "FREE", "STARTER", "PRO", "ENTERPRISE"
  plan_started_at     TIMESTAMPTZ
  plan_expires_at     TIMESTAMPTZ           -- null = indefinite (monthly subscription)
  
  -- Limits (denormalized from plan for fast querying)
  daily_quota_limit   INTEGER DEFAULT 100    -- evaluation calls/day
  max_projects        INTEGER DEFAULT 3      -- project count limit
  max_api_keys        INTEGER DEFAULT 3
  max_share_links     INTEGER DEFAULT 10     -- per workspace
  
  -- State
  workspace_status    ENUM ('ACTIVE','SUSPENDED','DELETED') DEFAULT 'ACTIVE'
  deleted_at          TIMESTAMPTZ
  
  created_at          TIMESTAMPTZ DEFAULT NOW()
  updated_at          TIMESTAMPTZ DEFAULT NOW()
}
```

**Notes for implementors:**
- `slug` is optional in MVP but essential for future workspace-namespaced URLs.
- On user signup, create workspace automatically with `name = "{user.full_name}'s Workspace"`.
- The `owner_user_id` is the only member in Day 1 MVP. `workspace_members` table exists but for Phase 2.

### workspace_members

```sql
workspace_members {
  member_id           UUID PRIMARY KEY DEFAULT gen_random_uuid()
  workspace_id        UUID NOT NULL FK -> workspaces.workspace_id
  user_id             UUID NOT NULL FK -> users.user_id
  role                ENUM ('OWNER','ADMIN','ANALYST','VIEWER') NOT NULL
  
  invited_by          UUID FK -> users.user_id
  invitation_email    VARCHAR(254)          -- email used in invite (may differ from user email)
  invitation_accepted_at TIMESTAMPTZ
  
  joined_at           TIMESTAMPTZ DEFAULT NOW()
  removed_at          TIMESTAMPTZ
  is_active           BOOLEAN DEFAULT TRUE
  
  UNIQUE (workspace_id, user_id)
}
```

**Day 1 behavior:** On workspace creation, insert one row: `{workspace_id, owner_user_id, role: OWNER}`. No invite flow in MVP UI.

### api_keys

```sql
api_keys {
  key_id              UUID PRIMARY KEY DEFAULT gen_random_uuid()
  workspace_id        UUID NOT NULL FK -> workspaces.workspace_id
  created_by          UUID NOT NULL FK -> users.user_id
  
  -- Key identity
  key_prefix          VARCHAR(12) NOT NULL   -- First 8 chars shown after creation, e.g. "pk_live_"
  key_hash            TEXT NOT NULL          -- SHA-256 of the full key. NEVER store plaintext.
  key_preview         VARCHAR(16) NOT NULL   -- First 8 + "..." + last 4, for display
  
  label               VARCHAR(100)           -- User-assigned name, e.g., "Production Key", "CI/CD"
  
  -- State
  status              ENUM ('ACTIVE','REVOKED','ROTATED') DEFAULT 'ACTIVE'
  revoked_at          TIMESTAMPTZ
  revoked_by          UUID FK -> users.user_id
  rotated_to          UUID FK -> api_keys.key_id   -- If rotated, new key ID
  
  -- Usage
  last_used_at        TIMESTAMPTZ
  last_used_ip        INET
  total_requests      BIGINT DEFAULT 0
  
  -- Expiry (optional, for future scope-limited keys)
  expires_at          TIMESTAMPTZ            -- null = never expires
  
  created_at          TIMESTAMPTZ DEFAULT NOW()
}
```

**Key format:** `pk_live_` + 32 random hex chars = 40 chars total. Example: `pk_live_a3f8c2d1e4b7a9f0c1d2e3f4a5b6c7d8`
**Storage rule:** Only `key_hash = SHA256(full_key)` is stored. The full key is shown ONCE to the user on creation and never retrievable after.
**Display after creation:** Show first 8 + "..." + last 4, e.g., `pk_live_a3f8...c7d8`

### projects (= BusinessProfile with SaaS layer)

This extends the Part A `business_profile` table with SaaS-layer fields:

```sql
-- Part A business_profile table PLUS these additional columns:
ALTER TABLE business_profile ADD COLUMN (

  workspace_id        UUID NOT NULL FK -> workspaces.workspace_id,
  project_name        VARCHAR(200) NOT NULL,  -- Display name separate from legal_name
  project_slug        VARCHAR(100),           -- URL-safe slug for project URLs
  project_status      ENUM ('ACTIVE','ARCHIVED','DELETED') DEFAULT 'ACTIVE',
  archived_at         TIMESTAMPTZ,
  deleted_at          TIMESTAMPTZ,
  
  -- Last evaluation tracking
  last_evaluated_at   TIMESTAMPTZ,
  last_evaluation_library_version VARCHAR(20),
  evaluation_is_stale BOOLEAN DEFAULT TRUE,   -- True until first evaluation runs
  
  -- Onboarding state
  questionnaire_completeness_pct SMALLINT DEFAULT 0,
  
  -- Cloning
  cloned_from_project_id UUID FK -> business_profile.business_id,
  
  created_by          UUID NOT NULL FK -> users.user_id,
  updated_by          UUID FK -> users.user_id
)
```

**Project vs Business:**
In this product, "Project" = "Business Profile". They are the same entity. The word "Project" is used in developer-facing API; "Business" is used in the user-facing UI. Do not create two tables.

### usage_events

```sql
usage_events {
  event_id            UUID PRIMARY KEY DEFAULT gen_random_uuid()
  workspace_id        UUID NOT NULL FK -> workspaces.workspace_id
  user_id             UUID FK -> users.user_id     -- null for API key calls
  api_key_id          UUID FK -> api_keys.key_id   -- null for UI calls
  
  event_type          ENUM (
                        'EVALUATION',    -- compliance evaluation triggered
                        'EXPORT',        -- export generated
                        'DEMO'           -- anonymous demo call
                      )
  
  project_id          UUID FK -> business_profile.business_id
  source              ENUM ('UI','API','DEMO')
  
  -- Quota tracking
  quota_units_used    SMALLINT DEFAULT 1
  quota_date          DATE NOT NULL              -- UTC date of this event
  
  -- Request context
  request_id          VARCHAR(50)
  response_status     SMALLINT                   -- HTTP status
  duration_ms         INTEGER
  ip_address          INET
  
  created_at          TIMESTAMPTZ DEFAULT NOW()
}

-- Critical index for quota queries
CREATE INDEX idx_usage_events_workspace_date ON usage_events(workspace_id, quota_date);
CREATE INDEX idx_usage_events_key_date ON usage_events(api_key_id, quota_date) WHERE api_key_id IS NOT NULL;
```

### onboarding_progress

```sql
onboarding_progress {
  progress_id         UUID PRIMARY KEY DEFAULT gen_random_uuid()
  user_id             UUID NOT NULL FK -> users.user_id
  workspace_id        UUID NOT NULL FK -> workspaces.workspace_id
  
  -- Step completion flags
  step_account_created      BOOLEAN DEFAULT TRUE    -- Always true at start
  step_first_project        BOOLEAN DEFAULT FALSE
  step_questionnaire_core   BOOLEAN DEFAULT FALSE   -- Min 70% complete
  step_first_evaluation     BOOLEAN DEFAULT FALSE
  step_viewed_due_dates     BOOLEAN DEFAULT FALSE
  step_viewed_heat_map      BOOLEAN DEFAULT FALSE
  step_api_key_copied       BOOLEAN DEFAULT FALSE
  step_first_api_call       BOOLEAN DEFAULT FALSE   -- Detected via API key first use
  step_first_export         BOOLEAN DEFAULT FALSE
  
  onboarding_dismissed_at   TIMESTAMPTZ            -- When user closed the checklist
  completed_at              TIMESTAMPTZ            -- When all core steps done
  
  created_at                TIMESTAMPTZ DEFAULT NOW()
  updated_at                TIMESTAMPTZ DEFAULT NOW()
}
```

### exports

```sql
exports {
  export_id           UUID PRIMARY KEY DEFAULT gen_random_uuid()
  workspace_id        UUID NOT NULL FK -> workspaces.workspace_id
  project_id          UUID NOT NULL FK -> business_profile.business_id
  created_by          UUID FK -> users.user_id
  api_key_id          UUID FK -> api_keys.key_id
  
  export_type         ENUM ('JSON','CSV','PRINT_REPORT')
  format_version      VARCHAR(10) DEFAULT '1.0'   -- Export schema version
  
  -- Snapshot info
  library_version     VARCHAR(20)
  evaluated_at        TIMESTAMPTZ                 -- Evaluation time the snapshot is from
  
  -- File storage
  file_size_bytes     INTEGER
  storage_path        TEXT                        -- Internal storage path or URL
  download_url        TEXT                        -- Signed URL for download
  download_expires_at TIMESTAMPTZ                 -- URL expiry (e.g., 24 hours)
  
  status              ENUM ('GENERATING','READY','FAILED') DEFAULT 'GENERATING'
  
  -- Metadata embedded in export
  generated_at        TIMESTAMPTZ DEFAULT NOW()
  disclaimer_text     TEXT                        -- Snapshot of disclaimer at generation time
  
  created_at          TIMESTAMPTZ DEFAULT NOW()
}
```

### share_links

```sql
share_links {
  link_id             UUID PRIMARY KEY DEFAULT gen_random_uuid()
  workspace_id        UUID NOT NULL FK -> workspaces.workspace_id
  project_id          UUID NOT NULL FK -> business_profile.business_id
  created_by          UUID NOT NULL FK -> users.user_id
  
  -- Token (cryptographically random, stored as hash)
  token_hash          TEXT NOT NULL UNIQUE        -- SHA-256 of the share token
  token_preview       VARCHAR(16)                 -- First 8 chars for admin display
  
  -- What the share shows
  label               VARCHAR(100)                -- Optional: "Q1 Report for CA"
  include_legal_name  BOOLEAN DEFAULT FALSE       -- Safety: don't expose legal name by default
  include_pan_gstin   BOOLEAN DEFAULT FALSE       -- Never expose by default
  snapshot_evaluation_id UUID                     -- FK to the specific evaluation snapshot shown
  is_live             BOOLEAN DEFAULT FALSE        -- If true, shows live re-evaluated data (Phase 2)
  
  -- Access control
  status              ENUM ('ACTIVE','REVOKED') DEFAULT 'ACTIVE'
  expires_at          TIMESTAMPTZ                 -- null = never expires (until revoked)
  revoked_at          TIMESTAMPTZ
  revoked_by          UUID FK -> users.user_id
  
  -- Usage tracking
  access_count        INTEGER DEFAULT 0
  last_accessed_at    TIMESTAMPTZ
  last_access_ip      INET
  
  created_at          TIMESTAMPTZ DEFAULT NOW()
}
```

### audit_log

```sql
audit_log {
  log_id              UUID PRIMARY KEY DEFAULT gen_random_uuid()
  workspace_id        UUID FK -> workspaces.workspace_id
  user_id             UUID FK -> users.user_id
  api_key_id          UUID FK -> api_keys.key_id
  
  action              VARCHAR(100) NOT NULL
                      -- e.g., 'api_key.created', 'api_key.revoked', 'api_key.rotated',
                      --       'project.created', 'project.deleted', 'project.archived',
                      --       'share_link.created', 'share_link.revoked',
                      --       'export.generated', 'evaluation.triggered',
                      --       'user.login', 'user.login_failed', 'user.password_reset',
                      --       'workspace.plan_changed'
  
  resource_type       VARCHAR(50)               -- 'api_key', 'project', 'share_link', etc.
  resource_id         UUID
  
  ip_address          INET
  user_agent          TEXT
  request_id          VARCHAR(50)
  
  metadata            JSONB                     -- action-specific details (key label, export type, etc.)
  
  created_at          TIMESTAMPTZ DEFAULT NOW()
}

-- Index for workspace-scoped audit queries
CREATE INDEX idx_audit_log_workspace ON audit_log(workspace_id, created_at DESC);
CREATE INDEX idx_audit_log_user ON audit_log(user_id, created_at DESC);
```

---

## 3. ROLE PERMISSION MATRIX

| Action | OWNER | ADMIN | ANALYST | VIEWER |
|--------|-------|-------|---------|--------|
| Create project | ✓ | ✓ | ✓ | ✗ |
| Edit project questionnaire | ✓ | ✓ | ✓ | ✗ |
| Trigger evaluation | ✓ | ✓ | ✓ | ✗ |
| Mark compliance as done | ✓ | ✓ | ✓ | ✗ |
| View compliance output | ✓ | ✓ | ✓ | ✓ |
| Export data | ✓ | ✓ | ✓ | ✓ |
| Create share link | ✓ | ✓ | ✓ | ✗ |
| Revoke share link | ✓ | ✓ | ✗ | ✗ |
| Archive/delete project | ✓ | ✓ | ✗ | ✗ |
| Create API key | ✓ | ✓ | ✗ | ✗ |
| Revoke/rotate API key | ✓ | ✓ | ✗ | ✗ |
| View API keys (partial) | ✓ | ✓ | ✓ | ✗ |
| View usage | ✓ | ✓ | ✓ | ✗ |
| Change workspace settings | ✓ | ✓ | ✗ | ✗ |
| Invite members | ✓ | ✓ | ✗ | ✗ |
| Remove members | ✓ | ✗ | ✗ | ✗ |
| Transfer ownership | ✓ | ✗ | ✗ | ✗ |
| Delete workspace | ✓ | ✗ | ✗ | ✗ |
| Upgrade plan | ✓ | ✗ | ✗ | ✗ |

**Day 1 MVP:** Only OWNER role exists in practice. Role infrastructure is present in the DB but the invite flow and multi-member UI are deferred to Phase 2.

---

## 4. TENANT ISOLATION RULES

**Rule T1:** Every query that touches `business_profile`, `compliance_period_instance`, `exports`, `share_links`, or `audit_log` MUST include a `workspace_id` condition. No exceptions.

**Rule T2:** API keys are workspace-scoped. When an API request authenticates with a key, the `workspace_id` is derived from the key's workspace, not from any user-provided parameter. A user cannot use Key A (workspace X) to access data in workspace Y.

**Rule T3:** Share link tokens are globally unique but resolve to a project inside a workspace. The share endpoint does NOT accept `workspace_id` as a parameter — it derives it from the token's associated record.

**Rule T4:** The compliance master library (`compliance_master`, `source_master`, `due_date_rule`, etc.) is global/shared. No workspace-specific rules in MVP.

**Rule T5:** PostgreSQL Row Level Security (RLS) should be enabled on all tenant-scoped tables with policies that enforce `workspace_id` checks. This is defense-in-depth even if application-level checks are correct.

---

## 5. OWNERSHIP AND DELETION

### Project Deletion
- Soft delete only: set `project_status = 'DELETED'`, `deleted_at = NOW()`
- Compliance period instances for deleted projects: retained for 90 days, then purged
- Exports for deleted projects: download URLs expire normally; files purged after 30 days
- Share links for deleted projects: immediately revoked on project deletion

### Workspace Deletion
- Only OWNER can delete workspace
- Requires confirmation (email with deletion code)
- Hard delete scheduled 30 days after request (grace period for recovery)
- All projects, instances, exports, keys, and share links marked deleted immediately

### Ownership Transfer
- OWNER can transfer ownership to another ADMIN in the workspace (Phase 2 feature)
- Not in MVP; current OWNER is always the user who created the workspace
