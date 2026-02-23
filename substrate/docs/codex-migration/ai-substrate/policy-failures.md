# Policy Failure Handling

## UI messaging
- Default message: “You are not permitted to perform that action.”
- Action-specific overrides tied to `resource` fields (e.g., `comment:update` shows detail about owning the comment).

## HTTP mapping
- Authorization failures return HTTP 403 with `{"error": "FORBIDDEN", "reason": "<resource> not available"}`.
- Backend logs include `permissionContext` JSON from `lib/auth/policy.ts`.

## Audit log
- Failures are appended to `logs/ai-substrate/policy-denials.log` with timestamps and role context.
- Retention policy: 30 days rolling window, rotated monthly.
