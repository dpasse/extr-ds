from typing import List, Generator
from .models import Token, TokenGroup
from extr import Location


def tokenizer(text: str, sentences: Generator[List[TokenGroup], None, None]) -> Generator[List[TokenGroup], None, None]:
    offset = 0
    cache = text[:]
    for sentence in sentences:

        sentence_start = offset

        counter = 0
        tokens_in_sentence = []
        for term in sentence:
            start = cache.find(term)
            end = start + len(term)

            actual_term = cache[start:end]
            assert actual_term == term, f'mismatch("{actual_term}", "{term}")'
            
            tokens_in_sentence.append(
                Token(term, Location(offset + start, offset + end), counter)
            )

            cache = cache[end:]
            offset += end
            counter += 1
        
        yield TokenGroup(Location(sentence_start, offset), tokens_in_sentence)
