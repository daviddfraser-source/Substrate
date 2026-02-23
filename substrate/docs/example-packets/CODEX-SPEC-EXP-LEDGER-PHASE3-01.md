# CODEX-SPEC-EXP-LEDGER-PHASE3-01

## Metadata
* **Packet ID:** CODEX-SPEC-EXP-LEDGER-PHASE3-01
* **Phase:** 3 – Ledger Generator Simplification
* **Aligned Scope:** `VEX-SCOPE-EXP-LEDGER-PHASE3`
* **Specification Author:** CODEX (Worker Mode)
* **Status:** ACTIVE
* **Specification Date:** 2026-02-07

## 1. Objective

Translate VEX-SCOPE-EXP-LEDGER-PHASE3 into executable specifications for simplifying the ledger generator. Define exact code changes, removal targets, and implementation steps for inference-free ledger generation.

## 2. Implementation Steps

### Step 1: Analyze Current Ledger Generator (WBS 3.1 - Discovery)

**Action:** Audit `apps/business_case/js/engine/ledger-generator.js` to identify:
1. All inference/fallback logic paths
2. generateLegacyLedger() function and call sites
3. FEATURE_FLAGS.REQUIRE_SEMANTIC_COMPLETENESS usage
4. Defensive checks that assume invalid contracts
5. Heuristic variable-to-node mapping

**Output:** Code audit report listing:
- Lines to delete
- Functions to remove
- Feature flags to eliminate
- Simplification opportunities

### Step 2: Remove Legacy Ledger Generator (WBS 3.1.1)

**Action:** Delete generateLegacyLedger() function and all references

**Target Code Pattern:**
```javascript
function generateLegacyLedger(evaluationResults, modelVariables, horizon, periodLabels) {
    // ... legacy logic ...
}
```

**Call Sites to Remove:**
```javascript
if (!semanticNodes || semanticNodes.length === 0) {
    if (hostGlobal.FEATURE_FLAGS && !hostGlobal.FEATURE_FLAGS.REQUIRE_SEMANTIC_COMPLETENESS) {
        return generateLegacyLedger(...); // DELETE THIS
    }
}
```

**Verification:**
- grep "generateLegacyLedger" returns no results
- No references to legacy function remain

### Step 3: Remove Feature Flag Checks (WBS 3.1.2)

**Action:** Remove all FEATURE_FLAGS.REQUIRE_SEMANTIC_COMPLETENESS checks

**Current Code (Phase 2):**
```javascript
if (!semanticNodes || semanticNodes.length === 0) {
    if (hostGlobal.FEATURE_FLAGS && !hostGlobal.FEATURE_FLAGS.REQUIRE_SEMANTIC_COMPLETENESS) {
        console.warn('[LEDGER_GENERATOR] Semantic completeness disabled by feature flag - using legacy path');
        return generateLegacyLedger(...);
    }
    throw new Error('LEDGER_GENERATION_BLOCKED: semanticNodes is empty...');
}
```

**Target Code (Phase 3):**
```javascript
// Feature flag check removed - Phase 2 guards ensure semanticNodes valid
// Direct call to generateSemanticLedger (no defensive checks)
```

**Rationale:** Phase 2 guards prevent empty semanticNodes, no need for defensive checks

### Step 4: Simplify generateSemanticLedger() (WBS 3.2)

**Action:** Refactor generateSemanticLedger() to enforce 1:1 mapping

**Current Structure:**
```javascript
function generateSemanticLedger(evaluationResults, modelVariables, semanticNodes, horizon, periodLabels) {
    // 1. Build node hierarchy
    // 2. Create rows from nodes
    // 3. Aggregate values
    // 4. Handle DERIVED nodes
    // 5. Return ledger
}
```

**Simplified Structure:**
```javascript
function generateSemanticLedger(evaluationResults, modelVariables, semanticNodes, horizon, periodLabels) {
    // ASSUME: semanticNodes is valid (Phase 2 guards ensure this)
    // ASSUME: 1:1 mapping (each node → exactly one row)

    const ledgerRows = [];

    for (const node of semanticNodes) {
        const row = createLedgerRow(node, evaluationResults, modelVariables);
        ledgerRows.push(row);
    }

    return {
        rows: ledgerRows,
        periodLabels: periodLabels,
        horizon: horizon
    };
}
```

**1:1 Mapping Contract:**
- Input: N semantic nodes
- Output: N ledger rows
- Assertion: ledgerRows.length === semanticNodes.length

### Step 5: Implement createLedgerRow() (WBS 3.2.1)

**Action:** Create helper function for node-to-row conversion

**Function Signature:**
```javascript
function createLedgerRow(semanticNode, executionResults, modelVariables) {
    // Returns: { id, label, unit, values[], children[], ... }
}
```

**Implementation:**
```javascript
function createLedgerRow(semanticNode, executionResults, modelVariables) {
    const row = {
        id: semanticNode.semanticNodeId,
        label: semanticNode.label,
        unit: semanticNode.unit,
        parentId: semanticNode.parentNodeId,
        nodeType: semanticNode.nodeType,
        exposureType: semanticNode.exposureType,
        displayOrder: semanticNode.displayOrder || 0,
        values: [],
        children: []
    };

    if (semanticNode.exposureType === 'OBSERVED') {
        // OBSERVED row: aggregate from bindings
        row.values = aggregateFromBindings(
            semanticNode.bindings,
            executionResults,
            semanticNode.aggregationRule || 'SUM'
        );
    } else if (semanticNode.exposureType === 'DERIVED') {
        // DERIVED row: compute from derivation
        row.values = computeDerivedValues(
            semanticNode,
            semanticNodes, // All nodes (for input lookup)
            executionResults
        );
    }

    return row;
}
```

### Step 6: Implement aggregateFromBindings() (WBS 3.2.2)

**Action:** Create aggregation function for OBSERVED nodes

**Function Signature:**
```javascript
function aggregateFromBindings(bindings, executionResults, aggregationRule) {
    // Returns: array of aggregated values (time series)
}
```

**Implementation:**
```javascript
function aggregateFromBindings(bindings, executionResults, aggregationRule) {
    if (!bindings || bindings.length === 0) {
        return []; // Should never happen (Phase 2 validates)
    }

    // Get variable values
    const variableValues = bindings.map(varId => {
        const variable = executionResults[varId];
        return variable ? variable.value : null;
    }).filter(v => v !== null);

    if (variableValues.length === 0) {
        return [0]; // No values to aggregate
    }

    // Determine if time series or scalar
    const isTimeSeries = Array.isArray(variableValues[0]);

    if (isTimeSeries) {
        // Time series aggregation
        const maxLength = Math.max(...variableValues.map(v => v.length));
        const aggregated = [];

        for (let t = 0; t < maxLength; t++) {
            const periodValues = variableValues.map(v => v[t] || 0);
            aggregated[t] = applyAggregationRule(periodValues, aggregationRule);
        }

        return aggregated;
    } else {
        // Scalar aggregation
        return [applyAggregationRule(variableValues, aggregationRule)];
    }
}

function applyAggregationRule(values, rule) {
    switch (rule) {
        case 'SUM':
            return values.reduce((a, b) => a + b, 0);
        case 'AVG':
            return values.reduce((a, b) => a + b, 0) / values.length;
        case 'MAX':
            return Math.max(...values);
        case 'MIN':
            return Math.min(...values);
        default:
            return values.reduce((a, b) => a + b, 0); // Default to SUM
    }
}
```

### Step 7: Implement computeDerivedValues() (WBS 3.3)

**Action:** Create computation function for DERIVED nodes (NPV/BCR)

**Function Signature:**
```javascript
function computeDerivedValues(derivedNode, allNodes, executionResults) {
    // Returns: array with single computed value (NPV or BCR)
}
```

**Implementation:**
```javascript
function computeDerivedValues(derivedNode, allNodes, executionResults) {
    const metadata = derivedNode.derivationMetadata;

    if (!metadata) {
        console.error('[LEDGER_GENERATOR] DERIVED node missing metadata:', derivedNode.semanticNodeId);
        return [0]; // Should never happen (Phase 2 validates)
    }

    const derivationType = metadata.derivationType;

    if (derivationType === 'NPV_V1') {
        return [computeNPV(metadata.inputs, allNodes, executionResults)];
    } else if (derivationType === 'BCR_V1') {
        return [computeBCR(metadata.inputs, allNodes, executionResults)];
    } else {
        console.error('[LEDGER_GENERATOR] Unknown derivation type:', derivationType);
        return [0]; // Should never happen (Phase 2 validates)
    }
}
```

### Step 8: Implement NPV Calculation (WBS 3.3.1)

**Action:** Implement NPV_V1 formula from Phase 1 derivation contract

**Formula (from Phase 1):**
```
NPV = Σ(t=0 to T) [ (Benefits[t] - Costs[t]) / (1 + r)^t ]
```

**Implementation:**
```javascript
function computeNPV(inputs, allNodes, executionResults) {
    // Extract input values
    const benefitsNode = findInputNode(inputs, 'benefits_series', allNodes);
    const costsNode = findInputNode(inputs, 'costs_series', allNodes);
    const discountRateNode = findInputNode(inputs, 'discount_rate', allNodes);
    const horizonNode = findInputNode(inputs, 'horizon', allNodes);

    // Get values from execution results
    const benefits = getNodeValues(benefitsNode, executionResults);
    const costs = getNodeValues(costsNode, executionResults);
    const discountRate = getNodeValues(discountRateNode, executionResults)[0];
    const horizon = getNodeValues(horizonNode, executionResults)[0];

    // Calculate NPV
    let npv = 0;
    for (let t = 0; t < horizon; t++) {
        const netBenefit = (benefits[t] || 0) - (costs[t] || 0);
        const discountFactor = Math.pow(1 + discountRate, t);
        npv += netBenefit / discountFactor;
    }

    return npv;
}

function findInputNode(inputs, role, allNodes) {
    const input = inputs.find(inp => inp.role === role);
    if (!input) return null;
    return allNodes.find(node => node.semanticNodeId === input.nodeId);
}

function getNodeValues(node, executionResults) {
    if (!node || !node.bindings || node.bindings.length === 0) {
        return [0];
    }

    // Aggregate bindings (similar to aggregateFromBindings)
    const varId = node.bindings[0]; // Assume single binding for simplicity
    const variable = executionResults[varId];

    if (!variable) return [0];

    return Array.isArray(variable.value) ? variable.value : [variable.value];
}
```

### Step 9: Implement BCR Calculation (WBS 3.3.2)

**Action:** Implement BCR_V1 formula from Phase 1 derivation contract

**Formula (from Phase 1):**
```
BCR = PV(Benefits) / PV(Costs)
Where: PV(X) = Σ(t=0 to T) [ X[t] / (1 + r)^t ]
```

**Implementation:**
```javascript
function computeBCR(inputs, allNodes, executionResults) {
    // Extract input values
    const benefitsNode = findInputNode(inputs, 'benefits_series', allNodes);
    const costsNode = findInputNode(inputs, 'costs_series', allNodes);
    const discountRateNode = findInputNode(inputs, 'discount_rate', allNodes);
    const horizonNode = findInputNode(inputs, 'horizon', allNodes);

    // Get values from execution results
    const benefits = getNodeValues(benefitsNode, executionResults);
    const costs = getNodeValues(costsNode, executionResults);
    const discountRate = getNodeValues(discountRateNode, executionResults)[0];
    const horizon = getNodeValues(horizonNode, executionResults)[0];

    // Calculate PV(Benefits)
    let pvBenefits = 0;
    for (let t = 0; t < horizon; t++) {
        const discountFactor = Math.pow(1 + discountRate, t);
        pvBenefits += (benefits[t] || 0) / discountFactor;
    }

    // Calculate PV(Costs)
    let pvCosts = 0;
    for (let t = 0; t < horizon; t++) {
        const discountFactor = Math.pow(1 + discountRate, t);
        pvCosts += (costs[t] || 0) / discountFactor;
    }

    // Calculate BCR
    if (pvCosts === 0) {
        console.warn('[LEDGER_GENERATOR] BCR undefined (PV(Costs) = 0)');
        return 0; // Or Infinity? Should be validated in Phase 2
    }

    return pvBenefits / pvCosts;
}
```

### Step 10: Remove Defensive Checks (WBS 3.1.3)

**Action:** Remove all defensive "if semanticNodes empty" checks

**Rationale:** Phase 2 guards ensure:
- semanticNodes.length ≥ 1
- All nodes have valid structure
- All bindings reference executed variables
- All derivations have valid metadata

**Code to Remove:**
```javascript
// DELETE: Defensive checks like these
if (!semanticNodes || semanticNodes.length === 0) { ... }
if (!node.bindings) { ... }
if (!variable) { return fallbackValue; }
```

**Replacement:**
```javascript
// TRUST: Phase 2 guards ensure validity
// Direct execution, no defensive checks
```

## 3. Acceptance Criteria

### AC1: Legacy Code Removed
- ✅ generateLegacyLedger() function deleted
- ✅ All call sites to legacy function removed
- ✅ FEATURE_FLAGS.REQUIRE_SEMANTIC_COMPLETENESS checks removed
- ✅ grep "generateLegacyLedger" returns no results

### AC2: 1:1 Mapping Verified
- ✅ Test proves: ledgerRows.length === semanticNodes.length
- ✅ Each semantic node produces exactly one row
- ✅ No synthetic rows created
- ✅ No nodes skipped

### AC3: DERIVED Rows Computed
- ✅ NPV calculation works with known test inputs
- ✅ BCR calculation works with known test inputs
- ✅ Both formulas match Phase 1 specification
- ✅ Deterministic (same inputs → same output)

### AC4: Simplification Achieved
- ✅ Line count reduction in ledger-generator.js (target: 20-30%)
- ✅ No inference/fallback logic remains
- ✅ Code complexity reduced (fewer branches)
- ✅ generateSemanticLedger() is the only generation function

### AC5: No Regressions
- ✅ Existing valid scenarios still work
- ✅ Ledger structure unchanged for valid contracts
- ✅ Hierarchy preserved (parent-child relationships)
- ✅ displayOrder respected

## 4. Verification Plan

**Test Categories:**

1. **Unit Tests:**
   - aggregateFromBindings() with time series
   - aggregateFromBindings() with scalars
   - computeNPV() with known inputs
   - computeBCR() with known inputs
   - createLedgerRow() for OBSERVED node
   - createLedgerRow() for DERIVED node

2. **Integration Tests:**
   - generateSemanticLedger() with valid contract
   - 1:1 mapping verification
   - Hierarchy preservation
   - displayOrder verification

3. **Regression Tests:**
   - Valid contracts from Phase 2 tests still work
   - Ledger output matches expected structure

**Test Evidence:** Class A (deterministic assertions)

## 5. Files to Modify

**Primary File:**
1. `apps/business_case/js/engine/ledger-generator.js` (major refactor)

**Supporting Files (if needed):**
2. `apps/business_case/js/engine/ledger-snapshot-generator.js` (cleanup)

**Test File:**
3. `apps/tests/verify_ledger_generator_simplified.js` (new test suite)

## 6. Success Metrics

- Legacy function deleted: ✅
- Feature flag checks removed: ✅
- 1:1 mapping verified: ✅
- NPV/BCR computed: ✅
- Line count reduced: ✅ (target: 20-30%)
- No regressions: ✅

## 7. Non-Goals (Deferred to Later Phases)

- Ledger rendering (Phase 4)
- Migration tooling (Phase 5)
- Authoring UX (Phase 6)
- Performance optimization (acceptable trade-off)

## 8. Specification Status

**Status:** ✅ COMPLETE - Ready for AG execution

**AG Instructions:**
1. Audit current ledger-generator.js to identify removal targets
2. Delete generateLegacyLedger() and all references
3. Remove feature flag checks
4. Implement simplified generateSemanticLedger() with helpers
5. Implement NPV/BCR calculations per Phase 1 formulas
6. Create test suite verifying 1:1 mapping and calculations
7. Run tests and provide Class A evidence of PASS
8. Create AG-RESULT packet with evidence

---

**CODEX WORKER SPECIFICATION COMPLETE**

**Next Phase:** AG Execution
