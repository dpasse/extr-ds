# extr-ds
> Library to quickly build basic datasets for Named Entity Recognition (NER) and Relation Extraction (RE) Machine Learning tasks. <br /><br />Extension of the [extr]('https://github.com/dpasse/extr') library.

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
from extr-ds import IOB

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
##     ['B-PERSON', 'I-PERSON', 'O', 'O', 'B-POSITION', 'O'],
##     ['B-PERSON', 'O', 'O', 'O', 'O', 'O']
## ]
```
