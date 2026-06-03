# C4 — Applicability Encoding Framework
## How Applicability Logic Is Represented, Evaluated, and Surfaced

---

## 1. Objective

Define exactly how a compliance obligation's applicability logic is encoded in the master library, how that logic is evaluated against a business profile at runtime, and what outputs the evaluation produces. Establish a clear boundary between what belongs in the master layer and what belongs in the instance layer.

---

## 2. Why It Matters to the Compliance Engine

The applicability engine is the mechanism by which the system determines whether a given law applies to a given business. An incorrectly encoded applicability rule creates false positives (showing irrelevant obligations) or false negatives (missing applicable obligations). Both are harmful — false negatives in a compliance product carry legal risk for the user.

---

## 3. Three-Layer Separation

The single most important principle in this section:

```
LAYER 1 — MASTER LIBRARY (static, shared)
  Stores: the rule expression encoding what conditions make a law applicable
  Ask: "What facts about a business would make this law apply?"
  Lives in: applicability_rule.rule_expression (JSONB)

LAYER 2 — BUSINESS PROFILE (dynamic, per-business)
  Stores: the actual facts about a specific business
  Ask: "What are the facts about THIS business?"
  Lives in: business_profile fields (entity_type, gst_registered, etc.)

LAYER 3 — RUNTIME EVALUATION (computed, per-business-per-rule)
  Stores: the determination produced by evaluating Layer 1 against Layer 2
  Ask: "Given these facts, does this law apply to this business?"
  Lives in: compliance_period_instance.applicability_status + why_it_applies
```

**Nothing in Layer 1 references a specific business.** Nothing in Layer 3 references raw legal provisions — it references evaluation outputs. The evaluation engine reads Layer 1 and Layer 2 and produces Layer 3.

---

## 4. Applicability Rule Node Types

The applicability rule is stored as a tree of condition nodes. The following node types are recognized. They are defined here as documentation constructs — not as code.

---

### Node Type: CONDITION

**Purpose:** Evaluate a simple boolean or equality condition against a business profile field.

**Documentation form:**
```
CONDITION {
  field: <business_profile_field_name>
  operator: EQ | NEQ | IN | NOT_IN | IS_NULL | IS_NOT_NULL
  value: <expected_value>      (for EQ/NEQ)
  values: [<val1>, <val2>...]  (for IN/NOT_IN)
  confidence_contribution: HIGH | MEDIUM | LOW
}
```

**When to use:** When the applicability check is binary and the field value is directly known. Example: `gst_registered = true` for all GST obligations.

---

### Node Type: THRESHOLD

**Purpose:** Evaluate whether a numeric field meets a threshold, handling the case where only a band (not an exact value) is known.

**Documentation form:**
```
THRESHOLD {
  field: <numeric_field>
  operator: GT | GTE | LT | LTE
  value: <threshold_number>
  
  // If exact field value not available, fall back to band field:
  band_field: <band_enum_field>                   (optional)
  band_values_above_threshold: [<enum_val>...]     (unambiguously above)
  band_values_below_threshold: [<enum_val>...]     (unambiguously below)
  band_values_ambiguous: [<enum_val>...]           (threshold might or might not be crossed)
  
  confidence_if_exact: HIGH
  confidence_if_band_above: HIGH
  confidence_if_band_below: HIGH
  confidence_if_band_ambiguous: MEDIUM
}
```

**When to use:** For turnover-based thresholds (e-invoicing, GST registration, tax audit), employee-count thresholds (EPF, ESI, Bonus Act), capital thresholds (small company definition).

**Band ambiguity example:**
- E-invoicing threshold: ₹5 Cr
- Business in `1CR_5CR` band → cannot confirm whether above or below ₹5 Cr
- Result: `applicability_status: CHECK_THRESHOLD`, confidence: MEDIUM
- Output to user: "Your turnover band (₹1 Cr – ₹5 Cr) means e-invoicing may apply. Confirm if your actual turnover exceeds ₹5 Cr."

---

### Node Type: AND

**Purpose:** All child conditions must be true.

**Documentation form:**
```
AND {
  conditions: [<node1>, <node2>, ...]
  confidence_aggregation: MIN  (result confidence = lowest among children)
}
```

**When to use:** When multiple conditions must simultaneously hold. Example: GSTR-3B requires `gst_registered = true` AND `gst_scheme = REGULAR` AND `filing_frequency = MONTHLY`.

---

### Node Type: OR

**Purpose:** At least one child condition must be true.

**Documentation form:**
```
OR {
  conditions: [<node1>, <node2>, ...]
  confidence_aggregation: MAX  (result confidence = highest among applicable children)
}
```

**When to use:** When any one of multiple conditions triggers the obligation. Example: Mandatory GST registration triggers if `has_interstate_supply = true` OR `has_ecommerce = true` OR `annual_turnover > ₹20L` (goods) / ₹10L (special category states).

---

### Node Type: NOT_APPLICABLE_IF

**Purpose:** Defines a condition under which the obligation explicitly does NOT apply, even if other conditions are met.

**Documentation form:**
```
NOT_APPLICABLE_IF {
  conditions: [<node1>, <node2>, ...]
  reason: <string: why this condition negates applicability>
}
```

**When to use:** For statutory exemptions. Example: DPT-3 — "NOT_APPLICABLE if entity_type = GOVERNMENT_COMPANY" (per Rule 16A(3) explicit exclusion).

---

### Node Type: STATE_SPECIFIC

**Purpose:** Handles obligations that apply only in specific states, with a fallback for uncovered states.

**Documentation form:**
```
STATE_SPECIFIC {
  field: principal_state  (or state_codes_present for multi-state)
  covered_states: ["MH", "KA", "TN", ...]
  uncovered_states_behavior: STATE_SPECIFIC  (or NOT_APPLICABLE)
  covered_state_rule: <child_rule_node>
}
```

**When to use:** Professional Tax, Shops & Establishments, Factories Act compliance, state-specific labour laws.

**For states not in covered_states:** The evaluation returns `applicability_status: STATE_SPECIFIC` with the note "Check the applicable rules in your state. This rule has not yet been encoded for your state."

---

### Node Type: EVENT_TRIGGERED

**Purpose:** The obligation only arises when a specific event occurs (change of director, share allotment, etc.).

**Documentation form:**
```
EVENT_TRIGGERED {
  event_field: <boolean_field_in_profile>  (e.g., has_pending_director_changes)
  event_date_field: <date_field>           (e.g., director_change_date)
  if_event_not_occurred: EVENT_TRIGGERED
  if_event_occurred: <child_rule_node for entity-type check, etc.>
}
```

**Output when event not yet occurred:** `applicability_status: EVENT_TRIGGERED`, display message: "Does not apply unless this type of change occurs in your business. Provide the event date if it has already occurred."

---

### Node Type: REQUIRE_FIELD

**Purpose:** Halts evaluation and returns INSUFFICIENT_DATA if a required business profile field is missing.

**Documentation form:**
```
REQUIRE_FIELD {
  required_fields: [<field1>, <field2>, ...]
  if_fields_missing: INSUFFICIENT_DATA
  then_rule: <child_rule_node to evaluate when fields are present>
}
```

**When to use:** For rules that cannot be evaluated without specific inputs the user has not yet provided. Example: Factory Act applicability cannot be determined without `has_manufacturing`, `uses_power_in_mfg`, and `employee_count`.

---

### Node Type: HUMAN_REVIEW_REQUIRED

**Purpose:** Marks conditions where the complexity or ambiguity exceeds what rule expressions can handle.

**Documentation form:**
```
HUMAN_REVIEW_REQUIRED {
  reason: <string: why professional review is needed>
  prerequisite_condition: <optional child node — only trigger if this is met>
}
```

**When to use:** Foreign ownership (FEMA/FDI complexity), regulated sector compliance, complex transfer pricing, multi-state factory operations.

---

## 5. Confidence Propagation Rules

When child nodes are combined via AND or OR, the output confidence follows these aggregation rules:

**AND aggregation (use MIN):**
```
HIGH AND HIGH = HIGH
HIGH AND MEDIUM = MEDIUM
HIGH AND LOW = LOW
MEDIUM AND LOW = LOW
Any INSUFFICIENT_DATA = INSUFFICIENT_DATA (regardless of other conditions)
```

**OR aggregation (use MAX of applicable children):**
```
If any applicable child = HIGH → result = HIGH
If highest applicable child = MEDIUM → result = MEDIUM
If all children = LOW → result = LOW
```

---

## 6. Output States

The evaluation of a rule against a business profile produces one of these applicability statuses:

| Status | Meaning | Display to User |
|--------|---------|----------------|
| `APPLICABLE` | Conditions met, confidence HIGH or MEDIUM | Full compliance item shown with due date |
| `LIKELY_APPLICABLE` | Strong indicators, at least one condition MEDIUM confidence | Shown with amber indicator + "Confirm applicability" |
| `CHECK_THRESHOLD` | Threshold ambiguous due to band input | Shown with "Check if your [turnover/employee count] exceeds [threshold]" |
| `EVENT_TRIGGERED` | Not applicable unless a specific event occurs | Shown in "Event-Triggered" section. "Provide event date if applicable." |
| `STATE_SPECIFIC` | Applies in some states; state not yet encoded | "Check applicable rules in your state." |
| `RECOMMENDED` | Not mandatory; beneficial | Shown in separate "Recommended" section |
| `NOT_APPLICABLE` | Clearly does not apply | Not shown (or in collapsed section) |
| `INSUFFICIENT_DATA` | Profile incomplete to evaluate | Shown in "Needs More Information" section with missing field names |
| `HUMAN_REVIEW_REQUIRED` | Too complex for rule expression | Shown with "Professional review recommended" flag |
| `FUTURE_TRIGGER` | Will apply if business grows/changes past threshold | Shown in "Watch List" |

---

## 7. Handling Missing Business Profile Data

When a business profile is incomplete, the evaluation must degrade gracefully:

**Missing optional fields:** Evaluate without them. If the field being checked is null/unknown and the condition requires it, use REQUIRE_FIELD to return INSUFFICIENT_DATA rather than making an incorrect determination.

**Missing fields that could only increase applicability:** If a missing field (e.g., `has_manufacturing`) could only expand obligations (not reduce them), a conservative system might treat the missing value as false (safe — does not falsely trigger an obligation). However, this means a manufacturing business that hasn't answered the question will miss the Factory Act flag. The preferred approach: surface INSUFFICIENT_DATA and prompt the user to answer.

**Missing fields that could reduce applicability:** For example, if `has_interstate_supply` is null, the system should NOT assume the business has no interstate supply, because that could cause it to miss mandatory GST registration. In ambiguous direction cases, default to showing the obligation as LIKELY_APPLICABLE and flagging the missing input.

---

## 8. What Should Be Deferred

- Applicability rules for state-specific obligations beyond the top 5 priority states should be deferred to Phase 2 population.
- Complex sector-specific rules (pharma, food processing regulations, mining) should be deferred and shown as HUMAN_REVIEW_REQUIRED.
- Rules requiring matching of the business's specific supplier/customer profile (e.g., whether counterparties are MSME-registered) cannot be fully automated and should be shown as CHECK_THRESHOLD with user guidance.
