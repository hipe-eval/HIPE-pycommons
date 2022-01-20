import ipdb
from hipe_commons.helpers.tsv import parse_tsv, HipeDocument

def test_parse_tsv(ajmc_en_sample_path):

    docs = parse_tsv(ajmc_en_sample_path)

    assert len(docs) > 0
    assert all([isinstance(doc, HipeDocument) for doc in docs])

    #ipdb.set_trace()