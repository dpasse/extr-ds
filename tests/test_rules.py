import os
import sys

sys.path.insert(0, os.path.join('../src'))

from extr_ds.rules import Majority, InferenceResult


def test_majority_1():
    majority = Majority()

    instances = [
        InferenceResult(['A', 'A', '', 'B'], [.9, .9, .9, .9], 1.0),
        InferenceResult(['A', '', '', 'B'], [.9, .9, .9, .9], 0.5),
        InferenceResult(['A', 'A', '', ''], [.9, .9, .9, .9], 1.0),
    ]

    observation = majority.merge(instances)

    assert observation == ['A', 'A', '', 'B']

def test_majority_2():
    majority = Majority()

    instances = [
        InferenceResult(['A', 'A', '', 'B'], [.9, .9, .9, .9], 1.0),
        InferenceResult(['A', '', '', 'B'], [.9, .62, .9, .9], 1.0),
        InferenceResult(['A', 'A', '', ''], [.9, .9, .9, .51], 1.0),
        InferenceResult(['A', '', '', ''], [.9, .72, .9, .9], 1.0),
    ]

    observation = majority.merge(instances)

    assert observation == ['A', 'A', '', 'B']
