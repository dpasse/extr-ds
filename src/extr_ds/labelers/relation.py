from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Tuple, DefaultDict, Set, Optional
from collections import defaultdict
from extr import Relation, Entity
from extr.entities import AbstractEntityExtractor, \
                          EntityAnnotator
from extr.relations import RelationExtractor, RelationAnnotator, RelationAnnotatorWithEntityType
from extr.utils import Query
from ..models import RelationLabel


class RelationBuilder:
    def __init__(self, relation_formats: List[Tuple[str, str, str]]):
        self._relation_formats = relation_formats

        self._entity_labels = set()
        for e1, e2, _ in relation_formats:
            self._entity_labels.add(e1)
            self._entity_labels.add(e2)

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
                 relation_annotator: RelationAnnotator = RelationAnnotatorWithEntityType()):
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
                 relation_builder: RelationBuilder,
                 relation_annotator: RelationAnnotator = RelationAnnotatorWithEntityType()):
        super().__init__(relation_annotator)
        self._relation_builder = relation_builder

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
                 entity_annotator = EntityAnnotator(),
                 relation_annotator: RelationAnnotator = RelationAnnotatorWithEntityType()):
        super().__init__(relation_annotator)
        self._relation_extractor = relation_extractor
        self._entity_annotator = entity_annotator

    def label(self, text: str, entities: List[Entity]) -> List[RelationLabel]:
        annotated_text = self._entity_annotator.annotate(text, entities)
        relations = self._relation_extractor.extract(annotated_text, entities)

        return self.create_relation_labels(
            text,
            relations
        )

@dataclass
class RelationClassificationResult:
    entities: List[Entity]
    relation_labels: List[RelationLabel]

    def totuple(self, exclude: Optional[List[str]] = None) -> Tuple[List[Entity], List[RelationLabel]]:
        if exclude is None:
            return (self.entities, self.relation_labels)

        labels_to_include = []
        for relation_label in self.relation_labels:
            if relation_label.label in exclude:
                continue

            labels_to_include.append(relation_label)

        return (self.entities, labels_to_include)

class RelationClassification:
    def __init__(self,
                 entity_extractor: AbstractEntityExtractor,
                 base_labeler: BaseRelationLabeler,
                 additional_relation_labelers: Optional[List[RelationLabeler]] = None):
        self._entity_extractor = entity_extractor
        self._base_labeler = base_labeler
        self._relation_labelers: List[RelationLabeler] = [self._base_labeler]
        if additional_relation_labelers:
            self._relation_labelers += additional_relation_labelers

    def label(self, text: str) -> RelationClassificationResult:
        entities = self._entity_extractor.get_entities(text)

        entities_in_relations = []
        for entity in entities:
            if entity.label in self._base_labeler.supported_entity_labels:
                entities_in_relations.append(entity)

        relation_labels = {}
        for labeler in self._relation_labelers:
            for relation_label in labeler.label(text, entities_in_relations):
                relation_labels[relation_label.relation.key] = relation_label

        return RelationClassificationResult(
            entities=entities,
            relation_labels=list(relation_labels.values())
        )
