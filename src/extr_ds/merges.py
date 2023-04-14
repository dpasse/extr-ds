from typing import List
from dataclasses import dataclass


@dataclass
class Differences:
    sentence_labels_1: List[str]
    sentence_labels_2: List[str]
    diffs_between_labels: List[int]

    @property
    def has_diffs(self) -> bool:
        return len(self.diffs_between_labels) > 0

def check_for_differences(sentence_labels_1: List[str], sentence_labels_2: List[str]) -> Differences:
    assert len(sentence_labels_1) == len(sentence_labels_2)

    diffs = []
    for i, label_1 in enumerate(sentence_labels_1):
        if label_1 != sentence_labels_2[i]:
            diffs.append(i)

    return Differences(
        sentence_labels_1,
        sentence_labels_2,
        diffs
    )
