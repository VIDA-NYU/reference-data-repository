# This file is part of the Reference Data Repository (refdata).
#
# Copyright (C) 2021 New York University.
#
# refdata is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Unit tests for the dataset handle."""

import pytest

from refdata.store.dataset import DatasetHandle

import refdata.error as err


def test_format_error():
    """Ensure that the proper error is raised when initializing a dataset
    handle with an invalid format identifier.
    """
    doc = {
        'id': '0000',
        'url': 'countries.json',
        "checksum": "403126a5fb62f83b2ff65fb2bd7a3e87d57c0041cc086da813134035e7b0157c",
        "schema": [{"id": "name"}, {"id": "alpha2Code"}],
        "format": {
            "type": "unknown",
            "parameters": {}
        }
    }
    with pytest.raises(err.InvalidFormatError):
        DatasetHandle(doc=doc, datafile='/dev/null')
