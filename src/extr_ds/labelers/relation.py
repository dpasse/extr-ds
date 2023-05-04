from typing import Callable, Dict, List, Tuple
from extr import Relation, Entity, TokenGroup
from extr.entities import EntityExtractor, \
                          EntityAnnotator
from extr.relations import RelationExtractor, RelationAnnotator
from extr.tokenizers import tokenizer
from extr.utils import Query
from ..models import RelationLabel


class RelationClassification:
    def __init__(self,
                 sentence_tokenizer: Callable[[str], List[List[str]]],
                 entity_extractor: EntityExtractor,
                 relation_extractor: RelationExtractor,
                 no_relations: List[Tuple[str, str, str]]):
        self._sentence_tokenizer = sentence_tokenizer
        self._entity_extractor = entity_extractor
        self._relation_extractor = relation_extractor
        self._no_relations = no_relations

        self._entities_we_care_about = set()
        for e1, e2, _ in self._no_relations:
            self._entities_we_care_about.add(e1)
            self._entities_we_care_about.add(e2)

        self._entity_annotator = EntityAnnotator()
        self._relation_annotator = RelationAnnotator()

    def label(self, text: str) -> List[RelationLabel]:
        found_entities = Query(self._entity_extractor.get_entities(text)) \
            .filter(lambda entity: entity.label in self._entities_we_care_about) \
            .tolist()

        found_relations = self._relation_extractor.extract(
            self._entity_annotator.annotate(text, found_entities)
        )

        def get_entities_in_token_group(token_group: TokenGroup) -> List[Entity]:
            return Query(found_entities) \
                .filter(token_group.contains) \
                .tolist()

        def get_relations_in_token_group(token_group: TokenGroup) -> List[Relation]:
            return Query(found_relations) \
                .filter(lambda relation: (
                    token_group.contains(relation.e1) and \
                    token_group.contains(relation.e2)
                )) \
                .tolist()

        relation_labels: List[RelationLabel] = []
        for token_group in tokenizer(text, self._sentence_tokenizer(text)):
            relation_mapping = self._get_mappings(
                get_entities_in_token_group(token_group),
                get_relations_in_token_group(token_group)
            )

            offset = token_group.location.start
            for relation in relation_mapping.values():
                relation_labels.append(
                    RelationLabel(
                        self._relation_annotator.annotate(
                            token_group.sentence,
                            relation,
                            offset
                        ).strip(),
                        relation
                    )
                )

        return relation_labels

    def _get_mappings(self, entities_in_sentence: List[Entity], relations_in_sentence: List[Relation]) -> Dict[str, Relation]:
        def get_entities_for_label(label: str) -> List[Entity]:
            return Query(entities_in_sentence) \
                .filter(lambda e: e.label == label) \
                .tolist()

        relation_mapping: Dict[str, Relation] = {}
        for entity1_label, entity2_label, label in self._no_relations:
            e1s = get_entities_for_label(entity1_label)
            e2s = get_entities_for_label(entity2_label)
            for e1 in e1s:
                for e2 in e2s:
                    key = Relation.create_key(e1, e2)
                    relation_mapping[key] = Relation(
                        label,
                        e1,
                        e2
                    )

        for relation in relations_in_sentence:
            relation_mapping[relation.key] = relation

        return relation_mapping
