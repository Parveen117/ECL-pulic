"""Advanced closure-audit engine for ECL.

The engine evaluates a declared expected trajectory against an observed
trajectory before a transition is committed. It provides deterministic,
machine-readable metrics and certificates. The implementation is a bounded
research model, not a proof of a universal physical law or a substitute for an
audited consensus, cryptographic-signature, or safety system.
"""

from __future__ import annotations

import argparse
import cmath
import hashlib
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence


_EPSILON = 1e-12
_TWO_PI = 2.0 * math.pi


def canonical_json_hash(payload: Any) -> str:
    """Return SHA-256 over compact, sorted canonical JSON."""
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def principal_angle(angle: float) -> float:
    """Map an angle to the half-open interval [-pi, pi)."""
    return (angle + math.pi) % _TWO_PI - math.pi


def unwrap_angles(angles: Sequence[float]) -> list[float]:
    """Unwrap a phase sequence using principal consecutive increments."""
    if not angles:
        return []
    unwrapped = [float(angles[0])]
    for current in angles[1:]:
        step = principal_angle(float(current) - unwrapped[-1])
        unwrapped.append(unwrapped[-1] + step)
    return unwrapped


def winding_number(angles: Sequence[float]) -> int:
    """Estimate integer winding from an unwrapped phase trajectory."""
    if len(angles) < 2:
        return 0
    unwrapped = unwrap_angles(angles)
    return int(round((unwrapped[-1] - unwrapped[0]) / _TWO_PI))


@dataclass(frozen=True)
class ComplexPoint:
    real: float
    imag: float

    @classmethod
    def from_complex(cls, value: complex) -> "ComplexPoint":
        return cls(real=float(value.real), imag=float(value.imag))

    def as_complex(self) -> complex:
        return complex(self.real, self.imag)


@dataclass(frozen=True)
class ClosureSample:
    """One declared expected/observed sample in a closure trajectory."""

    coordinate: float
    expected: ComplexPoint
    observed: ComplexPoint
    expected_phase: float
    observed_phase: float
    expected_orientation: int = 1
    observed_orientation: int = 1

    def validate(self) -> None:
        values = (
            self.coordinate,
            self.expected.real,
            self.expected.imag,
            self.observed.real,
            self.observed.imag,
            self.expected_phase,
            self.observed_phase,
        )
        if not all(math.isfinite(value) for value in values):
            raise ValueError("all sample values must be finite")
        if self.expected_orientation not in (-1, 1):
            raise ValueError("expected_orientation must be -1 or 1")
        if self.observed_orientation not in (-1, 1):
            raise ValueError("observed_orientation must be -1 or 1")


@dataclass(frozen=True)
class ClosureThresholds:
    max_normalized_defect: float = 0.05
    rupture_supremum: float = 0.05
    rupture_rms: float = 0.025
    phase_lock_rms: float = 0.05
    topology_mismatch: float = 0.0
    hold_multiplier: float = 1.5

    def validate(self) -> None:
        for field_name in (
            "max_normalized_defect",
            "rupture_supremum",
            "rupture_rms",
            "phase_lock_rms",
            "topology_mismatch",
        ):
            value = getattr(self, field_name)
            if not math.isfinite(value) or value < 0.0:
                raise ValueError(f"{field_name} must be finite and non-negative")
        if not math.isfinite(self.hold_multiplier) or self.hold_multiplier < 1.0:
            raise ValueError("hold_multiplier must be finite and at least 1")


@dataclass(frozen=True)
class ClosureErrorVector:
    """Five declared components used by the closure-before-commit gate."""

    normalized_closure_defect: float
    seam_rupture_supremum: float
    seam_rupture_rms: float
    phase_lock_residual: float
    topology_mismatch: float


@dataclass(frozen=True)
class ClosureMetrics:
    sample_count: int
    closure_defect_l2: float
    closure_defect_rms: float
    max_normalized_defect: float
    rupture_supremum: float
    rupture_rms: float
    phase_lock_rms: float
    expected_winding: int
    observed_winding: int
    winding_mismatch: int
    orientation_mismatch_rate: float
    topology_mismatch: float
    error_vector: ClosureErrorVector


@dataclass(frozen=True)
class ClosureCertificate:
    object: str
    version: str
    rule: str
    sample_digest: str
    thresholds: dict[str, float]
    metrics: dict[str, Any]
    component_pass: dict[str, bool]
    classification: str
    closure_before_commit: bool
    limitations: list[str]
    certificate_hash: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def _rms(values: Sequence[float]) -> float:
    return math.sqrt(sum(value * value for value in values) / len(values)) if values else 0.0


def _validate_samples(samples: Sequence[ClosureSample]) -> None:
    if len(samples) < 2:
        raise ValueError("at least two closure samples are required")
    previous_coordinate: float | None = None
    for sample in samples:
        sample.validate()
        if previous_coordinate is not None and sample.coordinate <= previous_coordinate:
            raise ValueError("sample coordinates must be strictly increasing")
        previous_coordinate = sample.coordinate


def compute_metrics(samples: Sequence[ClosureSample]) -> ClosureMetrics:
    """Compute closure, rupture, phase, winding, and orientation metrics."""
    _validate_samples(samples)

    defects: list[complex] = []
    normalized_defects: list[float] = []
    phase_residuals: list[float] = []
    expected_phases: list[float] = []
    observed_phases: list[float] = []
    orientation_mismatches = 0

    for sample in samples:
        expected = sample.expected.as_complex()
        observed = sample.observed.as_complex()
        defect = observed - expected
        defects.append(defect)
        normalized_defects.append(abs(defect) / max(abs(expected), _EPSILON))
        phase_residuals.append(
            abs(principal_angle(sample.observed_phase - sample.expected_phase))
        )
        expected_phases.append(sample.expected_phase)
        observed_phases.append(sample.observed_phase)
        orientation_mismatches += int(
            sample.expected_orientation != sample.observed_orientation
        )

    rupture_values = [
        abs(defects[index] - defects[index - 1])
        for index in range(1, len(defects))
    ]
    defect_magnitudes = [abs(defect) for defect in defects]
    expected_winding = winding_number(expected_phases)
    observed_winding = winding_number(observed_phases)
    winding_mismatch = abs(observed_winding - expected_winding)
    orientation_mismatch_rate = orientation_mismatches / len(samples)
    topology_mismatch = max(float(winding_mismatch), orientation_mismatch_rate)

    error_vector = ClosureErrorVector(
        normalized_closure_defect=max(normalized_defects),
        seam_rupture_supremum=max(rupture_values, default=0.0),
        seam_rupture_rms=_rms(rupture_values),
        phase_lock_residual=_rms(phase_residuals),
        topology_mismatch=topology_mismatch,
    )

    return ClosureMetrics(
        sample_count=len(samples),
        closure_defect_l2=math.sqrt(sum(value * value for value in defect_magnitudes)),
        closure_defect_rms=_rms(defect_magnitudes),
        max_normalized_defect=error_vector.normalized_closure_defect,
        rupture_supremum=error_vector.seam_rupture_supremum,
        rupture_rms=error_vector.seam_rupture_rms,
        phase_lock_rms=error_vector.phase_lock_residual,
        expected_winding=expected_winding,
        observed_winding=observed_winding,
        winding_mismatch=winding_mismatch,
        orientation_mismatch_rate=orientation_mismatch_rate,
        topology_mismatch=topology_mismatch,
        error_vector=error_vector,
    )


def _component_values(metrics: ClosureMetrics) -> dict[str, float]:
    return {
        "max_normalized_defect": metrics.max_normalized_defect,
        "rupture_supremum": metrics.rupture_supremum,
        "rupture_rms": metrics.rupture_rms,
        "phase_lock_rms": metrics.phase_lock_rms,
        "topology_mismatch": metrics.topology_mismatch,
    }


def _threshold_values(thresholds: ClosureThresholds) -> dict[str, float]:
    values = asdict(thresholds)
    values.pop("hold_multiplier")
    return values


def classify(metrics: ClosureMetrics, thresholds: ClosureThresholds) -> tuple[str, dict[str, bool]]:
    """Classify a trajectory as COMMIT, HOLD, or REJECT."""
    thresholds.validate()
    values = _component_values(metrics)
    limits = _threshold_values(thresholds)
    component_pass = {
        name: values[name] <= limits[name]
        for name in values
    }
    if all(component_pass.values()):
        return "COMMIT", component_pass

    topology_failed = not component_pass["topology_mismatch"]
    within_hold_band = all(
        values[name] <= limits[name] * thresholds.hold_multiplier
        for name in values
        if name != "topology_mismatch"
    )
    if not topology_failed and within_hold_band:
        return "HOLD", component_pass
    return "REJECT", component_pass


def certify(
    samples: Sequence[ClosureSample],
    thresholds: ClosureThresholds | None = None,
) -> ClosureCertificate:
    """Create a deterministic closure certificate for a trajectory."""
    active_thresholds = thresholds or ClosureThresholds()
    active_thresholds.validate()
    metrics = compute_metrics(samples)
    classification, component_pass = classify(metrics, active_thresholds)

    sample_payload = [asdict(sample) for sample in samples]
    sample_digest = canonical_json_hash(sample_payload)
    payload: dict[str, Any] = {
        "object": "ECL Advanced Closure Certificate",
        "version": "0.2.0",
        "rule": "closure-before-commit",
        "sample_digest": sample_digest,
        "thresholds": asdict(active_thresholds),
        "metrics": asdict(metrics),
        "component_pass": component_pass,
        "classification": classification,
        "closure_before_commit": classification == "COMMIT",
        "limitations": [
            "Metrics are defined by this repository and require external validation for broader claims.",
            "The certificate hash is a content fingerprint, not a digital signature or trusted timestamp.",
            "Passing thresholds does not establish physical validity, safety, legal priority, or production readiness.",
        ],
    }
    return ClosureCertificate(
        **payload,
        certificate_hash=canonical_json_hash(payload),
    )


def unit_circle_trajectory(
    count: int = 65,
    turns: float = 1.0,
    radial_bias: float = 0.0,
    phase_bias: float = 0.0,
    rupture_index: int | None = None,
    rupture_size: float = 0.0,
    orientation_flip_index: int | None = None,
) -> list[ClosureSample]:
    """Generate a deterministic fixture for examples and self-tests."""
    if count < 2:
        raise ValueError("count must be at least 2")
    samples: list[ClosureSample] = []
    for index in range(count):
        fraction = index / (count - 1)
        expected_phase = _TWO_PI * turns * fraction
        observed_phase = expected_phase + phase_bias
        radius = 1.0 + radial_bias
        if rupture_index is not None and index >= rupture_index:
            radius += rupture_size
        expected = cmath.rect(1.0, expected_phase)
        observed = cmath.rect(radius, observed_phase)
        observed_orientation = -1 if (
            orientation_flip_index is not None and index >= orientation_flip_index
        ) else 1
        samples.append(
            ClosureSample(
                coordinate=fraction,
                expected=ComplexPoint.from_complex(expected),
                observed=ComplexPoint.from_complex(observed),
                expected_phase=expected_phase,
                observed_phase=observed_phase,
                expected_orientation=1,
                observed_orientation=observed_orientation,
            )
        )
    return samples


def samples_from_dicts(records: Iterable[dict[str, Any]]) -> list[ClosureSample]:
    samples: list[ClosureSample] = []
    for record in records:
        samples.append(
            ClosureSample(
                coordinate=float(record["coordinate"]),
                expected=ComplexPoint(**record["expected"]),
                observed=ComplexPoint(**record["observed"]),
                expected_phase=float(record["expected_phase"]),
                observed_phase=float(record["observed_phase"]),
                expected_orientation=int(record.get("expected_orientation", 1)),
                observed_orientation=int(record.get("observed_orientation", 1)),
            )
        )
    return samples


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the ECL advanced closure audit")
    parser.add_argument("--input", type=Path, help="JSON file containing a list of closure samples")
    parser.add_argument("--output", type=Path, default=Path("outputs/closure-certificate.json"))
    parser.add_argument("--fixture", choices=("exact", "bounded", "rupture", "orientation"), default="bounded")
    parser.add_argument("--max-normalized-defect", type=float, default=0.05)
    parser.add_argument("--rupture-supremum", type=float, default=0.05)
    parser.add_argument("--rupture-rms", type=float, default=0.025)
    parser.add_argument("--phase-lock-rms", type=float, default=0.05)
    parser.add_argument("--topology-mismatch", type=float, default=0.0)
    args = parser.parse_args()

    if args.input:
        raw = json.loads(args.input.read_text(encoding="utf-8"))
        samples = samples_from_dicts(raw)
    elif args.fixture == "exact":
        samples = unit_circle_trajectory()
    elif args.fixture == "bounded":
        samples = unit_circle_trajectory(radial_bias=0.01, phase_bias=0.01)
    elif args.fixture == "rupture":
        samples = unit_circle_trajectory(rupture_index=32, rupture_size=0.25)
    else:
        samples = unit_circle_trajectory(orientation_flip_index=32)

    thresholds = ClosureThresholds(
        max_normalized_defect=args.max_normalized_defect,
        rupture_supremum=args.rupture_supremum,
        rupture_rms=args.rupture_rms,
        phase_lock_rms=args.phase_lock_rms,
        topology_mismatch=args.topology_mismatch,
    )
    certificate = certify(samples, thresholds).as_dict()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(certificate, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(certificate, indent=2, sort_keys=True))
    raise SystemExit(0 if certificate["closure_before_commit"] else 2)


if __name__ == "__main__":
    main()
