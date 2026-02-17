# CODEX-SPEC-EXP-LEDGER-PHASE4-01

## Metadata
* **Packet ID:** CODEX-SPEC-EXP-LEDGER-PHASE4-01
* **Phase:** 4 – Renderer Contract Hardening
* **Aligned Scope:** `VEX-SCOPE-EXP-LEDGER-PHASE4`
* **Specification Author:** CODEX (Worker Mode)
* **Status:** ACTIVE
* **Specification Date:** 2026-02-07

## 1. Objective

Translate VEX-SCOPE-EXP-LEDGER-PHASE4 into executable specifications for hardening the ledger renderer. Define exact code changes, defensive logic removal, and explicit error UI implementation.

## 2. Implementation Steps

### Step 1: Audit Renderer Code (WBS 4.1 - Discovery)

**Action:** Identify all files that consume and render ledger data

**Likely Targets:**
1. `apps/business_case/scenario-output.js` - Main ledger consumer
2. `apps/business_case/scenario-output.html` - Ledger display page
3. `apps/business_case/js/scenario-output.js` - Ledger rendering logic
4. Any chart renderers (Plotly adapters, etc.)

**Audit Checklist:**
- [ ] Find all "ledger" or "ledgerSnapshot" variable usages
- [ ] Identify defensive checks (|| default values)
- [ ] Identify silent failures (console.error with no UI feedback)
- [ ] Identify blank screen paths (return without rendering)
- [ ] List all rendering entry points

**Output:** Code audit report listing removal targets

### Step 2: Remove Defensive Compensation Logic (WBS 4.1.1)

**Action:** Remove all "fallback to default" and "compensate for missing" logic

**Pattern 1: Defensive Defaults**
```javascript
// REMOVE THIS PATTERN:
const label = row.label || 'Unknown';
const unit = row.unit || '';
const values = row.values || [];
const parentId = row.parentId || null;

// REPLACE WITH (trust contract):
const label = row.label;       // Guaranteed by Phase 2
const unit = row.unit;         // Guaranteed by Phase 2
const values = row.values;     // Guaranteed by Phase 3
const parentId = row.parentId; // Guaranteed by Phase 2
```

**Pattern 2: Structure Compensation**
```javascript
// REMOVE THIS PATTERN:
if (!ledger.rows || ledger.rows.length === 0) {
    ledger.rows = []; // Create empty array
}

// REPLACE WITH (fail explicitly):
if (!ledger.rows || ledger.rows.length === 0) {
    return renderError('EMPTY_LEDGER', 'Ledger has no rows to display');
}
```

**Pattern 3: Graceful Degradation**
```javascript
// REMOVE THIS PATTERN:
function renderRow(row) {
    if (!row) return ''; // Silent skip
    if (!row.id) return ''; // Silent skip
    // ... render row
}

// REPLACE WITH (fail explicitly):
function renderRow(row) {
    if (!row) {
        throw new Error('INVALID_ROW: Row is null or undefined');
    }
    if (!row.id) {
        throw new Error('INVALID_ROW: Row missing required field "id"');
    }
    // ... render row (trust structure)
}
```

### Step 3: Create Error Rendering Module (WBS 4.2.1)

**Action:** Create `apps/business_case/js/ledger-error-renderer.js`

**Module Structure:**
```javascript
/**
 * Ledger Error Renderer
 * Responsibility: Render explicit error states for ledger failures
 *
 * Packet: VEX-SCOPE-EXP-LEDGER-PHASE4
 * Authority: Phase 4 - Renderer Contract Hardening
 *
 * PHASE 4 MANDATE:
 * - Blank screens are FORBIDDEN
 * - All failures must be explicit and visible
 * - Error messages must include error code + human-readable text
 */

const LedgerErrorRenderer = (function() {
    'use strict';

    /**
     * Render error state (replaces blank screen)
     *
     * @param {String} errorCode - Machine-readable error code
     * @param {String} message - Human-readable error message
     * @param {Object} context - Additional error context
     * @returns {HTMLElement} Error UI element
     */
    function renderError(errorCode, message, context = {}) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'ledger-error-state';
        errorDiv.innerHTML = `
            <div class="error-container">
                <div class="error-icon">⚠️</div>
                <div class="error-title">Ledger Rendering Failed</div>
                <div class="error-code">Error Code: <code>${errorCode}</code></div>
                <div class="error-message">${escapeHtml(message)}</div>
                ${renderContext(context)}
                <div class="error-help">
                    <strong>What to do:</strong><br>
                    This ledger did not pass validation. Please check the model's semantic nodes
                    and ensure all required fields are present.
                </div>
                <div class="error-technical">
                    <details>
                        <summary>Technical Details</summary>
                        <pre>${JSON.stringify({ errorCode, message, context }, null, 2)}</pre>
                    </details>
                </div>
            </div>
        `;
        return errorDiv;
    }

    /**
     * Render error context (if provided)
     */
    function renderContext(context) {
        if (!context || Object.keys(context).length === 0) {
            return '';
        }

        const entries = Object.entries(context).map(([key, value]) => {
            return `<li><strong>${escapeHtml(key)}:</strong> ${escapeHtml(String(value))}</li>`;
        }).join('');

        return `
            <div class="error-context">
                <strong>Context:</strong>
                <ul>${entries}</ul>
            </div>
        `;
    }

    /**
     * Escape HTML to prevent XSS
     */
    function escapeHtml(unsafe) {
        return String(unsafe)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    /**
     * Error codes and standard messages
     */
    const ERROR_MESSAGES = {
        'MISSING_LEDGER': 'No ledger data was provided to the renderer',
        'INVALID_LEDGER_STRUCTURE': 'Ledger is missing required structure (rows array)',
        'EMPTY_LEDGER': 'Ledger has no rows to display',
        'INVALID_ROW': 'Ledger row is missing required fields',
        'RENDERING_EXCEPTION': 'An unexpected error occurred during rendering'
    };

    /**
     * Get standard error message for code
     */
    function getStandardMessage(errorCode) {
        return ERROR_MESSAGES[errorCode] || 'An unknown error occurred';
    }

    // Public API
    return {
        renderError: renderError,
        getStandardMessage: getStandardMessage
    };
})();

// Export for module usage
if (typeof window !== 'undefined') {
    window.LedgerErrorRenderer = LedgerErrorRenderer;
}
```

### Step 4: Add Error Boundary to Renderer (WBS 4.2.2)

**Action:** Wrap main rendering function with try/catch error boundary

**Location:** `apps/business_case/js/scenario-output.js` (or main rendering file)

**Implementation:**
```javascript
/**
 * Render ledger with error boundary
 * PHASE 4: Catch all rendering exceptions and display error UI
 */
function renderLedgerWithBoundary(ledgerSnapshot, targetElement) {
    try {
        // Validate ledger structure (trust but verify)
        validateLedgerStructure(ledgerSnapshot);

        // Render ledger (trust structure is valid)
        const renderedHTML = renderLedgerTable(ledgerSnapshot);

        // Insert into DOM
        targetElement.innerHTML = renderedHTML;

    } catch (error) {
        console.error('[LEDGER_RENDERER] Rendering failed:', error);

        // Determine error code
        const errorCode = error.code || 'RENDERING_EXCEPTION';
        const message = error.message || 'An unexpected error occurred';

        // Render error UI (no blank screens)
        const errorUI = LedgerErrorRenderer.renderError(errorCode, message, {
            stack: error.stack?.split('\n')[0] // First line of stack
        });

        targetElement.innerHTML = '';
        targetElement.appendChild(errorUI);
    }
}
```

### Step 5: Implement Ledger Structure Validation (WBS 4.2.3)

**Action:** Create validation function for renderer preconditions

**Implementation:**
```javascript
/**
 * Validate ledger structure (renderer preconditions)
 * PHASE 4: Trust but verify - explicit checks with fail-fast
 *
 * @param {Object} ledger - Ledger snapshot
 * @throws {Error} If ledger structure invalid
 */
function validateLedgerStructure(ledger) {
    // Check 1: Ledger exists
    if (!ledger) {
        const error = new Error('No ledger data provided');
        error.code = 'MISSING_LEDGER';
        throw error;
    }

    // Check 2: Rows array exists
    if (!ledger.rows || !Array.isArray(ledger.rows)) {
        const error = new Error('Ledger missing rows array');
        error.code = 'INVALID_LEDGER_STRUCTURE';
        error.context = { hasRows: !!ledger.rows, isArray: Array.isArray(ledger.rows) };
        throw error;
    }

    // Check 3: Rows array not empty
    if (ledger.rows.length === 0) {
        const error = new Error('Ledger has no rows to display');
        error.code = 'EMPTY_LEDGER';
        throw error;
    }

    // Check 4: Each row has required fields
    for (let i = 0; i < ledger.rows.length; i++) {
        const row = ledger.rows[i];

        if (!row.id) {
            const error = new Error(`Row at index ${i} missing required field "id"`);
            error.code = 'INVALID_ROW';
            error.context = { rowIndex: i, row: row };
            throw error;
        }

        if (!row.values || !Array.isArray(row.values)) {
            const error = new Error(`Row "${row.id}" missing values array`);
            error.code = 'INVALID_ROW';
            error.context = { rowId: row.id, rowIndex: i };
            throw error;
        }
    }

    // All checks passed
    return true;
}
```

### Step 6: Add Error Styling (WBS 4.2.4)

**Action:** Create CSS for error UI

**Location:** `apps/business_case/css/scenario-output.css` (or create new file)

**CSS:**
```css
/* Ledger Error State Styling */
.ledger-error-state {
    padding: 20px;
    margin: 20px 0;
}

.error-container {
    background-color: #fff3cd;
    border: 2px solid #ffc107;
    border-radius: 8px;
    padding: 24px;
    max-width: 800px;
    margin: 0 auto;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}

.error-icon {
    font-size: 48px;
    text-align: center;
    margin-bottom: 16px;
}

.error-title {
    font-size: 24px;
    font-weight: bold;
    text-align: center;
    color: #856404;
    margin-bottom: 12px;
}

.error-code {
    text-align: center;
    font-size: 14px;
    color: #856404;
    margin-bottom: 16px;
}

.error-code code {
    background-color: #fff;
    padding: 4px 8px;
    border-radius: 4px;
    font-family: "Courier New", monospace;
    border: 1px solid #ffc107;
}

.error-message {
    font-size: 16px;
    color: #333;
    margin-bottom: 16px;
    padding: 12px;
    background-color: #fff;
    border-left: 4px solid #ffc107;
}

.error-context {
    font-size: 14px;
    color: #666;
    margin-bottom: 16px;
}

.error-context ul {
    list-style: none;
    padding-left: 0;
}

.error-context li {
    padding: 4px 0;
}

.error-help {
    font-size: 14px;
    color: #856404;
    background-color: #fff;
    padding: 12px;
    border-radius: 4px;
    margin-bottom: 16px;
}

.error-technical {
    margin-top: 16px;
}

.error-technical details {
    cursor: pointer;
}

.error-technical summary {
    font-size: 14px;
    color: #856404;
    padding: 8px;
    background-color: #fff;
    border-radius: 4px;
}

.error-technical pre {
    background-color: #f8f9fa;
    padding: 12px;
    border-radius: 4px;
    overflow-x: auto;
    font-size: 12px;
    margin-top: 8px;
}
```

### Step 7: Update Main Rendering Entry Point (WBS 4.3)

**Action:** Modify main ledger rendering function to use error boundary

**Before (Phase 3):**
```javascript
function loadAndRenderLedger(runId) {
    const execution = getExecutionFromRegistry(runId);
    if (!execution) {
        console.error('Execution not found:', runId);
        return; // BLANK SCREEN
    }

    const ledger = execution.ledgerSnapshot;
    if (!ledger) {
        console.error('No ledger in execution');
        return; // BLANK SCREEN
    }

    renderLedgerTable(ledger);
}
```

**After (Phase 4):**
```javascript
function loadAndRenderLedger(runId) {
    const targetElement = document.getElementById('ledger-container');

    try {
        // Load execution
        const execution = getExecutionFromRegistry(runId);
        if (!execution) {
            const error = new Error(`Execution not found: ${runId}`);
            error.code = 'MISSING_EXECUTION';
            throw error;
        }

        // Load ledger
        const ledger = execution.ledgerSnapshot;
        if (!ledger) {
            const error = new Error('Execution has no ledger snapshot');
            error.code = 'MISSING_LEDGER';
            error.context = { runId: runId };
            throw error;
        }

        // Render with error boundary
        renderLedgerWithBoundary(ledger, targetElement);

    } catch (error) {
        console.error('[SCENARIO_OUTPUT] Load failed:', error);

        // Render error UI (no blank screens)
        const errorUI = LedgerErrorRenderer.renderError(
            error.code || 'LOADING_FAILED',
            error.message || 'Failed to load ledger',
            error.context || {}
        );

        targetElement.innerHTML = '';
        targetElement.appendChild(errorUI);
    }
}
```

## 3. Acceptance Criteria

### AC1: Defensive Logic Removed
- ✅ No "|| default" patterns for guaranteed fields (id, label, unit, values)
- ✅ No silent skips (return '' or return without error)
- ✅ No structure compensation (creating empty arrays, etc.)

### AC2: Error UI Implemented
- ✅ LedgerErrorRenderer module created
- ✅ Error CSS styling added
- ✅ All error states render visible UI (no blank screens)

### AC3: Error Boundary Installed
- ✅ Main rendering function wrapped in try/catch
- ✅ All exceptions caught and displayed
- ✅ Error codes assigned to all error types

### AC4: Validation Implemented
- ✅ validateLedgerStructure() function checks:
  - Ledger exists
  - rows[] array exists and is array
  - rows[] not empty
  - Each row has id and values
- ✅ Validation throws errors with codes

### AC5: No Regressions
- ✅ Valid ledgers render correctly
- ✅ All existing functionality preserved
- ✅ Charts/graphs still work

## 4. Verification Plan

**Test Categories:**

1. **Positive Tests (No Regressions):**
   - Valid OBSERVED-only ledger renders
   - Valid DERIVED ledger (NPV/BCR) renders
   - Charts render from valid ledger
   - Hierarchy displays correctly

2. **Negative Tests (Error UI):**
   - Missing ledger → Error UI displayed
   - Empty rows → Error UI displayed
   - Invalid row (missing id) → Error UI displayed
   - Rendering exception → Error boundary catches

3. **Visual Tests:**
   - Error UI has warning icon
   - Error code displayed
   - Error message readable
   - Technical details expandable

**Test Evidence:** Class A (automated checks for error UI presence)

## 5. Files to Create/Modify

**New Files:**
1. `apps/business_case/js/ledger-error-renderer.js` (~150 lines)
2. `apps/business_case/css/ledger-error.css` (~100 lines)

**Modified Files:**
1. `apps/business_case/js/scenario-output.js` (add error boundary)
2. `apps/business_case/scenario-output.html` (include error CSS)

**Test File:**
3. `apps/tests/verify_ledger_renderer_hardening.js` (new test suite)

**Total Files:** 2 new, 2 modified, 1 test

## 6. Success Metrics

- Defensive logic removed: ✅
- Error UI module created: ✅
- Error boundary installed: ✅
- Blank screens eliminated: ✅
- Valid ledgers still render: ✅

## 7. Non-Goals (Deferred to Later Phases)

- Polished error UI design (Phase 6)
- Migration tooling (Phase 5)
- Performance optimization (acceptable trade-off)

## 8. Specification Status

**Status:** ✅ COMPLETE - Ready for AG execution

**AG Instructions:**
1. Audit scenario-output.js and related renderers
2. Create LedgerErrorRenderer module
3. Create error CSS styling
4. Add error boundary to main rendering
5. Remove defensive compensation logic
6. Create test suite for error states
7. Run tests and provide Class A evidence of PASS
8. Create AG-RESULT packet with evidence

---

**CODEX WORKER SPECIFICATION COMPLETE**

**Next Phase:** AG Execution
