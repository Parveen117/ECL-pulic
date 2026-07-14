import json

from ecl.closure_engine import certify, unit_circle_trajectory


samples = unit_circle_trajectory(radial_bias=0.01, phase_bias=0.01)
certificate = certify(samples)
print(json.dumps(certificate.as_dict(), indent=2, sort_keys=True))
