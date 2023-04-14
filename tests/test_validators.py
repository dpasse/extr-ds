import os
import sys

sys.path.insert(0, os.path.join('../src'))

from extr_ds.validators import check_for_differences, DifferenceTypes


def test_check_for_differences_should_return_missing_s2_at_index_1():
    differences = check_for_differences(
        ['B-PERSON', 'I-PERSON', 'O', 'O'],
        ['B-PERSON', 'O', 'O', 'O']
    )

    assert differences.has_diffs

    assert len(differences.diffs_between_labels) == 1

    difference = differences.diffs_between_labels[0]

    assert difference.diff_type == DifferenceTypes.S2_MISSING
    assert difference.index == 1

def test_check_for_differences_should_return_missing_s1_at_index_1():
    differences = check_for_differences(
        ['B-PERSON', 'O', 'O', 'O'],
        ['B-PERSON', 'I-PERSON', 'O', 'O']
    )

    assert differences.has_diffs

    assert len(differences.diffs_between_labels) == 1

    difference = differences.diffs_between_labels[0]

    assert difference.diff_type == DifferenceTypes.S1_MISSING
    assert difference.index == 1

def test_check_for_differences_should_return_mismatch_when_both_are_labelled():
    differences = check_for_differences(
        ['B-PERSON', 'I-PERSON', 'O', 'O'],
        ['B-PERSON', 'B-POSITION', 'O', 'O']
    )

    assert differences.has_diffs

    assert len(differences.diffs_between_labels) == 1

    difference = differences.diffs_between_labels[0]

    assert difference.diff_type == DifferenceTypes.MISMATCH
    assert difference.index == 1

def test_check_for_differences_should_return_false_when_no_diffs_exist():
    differences = check_for_differences(
        ['B-PERSON', 'I-PERSON', 'O', 'O'],
        ['B-PERSON', 'I-PERSON', 'O', 'O']
    )

    assert not differences.has_diffs
