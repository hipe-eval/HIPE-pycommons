import os
from hipe_commons.helpers.tsv import parse_tsv, HipeDocument, tsv_to_dataframe, tsv_to_lists
import urllib


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


def test_tsv_to_dataframe():
    df = tsv_to_dataframe('data/tsv_sample.tsv')
    with open('data/tsv_sample.tsv') as f:
        # Make sure there are as many annotation row in the file as there are rows in the df
        assert len(df) + 1 == len([True for line in f.readlines() if not line.startswith('#') and line.strip('\n')])


def test_tsv_to_lists():
    segmentation_flag = 'EndOfLine'
    d = tsv_to_lists(['NE-COARSE-LIT', 'NEL-LIT'], path='data/tsv_sample.tsv', segmentation_flag=segmentation_flag)
    with open('data/tsv_sample.tsv') as f:
        segmentation_flag_count = sum([1 for l in f.readlines() if segmentation_flag in l])
        assert len(d['examples']) in [segmentation_flag_count, segmentation_flag_count+1]  # In case the file doesn't end with flag.



