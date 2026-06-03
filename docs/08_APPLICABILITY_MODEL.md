# Document 08 — Applicability Model
## Applicability Status Taxonomy, Confidence Model, and Rule Expressions

---

## 1. APPLICABILITY STATUS TAXONOMY

Every compliance item evaluated against a business profile must produce one of these statuses:

### APPLICABLE
**Definition:** Clearly applies based on confirmed inputs. High confidence.
**Example:** Business is GST-registered regular taxpayer → GSTR-3B is APPLICABLE.
**What the system shows:** Full compliance record with due dates and severity.

### LIKELY_APPLICABLE
**Definition:** Strong indicators suggest it applies, but one or more inputs are uncertain or unconfirmed.
**Example:** Turnover entered as "₹5Cr–₹10Cr" but E-invoicing threshold is ₹5Cr → likely applicable but exact threshold crossing unconfirmed.
**What the system shows:** Compliance shown with amber indicator + "Confirm applicability" note.

### CHECK_THRESHOLD
**Definition:** Applicability depends on a specific threshold that the system knows about but the business hasn't confirmed crossing.
**Example:** Employee count entered as 15–19 → EPF threshold is 20 → "Check if you've reached 20 employees."
**What the system shows:** Compliance shown as "Threshold Check Required" with the specific threshold and current known data.

### EVENT_TRIGGERED
**Definition:** Compliance only arises when a specific event occurs. No event has been reported yet.
**Example:** DIR-12 (director change) → no director change reported by user.
**What the system shows:** Shown in "Event-Triggered" section. "Does not apply unless a relevant event occurs. If it has, provide the event date."

### STATE_SPECIFIC
**Definition:** Whether this compliance applies depends on state-level rules not fully modeled for the user's state.
**Example:** Professional Tax in a state where PT rates/rules are not yet in the database.
**What the system shows:** Compliance shown with state flag and "Check applicable rules for [State]."

### RECOMMENDED
**Definition:** Not legally mandatory, but strongly recommended for business benefit or risk reduction.
**Example:** Udyam registration for an MSME-eligible business (not mandatory but unlocks benefits).
**What the system shows:** Shown in a "Recommended / Optional" section separate from mandatory obligations.

### NOT_APPLICABLE
**Definition:** Clearly does not apply based on inputs.
**Example:** EPF compliance for a business with 0 employees.
**What the system shows:** Not shown at all, or shown in a collapsed "Not Applicable" section.

### INSUFFICIENT_DATA
**Definition:** The system cannot make even a LIKELY_APPLICABLE determination because a critical input is missing.
**Example:** Whether Factory Act applies cannot be determined without knowing if manufacturing activity exists and worker count.
**What the system shows:** Shown in "Need More Information" section with specific missing questions.

### HUMAN_REVIEW_REQUIRED
**Definition:** The compliance involves complexity, nuance, or legal interpretation that the rules engine cannot reliably handle. A professional review is needed.
**Example:** FEMA/FDI compliance if foreign ownership is present. Specific exemptions under IT Act. Export-related DGFT obligations.
**What the system shows:** Shown with a "Professional Review Required" flag and a brief reason.

### FUTURE_TRIGGER
**Definition:** Does not apply now, but will apply if the business crosses a predictable threshold or event horizon.
**Example:** "Your turnover is currently ₹3 Cr. If it crosses ₹5 Cr, e-invoicing will become mandatory."
**What the system shows:** Shown in "Watch List" section with the trigger condition and current distance from it.

---

## 2. CONFIDENCE LEVELS

Every applicability decision carries a confidence level separate from the status.

| Confidence | Meaning |
|------------|---------|
| HIGH | ≥ 90% confidence: the rule is clear and inputs are confirmed |
| MEDIUM | 70–89% confidence: the rule is clear but some inputs are estimated or uncertain |
| LOW | < 70% confidence: the rule itself has ambiguity, or inputs are substantially incomplete |

**Confidence affects UI presentation:**
- HIGH confidence → show normally
- MEDIUM confidence → show with "(verify)" note
- LOW confidence → show with amber warning and incomplete-data note

---

## 3. APPLICABILITY DECISION RECORD

For each compliance evaluated for a business, the system stores:

```
applicability_decision {
  business_id
  compliance_id
  applicability_status        (from taxonomy above)
  applicability_confidence    (HIGH / MEDIUM / LOW)
  
  why_it_applies              -- Text: which inputs triggered this
  why_it_may_not_apply        -- Text: edge cases or counterarguments
  missing_inputs              -- List of profile fields that would improve confidence
  threshold_basis             -- Which threshold is the key deciding factor
  state_dependency_basis      -- If state-dependent, which state rule applies
  
  rule_evaluated              -- rule_id from applicability_rule table
  rule_version_used           -- version of rule at evaluation time
  
  human_verification_required -- bool
  professional_review_flag    -- bool
  
  evaluated_at                -- timestamp
  profile_version_at_eval     -- hash of business profile at evaluation time
}
```

---

## 4. RULE EXPRESSION FORMAT

Applicability rules are stored as structured JSON in the `applicability_rule` table.
The engine evaluates these expressions against the `BusinessProfile`.

### 4.1 Simple Condition

```json
{
  "type": "CONDITION",
  "field": "gst_registered",
  "operator": "EQ",
  "value": true,
  "confidence_contribution": "HIGH"
}
```

### 4.2 IN / NOT_IN Condition

```json
{
  "type": "CONDITION",
  "field": "entity_type",
  "operator": "IN",
  "values": ["PRIVATE_LIMITED", "PUBLIC_LIMITED", "OPC"],
  "confidence_contribution": "HIGH"
}
```

### 4.3 Threshold Condition

```json
{
  "type": "THRESHOLD",
  "field": "annual_turnover_estimated",
  "operator": "GTE",
  "value": 10000000,
  "if_field_is_band": "turnover_band",
  "band_values_above_threshold": ["5CR_10CR", "ABOVE_10CR"],
  "band_values_ambiguous": ["1CR_5CR"],
  "confidence_if_exact": "HIGH",
  "confidence_if_band_above": "HIGH",
  "confidence_if_band_ambiguous": "MEDIUM",
  "confidence_if_band_below": "HIGH"
}
```

This handles the fact that users often provide turnover as a band, not an exact number.
If the band is unambiguously above the threshold → HIGH confidence applicable.
If the band straddles the threshold → MEDIUM confidence, needs confirmation.

### 4.4 AND Condition

```json
{
  "type": "AND",
  "conditions": [
    {
      "type": "CONDITION",
      "field": "entity_type",
      "operator": "IN",
      "values": ["PRIVATE_LIMITED", "PUBLIC_LIMITED", "OPC"]
    },
    {
      "type": "THRESHOLD",
      "field": "employee_count",
      "operator": "GTE",
      "value": 20,
      "if_field_is_band": "employee_count_band",
      "band_values_above_threshold": ["20_49", "50_PLUS"],
      "band_values_ambiguous": ["10_19"],
      "confidence_if_band_ambiguous": "MEDIUM"
    }
  ],
  "confidence_aggregation": "MIN"
}
```

### 4.5 OR Condition

```json
{
  "type": "OR",
  "conditions": [
    {
      "type": "CONDITION",
      "field": "has_interstate_supply",
      "operator": "EQ",
      "value": true
    },
    {
      "type": "CONDITION",
      "field": "has_ecommerce",
      "operator": "EQ",
      "value": true
    },
    {
      "type": "THRESHOLD",
      "field": "annual_turnover_estimated",
      "operator": "GTE",
      "value": 2000000
    }
  ],
  "confidence_aggregation": "MAX"
}
```

### 4.6 NOT_APPLICABLE Condition

```json
{
  "type": "NOT_APPLICABLE_IF",
  "conditions": [
    {
      "type": "CONDITION",
      "field": "entity_type",
      "operator": "IN",
      "values": ["PROPRIETORSHIP", "PARTNERSHIP"]
    }
  ],
  "reason": "MCA filing obligations do not apply to unincorporated entities"
}
```

### 4.7 State-Specific Condition

```json
{
  "type": "STATE_SPECIFIC",
  "field": "principal_state",
  "covered_states": ["MH", "KA", "WB", "GJ", "TN", "AP", "TS"],
  "uncovered_states_behavior": "STATE_SPECIFIC",
  "covered_state_rule": {
    "type": "CONDITION",
    "field": "makes_salary_payments",
    "operator": "EQ",
    "value": true
  }
}
```

For states not in `covered_states`, the applicability is STATUS: `STATE_SPECIFIC` rather than APPLICABLE.

### 4.8 Event-Triggered Condition

```json
{
  "type": "EVENT_TRIGGERED",
  "event_field": "has_pending_director_changes",
  "event_date_field": "director_change_date",
  "if_event_not_occurred": "EVENT_TRIGGERED",
  "if_event_occurred": {
    "type": "AND",
    "conditions": [
      {
        "type": "CONDITION",
        "field": "entity_type",
        "operator": "IN",
        "values": ["PRIVATE_LIMITED", "PUBLIC_LIMITED", "OPC"]
      }
    ]
  }
}
```

### 4.9 MISSING_DATA Condition

```json
{
  "type": "REQUIRE_FIELD",
  "required_fields": ["has_manufacturing", "uses_power_in_mfg", "employee_count"],
  "if_fields_missing": "INSUFFICIENT_DATA",
  "then_rule": {
    "type": "AND",
    "conditions": [
      { "type": "CONDITION", "field": "has_manufacturing", "operator": "EQ", "value": true },
      { "type": "CONDITION", "field": "uses_power_in_mfg", "operator": "EQ", "value": true },
      { "type": "THRESHOLD", "field": "employee_count", "operator": "GTE", "value": 10 }
    ]
  }
}
```

---

## 5. RULE EVALUATION ALGORITHM

```python
def evaluate_rule(rule_expression, business_profile):
    rule_type = rule_expression["type"]
    
    if rule_type == "CONDITION":
        return evaluate_simple_condition(rule_expression, business_profile)
    
    elif rule_type == "THRESHOLD":
        return evaluate_threshold(rule_expression, business_profile)
    
    elif rule_type == "AND":
        results = [evaluate_rule(c, business_profile) for c in rule_expression["conditions"]]
        if all(r.is_applicable for r in results):
            status = "APPLICABLE"
            confidence = aggregate_confidence(results, "MIN")
        elif any(r.status == "INSUFFICIENT_DATA" for r in results):
            status = "INSUFFICIENT_DATA"
            confidence = "LOW"
        else:
            status = "NOT_APPLICABLE"
            confidence = "HIGH"
        return ApplicabilityResult(status, confidence)
    
    elif rule_type == "OR":
        results = [evaluate_rule(c, business_profile) for c in rule_expression["conditions"]]
        if any(r.is_applicable for r in results):
            status = "APPLICABLE"
            confidence = aggregate_confidence(results, "MAX")
        else:
            status = "NOT_APPLICABLE"
            confidence = "HIGH"
        return ApplicabilityResult(status, confidence)
    
    elif rule_type == "STATE_SPECIFIC":
        state = business_profile.principal_state
        if state in rule_expression["covered_states"]:
            return evaluate_rule(rule_expression["covered_state_rule"], business_profile)
        else:
            return ApplicabilityResult("STATE_SPECIFIC", "LOW")
    
    elif rule_type == "EVENT_TRIGGERED":
        if business_profile.get(rule_expression["event_field"]):
            return evaluate_rule(rule_expression["if_event_occurred"], business_profile)
        else:
            return ApplicabilityResult("EVENT_TRIGGERED", "HIGH")
    
    elif rule_type == "REQUIRE_FIELD":
        missing = [f for f in rule_expression["required_fields"] 
                   if business_profile.get(f) is None]
        if missing:
            return ApplicabilityResult("INSUFFICIENT_DATA", "LOW", 
                                        missing_inputs=missing)
        else:
            return evaluate_rule(rule_expression["then_rule"], business_profile)
    
    elif rule_type == "NOT_APPLICABLE_IF":
        sub_results = evaluate_rule(
            {"type": "AND", "conditions": rule_expression["conditions"]}, 
            business_profile
        )
        if sub_results.is_applicable:
            return ApplicabilityResult("NOT_APPLICABLE", "HIGH",
                                        reason=rule_expression["reason"])
        else:
            return ApplicabilityResult("APPLICABLE", "HIGH")
```

---

## 6. CONFIDENCE AGGREGATION RULES

When combining multiple condition results:

```
MIN aggregation (AND logic):
  confidence = min(all sub-results confidence)
  HIGH AND HIGH = HIGH
  HIGH AND MEDIUM = MEDIUM
  MEDIUM AND MEDIUM = MEDIUM
  ANY LOW = LOW

MAX aggregation (OR logic):
  confidence = max(all sub-results confidence)
  HIGH OR MEDIUM = HIGH (if the HIGH one is applicable)
  MEDIUM OR MEDIUM = MEDIUM
```

---

## 7. MISSING DATA PROPAGATION

When required fields are missing from the business profile:
1. The rule returns `INSUFFICIENT_DATA`
2. The `missing_inputs` list identifies which fields are needed
3. The UI shows the compliance in the "Needs More Information" section
4. The question for the missing field is surfaced as a prompt in the questionnaire

This creates a feedback loop: the compliance library drives which questionnaire questions are shown as important.

---

## 8. HUMAN REVIEW TRIGGERS

Certain conditions should always elevate to `HUMAN_REVIEW_REQUIRED`:

| Condition | Reason |
|-----------|--------|
| `has_foreign_ownership = true` | FEMA/FDI rules are highly specific and changeable |
| `is_regulated_sector = true` | Sector-specific regulator compliance not in scope |
| `entity_type = PUBLIC_LIMITED` | Complexity of public company compliance exceeds standard model |
| `has_hazardous_material = true` | Environment/safety compliance requires specialist review |
| `activity_type involves chemical/pharma/mining` | Sector-specific compliance |
| Compliance record itself has `requires_human_review = true` | Tagged in master data |

Human review items must still be shown to the user — they are not suppressed. But they are flagged with: "We recommend verifying this with a qualified professional."
