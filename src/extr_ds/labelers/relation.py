from collections import defaultdict
from typing import Callable, List, Tuple, DefaultDict
from extr import Relation, Entity
from extr.entities import EntityExtractor, \
                          EntityAnnotator
from extr.relations import RelationExtractor, RelationAnnotator
from extr.tokenizers import tokenizer
from extr.utils import Query
from ..models import RelationLabel


class RelationBuilder:
    def __init__(self, relation_formats: List[Tuple[str, str, str]]):
        self._relation_formats = relation_formats

        self._entity_labels = set()
        for e1, e2, _ in relation_formats:
            self._entity_labels.add(e1)
            self._entity_labels.add(e2)

        self._relation_annotator = RelationAnnotator()

    def filter_entities(self, entities: List[Entity]) -> List[Entity]:
        return Query(entities) \
            .filter(lambda entity: entity.label in self._entity_labels) \
            .tolist()

    def create_relations(self, entities: List[Entity]) -> List[Relation]:
        entity_mapping: DefaultDict[str, List[str]] = defaultdict(list)
        for entity in entities:
            entity_mapping[entity.label].append(entity)

        relations: List[Relation] = []
        for e1, e2, default_label in self._relation_formats:
            for e1_entity in entity_mapping[e1]:
                for e2_entity in entity_mapping[e2]:
                    relation = Relation(
                        default_label,
                        e1_entity,
                        e2_entity
                    )

                    relations.append(relation)

        return relations

    def create_relation_labels(self, text: str, relations: List[Relation], offset: int = 0) -> List[RelationLabel]:
        relation_labels: List[RelationLabel] = []
        for relation in relations:
            relation_labels.append(
                RelationLabel(
                    self._relation_annotator.annotate(
                        text,
                        relation,
                        offset
                    ).strip(),
                    relation=relation
                )
            )

        return relation_labels

class RelationClassification:
    def __init__(self,
                 sentence_tokenizer: Callable[[str], List[List[str]]],
                 entity_extractor: EntityExtractor,
                 relation_extractor: RelationExtractor,
                 no_relations: List[Tuple[str, str, str]],
                 relation_annotator = RelationAnnotator()):
        self._sentence_tokenizer = sentence_tokenizer
        self._entity_extractor = entity_extractor
        self._relation_extractor = relation_extractor
        self._relation_builder = RelationBuilder(no_relations)
        self._entity_annotator = EntityAnnotator()
        self._relation_annotator = relation_annotator

    def label(self, text: str) -> List[RelationLabel]:
        found_entities = self._relation_builder.filter_entities(
            self._entity_extractor.get_entities(text)
        )

        found_relations = self._relation_extractor.extract(
            self._entity_annotator.annotate(text, found_entities)
        )

        relation_labels: List[RelationLabel] = []
        for token_group in tokenizer(text, self._sentence_tokenizer(text)):
            relations = self._relation_builder.create_relations(
                list(token_group.find_entities(found_entities))
            )

            relation_mapping = Query(relations) \
                .todict(lambda r: r.create_key(r.e1, r.e2))

            for relation in token_group.find_relations(found_relations):
                relation_mapping[relation.key] = relation

            relation_labels.extend(
                self._relation_builder.create_relation_labels(
                    token_group.sentence,
                    list(relation_mapping.values()),
                    offset=token_group.location.start
                )
            )

        return relation_labels
