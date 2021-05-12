# This file is part of the Reference Data Repository (refdata).
#
# Copyright (C) 2021 New York University.
#
# refdata is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Unit tests for the repository index loader."""

import os
import pytest

from refdata.repo.loader import DictLoader, FileLoader, UrlLoader
from refdata.repo.loader import FORMAT_JSON, FORMAT_YAML, get_file_format


"""Path to index files in the local test file directory."""
DIR = os.path.dirname(os.path.realpath(__file__))
DATA_DIR = os.path.join(DIR, '../.files')
JSON_FILE = os.path.join(DATA_DIR, 'index.json')
YAML_FILE = os.path.join(DATA_DIR, 'index.yaml')

"""Mocked Urls."""
JSON_URL = 'http://index.json'
YAML_URL = 'http://index.yaml'


def test_dictionary_loader():
    """Test the dictionary index loader."""
    doc = {'datasets': []}
    assert DictLoader(doc=doc).load() == doc


@pytest.mark.parametrize(
    'filename,ftype',
    [(YAML_FILE, None), (YAML_FILE, FORMAT_YAML), (JSON_FILE, None), (JSON_FILE, FORMAT_JSON)]
)
def test_file_loader(filename, ftype):
    """Test loading the repository index from files in different formats."""
    doc = FileLoader(filename=filename, ftype=ftype).load()
    assert len(doc['datasets']) == 3


@pytest.mark.parametrize(
    'ftype,filename,result',
    [
        (FORMAT_JSON, 'index.yaml', FORMAT_JSON),
        (FORMAT_YAML, 'index.json', FORMAT_YAML),
        (None, 'index.json', FORMAT_JSON),
        (None, 'index.yml', FORMAT_YAML),
        (None, 'index.json.yaml', FORMAT_YAML),
        (None, 'index_json_yaml', FORMAT_JSON)
    ]
)
def test_guess_file_format(ftype, filename, result):
    """Test various cases for guessing the index file format."""
    assert get_file_format(ftype=ftype, filename=filename) == result


def test_invalid_file_format():
    """Test error case where an invalid file format identifier is given."""
    with pytest.raises(ValueError):
        get_file_format(ftype='unknown', filename='index.json')


@pytest.mark.parametrize(
    'url,ftype',
    [(YAML_URL, None), (YAML_URL, FORMAT_YAML), (JSON_URL, None), (JSON_URL, FORMAT_JSON)]
)
def test_url_loader(url, ftype, mock_response):
    """Test loading the repository index from a Url in different formats."""
    doc = UrlLoader(url=url, ftype=ftype).load()
    assert len(doc['datasets']) == 3
