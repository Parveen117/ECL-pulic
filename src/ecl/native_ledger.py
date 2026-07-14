"""Deterministic public ECL native-ledger experiment.

The module compares a model-defined residue-processing condition with a shadow
condition. It is a reproducible research prototype, not a security proof or a
claim of independent physical validation.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class NativeLedgerConfig:
    events: int = 512
    root_dim: int = 12
    template_rate: float = 0.22
    phase_rate: float = 0.18
    compensator: float = 0.35
    ledger: float = 0.65
    seed: int = 117

    def validate(self) -> None:
        if self.events <= 0:
            raise ValueError("events must be greater than zero")
        if self.root_dim <= 0:
            raise ValueError("root_dim must be greater than zero")
        for name in ("template_rate", "phase_rate", "compensator", "ledger"):
            value = getattr(self, name)
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be between 0 and 1")


def sha256_canonical(obj: Any) -> str:
    """Return SHA-256 over compact, sorted UTF-8 JSON."""
    payload = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _agreement(left: list[int], right: list[int]) -> float:
    if len(left) != len(right) or not left:
        raise ValueError("agreement requires non-empty lists of equal length")
    return sum(a == b for a, b in zip(left, right)) / len(left)


def _make_bits(rng: random.Random, size: int) -> list[int]:
    return [rng.randrange(2) for _ in range(size)]


def _map_template(root: list[int], template: list[int]) -> list[int]:
    return [root_bit ^ template_bit for root_bit, template_bit in zip(root, template)]


def run_condition(config: NativeLedgerConfig, native_on: bool) -> dict[str, Any]:
    """Run one deterministic condition and return event rows and aggregates."""
    config.validate()
    rng = random.Random(config.seed)
    rows: list[dict[str, float | int]] = []
    k_memory = 0.0

    for event_id in range(1, config.events + 1):
        root = _make_bits(rng, config.root_dim)
        template = [
            1 if rng.random() < config.template_rate else 0
            for _ in range(config.root_dim)
        ]
        phase = [
            1 if rng.random() < config.phase_rate else 0
            for _ in range(config.root_dim)
        ]

        lawful = _map_template(root, template)
        observed = [lawful_bit ^ phase_bit for lawful_bit, phase_bit in zip(lawful, phase)]

        raw_total = 0.0
        compensated_total = 0.0
        ledgered_total = 0.0
        open_total = 0.0
        reconstructed: list[int] = []

        for lawful_bit, observed_bit in zip(lawful, observed):
            raw = float(observed_bit - lawful_bit)
            raw_total += abs(raw)

            if native_on:
                compensated = config.compensator * raw
                after_compensation = raw - compensated
                ledgered = config.ledger * after_compensation
                open_part = after_compensation - ledgered
                k_memory += ledgered
                corrected = observed_bit if abs(open_part) > 0.5 else lawful_bit
            else:
                compensated = 0.0
                ledgered = 0.0
                open_part = raw
                corrected = observed_bit

            compensated_total += abs(compensated)
            ledgered_total += abs(ledgered)
            open_total += abs(open_part)
            reconstructed.append(corrected)

        rows.append(
            {
                "event_id": event_id,
                "C_root_template_phase": _agreement(reconstructed, lawful),
                "G_UGD_native": open_total / raw_total if raw_total else 0.0,
                "G_shadow": 1.0 - _agreement(observed, lawful),
                "raw_residue": raw_total,
                "seam_compensated": compensated_total,
                "ledgered_memory": ledgered_total,
                "open_residue": open_total,
                "k_memory": k_memory,
            }
        )

    numeric_fields = [field for field in rows[0] if field != "event_id"]
    averages = {
        field: sum(float(row[field]) for row in rows) / len(rows)
        for field in numeric_fields
    }
    return {"final": rows[-1], "averages": averages, "rows": rows}


def build_report(config: NativeLedgerConfig) -> dict[str, Any]:
    """Build a deterministic comparison report with a certificate hash."""
    native_on = run_condition(config, native_on=True)
    native_off = run_condition(config, native_on=False)

    comparison = {
        "delta_C_root_template_phase": (
            native_on["averages"]["C_root_template_phase"]
            - native_off["averages"]["C_root_template_phase"]
        ),
        "delta_G_UGD_native": (
            native_on["averages"]["G_UGD_native"]
            - native_off["averages"]["G_UGD_native"]
        ),
        "delta_G_shadow": (
            native_on["averages"]["G_shadow"]
            - native_off["averages"]["G_shadow"]
        ),
        "native_advantage": bool(
            native_on["averages"]["C_root_template_phase"]
            > native_off["averages"]["C_root_template_phase"]
            and native_on["averages"]["G_UGD_native"]
            < native_off["averages"]["G_UGD_native"]
        ),
    }

    report: dict[str, Any] = {
        "marker": "ECL-Native-Ledger-v2-public",
        "grammar": "LOAD Root -> MAP Template -> LINK Context -> RUN Phase -> HALT Seam",
        "config": asdict(config),
        "native_on": native_on,
        "native_off": native_off,
        "comparison": comparison,
        "interpretation": "Model-defined deterministic research output; not an external validation claim.",
    }
    report["certificate_hash"] = sha256_canonical(report)
    return report


def write_report(report: dict[str, Any], out_dir: Path) -> None:
    """Write JSON, CSV, and summary artifacts."""
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True), encoding="utf-8"
    )

    for condition in ("native_on", "native_off"):
        rows = report[condition]["rows"]
        path = out_dir / f"{condition}_rows.csv"
        fields = ["condition", "certificate_hash", *rows[0].keys()]
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            for row in rows:
                writer.writerow(
                    {
                        "condition": condition,
                        "certificate_hash": report["certificate_hash"],
                        **row,
                    }
                )

    summary = (
        "# ECL Native Ledger Public Report\n\n"
        f"Certificate hash: `{report['certificate_hash']}`\n\n"
        "```json\n"
        f"{json.dumps(report['comparison'], indent=2, sort_keys=True)}\n"
        "```\n"
    )
    (out_dir / "SUMMARY.md").write_text(summary, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the public ECL native-ledger experiment")
    parser.add_argument("--events", type=int, default=512)
    parser.add_argument("--root-dim", type=int, default=12)
    parser.add_argument("--template-rate", type=float, default=0.22)
    parser.add_argument("--phase-rate", type=float, default=0.18)
    parser.add_argument("--compensator", type=float, default=0.35)
    parser.add_argument("--ledger", type=float, default=0.65)
    parser.add_argument("--seed", type=int, default=117)
    parser.add_argument("--out-dir", type=Path, default=Path("outputs/native-ledger"))
    args = parser.parse_args()

    config = NativeLedgerConfig(
        events=args.events,
        root_dim=args.root_dim,
        template_rate=args.template_rate,
        phase_rate=args.phase_rate,
        compensator=args.compensator,
        ledger=args.ledger,
        seed=args.seed,
    )
    report = build_report(config)
    write_report(report, args.out_dir)
    print(json.dumps({"certificate_hash": report["certificate_hash"], "comparison": report["comparison"]}, indent=2))
    print(f"output_dir: {args.out_dir}")


if __name__ == "__main__":
    main()
