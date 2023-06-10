from typing import List


class InferenceResult:
    def __init__(self, labels: List[str], confidences: List[float], weight: float = 1.0) -> None:
        assert len(labels) == len(confidences)

        self._labels = labels
        self._confidences = confidences
        self._weight = weight

    @property
    def labels(self) -> List[str]:
        return self._labels

    @property
    def confidences(self) -> List[float]:
        return self._confidences

    @property
    def weight(self) -> float:
        return self._weight

    @property
    def len(self) -> int:
        assert len(self.labels) == len(self.confidences)

        return len(self.labels)
