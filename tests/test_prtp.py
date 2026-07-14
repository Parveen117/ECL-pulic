import unittest

from ecl.prtp import ECLSeamPolicy, certify_event, demo_event


class PRTPTests(unittest.TestCase):
    def test_exact_transition_passes(self) -> None:
        certificate = certify_event(demo_event(exact=True, closure_tolerance=0.0))
        self.assertTrue(certificate.shadow_hash_match)
        self.assertTrue(certificate.native_pass)
        self.assertEqual(certificate.open_residue, 0.0)

    def test_mismatch_fails_with_zero_tolerance(self) -> None:
        certificate = certify_event(demo_event(exact=False, closure_tolerance=0.0))
        self.assertFalse(certificate.shadow_hash_match)
        self.assertFalse(certificate.native_pass)
        self.assertGreater(certificate.open_residue, 0.0)

    def test_explicit_tolerance_can_admit_small_residue(self) -> None:
        certificate = certify_event(demo_event(exact=False, closure_tolerance=0.005))
        self.assertFalse(certificate.shadow_hash_match)
        self.assertTrue(certificate.native_pass)
        self.assertLessEqual(certificate.open_residue, certificate.policy["closure_tolerance"])

    def test_invalid_policy_is_rejected(self) -> None:
        event = demo_event(exact=True)
        invalid = type(event)(
            root=event.root,
            template=event.template,
            phase=event.phase,
            observed_state_hash=event.observed_state_hash,
            seam_policy=ECLSeamPolicy(compensation_strength=1.5),
        )
        with self.assertRaises(ValueError):
            certify_event(invalid)


if __name__ == "__main__":
    unittest.main()
