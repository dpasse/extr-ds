from typing import List, Callable
from extr.entities import AbstractEntityExtractor
from .majority import InferenceResult
from ..labelers.iob import IOB


def create_static_inference_result(labels: List[str], weight=1, has_label=.99, has_no_label=.90) -> InferenceResult:
    return InferenceResult(
        labels=labels,
        confidences=[
            has_no_label if label == 'O' else has_label
            for label in labels
        ],
        weight=weight
    )

class StaticUnit():
    def __init__(self, tokenize: Callable[[str], List[str]], extractor: AbstractEntityExtractor):
        self._iob = IOB(tokenize, extractor)

    def __call__(self, text):
        return create_static_inference_result(
            self._iob.label(text).labels
        )
