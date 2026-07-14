import unittest

from ecl.closure_engine import (
    ClosureThresholds,
    certify,
    unit_circle_trajectory,
    winding_number,
)


class ClosureEngineTests(unittest.TestCase):
    def test_exact_trajectory_commits(self) -> None:
        certificate = certify(unit_circle_trajectory())
        self.assertEqual(certificate.classification, "COMMIT")
        self.assertTrue(certificate.closure_before_commit)
        self.assertEqual(certificate.metrics["topology_mismatch"], 0.0)

    def test_bounded_error_commits(self) -> None:
        certificate = certify(
            unit_circle_trajectory(radial_bias=0.01, phase_bias=0.01)
        )
        self.assertEqual(certificate.classification, "COMMIT")

    def test_borderline_continuous_error_holds(self) -> None:
        thresholds = ClosureThresholds(max_normalized_defect=0.05)
        certificate = certify(unit_circle_trajectory(radial_bias=0.06), thresholds)
        self.assertEqual(certificate.classification, "HOLD")
        self.assertFalse(certificate.closure_before_commit)

    def test_seam_rupture_rejects(self) -> None:
        certificate = certify(
            unit_circle_trajectory(rupture_index=32, rupture_size=0.25)
        )
        self.assertEqual(certificate.classification, "REJECT")
        self.assertFalse(certificate.component_pass["rupture_supremum"])

    def test_orientation_mismatch_rejects(self) -> None:
        certificate = certify(
            unit_circle_trajectory(orientation_flip_index=32)
        )
        self.assertEqual(certificate.classification, "REJECT")
        self.assertGreater(certificate.metrics["orientation_mismatch_rate"], 0.0)

    def test_winding_mismatch_rejects(self) -> None:
        samples = unit_circle_trajectory(turns=1.0)
        altered = [
            type(sample)(
                coordinate=sample.coordinate,
                expected=sample.expected,
                observed=sample.observed,
                expected_phase=sample.expected_phase,
                observed_phase=sample.observed_phase * 2.0,
                expected_orientation=sample.expected_orientation,
                observed_orientation=sample.observed_orientation,
            )
            for sample in samples
        ]
        certificate = certify(altered)
        self.assertEqual(certificate.classification, "REJECT")
        self.assertEqual(certificate.metrics["winding_mismatch"], 1)

    def test_certificate_is_deterministic(self) -> None:
        samples = unit_circle_trajectory(radial_bias=0.01, phase_bias=0.01)
        first = certify(samples)
        second = certify(samples)
        self.assertEqual(first.certificate_hash, second.certificate_hash)
        self.assertEqual(first, second)

    def test_winding_number(self) -> None:
        phases = [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.283185307179586]
        self.assertEqual(winding_number(phases), 1)


if __name__ == "__main__":
    unittest.main()
