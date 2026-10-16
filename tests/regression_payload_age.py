"""A pair's age must account for every contributing input payload."""
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from ftypes.adaptive import _conditional_k
from ftypes.model import case_from_spec
from ftypes.semantics import enumerate_executions


class PayloadAgeBound(unittest.TestCase):
    def test_older_second_payload_requires_the_maximum(self):
        spec = json.loads((ROOT/'inputs/static/worked-safe.json').read_text(encoding='utf-8'))
        spec['zones'] = [{'name':'singleton', 'bounds':{'b_a':[0,0], 'b_b':[-2,-2],
                        'r_p':[0,0], 'r_q':[0,0]}, 'constraints':[]}]
        spec['nodes'] = [{'name':'x', 'op':'pair', 'data':['p','q'], 'gates':[],
                          'delays':{'p':[0,0], 'q':[0,0]}}]
        case = case_from_spec(spec)
        executions = list(enumerate_executions(case))
        self.assertEqual(len(executions), 1)
        readiness = {'zero':0, 'r_p':0, 'r_q':0}
        closure = case.zones[0].close()
        contributions = [_conditional_k(case, closure, p, readiness) for p in ('p','q')]
        self.assertEqual(contributions, [0,2])
        _, _, emitted, age = executions[0].outputs[0]
        self.assertEqual((emitted, age), (0,2))
        self.assertGreater(age, emitted+contributions[0])
        self.assertEqual(age, emitted+max(contributions))


if __name__ == '__main__':
    unittest.main()
