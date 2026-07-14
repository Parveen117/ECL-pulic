import tempfile
import unittest
from pathlib import Path

from ecl.native_ledger import NativeLedgerConfig, build_report, write_report


class NativeLedgerTests(unittest.TestCase):
    def test_report_is_deterministic(self) -> None:
        config = NativeLedgerConfig(events=64, root_dim=8, seed=117)
        first = build_report(config)
        second = build_report(config)
        self.assertEqual(first["certificate_hash"], second["certificate_hash"])
        self.assertEqual(first, second)

    def test_default_model_reports_native_advantage(self) -> None:
        report = build_report(NativeLedgerConfig(events=64, root_dim=8, seed=117))
        self.assertTrue(report["comparison"]["native_advantage"])

    def test_outputs_are_written(self) -> None:
        report = build_report(NativeLedgerConfig(events=8, root_dim=4, seed=117))
        with tempfile.TemporaryDirectory() as directory:
            out_dir = Path(directory)
            write_report(report, out_dir)
            self.assertTrue((out_dir / "report.json").is_file())
            self.assertTrue((out_dir / "native_on_rows.csv").is_file())
            self.assertTrue((out_dir / "native_off_rows.csv").is_file())
            self.assertTrue((out_dir / "SUMMARY.md").is_file())

    def test_invalid_config_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            build_report(NativeLedgerConfig(events=0))


if __name__ == "__main__":
    unittest.main()
