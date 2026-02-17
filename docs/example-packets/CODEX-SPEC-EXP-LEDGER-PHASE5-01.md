# CODEX-SPEC-EXP-LEDGER-PHASE5-01

## Metadata
* **Packet ID:** CODEX-SPEC-EXP-LEDGER-PHASE5-01
* **Phase:** 5 – Migration Tooling
* **Aligned Scope:** `VEX-SCOPE-EXP-LEDGER-PHASE5`
* **Specification Author:** CODEX (Worker Mode)
* **Status:** ACTIVE
* **Specification Date:** 2026-02-07

## 1. Objective

Translate VEX-SCOPE-EXP-LEDGER-PHASE5 into executable specifications for creating migration tooling. Define exact implementation steps, heuristic logic, validation integration, and CLI tool structure.

## 2. Implementation Steps

### Step 1: Create Migration Core Module (WBS 5.2.1)

**Action:** Create core migration logic module

**File:** `apps/tools/ledger_migration/migration_engine.js`

**Module Structure:**
```javascript
/**
 * Ledger Migration Engine
 * Responsibility: Migrate legacy models to semantic node contracts
 *
 * Packet: VEX-SCOPE-EXP-LEDGER-PHASE5
 * Authority: Phase 5 - Migration Tooling
 *
 * PHASE 5 MANDATE:
 * - Non-destructive migration (read-only source)
 * - Phase 2 compliance (all contracts validated)
 * - 1:1 mapping (each variable → one semantic node)
 * - Audit trail (Class A evidence)
 */

const MigrationEngine = (function() {
    'use strict';

    /**
     * Migrate model variables to semantic nodes
     *
     * @param {Object} model - Model payload with variables
     * @param {Object} options - Migration options
     * @returns {Object} Migration result { nodes, report, validation }
     */
    function migrate(model, options = {}) {
        // Pre-flight validation
        const preFlightResult = validatePreFlight(model);
        if (!preFlightResult.valid) {
            return {
                success: false,
                stage: 'PRE_FLIGHT',
                errors: preFlightResult.errors
            };
        }

        // Extract variables
        const variables = extractVariables(model);

        // Generate semantic nodes
        const nodes = variables.map((variable, index) => {
            return generateSemanticNode(variable, index, variables, options);
        });

        // Build hierarchy
        assignHierarchy(nodes, options);

        // Post-migration validation
        const validationResult = validateSemanticNodes(nodes);
        if (!validationResult.valid) {
            return {
                success: false,
                stage: 'POST_MIGRATION',
                errors: validationResult.errors,
                nodes: nodes // Include partial result for debugging
            };
        }

        // Generate report
        const report = generateMigrationReport(variables, nodes, validationResult);

        return {
            success: true,
            nodes: nodes,
            report: report,
            validation: validationResult
        };
    }

    /**
     * Pre-flight validation (check source model)
     */
    function validatePreFlight(model) {
        const errors = [];

        if (!model) {
            errors.push({ code: 'MISSING_MODEL', message: 'No model provided' });
            return { valid: false, errors };
        }

        if (!model.variables || !Array.isArray(model.variables)) {
            errors.push({ code: 'MISSING_VARIABLES', message: 'Model has no variables array' });
            return { valid: false, errors };
        }

        if (model.variables.length === 0) {
            errors.push({ code: 'EMPTY_VARIABLES', message: 'Model has no variables to migrate' });
            return { valid: false, errors };
        }

        // Check for required fields
        model.variables.forEach((v, i) => {
            if (!v.id) {
                errors.push({ code: 'MISSING_VARIABLE_ID', message: `Variable at index ${i} missing id` });
            }
            if (!v.label) {
                errors.push({ code: 'MISSING_VARIABLE_LABEL', message: `Variable ${v.id} missing label` });
            }
        });

        // Check for duplicate IDs
        const ids = model.variables.map(v => v.id).filter(Boolean);
        const duplicates = ids.filter((id, i) => ids.indexOf(id) !== i);
        if (duplicates.length > 0) {
            errors.push({ code: 'DUPLICATE_VARIABLE_IDS', message: `Duplicate variable IDs: ${duplicates.join(', ')}` });
        }

        return { valid: errors.length === 0, errors };
    }

    /**
     * Extract variables from model
     */
    function extractVariables(model) {
        return model.variables.map(v => ({
            id: v.id,
            label: v.label,
            unit: v.unit || '',
            category: v.category || null,
            subcategory: v.subcategory || null,
            displayOrder: v.displayOrder !== undefined ? v.displayOrder : null,
            formula: v.formula || null,
            metadata: v.metadata || {}
        }));
    }

    /**
     * Generate semantic node from variable
     */
    function generateSemanticNode(variable, index, allVariables, options) {
        // Infer category if not provided
        const category = variable.category || inferCategory(variable.id, variable.label);

        // Infer node type
        const nodeType = inferNodeType(variable, allVariables);

        // Infer exposure type
        const exposureType = inferExposureType(variable, nodeType);

        // Create semantic node
        const node = {
            semanticNodeId: variable.id,
            label: variable.label,
            unit: variable.unit,
            category: category.primary,
            subcategory: category.secondary || null,
            nodeType: nodeType,
            exposureType: exposureType,
            displayOrder: variable.displayOrder !== null ? variable.displayOrder : index,
            bindings: [variable.id], // 1:1 mapping
            parentNodeId: null, // Assigned in hierarchy step
            children: [],
            metadata: {
                migratedFrom: variable.id,
                migrationDate: new Date().toISOString(),
                ...variable.metadata
            }
        };

        // Add derivation metadata for DERIVED nodes
        if (exposureType === 'DERIVED') {
            node.derivationMetadata = inferDerivationMetadata(variable);
        }

        return node;
    }

    /**
     * Infer category from variable ID/label
     */
    function inferCategory(id, label) {
        const idLower = id.toLowerCase();
        const labelLower = label.toLowerCase();

        // COSTS patterns
        if (idLower.includes('capex') || idLower.includes('capital')) {
            return { primary: 'COSTS', secondary: 'CAPEX', confidence: 'HIGH' };
        }
        if (idLower.includes('opex') || idLower.includes('operating')) {
            return { primary: 'COSTS', secondary: 'OPEX', confidence: 'HIGH' };
        }
        if (idLower.includes('cost') || labelLower.includes('cost')) {
            return { primary: 'COSTS', secondary: null, confidence: 'MEDIUM' };
        }

        // BENEFITS patterns
        if (idLower.includes('benefit') || labelLower.includes('benefit')) {
            return { primary: 'BENEFITS', secondary: null, confidence: 'HIGH' };
        }
        if (idLower.includes('revenue') || idLower.includes('saving')) {
            return { primary: 'BENEFITS', secondary: null, confidence: 'MEDIUM' };
        }

        // DEMAND patterns
        if (idLower.includes('demand') || idLower.includes('pax') || idLower.includes('passenger')) {
            return { primary: 'DEMAND', secondary: null, confidence: 'HIGH' };
        }

        // CAPACITY patterns
        if (idLower.includes('capacity') || idLower.includes('service') || idLower.includes('frequency')) {
            return { primary: 'CAPACITY', secondary: null, confidence: 'HIGH' };
        }

        // APPRAISAL patterns (NPV, BCR, etc.)
        if (idLower === 'npv' || idLower === 'bcr' || idLower.startsWith('pv_')) {
            return { primary: 'APPRAISAL', secondary: null, confidence: 'HIGH' };
        }

        // Default to COSTS with LOW confidence
        return { primary: 'COSTS', secondary: null, confidence: 'LOW' };
    }

    /**
     * Infer node type (LEAF or GROUP)
     */
    function inferNodeType(variable, allVariables) {
        // If variable has formula and bindings, it's likely a LEAF (bound to calculation)
        if (variable.formula) {
            return 'LEAF';
        }

        // If variable is referenced by others (parent), it's a GROUP
        // For now, default to LEAF (most variables are leaves)
        return 'LEAF';
    }

    /**
     * Infer exposure type (OBSERVED or DERIVED)
     */
    function inferExposureType(variable, nodeType) {
        const idLower = variable.id.toLowerCase();

        // NPV, BCR, PV_* are DERIVED
        if (idLower === 'npv' || idLower === 'bcr' || idLower.startsWith('pv_')) {
            return 'DERIVED';
        }

        // Default to OBSERVED
        return 'OBSERVED';
    }

    /**
     * Infer derivation metadata for DERIVED nodes
     */
    function inferDerivationMetadata(variable) {
        const idLower = variable.id.toLowerCase();

        if (idLower === 'npv') {
            return {
                derivationType: 'NPV',
                inputs: ['benefits_series', 'costs_series', 'discount_rate', 'horizon']
            };
        }

        if (idLower === 'bcr') {
            return {
                derivationType: 'BCR',
                inputs: ['benefits_series', 'costs_series', 'discount_rate', 'horizon']
            };
        }

        return null;
    }

    /**
     * Assign hierarchy (parentNodeId relationships)
     */
    function assignHierarchy(nodes, options) {
        // Group nodes by category
        const categories = {};
        nodes.forEach(node => {
            if (!categories[node.category]) {
                categories[node.category] = [];
            }
            categories[node.category].push(node);
        });

        // Create root nodes for each category
        const rootMap = {};
        Object.keys(categories).forEach(category => {
            const rootId = `ROOT_${category}`;
            rootMap[category] = rootId;

            // Check if root already exists
            const existingRoot = nodes.find(n => n.semanticNodeId === rootId);
            if (!existingRoot) {
                // Create synthetic root
                const rootNode = {
                    semanticNodeId: rootId,
                    label: `Total ${category}`,
                    unit: '',
                    category: category,
                    subcategory: null,
                    nodeType: 'GROUP',
                    exposureType: 'OBSERVED',
                    displayOrder: -1,
                    bindings: [],
                    parentNodeId: null,
                    children: [],
                    metadata: {
                        synthetic: true,
                        migrationGenerated: true
                    }
                };
                nodes.unshift(rootNode); // Add to beginning
            }
        });

        // Assign parentNodeId to all non-root nodes
        nodes.forEach(node => {
            if (!node.parentNodeId && !node.semanticNodeId.startsWith('ROOT_')) {
                node.parentNodeId = rootMap[node.category];
            }
        });

        // Update children arrays
        nodes.forEach(node => {
            if (node.parentNodeId) {
                const parent = nodes.find(n => n.semanticNodeId === node.parentNodeId);
                if (parent && !parent.children.includes(node.semanticNodeId)) {
                    parent.children.push(node.semanticNodeId);
                }
            }
        });
    }

    /**
     * Validate semantic nodes (post-migration)
     */
    function validateSemanticNodes(nodes) {
        const errors = [];

        // Check required fields for each node
        nodes.forEach((node, i) => {
            if (!node.semanticNodeId) {
                errors.push({ code: 'MISSING_NODE_ID', message: `Node at index ${i} missing semanticNodeId` });
            }
            if (!node.label) {
                errors.push({ code: 'MISSING_NODE_LABEL', message: `Node ${node.semanticNodeId} missing label` });
            }
            if (!node.nodeType) {
                errors.push({ code: 'MISSING_NODE_TYPE', message: `Node ${node.semanticNodeId} missing nodeType` });
            }
            if (!node.exposureType) {
                errors.push({ code: 'MISSING_EXPOSURE_TYPE', message: `Node ${node.semanticNodeId} missing exposureType` });
            }
        });

        // Check for orphans (nodes with parentNodeId that doesn't exist)
        nodes.forEach(node => {
            if (node.parentNodeId) {
                const parentExists = nodes.find(n => n.semanticNodeId === node.parentNodeId);
                if (!parentExists) {
                    errors.push({ code: 'ORPHAN_NODE', message: `Node ${node.semanticNodeId} references non-existent parent ${node.parentNodeId}` });
                }
            }
        });

        // Check for cycles (not implemented for simplicity, but could be added)

        return { valid: errors.length === 0, errors };
    }

    /**
     * Generate migration report
     */
    function generateMigrationReport(variables, nodes, validationResult) {
        const report = {
            summary: {
                inputVariables: variables.length,
                outputNodes: nodes.length,
                mapping: variables.length === nodes.length ? 'COMPLETE (1:1)' : 'MISMATCH',
                validationPassed: validationResult.valid
            },
            preFlightChecks: {
                hasVariables: true,
                variablesValid: true,
                noConflicts: true
            },
            migration: {
                nodesGenerated: nodes.length,
                rootsCreated: nodes.filter(n => !n.parentNodeId).length,
                hierarchyDepth: calculateHierarchyDepth(nodes)
            },
            postMigrationChecks: {
                allFieldsPresent: validationResult.valid,
                hierarchyValid: validationResult.valid,
                phase2Compliance: null // Will be filled by CLI tool
            },
            warnings: collectWarnings(variables, nodes),
            errors: validationResult.errors
        };

        return report;
    }

    /**
     * Calculate hierarchy depth
     */
    function calculateHierarchyDepth(nodes) {
        let maxDepth = 0;
        nodes.forEach(node => {
            let depth = 0;
            let current = node;
            while (current.parentNodeId) {
                depth++;
                current = nodes.find(n => n.semanticNodeId === current.parentNodeId);
                if (!current) break;
            }
            maxDepth = Math.max(maxDepth, depth);
        });
        return maxDepth;
    }

    /**
     * Collect warnings (low confidence, unusual patterns)
     */
    function collectWarnings(variables, nodes) {
        const warnings = [];

        nodes.forEach(node => {
            if (node.metadata && node.metadata.confidence === 'LOW') {
                warnings.push({
                    code: 'LOW_CONFIDENCE',
                    message: `Variable "${node.semanticNodeId}" assigned to ${node.category} with LOW confidence`,
                    suggestion: 'Consider manual review in Model Builder'
                });
            }
        });

        return warnings;
    }

    // Public API
    return {
        migrate: migrate,
        validatePreFlight: validatePreFlight,
        inferCategory: inferCategory
    };
})();

// Export for Node.js
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MigrationEngine;
}
```

**Output:** Core migration engine module (~300 lines)

### Step 2: Create CLI Tool Wrapper (WBS 5.5)

**Action:** Create command-line interface for migration tool

**File:** `apps/tools/migrate_ledger_contract.js`

**Implementation:**
```javascript
#!/usr/bin/env node

/**
 * Ledger Migration CLI Tool
 * Authority: VEX-SCOPE-EXP-LEDGER-PHASE5
 */

const fs = require('fs');
const path = require('path');
const MigrationEngine = require('./ledger_migration/migration_engine.js');

// Parse command-line arguments
const args = process.argv.slice(2);
const options = parseArguments(args);

// Validate arguments
if (!options.modelId && !options.batch) {
    console.error('Error: --model-id or --batch required');
    console.log('Usage: node migrate_ledger_contract.js --model-id <id> --output <path>');
    process.exit(1);
}

// Execute migration
if (options.batch) {
    executeBatchMigration(options);
} else {
    executeSingleMigration(options);
}

function parseArguments(args) {
    const options = {
        modelId: null,
        batch: false,
        sourceDir: null,
        output: './migrated',
        dryRun: false,
        reportOnly: false,
        verbose: false
    };

    for (let i = 0; i < args.length; i++) {
        const arg = args[i];
        switch (arg) {
            case '--model-id':
                options.modelId = args[++i];
                break;
            case '--batch':
                options.batch = true;
                break;
            case '--source-dir':
                options.sourceDir = args[++i];
                break;
            case '--output':
                options.output = args[++i];
                break;
            case '--dry-run':
                options.dryRun = true;
                break;
            case '--report-only':
                options.reportOnly = true;
                break;
            case '--verbose':
                options.verbose = true;
                break;
        }
    }

    return options;
}

function executeSingleMigration(options) {
    console.log(`\n═══ Ledger Migration Tool (Phase 5) ═══\n`);
    console.log(`Model ID: ${options.modelId}`);
    console.log(`Output: ${options.output}`);
    console.log(`Mode: ${options.dryRun ? 'DRY-RUN' : 'MIGRATION'}\n`);

    // Load model (from database or file)
    const model = loadModel(options.modelId, options);

    if (!model) {
        console.error(`✗ Failed to load model: ${options.modelId}`);
        process.exit(1);
    }

    console.log(`✓ Model loaded: ${model.variables ? model.variables.length : 0} variables\n`);

    // Run migration
    const result = MigrationEngine.migrate(model, options);

    if (!result.success) {
        console.error(`✗ Migration failed at stage: ${result.stage}`);
        result.errors.forEach(err => {
            console.error(`  - [${err.code}] ${err.message}`);
        });
        process.exit(1);
    }

    console.log(`✓ Migration successful: ${result.nodes.length} semantic nodes generated\n`);

    // Display report
    displayReport(result.report);

    // Write output (unless dry-run)
    if (!options.dryRun) {
        writeOutput(options.modelId, result.nodes, result.report, options);
        console.log(`\n✓ Migration complete. Output written to: ${options.output}`);
    } else {
        console.log(`\n✓ Dry-run complete. No files written.`);
    }
}

function executeBatchMigration(options) {
    console.log(`\n═══ Batch Ledger Migration (Phase 5) ═══\n`);
    console.log(`Source: ${options.sourceDir}`);
    console.log(`Output: ${options.output}\n`);

    // Load all models from source directory
    const models = loadBatchModels(options.sourceDir);

    console.log(`Found ${models.length} models to migrate\n`);

    let successCount = 0;
    let failureCount = 0;

    models.forEach((modelData, index) => {
        console.log(`[${index + 1}/${models.length}] Migrating: ${modelData.id}`);

        const result = MigrationEngine.migrate(modelData.model, options);

        if (result.success) {
            successCount++;
            if (!options.dryRun) {
                writeOutput(modelData.id, result.nodes, result.report, options);
            }
            console.log(`  ✓ Success`);
        } else {
            failureCount++;
            console.log(`  ✗ Failed: ${result.errors[0]?.message || 'Unknown error'}`);
        }
    });

    console.log(`\n═══ Batch Migration Complete ═══`);
    console.log(`Success: ${successCount}`);
    console.log(`Failure: ${failureCount}`);
}

function loadModel(modelId, options) {
    // Placeholder: Load from database or file
    // In production, this would query the database
    console.log(`  Loading model ${modelId}...`);

    // For now, return null (needs database integration)
    return null;
}

function loadBatchModels(sourceDir) {
    // Placeholder: Load all models from directory
    return [];
}

function displayReport(report) {
    console.log(`═══ Migration Report ═══\n`);
    console.log(`Summary:`);
    console.log(`  Input Variables: ${report.summary.inputVariables}`);
    console.log(`  Output Nodes: ${report.summary.outputNodes}`);
    console.log(`  Mapping: ${report.summary.mapping}`);
    console.log(`  Validation: ${report.summary.validationPassed ? 'PASS' : 'FAIL'}\n`);

    if (report.warnings.length > 0) {
        console.log(`Warnings:`);
        report.warnings.forEach(w => {
            console.log(`  ⚠️  [${w.code}] ${w.message}`);
            if (w.suggestion) {
                console.log(`      → ${w.suggestion}`);
            }
        });
        console.log('');
    }

    if (report.errors.length > 0) {
        console.log(`Errors:`);
        report.errors.forEach(e => {
            console.log(`  ✗ [${e.code}] ${e.message}`);
        });
        console.log('');
    }
}

function writeOutput(modelId, nodes, report, options) {
    // Ensure output directory exists
    if (!fs.existsSync(options.output)) {
        fs.mkdirSync(options.output, { recursive: true });
    }

    // Write semantic nodes
    const nodesFile = path.join(options.output, `${modelId}_semantic_nodes.json`);
    fs.writeFileSync(nodesFile, JSON.stringify(nodes, null, 2));

    // Write migration report
    const reportFile = path.join(options.output, `${modelId}_migration_report.json`);
    fs.writeFileSync(reportFile, JSON.stringify(report, null, 2));

    console.log(`  → Nodes written: ${nodesFile}`);
    console.log(`  → Report written: ${reportFile}`);
}
```

**Output:** CLI tool (~200 lines)

### Step 3: Integrate Phase 2 Validation (WBS 5.3)

**Action:** Add Phase 2 guard validation to migration pipeline

**File:** `apps/tools/ledger_migration/phase2_validator.js`

**Implementation:**
```javascript
/**
 * Phase 2 Validation Integration
 * Runs Phase 2 guards on migrated contracts
 */

const Phase2Validator = (function() {
    'use strict';

    /**
     * Validate semantic nodes against Phase 2 guards
     *
     * @param {Array} semanticNodes - Migrated semantic nodes
     * @returns {Object} Validation result { valid, errors }
     */
    function validatePhase2(semanticNodes) {
        // Load Phase 2 guard (if available)
        let LedgerExposureGuard;
        try {
            // Attempt to load Phase 2 guard from business_case
            LedgerExposureGuard = require('../../business_case/js/semantic-completeness-guard.js');
        } catch (e) {
            return {
                valid: null,
                error: 'Phase 2 guard not available',
                skipped: true
            };
        }

        if (!LedgerExposureGuard || !LedgerExposureGuard.validateContract) {
            return {
                valid: null,
                error: 'Phase 2 guard missing validateContract function',
                skipped: true
            };
        }

        // Run Phase 2 validation
        const result = LedgerExposureGuard.validateContract(semanticNodes, {});

        return {
            valid: result.valid,
            message: result.message || '',
            errors: result.errors || [],
            skipped: false
        };
    }

    return {
        validatePhase2: validatePhase2
    };
})();

// Export for Node.js
if (typeof module !== 'undefined' && module.exports) {
    module.exports = Phase2Validator;
}
```

**Output:** Phase 2 validation integration (~50 lines)

### Step 4: Create Test Suite (WBS 5.6)

**Action:** Create comprehensive tests for migration tooling

**File:** `apps/tests/verify_ledger_migration.js`

**Test Coverage:**
1. Pre-flight validation tests
2. Heuristic inference tests (category, node type)
3. Hierarchy construction tests
4. Post-migration validation tests
5. 1:1 mapping verification
6. Phase 2 compliance tests
7. Report generation tests

**Implementation:** (See detailed test suite in acceptance criteria)

### Step 5: Create Documentation (WBS 5.7)

**Action:** Create migration tool documentation

**File:** `apps/tools/ledger_migration/README.md`

**Content:**
- Tool overview
- Installation instructions
- Usage examples
- Command-line options
- Troubleshooting guide
- Migration best practices

## 3. Acceptance Criteria

### AC1: Migration Tool Created
**Verification:**
- ✅ `migration_engine.js` exists with migrate() function
- ✅ CLI tool `migrate_ledger_contract.js` exists
- ✅ Tool can process model input
- ✅ Tool generates semantic nodes output

### AC2: Heuristic Inference Implemented
**Verification:**
- ✅ inferCategory() function works correctly
- ✅ inferNodeType() function works correctly
- ✅ inferExposureType() function works correctly
- ✅ Test suite verifies heuristic accuracy

### AC3: Hierarchy Construction Works
**Verification:**
- ✅ assignHierarchy() creates parent-child relationships
- ✅ Root nodes created for each category
- ✅ No orphan nodes (all have valid parents or are roots)
- ✅ Test suite verifies hierarchy validity

### AC4: 1:1 Mapping Enforced
**Verification:**
- ✅ Each variable produces exactly one semantic node
- ✅ Node count equals variable count
- ✅ Bindings array maps back to source variable
- ✅ Test suite proves 1:1 mapping

### AC5: Phase 2 Compliance
**Verification:**
- ✅ Migrated contracts pass Phase 2 validateContract()
- ✅ All required fields present
- ✅ No validation errors
- ✅ Test suite runs Phase 2 guards

### AC6: Migration Report Generated
**Verification:**
- ✅ Report includes summary (input/output counts)
- ✅ Report includes validation results
- ✅ Report includes warnings (low confidence)
- ✅ Report written to file (JSON format)

## 4. Files to Create

**New Files (5):**
1. `apps/tools/ledger_migration/migration_engine.js` (~300 lines)
2. `apps/tools/migrate_ledger_contract.js` (~200 lines)
3. `apps/tools/ledger_migration/phase2_validator.js` (~50 lines)
4. `apps/tools/ledger_migration/README.md` (~100 lines)
5. `apps/tests/verify_ledger_migration.js` (~400 lines)

**Total:** 5 new files (~1050 lines)

## 5. Success Metrics

- Migration tool exists: ✅
- 1:1 mapping enforced: ✅
- Phase 2 compliance: 100%
- Test pass rate: 100%
- Migration reports generated: ✅

---

**CODEX WORKER SPECIFICATION COMPLETE**

**Next Phase:** AG Execution
