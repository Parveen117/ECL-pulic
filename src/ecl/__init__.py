"""ECL public research package."""

from .closure_engine import (
    ClosureCertificate,
    ClosureErrorVector,
    ClosureMetrics,
    ClosureSample,
    ClosureThresholds,
    ComplexPoint,
    certify,
    compute_metrics,
    unit_circle_trajectory,
)
from .native_ledger import NativeLedgerConfig, build_report, sha256_canonical
from .prtp import (
    ECLPhase,
    ECLPRTPEvent,
    ECLRoot,
    ECLSeamPolicy,
    ECLTemplate,
    certify_event,
)

__all__ = [
    "ClosureCertificate",
    "ClosureErrorVector",
    "ClosureMetrics",
    "ClosureSample",
    "ClosureThresholds",
    "ComplexPoint",
    "certify",
    "compute_metrics",
    "unit_circle_trajectory",
    "NativeLedgerConfig",
    "build_report",
    "sha256_canonical",
    "ECLRoot",
    "ECLTemplate",
    "ECLPhase",
    "ECLSeamPolicy",
    "ECLPRTPEvent",
    "certify_event",
]

__version__ = "0.2.0"
