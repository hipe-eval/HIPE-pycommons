import os
import sys

import pip
import pytest

from hipe_commons.helpers.tsv import parse_tsv, HipeDocument, tsv_to_dataframe, tsv_to_segmented_lists, tsv_to_torch_dataset, \
    get_unique_labels, tsv_to_huggingface_dataset, tsv_to_dict


def test_parse_tsv_from_file(sample_tsv_path_v1):
    docs = parse_tsv(hipe_format_version="v1", file_path=sample_tsv_path_v1)

    assert len(docs) > 0
    assert all([isinstance(doc, HipeDocument) for doc in docs])


def test_parse_tsv_from_file_v2(sample_tsv_path_v2):
    docs = parse_tsv(hipe_format_version="v2", file_path=sample_tsv_path_v2)

    assert len(docs) > 0
    assert all([isinstance(doc, HipeDocument) for doc in docs])


def test_parse_tsv_from_url(sample_tsv_url):
    docs = parse_tsv(file_url=sample_tsv_url)

    assert len(docs) > 0
    assert all([isinstance(doc, HipeDocument) for doc in docs])


def test_tsv_to_dataframe(sample_tsv_url, sample_tsv_string):
    df = tsv_to_dataframe(url=sample_tsv_url)
    tsv_lines = [line for line in sample_tsv_string.split('\n') if (not line.startswith('#')) and line.strip('\n')]
    
    # Make sure there are as many annotation row in the file as there are rows in the df
    # NOTE: the `+1` is needed as in HIPE format v1 the TSV header
    # is not commented out and is therefore pickped up in `tsv_lines` above
    assert len(df) + 1 == len(tsv_lines)


def test_tsv_to_dataframe_v2(sample_tsv_path_v2):
    df = tsv_to_dataframe(path=sample_tsv_path_v2, hipe_format_version="v2")
    sample_tsv_string = open(sample_tsv_path_v2).read()
    tsv_lines = [line for line in sample_tsv_string.split('\n') if (not line.startswith('#')) and line.strip('\n')]
    
    # Make sure there are as many annotation row in the file as there are rows in the df
    # NOTE: the `+1` is *not* needed here as in HIPE format v2 the TSV header
    # is commented out and is therefore not pickped up in `tsv_lines` above
    assert len(df) == len(tsv_lines)


def test_tsv_to_lists(sample_tsv_url, sample_tsv_string, sample_label):
    d = tsv_to_segmented_lists([sample_label], url=sample_tsv_url)
    segmentation_flag_count = sum([1 for l in sample_tsv_string.split('\n') if 'EndOf' in l])
    assert len(d['texts']) in [segmentation_flag_count,
                               segmentation_flag_count + 1]  # In case the file doesn't end with flag.


def test_tsv_to_lists_v2(sample_tsv_path_v2, sample_label):
    data = tsv_to_segmented_lists([sample_label], path=sample_tsv_path_v2, hipe_format_version="v2")
    sample_tsv_string = open(sample_tsv_path_v2).read()
    segmentation_flag_count = sum([1 for l in sample_tsv_string.split('\n') if 'EndOf' in l])
    assert len(data['texts']) in [segmentation_flag_count,
                               segmentation_flag_count + 1]  # In case the file doesn't end with flag.


@pytest.mark.skipif(pip.main(['show', 'torch']) != 0 or pip.main(['show', 'transformers']) != 0,
                    reason="""`torch` or `transformers` not installed, skipping test.""")
def test_tsv_to_torch_dataset(sample_tsv_url, sample_label):
    from transformers import AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained('bert-base-cased')
    data_lists = tsv_to_segmented_lists([sample_label], url=sample_tsv_url)
    unique_labels = get_unique_labels(label_list=[l for l_list in data_lists[sample_label] for l in l_list])
    labels_to_ids = {l: i for i, l in enumerate(unique_labels)}

    dataset = tsv_to_torch_dataset(sample_label, labels_to_ids, tokenizer, url=sample_tsv_url)

    assert len(data_lists['texts']) == len(dataset.labels)


@pytest.mark.skipif(pip.main(['show', 'datasets']) != 0,
                    reason="""`datasets` not installed, skipping test.""")
def test_tsv_to_torch_dataset(sample_tsv_url, sample_label):
    data_lists = tsv_to_segmented_lists([sample_label], url=sample_tsv_url)
    dataset = tsv_to_huggingface_dataset([sample_label], url=sample_tsv_url)
    assert all([a == b['texts'] for a, b in zip(data_lists['texts'], dataset)])


def test_tsv_to_dict(sample_tsv_url, sample_tsv_string):
    dict_ = tsv_to_dict(url=sample_tsv_url, hipe_format_version="v1")
    # Make sure there are as many annotation row in the file as there are rows in the df
    file_lines = len([1 for line in sample_tsv_string.split('\n') if (not line.startswith('#')) and line.strip('\n')])
    assert all([len(dict_[k])+1 == file_lines for k in dict_.keys()])
