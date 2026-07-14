from pathlib import Path

from ecl.native_ledger import NativeLedgerConfig, build_report, write_report


config = NativeLedgerConfig(events=128, seed=117)
report = build_report(config)
write_report(report, Path("outputs/example-native-ledger"))
print(report["certificate_hash"])
