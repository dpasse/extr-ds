from typing import List
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

def check_for_differences(sentence_labels_1: List[str], sentence_labels_2: List[str]) -> Differences:
    assert len(sentence_labels_1) == len(sentence_labels_2)

    diffs_between_labels = []
    for i, [label_1, label_2] in enumerate(zip(sentence_labels_1, sentence_labels_2)):

        if label_1 != label_2:
            diff_type = DifferenceTypes.NONE
            if label_2 == 'O' or len(label_2) == 0:
                diff_type = DifferenceTypes.S2_MISSING
            elif label_1 == 'O' or len(label_1) == 0:
                diff_type = DifferenceTypes.S1_MISSING
            else:
                diff_type = DifferenceTypes.MISMATCH

            diffs_between_labels.append(
                Difference(i, diff_type)
            )

    return Differences(
        sentence_labels_1,
        sentence_labels_2,
        diffs_between_labels
    )
