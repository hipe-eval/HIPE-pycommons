from typing import Dict
from typing import List, Dict
from .helpers.tsv import HipeDocument, parse_tsv, ENTITY_TYPES

def count_entities(docs: List[HipeDocument]) -> Dict:

    counts = {}
    
    for e_type in ENTITY_TYPES:
        for doc in docs:
            if e_type in doc.entities:
                if e_type not in counts:
                    counts[e_type] = 0
                counts[e_type] += len(doc.entities[e_type])

    return counts

def describe_dataset(path: str) -> str:

    docs = parse_tsv(path)

    desc = ""
    desc += f'\nPath of the TSV file: {path} \n'
    desc += f'Number of documents: {len(docs)} \n'
    desc += f'Number of entities: {count_entities(docs)} \n'
    return desc