from typing import Callable, Dict, List, Tuple
from extr import EntityExtractor, \
                 EntityAnnotator, \
                 RelationExtractor, \
                 Relation, \
                 Entity

from ..models import RelationLabel
from ..tokenizer import tokenizer

class RelationClassification:
    def __init__(self,
                 sentence_tokenizer: Callable[[str], List[List[str]]],
                 entity_extractor: EntityExtractor,
                 relation_extractor: RelationExtractor,
                 no_relations: List[Tuple[str, str, str]]):
        self._sentence_tokenizer = sentence_tokenizer
        self._entity_extractor = entity_extractor
        self._entity_annotator = EntityAnnotator()
        self._relation_extractor = relation_extractor
        self._no_relations = no_relations

    def label(self, text: str) -> List[RelationLabel]:
        entities = self._entity_extractor.get_entities(text)
        annotations = self._entity_annotator.annotate(text, entities)
        found_relations = self._relation_extractor.extract(annotations)

        relation_labels = []

        token_groups = tokenizer(text, self._sentence_tokenizer(text))
        for token_group in token_groups:
            relation_mapping: Dict[str, Relation]= {}
            entities_in_sentence: List[Entity] = list(
                filter(token_group.contains, entities)
            )

            for entity1_label, entity2_label, label in self._no_relations:
                e2s_in_sentence: List[Entity] = list(
                    filter(
                        lambda entity: entity.label == entity2_label,
                        entities_in_sentence
                    )
                )

                for e1 in filter(
                    lambda entity: entity.label == entity1_label,
                    entities_in_sentence
                ):
                    for e2 in e2s_in_sentence:
                        key = f'{e1.identifier}_{e2.identifier}'
                        relation_mapping[key] = Relation(
                            label,
                            e1,
                            e2
                        )

                for relation in filter(
                    lambda relation: (
                        token_group.contains(relation.e1) and \
                        token_group.contains(relation.e2)
                    ),
                    found_relations
                ):
                    e1 = relation.e1
                    e2 = relation.e2
                    key = f'{e1.identifier}_{e2.identifier}'
                    relation_mapping[key] = relation

            offset = token_group.location.start
            for relation in relation_mapping.values():
                sentence = token_group.sentence[:]

                e1_start = relation.e1.location.start - offset
                e1_end = relation.e1.location.end - offset

                e2_start = relation.e2.location.start - offset
                e2_end = relation.e2.location.end - offset

                if e1.location.start < e2.location.start:
                    sentence = sentence[:e1_start] + \
                        f'<e1>{e1.text}</e1>' + \
                        sentence[e1_end:e2_start] + \
                        f'<e2>{e2.text}</e2>' + \
                        sentence[e2_end:]
                else:
                    sentence = sentence[:e2_start] + \
                        f'<e2>{e2.text}</e2>' + \
                        sentence[e2_end:e1_start] + \
                        f'<e1>{e1.text}</e1>' + \
                        sentence[e1_end:]

                relation_labels.append(
                    RelationLabel(sentence.strip(), relation.label)
                )

        return relation_labels
