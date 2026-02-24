# Audit Viewer and Export Contract

Date: 2026-02-24
Packet: PRD-4-3

## Backend Contract

File: `src/app/audit.py`

- Filtered query by tenant, actor, packet, date range
- Pagination helper
- JSON export path
- CSV export path

## UI Contract

File: `app/src/ui/auditViewer.ts`

- Filter model with pagination fields
- Query parameter formatter for API calls

## Immutability

Audit viewer is read-only and export-only by contract; no mutation path is exposed.

## Validation

- `python3 -m unittest tests/test_audit_viewer.py`
