import urllib
import pytest


@pytest.fixture(scope="session")
def sample_tsv_path_v1():
    # return "/Users/matteo/Documents/AjaxMultiCommentary/HIPE2022-corpus/data/release/v2.0/HIPE-2022-v2.0-ajmc-dev-en.tsv"
    #return '/Users/sven/drive/_AJAX/AjaxMultiCommentary/data/epibau/EpibauCorpus/data/release/v0.3/EpiBau-data-v0.3-test.tsv'
    return './tests/data/v1-HIPE-2022-v2.0-ajmc-dev-de.tsv'


@pytest.fixture(scope="session")
def sample_tsv_path_v2():
    # return "/Users/matteo/Documents/AjaxMultiCommentary/HIPE2022-corpus/data/release/v2.0/HIPE-2022-v2.0-ajmc-dev-en.tsv"
    #return '/Users/sven/drive/_AJAX/AjaxMultiCommentary/data/epibau/EpibauCorpus/data/release/v0.3/EpiBau-data-v0.3-test.tsv'
    return './tests/data/v2-HIPE-newsbench-v0.9.0-hipe2020-test-fr.tsv'


@pytest.fixture(scope="session")
def ajmc_en_sample_path():
    return "/Users/matteo/Documents/AjaxMultiCommentary/HIPE2022-corpus/data/release/v2.0/HIPE-2022-v2.0-ajmc-dev-en.tsv"


@pytest.fixture(scope="session")
def ajmc_de_sample_path():
    return "/Users/matteo/Documents/AjaxMultiCommentary/HIPE2022-corpus/data/release/v2.0/HIPE-2022-v2.0-ajmc-dev-de.tsv"


@pytest.fixture(scope="session")
def sample_tsv_url():
    return 'https://raw.githubusercontent.com/hipe-eval/HIPE-2022-data/main/data/v2.0/ajmc/de/HIPE-2022-v2.0-ajmc-dev-de.tsv'


@pytest.fixture(scope="session")
def sample_tsv_string():
    response = urllib.request.urlopen('https://raw.githubusercontent.com/hipe-eval/HIPE-2022-data/main/data/v2.0/ajmc/de/HIPE-2022-v2.0-ajmc-dev-de.tsv')
    return response.read().decode('utf-8')


@pytest.fixture(scope="session")
def sample_label():
    return 'NE-COARSE-LIT'


