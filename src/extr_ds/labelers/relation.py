from abc import ABC, abstractmethod
from typing import List, Tuple, DefaultDict, Set
from collections import defaultdict
from extr import Relation, Entity
from extr.entities import AbstractEntityExtractor, \
                          EntityAnnotator
from extr.relations import RelationExtractor, RelationAnnotator
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

    @property
    def entity_labels(self) -> Set[str]:
        return self._entity_labels

    def filter_entities(self, entities: List[Entity]) -> List[Entity]:
        return Query(entities) \
            .filter(lambda entity: entity.label in self.entity_labels) \
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

class RelationLabeler(ABC):
    def __init__(self,
                 relation_annotator = RelationAnnotator()):
        self._relation_annotator = relation_annotator

    @abstractmethod
    def label(self, text: str, entities: List[Entity]) -> List[RelationLabel]:
        pass

    def create_relation_labels(self, text: str, relations: List[Relation]) -> List[RelationLabel]:
        relation_labels: List[RelationLabel] = []
        for relation in relations:
            relation_labels.append(
                RelationLabel(
                    self._relation_annotator.annotate(
                        text,
                        relation
                    ),
                    relation=relation
                )
            )

        return relation_labels

class BaseRelationLabeler(RelationLabeler):
    def __init__(self,
                 relation_formats: List[Tuple[str, str, str]],
                 relation_annotator = RelationAnnotator()):
        super().__init__(relation_annotator)
        self._relation_builder = RelationBuilder(relation_formats)

    @property
    def supported_entity_labels(self) -> Set[str]:
        return self._relation_builder.entity_labels

    def label(self, text: str, entities: List[Entity]) -> List[RelationLabel]:
        relations = self._relation_builder.create_relations(entities)
        return self.create_relation_labels(
            text,
            relations
        )

class RuleBasedRelationLabeler(RelationLabeler):
    def __init__(self,
                 relation_extractor: RelationExtractor,
                 relation_annotator = RelationAnnotator()):
        super().__init__(relation_annotator)
        self._entity_annotator = EntityAnnotator()
        self._relation_extractor = relation_extractor

    def label(self, text: str, entities: List[Entity]) -> List[RelationLabel]:
        relations = self._relation_extractor.extract(
            self._entity_annotator.annotate(text, entities)
        )

        return self.create_relation_labels(
            text,
            relations
        )

class RelationClassification:
    def __init__(self,
                 entity_extractor: AbstractEntityExtractor,
                 base_labeler: BaseRelationLabeler,
                 relation_labelers: List[RelationLabeler]):
        self._entity_extractor = entity_extractor
        self._base_labeler = base_labeler
        self._relation_labelers: List[RelationLabeler] = [self._base_labeler] + relation_labelers

    def label(self, text: str) -> List[RelationLabel]:
        entities = []
        for i, entity in enumerate(self._entity_extractor.get_entities(text)):
            entity.identifier = i

            if entity.label in self._base_labeler.supported_entity_labels:
                entities.append(entity)

        relation_labels = {}
        for labeler in self._relation_labelers:
            for relation_label in labeler.label(text, entities):
                relation_labels[relation_label.relation.key] = relation_label

        return list(relation_labels.values())
