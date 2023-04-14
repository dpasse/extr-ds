# extr-ds
> Library to quickly build basic datasets for Named Entity Recognition (NER) and Relation Extraction (RE) Machine Learning tasks.

<br />

## Install

```
pip install extr-ds
```

## Example

```python
text = 'Ted Johnson is a pitcher. Ted went to my school.'
```

### 1. Label Entities for Named-Entity Recognition Task (NER)

```python
from extr import RegEx, RegExLabel, EntityExtactor
from extr_ds import IOB

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

### 2. Find and define the type of difference between labels

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
