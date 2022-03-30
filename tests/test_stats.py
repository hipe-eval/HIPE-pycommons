import pytest

from hipe_commons.stats import describe_dataset

# Todo @matteo
@pytest.mark.skip(reason='No test, todo ')
def test_describe_dataset(ajmc_en_sample_path, ajmc_de_sample_path):
    print(describe_dataset(file_path=ajmc_en_sample_path))
    print(describe_dataset(file_path=ajmc_de_sample_path))