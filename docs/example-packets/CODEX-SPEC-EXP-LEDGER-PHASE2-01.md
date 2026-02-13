# CODEX-SPEC-EXP-LEDGER-PHASE2-01

## Metadata
* **Packet ID:** CODEX-SPEC-EXP-LEDGER-PHASE2-01
* **Phase:** 2 – Ledger Exposure Guard (Hard Gate)
* **Aligned Scope:** `VEX-SCOPE-EXP-LEDGER-PHASE2`
* **Specification Author:** CODEX (Worker Mode)
* **Status:** ACTIVE
* **Specification Date:** 2026-02-07

## 1. Objective

Translate VEX-SCOPE-EXP-LEDGER-PHASE2 into executable specifications for implementing the LedgerExposureGuard validation module. Define exact implementation steps, validation algorithms, error structures, and gate installation points.

## 2. Implementation Steps

### Step 1: Create LedgerExposureGuard Module (WBS 2.1)

**Action:** Create `apps/business_case/js/engine/ledger-exposure-guard.js`

**Module Structure:**
```javascript
/**
 * LedgerExposureGuard - Validates ledger exposure contracts
 * Enforces Phase 1 schema, branch completeness, and derivation rules
 *
 * Authority: VEX-SCOPE-EXP-LEDGER-PHASE2
 * Schema: ledger_exposure_schema_v1.json
 * Branch Rules: branch_completeness_rule_v1.md
 * Derivation Rules: derivation_contract_v1.md
 */

const LedgerExposureGuard = {
    // Main validation entry point
    validateContract(semanticNodes, executionResults = null),

    // Validation 1: Non-empty semantic spine
    validateNonEmptySpine(semanticNodes),

    // Validation 2: Bindings reference executed variables
    validateBindingsToExecution(semanticNodes, executionResults),

    // Validation 3: No unbound leaves
    validateNoUnboundLeaves(semanticNodes),

    // Validation 4: No orphaned branches (from Phase 1)
    validateBranchCompleteness(semanticNodes),

    // Validation 5: No duplicate bindings
    validateNoDuplicateBindings(semanticNodes),

    // Validation 6: Derivations comply with allowed set
    validateDerivations(semanticNodes)
};
```

**Validation Function Specifications:**

#### Validation 1: validateNonEmptySpine(semanticNodes)

**Purpose:** Ensure contract has at least one semantic node

**Algorithm:**
```
1. Check if semanticNodes is an array
2. Check if semanticNodes.length >= 1
3. If false, return error EMPTY_SEMANTIC_SPINE
4. Return { valid: true }
```

**Error Response:**
```json
{
  "valid": false,
  "errorCode": "EMPTY_SEMANTIC_SPINE",
  "message": "Ledger exposure contract must have at least one semantic node",
  "context": {},
  "blocking": true
}
```

#### Validation 2: validateBindingsToExecution(semanticNodes, executionResults)

**Purpose:** Ensure OBSERVED nodes bind to variables in execution results

**Algorithm:**
```
1. If executionResults is null, return { valid: true } (pre-execution check)
2. Extract all variable IDs from executionResults
3. For each node in semanticNodes:
   a. If node.exposureType === "OBSERVED":
      - For each bindingId in node.bindings:
        * If bindingId NOT in executionResults variable IDs:
          - Return error UNBOUND_OBSERVED_NODE
4. Return { valid: true }
```

**Error Response:**
```json
{
  "valid": false,
  "errorCode": "UNBOUND_OBSERVED_NODE",
  "message": "OBSERVED node references variable not in execution results",
  "context": {
    "nodeId": "<semanticNodeId>",
    "unboundVariable": "<variableId>"
  },
  "blocking": true
}
```

#### Validation 3: validateNoUnboundLeaves(semanticNodes)

**Purpose:** Ensure all LEAF nodes have at least one binding

**Algorithm:**
```
1. For each node in semanticNodes:
   a. If node.nodeType === "LEAF":
      - If node.bindings.length === 0:
        * Return error UNBOUND_LEAF
2. Return { valid: true }
```

**Error Response:**
```json
{
  "valid": false,
  "errorCode": "UNBOUND_LEAF",
  "message": "LEAF node must have at least one binding",
  "context": {
    "nodeId": "<semanticNodeId>"
  },
  "blocking": true
}
```

#### Validation 4: validateBranchCompleteness(semanticNodes)

**Purpose:** Apply Phase 1 branch completeness rule

**Algorithm (from Phase 1 branch_completeness_rule_v1.md):**
```
1. Find ROOT nodes (parentNodeId === null)
2. If ROOT count !== 1:
   - Return error NO_ROOT or MULTIPLE_ROOTS
3. Build parent-child map
4. For each non-ROOT node:
   - Validate parent exists (error: INVALID_PARENT_REF)
5. Detect cycles using ancestry chain validation
   - If cycle detected, return error CYCLE_DETECTED
6. Find terminal nodes (no children)
7. For each terminal node:
   - If nodeType !== "LEAF": Return error TERMINAL_NOT_LEAF
   - If bindings.length === 0: Return error TERMINAL_NO_BINDINGS
8. Return { valid: true }
```

**Error Responses:**
```json
{
  "valid": false,
  "errorCode": "NO_ROOT | MULTIPLE_ROOTS | INVALID_PARENT_REF | CYCLE_DETECTED | TERMINAL_NOT_LEAF | TERMINAL_NO_BINDINGS",
  "message": "<specific message>",
  "context": { "nodeId": "<semanticNodeId>" },
  "blocking": true
}
```

#### Validation 5: validateNoDuplicateBindings(semanticNodes)

**Purpose:** Ensure same variable ID not bound to multiple LEAF nodes

**Algorithm:**
```
1. Create bindingMap: { variableId -> [nodeIds] }
2. For each node in semanticNodes:
   a. If node.nodeType === "LEAF":
      - For each bindingId in node.bindings:
        * Add node.semanticNodeId to bindingMap[bindingId]
3. For each variableId in bindingMap:
   - If bindingMap[variableId].length > 1:
     * Return error DUPLICATE_BINDING
4. Return { valid: true }
```

**Error Response:**
```json
{
  "valid": false,
  "errorCode": "DUPLICATE_BINDING",
  "message": "Variable ID bound to multiple LEAF nodes",
  "context": {
    "variableId": "<variableId>",
    "boundToNodes": ["<nodeId1>", "<nodeId2>"]
  },
  "blocking": true
}
```

#### Validation 6: validateDerivations(semanticNodes)

**Purpose:** Validate DERIVED nodes comply with NPV_V1/BCR_V1 contract

**Algorithm:**
```
1. For each node in semanticNodes:
   a. If node.exposureType === "DERIVED":
      - If !node.derivationMetadata: Return error MISSING_DERIVATION_METADATA
      - If derivationType NOT in ["NPV_V1", "BCR_V1"]: Return error UNKNOWN_DERIVATION
      - For each input in derivationMetadata.inputs:
        * Find input node by nodeId
        * If not found: Return error MISSING_INPUT
        * If inputNode.exposureType !== "OBSERVED": Return error INPUT_NOT_OBSERVED
2. Return { valid: true }
```

**Error Responses:**
```json
{
  "valid": false,
  "errorCode": "UNKNOWN_DERIVATION | MISSING_INPUT | INPUT_NOT_OBSERVED | MISSING_DERIVATION_METADATA",
  "message": "<specific message>",
  "context": {
    "nodeId": "<semanticNodeId>",
    "derivationType": "<type>",
    "missingInput": "<inputNodeId>"
  },
  "blocking": true
}
```

### Step 2: Define Error Response Structure (WBS 2.2)

**Action:** Create standardized error response format

**Error Response Schema:**
```javascript
{
  valid: Boolean,           // false for errors
  errorCode: String,        // Machine-readable error code
  message: String,          // Human-readable description
  context: Object,          // Error-specific context (nodeId, variableId, etc.)
  blocking: Boolean         // true = halt execution
}
```

**Success Response Schema:**
```javascript
{
  valid: true
}
```

**Behavior Specification:**

**Option A: Fail-Fast (Recommended)**
- Stop on first validation failure
- Return single error object
- Throw exception with error details

**Option B: Collect-All**
- Run all validations
- Collect all errors in array
- Return array of error objects
- Still block execution if any error has blocking: true

**Implementation Decision:** Use **Fail-Fast** (Option A) for Phase 2
- Simpler error handling
- Faster detection of critical issues
- Can evolve to collect-all in future version

### Step 3: Install Guards at Enforcement Points (WBS 2.3)

**Gate Point 1: Model Load (Pre-Execution)**

**Location:** `apps/business_case/js/model-builder-data-adapter.js` or wherever model is loaded for execution

**Installation:**
```javascript
// In loadModelForExecution() or similar function
function loadModelForExecution(modelId) {
    const model = fetchModelFromDatabase(modelId);
    const semanticNodes = model.semanticNodes || [];

    // GATE 1: Pre-execution validation
    const validation = LedgerExposureGuard.validateContract(semanticNodes, null);
    if (!validation.valid) {
        throw new Error(`MODEL_LOAD_BLOCKED: ${validation.message} [${validation.errorCode}]`);
    }

    return model;
}
```

**Validates:**
- Contract structure (non-empty spine, branch completeness)
- LEAF nodes have bindings
- Derivation metadata present and valid
- No duplicate bindings

**Does NOT validate:**
- Bindings to execution results (no results yet)

**Gate Point 2: Post-Execution, Pre-Projection**

**Location:** `apps/business_case/js/engine/ledger-generator.js` - before generateLedger()

**Installation:**
```javascript
// In generateLedger() function
function generateLedger(executionResults, semanticNodes, modelMetadata) {
    // GATE 2: Post-execution validation
    const validation = LedgerExposureGuard.validateContract(semanticNodes, executionResults);
    if (!validation.valid) {
        throw new Error(`LEDGER_GENERATION_BLOCKED: ${validation.message} [${validation.errorCode}]`);
    }

    // Proceed with ledger generation
    // ... existing code ...
}
```

**Validates:**
- All Gate 1 validations
- OBSERVED nodes bind to executed variables
- Derivation inputs exist in execution results

**Gate Point 3: Projection Registration (Pre-Scenario Outputs)**

**Location:** `apps/business_case/js/scenario-output.js` or wherever execution is saved to registry

**Installation:**
```javascript
// In registerProjection() or saveExecutionToRegistry()
function registerProjection(execution) {
    const semanticNodes = execution.model.semanticNodes || [];
    const executionResults = execution.results;

    // GATE 3: Full contract + execution validation
    const validation = LedgerExposureGuard.validateContract(semanticNodes, executionResults);
    if (!validation.valid) {
        throw new Error(`PROJECTION_REGISTRATION_BLOCKED: ${validation.message} [${validation.errorCode}]`);
    }

    // Save to registry
    // ... existing code ...
}
```

**Validates:**
- All validations (Gate 1 + Gate 2)
- Full contract integrity

## 3. Acceptance Criteria

### AC1: Guard Module Exists
- ✅ File `apps/business_case/js/engine/ledger-exposure-guard.js` exists
- ✅ Module exports all 7 functions (validateContract + 6 validators)
- ✅ All functions are pure (no side effects, deterministic)

### AC2: Error Coverage
- ✅ All 15 error codes have explicit detection logic:
  - EMPTY_SEMANTIC_SPINE
  - UNBOUND_OBSERVED_NODE
  - UNBOUND_LEAF
  - NO_ROOT
  - MULTIPLE_ROOTS
  - INVALID_PARENT_REF
  - CYCLE_DETECTED
  - TERMINAL_NOT_LEAF
  - TERMINAL_NO_BINDINGS
  - DUPLICATE_BINDING
  - UNKNOWN_DERIVATION
  - MISSING_INPUT
  - INPUT_NOT_OBSERVED
  - MISSING_DERIVATION_METADATA
  - (1 additional error for robustness: INVALID_NODE_STRUCTURE)

### AC3: Gate Installation
- ✅ Gate 1 installed in model load path (pre-execution)
- ✅ Gate 2 installed in ledger generator (post-execution)
- ✅ Gate 3 installed in projection registration (pre-scenario outputs)
- ✅ All gates use fail-fast blocking behavior

### AC4: Negative Tests
- ✅ Test file `tests/verify_ledger_exposure_guard.js` exists
- ✅ Tests for all 15 error codes (each error can be triggered)
- ✅ Tests prove invalid contracts blocked at all 3 gates
- ✅ Tests use Class A evidence (deterministic assertions)

### AC5: Non-Projectable Blocking
- ✅ Test proves invalid contract cannot reach Scenario Outputs
- ✅ Error thrown before execution reaches scenario-output.js
- ✅ Registry remains unchanged when invalid contract blocked

## 4. Implementation Notes

**Determinism Requirements:**
- All validation functions MUST be deterministic (same input → same output)
- No dependency on wall-clock time, Math.random(), or external state
- Use only contract schema and execution results for validation

**Performance Considerations:**
- Branch completeness validation is O(N²) worst case (acceptable for typical tree sizes)
- Binding validation is O(N*M) where N=nodes, M=bindings per node
- Pre-execution validation runs once per model load (amortized cost)

**Error Message Quality:**
- Each error MUST include actionable message (what to fix)
- Context MUST include nodeId or variableId for debugging
- Error codes MUST be stable (do not change across versions)

## 5. Verification Plan

**Verification Method:** Create deterministic test suite

**Test Categories:**

1. **Valid Contract Tests** (should pass all gates)
   - Valid NPV contract
   - Valid BCR contract
   - Valid mixed contract (OBSERVED + DERIVED)

2. **Invalid Contract Tests** (should block at gates)
   - Empty semantic spine
   - Unbound LEAF node
   - Missing ROOT
   - Multiple ROOTs
   - Invalid parent reference
   - Cycle in tree
   - Terminal node not LEAF
   - Duplicate binding
   - Unknown derivation type
   - DERIVED node missing input
   - Input node not OBSERVED

3. **Gate Installation Tests**
   - Gate 1 blocks at model load
   - Gate 2 blocks at ledger generation
   - Gate 3 blocks at projection registration

4. **Evidence Quality**
   - All tests use Class A evidence (deterministic assertions)
   - No manual verification required
   - Test results are reproducible

## 6. Files to Create/Modify

**New Files:**
1. `apps/business_case/js/engine/ledger-exposure-guard.js` (~400 lines)
2. `tests/verify_ledger_exposure_guard.js` (~600 lines)

**Modified Files:**
1. `apps/business_case/js/model-builder-data-adapter.js` (add Gate 1)
2. `apps/business_case/js/engine/ledger-generator.js` (add Gate 2)
3. `apps/business_case/js/scenario-output.js` (add Gate 3)

**Total Files:** 2 new, 3 modified

## 7. Success Metrics

- All 6 validation functions implemented ✅
- All 15 error codes covered ✅
- All 3 gates installed ✅
- All negative tests pass ✅
- Non-projectable blocking verified ✅

## 8. Non-Goals (Deferred to Later Phases)

- Ledger generator simplification (Phase 3)
- Renderer contract hardening (Phase 4)
- Migration tooling (Phase 5)
- Authoring UX improvements (Phase 6)
- Auto-repair of invalid contracts (prohibited by Phase 0)

## 9. Dependencies

**Required Artifacts (from Phase 1):**
- ✅ `ARTIFACTS/ledger_exposure_schema_v1.json`
- ✅ `ARTIFACTS/branch_completeness_rule_v1.md`
- ✅ `ARTIFACTS/derivation_contract_v1.md`

**Required Code Access:**
- Model loading infrastructure (model-builder-data-adapter.js or equivalent)
- Ledger generator (ledger-generator.js)
- Projection registration (scenario-output.js or execution registry)

## 10. Specification Status

**Status:** ✅ COMPLETE - Ready for AG execution

**AG Instructions:**
1. Create ledger-exposure-guard.js with all 6 validation functions
2. Install guards at 3 enforcement points
3. Create comprehensive test suite (verify_ledger_exposure_guard.js)
4. Run tests and provide Class A evidence of PASS
5. Create AG-RESULT packet with evidence

---

**CODEX WORKER SPECIFICATION COMPLETE**

**Next Phase:** AG Execution
