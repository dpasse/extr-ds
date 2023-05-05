# extr-ds
> Library to programmatically build labeled datasets for Named-Entity Recognition (NER) and Relation Extraction (RE) Machine Learning tasks.

<br />

## Install

```
pip install extr-ds
```

## Command Line

see [Instructions](https://medium.com/@pasdan/building-custom-named-entity-recognition-models-e4d8d95804e) on how to use the command line utility to manage your project.

### 1. Init Project
```
extr-ds --init
```

### 2. Split and Annotate
```
extr-ds --split
```

### 3.a Annotate Entities or Relations Again?
```
extr-ds --annotate -ents
extr-ds --annotate -rels
```

### 3.b Change Relation Extraction Label
```
extr-ds --relate -label NO_RELATION=5,7,9
```

### 3.b Remove Relation Extraction Instance
```
extr-ds --relate -delete 5,6,7
```

### 4. Save
```
extr-ds --save -ents
extr-ds --save -rels
```

## API

## Example

```python
text = 'Ted Johnson is a pitcher. Ted went to my school.'
```

### 1. Label Entities for Named-Entity Recognition Task (NER)

```python
from extr import RegEx, RegExLabel
from extr.entities import EntityExtactor
from extr_ds.labelers import IOB

entity_extractor = EntityExtactor([
    RegExLabel('PERSON', [
        RegEx([r'(ted\s+johnson|ted)'], re.IGNORECASE)
    ]),
    RegExLabel('POSITION', [
        RegEx([r'pitcher'], re.IGNORECASE)
    ]),
])

sentence_tokenizer = ## 3rd party tokenizer ##
labels = IOB(sentence_tokenizer, entity_extractor).label(text)

## labels ==  [
##     <Label tokens=..., labels=['B-PERSON', 'I-PERSON', 'O', 'O', 'B-POSITION', 'O']>,
##     <Label tokens=..., labels=['B-PERSON', 'O', 'O', 'O', 'O', 'O']>
## ]
```

### 2. Annotate for Relation Extraction Task (RE)

```python
from extr.entities import EntityExtractor
from extr.relations import RegExRelationLabelBuilder, \
                           RelationExtractor
from extr_ds.labelers import RelationClassification

person_to_position_relationship = RegExRelationLabelBuilder('is_a') \
    .add_e1_to_e2(
        'PERSON',
        [
            r'\s+is\s+a\s+',
        ],
        'POSITION'
    ) \
    .build()

labeler = RelationClassification(
    sentence_tokenizer,
    EntityExtractor([
        RegExLabel('PERSON', [
            RegEx([r'(ted johnson|bob)'], re.IGNORECASE)
        ]),
        RegExLabel('POSITION', [
            RegEx([r'pitcher'], re.IGNORECASE)
        ]),
    ]),
    RelationExtractor([person_to_position_relationship]),
    [('PERSON', 'POSITION', 'NO_RELATION')],
)

labels = labeler.label(text)

## labels == [
##    <RelationLabel sentence="<e1>Ted Johnson</e1> is a <e2>pitcher</e2>." label="is_a">
## ]
```

### 3. Find and define the type of difference between labels

```python
from extr_ds.validators import check_for_differences

differences_in_labels = check_for_differences(
    ['B-PERSON', 'I-PERSON', 'O', 'O', 'B-POSITION', 'O'],
    ['B-PERSON', 'O', 'O', 'O', 'B-POSITION', 'O']
)

## differences_in_labels.has_diffs == True
## differences_in_labels.diffs_between_labels == [
##      <Difference index=1, diff_type=DifferenceTypes.S2_MISSING>
## ]

differences_in_labels = check_for_differences(
    ['B-PERSON', 'I-PERSON', 'O', 'O', 'B-POSITION', 'O'],
    ['B-PERSON', 'B-PERSON', 'O', 'O', 'B-POSITION', 'O']
)

## differences_in_labels.has_diffs == True
## differences_in_labels.diffs_between_labels == [
##      <Difference index=1, diff_type=DifferenceTypes.MISMATCH>
## ]
```
