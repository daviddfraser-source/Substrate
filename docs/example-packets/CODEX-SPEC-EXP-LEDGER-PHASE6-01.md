# CODEX-SPEC-EXP-LEDGER-PHASE6-01

## Metadata
* **Packet ID:** CODEX-SPEC-EXP-LEDGER-PHASE6-01
* **Phase:** 6 - Authoring UX Enhancement
* **Authority:** VEX-SCOPE-EXP-LEDGER-PHASE6
* **Author:** CODEX (Worker)
* **Status:** ACTIVE
* **Risk Tier:** 2 (Module - UI/UX Enhancement)

## 1. Objective

Translate VEX-SCOPE-EXP-LEDGER-PHASE6 into executable implementation steps. Create inline validation framework, error highlighting, and guided authoring features for Model Builder 2 semantic nodes tab.

## 2. Prerequisites

**Phase Dependencies:**
- ✅ Phase 2: LedgerExposureGuard.validateContract() available
- ✅ Phase 4: Error rendering patterns established
- ✅ Phase 5: Migration heuristics available (inferCategory, inferNodeType, inferExposureType)

**Files Required:**
- `apps/business_case/model-builder-2.html` (existing)
- `apps/business_case/js/model-builder-2.js` (existing)
- `apps/business_case/js/model-builder-ux.js` (existing)
- `apps/business_case/Governance/explicit_ledger_exposure/phase2_guards/LedgerExposureGuard.js`
- `apps/tools/ledger_migration/migration_engine.js`

## 3. Implementation Steps

### Step 1: Create Validation Framework Module (WBS 6.1)

**File:** `apps/business_case/js/mb2-semantic-validator.js` (NEW)

**Purpose:** Provide real-time validation of semantic nodes using Phase 2 guards

**Interface:**
```javascript
const MB2SemanticValidator = (function() {
    return {
        validate: function(semanticNodes) {
            // Returns: { valid: boolean, errors: [], warnings: [] }
        },
        validateNode: function(node) {
            // Validate single node
        },
        debounce: function(fn, delay) {
            // Debounce helper (500ms default)
        }
    };
})();
```

**Implementation Requirements:**

1. **validate(semanticNodes)** - Main validation function
   - Load Phase 2 guard: `LedgerExposureGuard.validateContract()`
   - Pass semantic nodes to guard
   - Parse validation result
   - Return: `{ valid, errors, warnings }`
   - Graceful fallback if guard unavailable

2. **validateNode(node)** - Single node validation
   - Check required fields: semanticNodeId, label, category, nodeType, exposureType
   - Check parent exists (if not root)
   - Check bindings array present and non-empty
   - Return: `{ valid, errors, warnings }`

3. **debounce(fn, delay)** - Debouncing utility
   - Standard debounce implementation
   - Default delay: 500ms
   - Clear timeout on subsequent calls

**Error Codes:**
- `MISSING_SEMANTIC_NODE_ID` - Node missing ID
- `MISSING_LABEL` - Node missing label
- `MISSING_CATEGORY` - Node missing category
- `INVALID_CATEGORY` - Category not in allowed list
- `MISSING_NODE_TYPE` - Node missing nodeType
- `INVALID_NODE_TYPE` - nodeType not LEAF or GROUP
- `MISSING_EXPOSURE_TYPE` - Node missing exposureType
- `INVALID_EXPOSURE_TYPE` - exposureType not OBSERVED or DERIVED
- `MISSING_BINDINGS` - Node missing bindings array
- `EMPTY_BINDINGS` - Bindings array empty
- `INVALID_PARENT` - Parent node does not exist
- `MISSING_DERIVATION_METADATA` - DERIVED node missing derivationMetadata

**Acceptance Criteria:**
- [ ] validate() returns { valid, errors, warnings }
- [ ] validateNode() validates single node
- [ ] debounce() delays execution by 500ms
- [ ] Graceful fallback if Phase 2 guard unavailable
- [ ] All error codes defined and used

---

### Step 2: Integrate Validation into MB2 Semantic Nodes Tab (WBS 6.1)

**File:** `apps/business_case/js/model-builder-2.js` (MODIFY)

**Changes Required:**

1. **Add Validation Trigger**
   - Listen for semantic node edits (input, textarea, select events)
   - Debounce validation calls (500ms delay)
   - Run validation on: add node, edit node, delete node, reorder nodes

2. **Add Validation State to Model Structure**
   ```javascript
   // Add to model.validation object
   model.validation = {
       semanticNodes: {
           valid: null,        // true/false/null (not run)
           errors: [],         // Array of error objects
           warnings: [],       // Array of warning objects
           lastRun: null       // ISO timestamp
       }
   };
   ```

3. **Add Validation Trigger Function**
   ```javascript
   let validationTimeout = null;

   function triggerSemanticNodeValidation() {
       clearTimeout(validationTimeout);
       validationTimeout = setTimeout(() => {
           runSemanticNodeValidation();
       }, 500);
   }

   function runSemanticNodeValidation() {
       const semanticNodes = extractSemanticNodesFromUI();
       const result = MB2SemanticValidator.validate(semanticNodes);

       model.validation.semanticNodes = {
           valid: result.valid,
           errors: result.errors,
           warnings: result.warnings,
           lastRun: new Date().toISOString()
       };

       updateValidationUI(result);
   }
   ```

4. **Hook Validation into UI Events**
   - Add event listeners to semantic node input fields
   - Trigger validation on blur, change events
   - Trigger validation after drag-drop reorder

**Acceptance Criteria:**
- [ ] Validation runs 500ms after last edit
- [ ] Validation state stored in model.validation
- [ ] Validation triggers on add/edit/delete/reorder
- [ ] No performance issues with large models (>100 nodes)

---

### Step 3: Create Error Highlighting UI (WBS 6.2)

**File:** `apps/business_case/js/mb2-error-highlighter.js` (NEW)

**Purpose:** Apply visual error/warning states to semantic node rows

**Interface:**
```javascript
const MB2ErrorHighlighter = (function() {
    return {
        highlightErrors: function(errors) {
            // Apply error states to rows
        },
        highlightWarnings: function(warnings) {
            // Apply warning states to rows
        },
        clearHighlights: function() {
            // Remove all error/warning states
        },
        attachTooltip: function(element, message, code) {
            // Add error tooltip to element
        }
    };
})();
```

**CSS Classes:**
```css
.semantic-node-row.error {
    border-left: 4px solid #dc3545;
    background-color: #fff5f5;
}

.semantic-node-row.warning {
    border-left: 4px solid #ffc107;
    background-color: #fffbf0;
}

.semantic-node-row.success {
    border-left: 4px solid #28a745;
}

.validation-badge {
    display: inline-block;
    padding: 2px 6px;
    border-radius: 3px;
    font-size: 11px;
    margin-left: 5px;
}

.validation-badge.error {
    background-color: #dc3545;
    color: white;
}

.validation-badge.warning {
    background-color: #ffc107;
    color: black;
}

.validation-tooltip {
    position: absolute;
    background: #333;
    color: white;
    padding: 8px 12px;
    border-radius: 4px;
    font-size: 12px;
    z-index: 1000;
    max-width: 300px;
}
```

**Implementation Requirements:**

1. **highlightErrors(errors)** - Apply error states
   - For each error, find corresponding semantic node row
   - Add `.error` class to row
   - Insert error badge with icon and code
   - Attach tooltip with message

2. **highlightWarnings(warnings)** - Apply warning states
   - For each warning, find corresponding row
   - Add `.warning` class to row
   - Insert warning badge
   - Attach tooltip

3. **clearHighlights()** - Remove all states
   - Remove `.error`, `.warning`, `.success` classes
   - Remove all badges
   - Remove all tooltips

4. **attachTooltip(element, message, code)** - Tooltip helper
   - Create tooltip element
   - Position near target element
   - Show on hover, hide on mouse leave
   - Format: `[CODE] Message`

**Acceptance Criteria:**
- [ ] Error rows have red left border
- [ ] Warning rows have yellow left border
- [ ] Error/warning badges display inline
- [ ] Tooltips show on hover with error code and message
- [ ] clearHighlights() removes all visual states

---

### Step 4: Create Validation Summary Panel (WBS 6.4)

**File:** `apps/business_case/js/mb2-validation-panel.js` (NEW)

**Purpose:** Display aggregated validation status at top of semantic nodes tab

**Interface:**
```javascript
const MB2ValidationPanel = (function() {
    return {
        render: function(validationResult, nodes) {
            // Returns: DOM element for panel
        },
        attachClickHandlers: function(panel) {
            // Make errors/warnings clickable (scroll to node)
        }
    };
})();
```

**HTML Structure:**
```html
<div class="validation-summary-panel">
    <div class="panel-header">
        <h3>Semantic Nodes Validation</h3>
        <button class="btn-run-validation">Run Validation</button>
    </div>
    <div class="panel-body">
        <div class="status-badge">
            <!-- ✅ Valid / ⚠️ Warnings / ❌ Errors -->
        </div>
        <div class="node-count">
            15 nodes (13 valid, 2 warnings, 0 errors)
        </div>
        <div class="error-list">
            <!-- Clickable error items -->
        </div>
        <div class="warning-list">
            <!-- Clickable warning items -->
        </div>
    </div>
</div>
```

**Implementation Requirements:**

1. **render(validationResult, nodes)** - Generate panel HTML
   - Calculate overall status: ✅ Valid / ⚠️ Warnings / ❌ Errors
   - Count nodes: total, valid, warnings, errors
   - Generate error list (clickable)
   - Generate warning list (clickable)
   - Add "Run Validation" button

2. **attachClickHandlers(panel)** - Make interactive
   - Click error → scroll to node row
   - Click warning → scroll to node row
   - Click "Run Validation" → trigger validation manually

3. **Panel Placement**
   - Insert at top of semantic nodes tab content
   - Sticky positioning (stays visible on scroll)

**Acceptance Criteria:**
- [ ] Panel displays at top of semantic nodes tab
- [ ] Status badge shows correct state
- [ ] Node counts accurate
- [ ] Clicking error scrolls to node
- [ ] "Run Validation" button triggers validation
- [ ] Panel sticky (visible during scroll)

---

### Step 5: Create Guided Node Creation (WBS 6.3)

**File:** `apps/business_case/js/mb2-guided-creation.js` (NEW)

**Purpose:** Suggest category/type based on Phase 5 heuristics

**Interface:**
```javascript
const MB2GuidedCreation = (function() {
    return {
        suggestCategory: function(nodeId, label) {
            // Returns: { category, subcategory, confidence }
        },
        suggestNodeType: function(node, variables) {
            // Returns: { nodeType, reason }
        },
        suggestExposureType: function(node) {
            // Returns: { exposureType, reason }
        },
        renderSuggestionBadge: function(suggestion) {
            // Returns: DOM element for suggestion badge
        }
    };
})();
```

**Implementation Requirements:**

1. **suggestCategory(nodeId, label)** - Use Phase 5 heuristics
   - Import `inferCategory()` from migration_engine.js
   - Call with nodeId and label
   - Return: `{ category, subcategory, confidence }`

2. **suggestNodeType(node, variables)** - Infer LEAF vs GROUP
   - If node name includes "total", "sum", "aggregate" → GROUP
   - If node has formula → LEAF
   - Default → LEAF

3. **suggestExposureType(node)** - Infer OBSERVED vs DERIVED
   - If nodeId matches "npv", "bcr", "pv_*" → DERIVED
   - Default → OBSERVED

4. **renderSuggestionBadge(suggestion)** - Visual suggestion UI
   - Display: "💡 Suggested: COSTS (CAPEX) - HIGH confidence"
   - Button: "Accept Suggestion" (1-click)
   - Button: "Dismiss"
   - Color-code by confidence: GREEN (high), YELLOW (medium), RED (low)

5. **Integration into Add Node Flow**
   - When user adds new semantic node:
     1. Capture nodeId and label
     2. Call suggestCategory()
     3. Display suggestion badge
     4. Pre-populate category dropdown if accepted
     5. Allow manual override

**Acceptance Criteria:**
- [ ] Suggestions use Phase 5 heuristics
- [ ] Suggestions display inline with confidence level
- [ ] "Accept" button pre-populates fields
- [ ] Manual override always possible
- [ ] Suggestions color-coded by confidence

---

### Step 6: Add Tooltips and Help System (WBS 6.6)

**File:** `apps/business_case/js/mb2-help-system.js` (NEW)

**Purpose:** Provide field-level tooltips and help panel

**Interface:**
```javascript
const MB2HelpSystem = (function() {
    return {
        attachTooltips: function(container) {
            // Attach tooltips to all fields with [data-help] attribute
        },
        showHelpPanel: function() {
            // Display help panel with documentation links
        }
    };
})();
```

**Tooltip Definitions:**
```javascript
const TOOLTIPS = {
    semanticNodeId: "Unique identifier for this semantic node. Must match variable ID for 1:1 binding.",
    label: "Display name for this node in reports and UI.",
    category: "Economic domain (COSTS, BENEFITS, DEMAND, CAPACITY, APPRAISAL).",
    subcategory: "Optional subcategory (e.g., CAPEX, OPEX for COSTS).",
    nodeType: "LEAF = variable binding (1:1), GROUP = rollup/aggregate (children summed).",
    exposureType: "OBSERVED = direct calculation, DERIVED = computed from other nodes (e.g., NPV).",
    bindings: "Variable IDs this node binds to. Usually [same as node ID] for 1:1 mapping.",
    parentNodeId: "Parent node in hierarchy. Leave blank for root nodes.",
    derivationMetadata: "Required for DERIVED nodes. Describes how value is computed."
};
```

**Implementation Requirements:**

1. **attachTooltips(container)** - Auto-attach tooltips
   - Find all elements with `[data-help]` attribute
   - Attach hover listener
   - Display tooltip on hover
   - Position near element

2. **showHelpPanel()** - Help panel modal
   - Modal overlay with help content
   - Links to Phase 5 migration guide
   - Links to Phase 2 contract specification
   - Close button

3. **HTML Additions**
   - Add `[data-help="field-name"]` to input labels
   - Add "?" icon next to each label
   - Add "Help" button to semantic nodes tab header

**Acceptance Criteria:**
- [ ] Tooltips display on hover for all fields
- [ ] Tooltips contain clear, concise descriptions
- [ ] Help panel opens on button click
- [ ] Help panel links to documentation
- [ ] "?" icons visible next to field labels

---

### Step 7: Add Migration Import Feature (WBS 6.5)

**File:** `apps/business_case/js/mb2-migration-importer.js` (NEW)

**Purpose:** Import semantic nodes from Phase 5 migration output

**Interface:**
```javascript
const MB2MigrationImporter = (function() {
    return {
        showImportDialog: function() {
            // Display file picker dialog
        },
        importNodes: function(jsonData) {
            // Parse and import nodes
        },
        validateImportData: function(data) {
            // Validate migration JSON structure
        }
    };
})();
```

**Implementation Requirements:**

1. **showImportDialog()** - File picker UI
   - Open file input dialog
   - Filter: `.json` files only
   - Read file as text
   - Parse JSON
   - Show preview: "15 nodes to import"
   - Confirm button

2. **importNodes(jsonData)** - Import logic
   - Validate JSON structure (array of semantic nodes)
   - Check required fields on each node
   - Insert nodes into model.semanticNodes
   - Trigger validation after import
   - Display success message

3. **validateImportData(data)** - Pre-import validation
   - Check data is array
   - Check each node has required fields
   - Check no duplicate IDs
   - Return: `{ valid, errors }`

4. **UI Integration**
   - Add "Import Migration Result" button to semantic nodes tab
   - Button placement: next to "Add Node" button
   - After import, scroll to first imported node

**Acceptance Criteria:**
- [ ] Import button opens file picker
- [ ] Only JSON files accepted
- [ ] Preview shows node count before import
- [ ] Validation runs before import
- [ ] Nodes inserted successfully
- [ ] Validation runs after import
- [ ] Success message displayed

---

### Step 8: Add CSS Styling (WBS 6.2)

**File:** `apps/business_case/css/model-builder-ux.css` (MODIFY)

**Add CSS Classes:**
```css
/* Validation States */
.semantic-node-row.error { ... }
.semantic-node-row.warning { ... }
.semantic-node-row.success { ... }

/* Validation Badges */
.validation-badge { ... }
.validation-badge.error { ... }
.validation-badge.warning { ... }

/* Validation Summary Panel */
.validation-summary-panel { ... }
.validation-summary-panel .panel-header { ... }
.validation-summary-panel .status-badge { ... }
.validation-summary-panel .error-list { ... }
.validation-summary-panel .error-list-item { ... }

/* Suggestion Badges */
.suggestion-badge { ... }
.suggestion-badge.high-confidence { ... }
.suggestion-badge.medium-confidence { ... }
.suggestion-badge.low-confidence { ... }

/* Tooltips */
.validation-tooltip { ... }
.help-icon { ... }
```

**Acceptance Criteria:**
- [ ] All visual states styled consistently
- [ ] Color scheme matches existing MB2 theme
- [ ] Responsive design (mobile-friendly)

---

### Step 9: Update Model Builder 2 HTML (WBS 6.1)

**File:** `apps/business_case/model-builder-2.html` (MODIFY)

**Add Script Tags:**
```html
<!-- Phase 2 Guard -->
<script src="Governance/explicit_ledger_exposure/phase2_guards/LedgerExposureGuard.js"></script>

<!-- Phase 6 Modules -->
<script src="js/mb2-semantic-validator.js"></script>
<script src="js/mb2-error-highlighter.js"></script>
<script src="js/mb2-validation-panel.js"></script>
<script src="js/mb2-guided-creation.js"></script>
<script src="js/mb2-help-system.js"></script>
<script src="js/mb2-migration-importer.js"></script>

<!-- Phase 5 Migration Heuristics -->
<script src="../tools/ledger_migration/migration_engine.js"></script>
```

**Acceptance Criteria:**
- [ ] All new modules loaded
- [ ] No console errors on page load
- [ ] Modules available in window scope

---

### Step 10: Create Test Suite (WBS 6.7)

**File:** `apps/tests/verify_mb2_authoring_ux.js` (NEW)

**Test Coverage:**

**Validation Framework Tests (5 tests):**
1. Validate function returns { valid, errors, warnings }
2. validateNode detects missing required fields
3. Debounce delays execution by 500ms
4. Validation integrates with Phase 2 guard
5. Graceful fallback when guard unavailable

**Error Highlighting Tests (4 tests):**
6. Error rows have red left border
7. Warning rows have yellow left border
8. Error badges display inline with code
9. Tooltips show on hover

**Validation Panel Tests (3 tests):**
10. Panel displays correct status and counts
11. Clicking error scrolls to node
12. Manual validation button triggers validation

**Guided Creation Tests (4 tests):**
13. Category suggestions use Phase 5 heuristics
14. Node type inference works correctly
15. Exposure type inference works correctly
16. Suggestion badge displays with confidence level

**Migration Import Tests (3 tests):**
17. Import validates JSON structure
18. Import rejects invalid data
19. Import inserts nodes successfully

**Help System Tests (2 tests):**
20. Tooltips attach to fields with [data-help]
21. Help panel opens on button click

**Total:** 21 tests

**Pass Criteria:** 21/21 tests pass

**Acceptance Criteria:**
- [ ] All 21 tests pass
- [ ] No console errors during test execution
- [ ] Evidence quality: Class A (deterministic)

---

## 4. Integration Points

**Phase 2 Integration:**
- Load `LedgerExposureGuard.validateContract()`
- Use error codes from Phase 2 taxonomy

**Phase 5 Integration:**
- Import `inferCategory()`, `inferNodeType()`, `inferExposureType()` from migration_engine.js
- Import feature uses migration output format

**Model Builder 2 Integration:**
- Hook into existing semantic nodes tab
- Use existing model structure
- Trigger validation on model mutations

---

## 5. Non-Goals

- Model Builder refactoring (use existing structure)
- Automatic error fixing (suggestions only)
- Real-time execution preview (defer to execution flow)
- Visual hierarchy editor (defer to future)
- Multi-node bulk editing (defer to future)

---

## 6. Acceptance Criteria (Exit Gate)

### Code Deliverables:
- [ ] `mb2-semantic-validator.js` created (validation framework)
- [ ] `mb2-error-highlighter.js` created (visual error states)
- [ ] `mb2-validation-panel.js` created (summary panel)
- [ ] `mb2-guided-creation.js` created (suggestions)
- [ ] `mb2-help-system.js` created (tooltips)
- [ ] `mb2-migration-importer.js` created (import feature)
- [ ] `model-builder-2.js` modified (integration)
- [ ] `model-builder-2.html` modified (script tags)
- [ ] `model-builder-ux.css` modified (styling)
- [ ] `verify_mb2_authoring_ux.js` created (test suite)

### Functional Criteria:
- [ ] Validation runs 500ms after edit (debounced)
- [ ] Errors/warnings display inline with error codes
- [ ] Validation summary panel shows aggregated status
- [ ] Category/type suggestions work (Phase 5 heuristics)
- [ ] Migration import feature works (Phase 5 output)
- [ ] Tooltips display on all fields
- [ ] No regressions in existing MB2 functionality

### Test Criteria:
- [ ] All 21 tests pass (100%)
- [ ] Evidence quality: Class A (deterministic)
- [ ] No console errors in browser

---

## 7. Risk Mitigation

**Risk 1: Performance**
- Mitigation: Debouncing (500ms), validation only on semantic nodes tab
- Mitigation: Incremental validation (only changed nodes)
- Test: Validate with 100+ node model

**Risk 2: UX Complexity**
- Mitigation: Collapsible warnings section
- Mitigation: "Hide LOW confidence warnings" toggle
- Mitigation: Progressive disclosure (show critical errors first)

**Risk 3: Phase 2 Guard Availability**
- Mitigation: Graceful fallback to structural validation
- Mitigation: SKIPPED status when guard unavailable
- Test: Verify fallback behavior

---

## 8. Evidence Requirements

**Class A Evidence (Required):**
- Test suite results (21/21 pass)
- Code audit (all deliverables present)
- No console errors on page load
- Integration test (validation runs on edit)

**Class B Evidence (Optional):**
- Screenshot of validation panel
- Screenshot of error highlighting
- Screenshot of suggestion badge

---

## 9. Verification Protocol (CODEX Auditor)

**Code Audit:**
1. Verify all 10 files created/modified
2. Check all functions present in modules
3. Check error codes defined and used
4. Check Phase 2/5 integration points

**Test Execution:**
1. Run `node tests/verify_mb2_authoring_ux.js`
2. Verify 21/21 tests pass
3. Check no console errors

**Functional Verification:**
1. Load Model Builder 2
2. Navigate to Semantic Nodes tab
3. Verify validation panel displays
4. Add new node → verify suggestion appears
5. Trigger validation → verify errors display
6. Import migration result → verify nodes inserted

---

## 10. Implementation Order

**Order of Steps:**
1. Step 1: Validation framework module (foundation)
2. Step 2: Integrate validation into MB2 (core feature)
3. Step 3: Error highlighting UI (visual feedback)
4. Step 4: Validation summary panel (aggregated view)
5. Step 5: Guided creation (suggestions)
6. Step 6: Tooltips and help (documentation)
7. Step 7: Migration import (Phase 5 integration)
8. Step 8: CSS styling (polish)
9. Step 9: Update HTML (integration)
10. Step 10: Test suite (verification)

**Rationale:** Foundation → Core → Enhancement → Testing

---

**CODEX SPECIFICATION COMPLETE**

**Risk Tier:** 2 (Module - UI/UX Enhancement)
**Next Step:** AG Execution (AG-RESULT-EXP-LEDGER-PHASE6-01)
**Estimated LOC:** ~1500 lines (6 new modules + modifications)
