from typing import List, Union
from dataclasses import dataclass
from enum import Enum


# class syntax
class DifferenceTypes(Enum):
    NONE = 0
    MISMATCH = 1
    S1_MISSING = 2
    S2_MISSING = 3

@dataclass
class Difference:
    index: int
    diff_type: DifferenceTypes

    def __repr__(self) -> str:
        return f'<Difference index={self.index} diff_type={self.diff_type}>'

@dataclass
class Differences:
    sentence_labels_1: List[str]
    sentence_labels_2: List[str]
    diffs_between_labels: List[Difference]

    @property
    def has_diffs(self) -> bool:
        return len(self.diffs_between_labels) > 0

EMPTY_SET = ['O', 'NO-RELATION']

def check_for_differences(l1: Union[List[str], str], l2: Union[List[str], str]) -> Differences:
    def get_difference_type(label_1: str, label_2: str) -> DifferenceTypes:
        diff_type = DifferenceTypes.NONE
        if label_2 in EMPTY_SET or len(label_2) == 0:
            diff_type = DifferenceTypes.S2_MISSING
        elif label_1 in EMPTY_SET or len(label_1) == 0:
            diff_type = DifferenceTypes.S1_MISSING
        else:
            diff_type = DifferenceTypes.MISMATCH

        return diff_type

    labels_1 = [l1] if isinstance(l1, str) else l1
    labels_2 = [l2] if isinstance(l2, str) else l2

    assert len(labels_1) == len(labels_2)

    diffs_between_labels = []
    for i, [label_1, label_2] in enumerate(zip(labels_1, labels_2)):
        if label_1 != label_2:
            diff_type = get_difference_type(label_1, label_2)
            diffs_between_labels.append(Difference(i, diff_type))

    return Differences(
        labels_1,
        labels_2,
        diffs_between_labels
    )
