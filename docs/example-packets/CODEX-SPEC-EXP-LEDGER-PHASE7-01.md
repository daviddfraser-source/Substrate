# CODEX-SPEC-EXP-LEDGER-PHASE7-01

## Metadata
* **Packet ID:** CODEX-SPEC-EXP-LEDGER-PHASE7-01
* **Phase:** 7 - MB2 Integration
* **Authority:** VEX-SCOPE-EXP-LEDGER-PHASE7
* **Author:** CODEX (Worker)
* **Status:** ACTIVE
* **Risk Tier:** 2 (Module - UI Integration)

## 1. Objective

Translate VEX-SCOPE-EXP-LEDGER-PHASE7 into executable implementation steps. Wire Phase 6 modules into Model Builder 2's semantic nodes workflow with validation, suggestions, help, and import functionality.

## 2. Prerequisites

**Phase Dependencies:**
- ✅ Phase 6: All modules implemented and tested
- ✅ model-builder-2.js exists and operational
- ✅ All Phase 6 modules loaded in model-builder.html

**Files Required:**
- `apps/business_case/js/model-builder-2.js` (existing)
- `apps/business_case/js/mb2-semantic-validator.js` (Phase 6)
- `apps/business_case/js/mb2-error-highlighter.js` (Phase 6)
- `apps/business_case/js/mb2-validation-panel.js` (Phase 6)
- `apps/business_case/js/mb2-guided-creation.js` (Phase 6)
- `apps/business_case/js/mb2-help-system.js` (Phase 6)
- `apps/business_case/js/mb2-migration-importer.js` (Phase 6)

## 3. Implementation Steps

### Step 1: Survey Current Semantic Nodes Tab (Research)

**File:** `apps/business_case/js/model-builder-2.js` (READ ONLY)

**Purpose:** Understand current semantic nodes tab structure before integration

**Actions:**
1. Read model-builder-2.js to locate semantic nodes tab code
2. Identify how semantic nodes are rendered
3. Find semantic node add/edit/delete functions
4. Document current state structure for semantic nodes
5. Identify integration points (where to inject validation, suggestions)

**Deliverable:** Survey report documenting:
- Semantic nodes tab location in code
- Current rendering approach
- Mutation functions
- Integration points

**No Code Changes:** This is research only

---

### Step 2: Add Validation State to Model Structure (WBS 7.1.1)

**File:** `apps/business_case/js/model-builder-2.js` (MODIFY)

**Purpose:** Add validation state storage to model structure

**Changes:**

Find the model initialization section (likely in `_loadModelPayload()` or similar):

```javascript
// Add to model structure initialization
_modelPayload: {
    // ... existing fields
    validation: {
        semanticNodes: null  // Will store { valid, errors, warnings, phase2Status }
    }
}
```

**Implementation:**
1. Locate model structure initialization
2. Add `validation` object if not exists
3. Add `validation.semanticNodes` property

**Acceptance Criteria:**
- [ ] `model.validation.semanticNodes` accessible
- [ ] Does not break existing model loading

---

### Step 3: Create Validation Trigger Functions (WBS 7.1.2)

**File:** `apps/business_case/js/model-builder-2.js` (MODIFY)

**Purpose:** Add validation trigger and execution functions

**New Functions to Add:**

```javascript
/**
 * Trigger semantic node validation (debounced)
 */
_triggerSemanticNodeValidation() {
    // Clear existing timeout
    if (this._validationTimeout) {
        clearTimeout(this._validationTimeout);
    }

    // Debounce 500ms
    this._validationTimeout = setTimeout(() => {
        this._runSemanticNodeValidation();
    }, 500);
},

/**
 * Run semantic node validation immediately
 */
_runSemanticNodeValidation() {
    if (!this._modelPayload || !window.MB2SemanticValidator) {
        console.warn('[MB2] Cannot run validation: missing model or validator');
        return;
    }

    const semanticNodes = this._modelPayload.semanticNodes || [];

    // Run validation
    const result = window.MB2SemanticValidator.validate(semanticNodes);

    // Store result
    this._modelPayload.validation = this._modelPayload.validation || {};
    this._modelPayload.validation.semanticNodes = result;

    console.log('[MB2] Validation complete:', result.valid ? 'PASS' : 'FAIL',
                `(${result.errors.length} errors, ${result.warnings.length} warnings)`);

    // Update UI
    this._updateValidationUI(result, semanticNodes);
},

/**
 * Update validation UI (panel + highlighting)
 */
_updateValidationUI(result, semanticNodes) {
    // Update validation panel
    if (window.MB2ValidationPanel) {
        const existingPanel = document.getElementById('mb2-validation-panel');
        if (existingPanel) {
            window.MB2ValidationPanel.update(result, semanticNodes);
        } else {
            this._renderValidationPanel(result, semanticNodes);
        }
    }

    // Clear and apply error highlighting
    if (window.MB2ErrorHighlighter) {
        window.MB2ErrorHighlighter.clearHighlights();
        if (result.errors.length > 0) {
            window.MB2ErrorHighlighter.highlightErrors(result.errors);
        }
        if (result.warnings.length > 0) {
            window.MB2ErrorHighlighter.highlightWarnings(result.warnings);
        }
    }
},

/**
 * Render validation panel
 */
_renderValidationPanel(result, semanticNodes) {
    if (!window.MB2ValidationPanel) return;

    const panel = window.MB2ValidationPanel.render(result, semanticNodes);
    window.MB2ValidationPanel.attachClickHandlers(panel);

    // Insert at top of semantic nodes tab
    const semanticTab = document.getElementById('view-semantic') ||
                        document.getElementById('semantic-nodes-container');
    if (semanticTab) {
        semanticTab.insertBefore(panel, semanticTab.firstChild);
    }
}
```

**Add to Class:**
- Add `_validationTimeout: null` to state properties
- Add all 4 functions to ModelBuilder2 object

**Acceptance Criteria:**
- [ ] Validation functions callable
- [ ] Debouncing works (500ms delay)
- [ ] Validation result stored in model
- [ ] UI updates after validation

---

### Step 4: Wire Validation to Semantic Node Mutations (WBS 7.1.3)

**File:** `apps/business_case/js/model-builder-2.js` (MODIFY)

**Purpose:** Trigger validation whenever semantic nodes are added/edited/deleted

**Find Semantic Node Mutation Functions:**
- Look for functions like `addSemanticNode()`, `editSemanticNode()`, `deleteSemanticNode()`
- Or look for event handlers that modify `this._modelPayload.semanticNodes`

**Add Validation Trigger:**

```javascript
// After semantic node add
addSemanticNode(node) {
    // ... existing add logic
    this._modelPayload.semanticNodes.push(node);

    // TRIGGER VALIDATION
    this._triggerSemanticNodeValidation();

    // ... existing render logic
}

// After semantic node edit
editSemanticNode(nodeId, updates) {
    // ... existing edit logic
    const node = this._modelPayload.semanticNodes.find(n => n.semanticNodeId === nodeId);
    Object.assign(node, updates);

    // TRIGGER VALIDATION
    this._triggerSemanticNodeValidation();

    // ... existing render logic
}

// After semantic node delete
deleteSemanticNode(nodeId) {
    // ... existing delete logic
    this._modelPayload.semanticNodes = this._modelPayload.semanticNodes.filter(
        n => n.semanticNodeId !== nodeId
    );

    // TRIGGER VALIDATION
    this._triggerSemanticNodeValidation();

    // ... existing render logic
}
```

**If No Explicit Mutation Functions Exist:**
- Add generic mutation handler
- Wire to form submit events
- Trigger validation on blur events

**Acceptance Criteria:**
- [ ] Validation runs after semantic node add
- [ ] Validation runs after semantic node edit
- [ ] Validation runs after semantic node delete
- [ ] Debouncing prevents excessive calls

---

### Step 5: Add Manual Validation Button (WBS 7.1.4)

**File:** `apps/business_case/js/model-builder-2.js` (MODIFY)

**Purpose:** Add "Run Validation" button to toolbar

**Find Toolbar Rendering:**
- Look for semantic nodes tab toolbar
- May be in `_renderSemanticNodesTab()` or similar

**Add Button:**

```javascript
// In toolbar rendering function
const toolbar = document.getElementById('semantic-toolbar-actions') ||
                document.querySelector('#toolbar-actions');

if (toolbar) {
    const validateBtn = document.createElement('button');
    validateBtn.textContent = '🔍 Run Validation';
    validateBtn.className = 'btn-secondary';
    validateBtn.id = 'btn-run-semantic-validation';
    validateBtn.addEventListener('click', () => {
        this._runSemanticNodeValidation();
    });
    toolbar.appendChild(validateBtn);
}
```

**Acceptance Criteria:**
- [ ] Button appears in semantic nodes toolbar
- [ ] Clicking button runs validation immediately
- [ ] Validation results display in panel

---

### Step 6: Integrate Guided Creation (WBS 7.2)

**File:** `apps/business_case/js/model-builder-2.js` (MODIFY)

**Purpose:** Add category/type suggestions during node creation

**Find Node Creation Form:**
- Look for "Add Semantic Node" form or modal
- Find input fields for semanticNodeId, label, category

**Add Suggestion Trigger:**

```javascript
// When rendering add/edit form
_renderSemanticNodeForm(node = null) {
    // ... existing form HTML

    // Add input listeners for suggestions
    const nodeIdInput = document.getElementById('semantic-node-id-input');
    const labelInput = document.getElementById('semantic-label-input');

    if (nodeIdInput && labelInput && window.MB2GuidedCreation) {
        const triggerSuggestion = () => {
            const nodeId = nodeIdInput.value;
            const label = labelInput.value;

            if (nodeId.length >= 3) {
                const suggestion = window.MB2GuidedCreation.suggestCategory(nodeId, label);

                // Remove existing badge
                const existingBadge = document.querySelector('.suggestion-badge');
                if (existingBadge) existingBadge.remove();

                // Render new badge
                const badge = window.MB2GuidedCreation.renderSuggestionBadge(suggestion);
                const categoryContainer = document.getElementById('category-input-container') ||
                                          labelInput.parentElement;
                categoryContainer.appendChild(badge);
            }
        };

        nodeIdInput.addEventListener('input', triggerSuggestion);
        labelInput.addEventListener('input', triggerSuggestion);
    }
}

// Listen for suggestion acceptance
window.addEventListener('MB2_SUGGESTION_ACCEPTED', (e) => {
    const suggestion = e.detail;
    const categorySelect = document.getElementById('category-select');
    const subcategorySelect = document.getElementById('subcategory-select');

    if (categorySelect) {
        categorySelect.value = suggestion.primary;
    }
    if (subcategorySelect && suggestion.subcategory) {
        subcategorySelect.value = suggestion.subcategory;
    }
});
```

**Add Node Type/Exposure Type Suggestions:**

```javascript
// After category suggestion
const nodeTypeSuggestion = window.MB2GuidedCreation.suggestNodeType({
    semanticNodeId: nodeId,
    label: label
});

const exposureTypeSuggestion = window.MB2GuidedCreation.suggestExposureType({
    semanticNodeId: nodeId
});

// Display suggestions as helper text below dropdowns
```

**Acceptance Criteria:**
- [ ] Suggestions appear when user types node ID
- [ ] Suggestion badge shows confidence level
- [ ] Accept button populates category field
- [ ] Manual override always works

---

### Step 7: Integrate Help System (WBS 7.3)

**File:** `apps/business_case/js/model-builder-2.js` (MODIFY)

**Purpose:** Add help tooltips and help button

**Add data-help Attributes:**

```javascript
// In form rendering
_renderSemanticNodeForm(node = null) {
    return `
        <div class="form-group">
            <label data-help="semanticNodeId">Semantic Node ID *</label>
            <input id="semantic-node-id-input" type="text" />
        </div>
        <div class="form-group">
            <label data-help="label">Label *</label>
            <input id="semantic-label-input" type="text" />
        </div>
        <div class="form-group">
            <label data-help="category">Category *</label>
            <select id="category-select" data-help="category">
                <option value="COSTS">COSTS</option>
                <option value="BENEFITS">BENEFITS</option>
                <!-- ... -->
            </select>
        </div>
        <!-- ... add data-help to all fields ... -->
    `;
}
```

**Initialize Help System:**

```javascript
// After rendering semantic nodes tab
_initializeSemanticNodesTab() {
    // ... existing initialization

    // Attach help tooltips
    if (window.MB2HelpSystem) {
        const semanticTab = document.getElementById('view-semantic') ||
                            document.getElementById('semantic-nodes-container');
        window.MB2HelpSystem.attachTooltips(semanticTab);
    }

    // Add help button to toolbar
    this._addHelpButton();
}

_addHelpButton() {
    const toolbar = document.getElementById('semantic-toolbar-actions');
    if (!toolbar || !window.MB2HelpSystem) return;

    const helpBtn = document.createElement('button');
    helpBtn.textContent = '❓ Help';
    helpBtn.className = 'btn-secondary';
    helpBtn.addEventListener('click', () => {
        window.MB2HelpSystem.showHelpPanel();
    });
    toolbar.appendChild(helpBtn);
}
```

**Acceptance Criteria:**
- [ ] All form fields have data-help attributes
- [ ] Help tooltips display on "?" icon hover
- [ ] Help button appears in toolbar
- [ ] Help panel opens on button click

---

### Step 8: Integrate Migration Import (WBS 7.4)

**File:** `apps/business_case/js/model-builder-2.js` (MODIFY)

**Purpose:** Add import button and handle import events

**Add Import Button:**

```javascript
// In toolbar rendering
_addImportButton() {
    const toolbar = document.getElementById('semantic-toolbar-actions');
    if (!toolbar || !window.MB2MigrationImporter) return;

    const importBtn = document.createElement('button');
    importBtn.textContent = '📥 Import Migration Result';
    importBtn.className = 'btn-secondary';
    importBtn.addEventListener('click', () => {
        window.MB2MigrationImporter.showImportDialog();
    });
    toolbar.appendChild(importBtn);
}
```

**Handle Import Event:**

```javascript
// In global listeners initialization
window.addEventListener('MB2_IMPORT_SEMANTIC_NODES', (e) => {
    const { nodes } = e.detail;

    if (!this._modelPayload) {
        console.error('[MB2] Cannot import: no model loaded');
        return;
    }

    // Insert nodes into model
    this._modelPayload.semanticNodes = this._modelPayload.semanticNodes || [];
    this._modelPayload.semanticNodes.push(...nodes);

    console.log(`[MB2] Imported ${nodes.length} semantic nodes`);

    // Trigger validation
    this._runSemanticNodeValidation();

    // Re-render semantic nodes table
    this._renderSemanticNodesTable();

    // Show success message
    alert(`Successfully imported ${nodes.length} semantic nodes`);
});
```

**Acceptance Criteria:**
- [ ] Import button appears in toolbar
- [ ] Clicking button opens file picker
- [ ] Importing nodes adds them to model
- [ ] Validation runs after import
- [ ] Table re-renders with imported nodes

---

### Step 9: Initialize All Phase 6 Features on Mount (WBS 7.6)

**File:** `apps/business_case/js/model-builder-2.js` (MODIFY)

**Purpose:** Wire all Phase 6 features during MB2 mount

**Modify Mount Function:**

```javascript
async mount(container, options = {}) {
    // ... existing mount logic

    // Phase 6 Integration: Initialize validation, help, import
    this._initializePhase6Features();

    // ... rest of mount logic
}

/**
 * Initialize Phase 6 features (validation, help, import)
 */
_initializePhase6Features() {
    console.log('[MB2] Initializing Phase 6 features...');

    // 1. Run initial validation
    if (this._modelPayload && this._modelPayload.semanticNodes) {
        this._runSemanticNodeValidation();
    }

    // 2. Initialize help system
    if (window.MB2HelpSystem) {
        const semanticTab = document.getElementById('view-semantic') ||
                            document.getElementById('semantic-nodes-container');
        if (semanticTab) {
            window.MB2HelpSystem.attachTooltips(semanticTab);
        }
    }

    // 3. Add toolbar buttons
    this._addHelpButton();
    this._addImportButton();
    // Validation button added in _renderValidationPanel

    console.log('[MB2] Phase 6 features initialized');
}
```

**Acceptance Criteria:**
- [ ] Phase 6 features initialize on mount
- [ ] Initial validation runs if semantic nodes exist
- [ ] Help tooltips attached
- [ ] Toolbar buttons added
- [ ] No errors in console

---

### Step 10: Add Cleanup on Unmount (WBS 7.6)

**File:** `apps/business_case/js/model-builder-2.js` (MODIFY)

**Purpose:** Clean up Phase 6 event listeners on unmount

**Modify Unmount Function:**

```javascript
unmount() {
    console.log('[MODEL_BUILDER_2] Unmounting...');

    // Clear validation timeout
    if (this._validationTimeout) {
        clearTimeout(this._validationTimeout);
        this._validationTimeout = null;
    }

    // Clear validation state
    if (window.MB2ErrorHighlighter) {
        window.MB2ErrorHighlighter.clearHighlights();
    }

    // Remove validation panel
    const panel = document.getElementById('mb2-validation-panel');
    if (panel) panel.remove();

    // ... existing unmount logic
}
```

**Acceptance Criteria:**
- [ ] Validation timeout cleared on unmount
- [ ] Error highlights removed
- [ ] Validation panel removed
- [ ] No memory leaks

---

### Step 11: Create Integration Test Suite (WBS 7.7)

**File:** `apps/tests/verify_mb2_phase6_integration.js` (NEW)

**Purpose:** Test Phase 6 integration into MB2

**Test Coverage:**

```javascript
/**
 * Test Suite: MB2 Phase 6 Integration
 */

// Integration Tests (10 tests):
1. Validation state added to model structure
2. Validation runs after semantic node add
3. Validation runs after semantic node edit
4. Validation runs after semantic node delete
5. Validation panel renders at top of tab
6. Errors highlighted in semantic node rows
7. Category suggestion appears on ID input
8. Help tooltips attached to form fields
9. Import button opens dialog
10. Import inserts nodes and triggers validation

// Regression Tests (5 tests):
11. Variables tab still works
12. Model loading still works
13. Model saving still works
14. Assumptions tab still works
15. Benefits tab still works
```

**Acceptance Criteria:**
- [ ] All 15 tests pass
- [ ] No regressions detected
- [ ] Evidence quality: Class A

---

## 4. Integration Points Summary

**Modified Functions:**
1. `_loadModelPayload()` - Add validation state
2. `addSemanticNode()` - Trigger validation
3. `editSemanticNode()` - Trigger validation
4. `deleteSemanticNode()` - Trigger validation
5. `_renderSemanticNodeForm()` - Add suggestions, help attributes
6. `mount()` - Initialize Phase 6 features
7. `unmount()` - Cleanup Phase 6 features

**New Functions:**
1. `_triggerSemanticNodeValidation()` - Debounced trigger
2. `_runSemanticNodeValidation()` - Immediate execution
3. `_updateValidationUI()` - Update panel + highlights
4. `_renderValidationPanel()` - Render panel
5. `_initializePhase6Features()` - Initialize all features
6. `_addHelpButton()` - Add help button
7. `_addImportButton()` - Add import button

**Event Listeners:**
1. `MB2_SUGGESTION_ACCEPTED` - Apply suggestion
2. `MB2_IMPORT_SEMANTIC_NODES` - Import nodes
3. `MB2_VALIDATE_SEMANTIC_NODES` - Manual validation trigger

---

## 5. Acceptance Criteria (Exit Gate)

### Code Deliverables:
- [ ] model-builder-2.js modified (integration code)
- [ ] verify_mb2_phase6_integration.js created (test suite)

### Functional Criteria:
- [ ] Validation runs automatically 500ms after edit
- [ ] Validation panel displays at top of semantic nodes tab
- [ ] Errors/warnings highlighted inline
- [ ] Category suggestions appear during node creation
- [ ] Help tooltips display on form fields
- [ ] Help button opens help panel
- [ ] Import button opens import dialog
- [ ] Import inserts nodes successfully
- [ ] No regressions in existing MB2 functionality

### Test Criteria:
- [ ] All 15 integration tests pass (100%)
- [ ] Evidence quality: Class A (deterministic)
- [ ] No console errors in browser
- [ ] Manual UX testing complete

---

## 6. Risk Mitigation

**Risk 1: Semantic Nodes Tab May Not Exist**
- Mitigation: Survey existing tab first (Step 1)
- Mitigation: Create minimal tab if needed
- Fallback: Document integration requirements for future

**Risk 2: State Management Conflicts**
- Mitigation: Use separate `validation` object in model
- Mitigation: Never mutate existing model fields
- Mitigation: Event-based communication (loose coupling)

**Risk 3: Performance Degradation**
- Mitigation: Debouncing (500ms)
- Mitigation: Only validate when semantic nodes change
- Mitigation: User can disable auto-validation

---

## 7. Evidence Requirements

**Class A Evidence (Required):**
- Integration test suite results (15/15 pass)
- Code diff showing modifications
- No console errors on page load
- Manual validation test (video/screenshots)

**Class B Evidence (Optional):**
- Screenshots of validation panel
- Screenshots of suggestion badges
- Screenshot of help panel

---

## 8. Verification Protocol (CODEX Auditor)

**Code Audit:**
1. Verify all 7 modified functions exist
2. Verify all 7 new functions exist
3. Check validation triggers after mutations
4. Check Phase 6 modules loaded

**Test Execution:**
1. Run `node tests/verify_mb2_phase6_integration.js`
2. Verify 15/15 tests pass
3. Check no console errors

**Functional Verification:**
1. Load Model Builder 2 in browser
2. Navigate to semantic nodes tab
3. Add semantic node → verify validation runs
4. Verify validation panel displays
5. Verify errors highlighted
6. Verify suggestion appears
7. Verify help tooltips work
8. Verify import button works

---

## 9. Implementation Order

**Sequential Steps (Cannot Parallelize):**
1. Step 1: Survey (understand current state)
2. Step 2: Add validation state
3. Step 3: Add validation functions
4. Step 4: Wire validation triggers
5. Step 5: Add manual validation button
6. Step 6: Integrate suggestions
7. Step 7: Integrate help system
8. Step 8: Integrate import
9. Step 9: Initialize on mount
10. Step 10: Cleanup on unmount
11. Step 11: Test suite

**Rationale:** Each step builds on previous, cannot parallelize

---

**CODEX SPECIFICATION COMPLETE**

**Risk Tier:** 2 (Module - UI Integration)
**Next Step:** AG Execution (AG-RESULT-EXP-LEDGER-PHASE7-01)
**Estimated Changes:** ~300 lines (modifications + new functions)
