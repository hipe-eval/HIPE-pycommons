from hipe_commons.stats import describe_dataset

def test_describe_dataset(ajmc_en_sample_path, ajmc_de_sample_path):
    print(describe_dataset(ajmc_en_sample_path))
    print(describe_dataset(ajmc_de_sample_path))