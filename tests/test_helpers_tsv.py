import os
import sys

import pip
import pytest

from hipe_commons.helpers.tsv import parse_tsv, HipeDocument, tsv_to_dataframe, tsv_to_lists, tsv_to_torch_dataset, \
    get_unique_labels, tsv_to_huggingface_dataset


def test_parse_tsv_from_file(sample_tsv_path):
    docs = parse_tsv(file_path=sample_tsv_path)

    assert len(docs) > 0
    assert all([isinstance(doc, HipeDocument) for doc in docs])


def test_parse_tsv_from_url(sample_tsv_url):
    docs = parse_tsv(file_url=sample_tsv_url)

    assert len(docs) > 0
    assert all([isinstance(doc, HipeDocument) for doc in docs])


def test_tsv_to_dataframe(sample_tsv_url, sample_tsv_string):
    df = tsv_to_dataframe(url=sample_tsv_url)
    # Make sure there are as many annotation row in the file as there are rows in the df
    assert len(df) + 1 == len(
        [1 for line in sample_tsv_string.split('\n') if (not line.startswith('#')) and line.strip('\n')])


def test_tsv_to_lists(sample_tsv_url, sample_tsv_string, sample_label):
    d = tsv_to_lists([sample_label], url=sample_tsv_url)
    segmentation_flag_count = sum([1 for l in sample_tsv_string.split('\n') if 'EndOf' in l])
    assert len(d['texts']) in [segmentation_flag_count,
                               segmentation_flag_count + 1]  # In case the file doesn't end with flag.


@pytest.mark.skipif(pip.main(['show', 'torch']) != 0 or pip.main(['show', 'transformers']) != 0,
                    reason="""`torch` or `transformers` not installed, skipping test.""")
def test_tsv_to_torch_dataset(sample_tsv_url, sample_label):
    from transformers import AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained('bert-base-cased')
    data_lists = tsv_to_lists([sample_label], url=sample_tsv_url)
    unique_labels = get_unique_labels(label_list=[l for l_list in data_lists[sample_label] for l in l_list])
    labels_to_ids = {l: i for i, l in enumerate(unique_labels)}

    dataset = tsv_to_torch_dataset(sample_label, labels_to_ids, tokenizer, url=sample_tsv_url)

    assert len(data_lists['texts']) == len(dataset.labels)


@pytest.mark.skipif(pip.main(['show', 'datasets']) != 0,
                    reason="""`datasets` not installed, skipping test.""")
def test_tsv_to_torch_dataset(sample_tsv_url, sample_label):
    data_lists = tsv_to_lists([sample_label], url=sample_tsv_url)
    dataset = tsv_to_huggingface_dataset([sample_label], url=sample_tsv_url)
    assert all([a == b['texts'] for a, b in zip(data_lists['texts'], dataset)])
