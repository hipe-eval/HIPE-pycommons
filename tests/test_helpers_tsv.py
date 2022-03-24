import os
from hipe_commons.helpers.tsv import parse_tsv, HipeDocument

def test_parse_tsv_from_file(ajmc_en_sample_path):

    docs = parse_tsv(file_path=ajmc_en_sample_path)

    assert len(docs) > 0
    assert all([isinstance(doc, HipeDocument) for doc in docs])

def test_parse_tsv_from_url():
    
    tsv_file_url = os.path.join(
        "https://raw.githubusercontent.com/impresso/CLEF-HIPE-2020-eval/",
        "master/data/release/v1.3/fr/HIPE-data-v1.3-test-fr.tsv"
    )

    docs = parse_tsv(file_url=tsv_file_url)

    assert len(docs) > 0
    assert all([isinstance(doc, HipeDocument) for doc in docs])