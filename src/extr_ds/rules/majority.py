from typing import List, Dict, cast, Any


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

class Majority():
    def merge(self, inference_results: List[InferenceResult]) -> List[str]:
        assert len(inference_results) > 0

        merged_instance: List[str] = []
        for index in range(0, self._get_length(inference_results)):
            merged_instance.append(
                self._get_majority(index, inference_results)
            )

        return merged_instance

    def _get_length(self, inference_results: List[InferenceResult]) -> int:
        length = inference_results[0].len
        for result in inference_results[1:]:
            assert length == result.len

        return length

    def _get_majority(self, index: int, inference_results: List[InferenceResult]) -> str:
        votes: Dict[str, Dict[str, float]] = {}
        for instance_result in inference_results:
            key = instance_result.labels[index]
            key_confidence = instance_result.confidences[index]
            if not key in votes:
                votes[key] = {'total': 0, 'weighted': 0.0}

            votes[key]['total'] += 1
            votes[key]['weighted'] += (instance_result.weight * key_confidence * 1)

        sorted_votes = [
            {
                'key': key,
                'total': items['total'],
                'weighted': items['weighted']
            }
            for key, items
            in sorted(votes.items(), key=lambda v: v[1]['total'], reverse=True)
        ]

        if len(sorted_votes) == 1:
            return cast(str, sorted_votes[0]['key'])

        vote_counts: List[Dict[str, Any]] = []
        for vote in sorted_votes:
            if len(vote_counts) == 0:
                vote_counts.append(vote)

            last_vote = vote_counts[-1]
            if last_vote['total'] == vote['total']:
                vote_counts.append(vote)

        if len(vote_counts) == 1:
            return cast(str, vote_counts[0]['key'])

        return cast(str, [
            items['key']
            for items
            in sorted(sorted_votes, key=lambda v: cast(float, v['weighted']), reverse=True)
        ][0])
