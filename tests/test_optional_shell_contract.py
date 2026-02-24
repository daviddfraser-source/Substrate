import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class OptionalShellContractTests(unittest.TestCase):
    def test_optional_shell_module_exists(self):
        target = ROOT / "app/src/ui/optionalShell.ts"
        self.assertTrue(target.exists())

    def test_disabled_mode_contract_present(self):
        content = (ROOT / "app/src/ui/optionalShell.ts").read_text(encoding="utf-8")
        self.assertIn("isDisabledModeSafe", content)
        self.assertIn("registerHook", content)
        self.assertIn("emit", content)


if __name__ == "__main__":
    unittest.main()
