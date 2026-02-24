# Risk Register UI Contract

Date: 2026-02-24
Packet: PRD-4-4

## Delivered Modules

- `src/app/risk_register.py`
- `app/src/ui/riskRegister.ts`

## Views

- Risk grid rows (`grid_rows`)
- Heatmap buckets (`heatmap`)
- Aging view (`aging_view`)
- Linked packet navigation (`linkedPacketPath`)

## Validation

- `python3 -m unittest tests/test_risk_register.py`
