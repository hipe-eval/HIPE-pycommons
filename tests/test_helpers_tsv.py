import ipdb
from hipe_commons.helpers.tsv import parse_tsv, HipeDocument

def test_parse_tsv_from_file(ajmc_en_sample_path):

    docs = parse_tsv(file_path=ajmc_en_sample_path)

    assert len(docs) > 0
    assert all([isinstance(doc, HipeDocument) for doc in docs])

# TODO
def test_parse_tsv_from_url():
    pass