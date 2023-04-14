import os
import sys

sys.path.insert(0, os.path.join('../src'))

from extr_ds.merges import check_for_differences

def test_check_for_differences_should_return_true_when_no_diffs_exist():
    differences = check_for_differences(
        ['B-PERSON', 'I-PERSON', 'O', 'O'],
        ['B-PERSON', 'O', 'O', 'O']
    )

    assert differences.has_diffs
    
    assert len(differences.diffs_between_labels) == 1
    assert differences.diffs_between_labels[0] == 1

def test_check_for_differences_should_return_false_when_no_diffs_exist():
    differences = check_for_differences(
        ['B-PERSON', 'I-PERSON', 'O', 'O'],
        ['B-PERSON', 'I-PERSON', 'O', 'O']
    )

    assert not differences.has_diffs
