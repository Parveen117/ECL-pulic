"""Compact PRTP-compatible event-certificate prototype for public ECL."""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


def stable_hash(payload: Any) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class ECLRoot:
    event_id: str
    payload_hash: str
    invariant_tag: str = "ecl_event_root"


@dataclass(frozen=True)
class ECLTemplate:
    name: str
    previous_state_hash: str
    transition_rule: str = "append_only_recognized_transition"


@dataclass(frozen=True)
class ECLPhase:
    timestamp: float
    context_hash: str
    nonce: str
    k_memory: float = 0.0
    phase_note: str = "timestamp_context_nonce"


@dataclass(frozen=True)
class ECLSeamPolicy:
    compensation_strength: float = 0.50
    ledger_strength: float = 0.40
    closure_tolerance: float = 0.0

    def validate(self) -> None:
        if not 0.0 <= self.compensation_strength <= 1.0:
            raise ValueError("compensation_strength must be between 0 and 1")
        if not 0.0 <= self.ledger_strength <= 1.0:
            raise ValueError("ledger_strength must be between 0 and 1")
        if self.closure_tolerance < 0.0:
            raise ValueError("closure_tolerance cannot be negative")


@dataclass(frozen=True)
class ECLPRTPEvent:
    root: ECLRoot
    template: ECLTemplate
    phase: ECLPhase
    observed_state_hash: str
    seam_policy: ECLSeamPolicy = ECLSeamPolicy()


@dataclass(frozen=True)
class ECLPRTPCertificate:
    object: str
    root: dict[str, Any]
    template: dict[str, Any]
    phase: dict[str, Any]
    policy: dict[str, Any]
    expected_state_hash: str
    observed_state_hash: str
    root_preserved: bool
    template_lawful: bool
    raw_residue: float
    seam_compensation: float
    ledger_memory: float
    open_residue: float
    G_UGD_native: float
    native_pass: bool
    shadow_hash_match: bool
    certificate_hash: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def expected_transition_hash(root: ECLRoot, template: ECLTemplate, phase: ECLPhase) -> str:
    return stable_hash(
        {
            "root_event_id": root.event_id,
            "payload_hash": root.payload_hash,
            "previous_state_hash": template.previous_state_hash,
            "transition_rule": template.transition_rule,
            "context_hash": phase.context_hash,
            "nonce": phase.nonce,
        }
    )


def hash_distance(left: str, right: str) -> float:
    """Return normalized character Hamming distance for two hexadecimal hashes."""
    if len(left) != len(right):
        size = max(len(left), len(right), 1)
        return abs(len(left) - len(right)) / size
    if not left:
        return 0.0
    return sum(a != b for a, b in zip(left, right)) / len(left)


def certify_event(event: ECLPRTPEvent) -> ECLPRTPCertificate:
    """Certify one event using the explicit policy carried by the event."""
    event.seam_policy.validate()
    expected = expected_transition_hash(event.root, event.template, event.phase)
    raw = hash_distance(expected, event.observed_state_hash)
    compensation = event.seam_policy.compensation_strength * raw
    after_compensation = max(0.0, raw - compensation)
    ledger_memory = event.seam_policy.ledger_strength * after_compensation
    open_residue = max(0.0, after_compensation - ledger_memory)
    g_ugd = open_residue / raw if raw else 0.0

    root_preserved = bool(event.root.event_id and event.root.payload_hash)
    template_lawful = event.template.transition_rule in {
        "append_only_recognized_transition",
        "signed_transition",
        "hash_chained_transition",
    }
    shadow_hash_match = expected == event.observed_state_hash
    native_pass = bool(
        root_preserved
        and template_lawful
        and open_residue <= event.seam_policy.closure_tolerance
    )

    payload: dict[str, Any] = {
        "object": "ECL PRTP Event Certificate v1 public",
        "root": asdict(event.root),
        "template": asdict(event.template),
        "phase": asdict(event.phase),
        "policy": asdict(event.seam_policy),
        "expected_state_hash": expected,
        "observed_state_hash": event.observed_state_hash,
        "root_preserved": root_preserved,
        "template_lawful": template_lawful,
        "raw_residue": raw,
        "seam_compensation": compensation,
        "ledger_memory": ledger_memory,
        "open_residue": open_residue,
        "G_UGD_native": g_ugd,
        "native_pass": native_pass,
        "shadow_hash_match": shadow_hash_match,
    }
    certificate_hash = stable_hash(payload)
    return ECLPRTPCertificate(**payload, certificate_hash=certificate_hash)


def demo_event(*, exact: bool = False, closure_tolerance: float = 0.005) -> ECLPRTPEvent:
    """Create a deterministic demonstration event.

    The non-exact demo perturbs one hexadecimal character. It passes only when
    the explicitly supplied closure tolerance admits the remaining open residue.
    """
    root = ECLRoot(
        event_id="ECL-DEMO-0001",
        payload_hash=stable_hash(
            {"file": "example_proof.txt", "claim": "recognized transition proof", "version": 1}
        ),
    )
    template = ECLTemplate(
        name="append_event",
        previous_state_hash=stable_hash({"genesis": True}),
    )
    phase = ECLPhase(
        timestamp=0.0,
        context_hash=stable_hash({"repo": "ECL public research preview"}),
        nonce="demo_nonce_001",
    )
    expected = expected_transition_hash(root, template, phase)
    observed = expected if exact else expected[:-1] + ("0" if expected[-1] != "0" else "1")
    return ECLPRTPEvent(
        root=root,
        template=template,
        phase=phase,
        observed_state_hash=observed,
        seam_policy=ECLSeamPolicy(closure_tolerance=closure_tolerance),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a public ECL PRTP demonstration certificate")
    parser.add_argument("--output", type=Path, default=Path("outputs/prtp-demo.json"))
    parser.add_argument("--exact", action="store_true", help="Use an exact expected-state hash")
    parser.add_argument("--closure-tolerance", type=float, default=0.005)
    args = parser.parse_args()

    certificate = certify_event(
        demo_event(exact=args.exact, closure_tolerance=args.closure_tolerance)
    ).as_dict()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(certificate, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(certificate, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
