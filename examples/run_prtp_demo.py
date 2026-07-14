import json

from ecl.prtp import certify_event, demo_event


certificate = certify_event(demo_event()).as_dict()
print(json.dumps(certificate, indent=2, sort_keys=True))
