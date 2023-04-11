import re

from extr import RegEx, RegExLabel, EntityExtractor


def test_get_entities():
    extractor = EntityExtractor([
        RegExLabel('PERSON', [
            RegEx([r'ted'], re.IGNORECASE)
        ]),
        RegExLabel('POSITION', [
            RegEx([r'pitcher'], re.IGNORECASE)
        ]),
    ])

    entities = extractor.get_entities('Ted is a Pitcher.')

    print(entities)

    assert len(entities) == 2
