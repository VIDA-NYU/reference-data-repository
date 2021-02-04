# This file is part of the Reference Data Repository (refdata).
#
# Copyright (C) 2021 New York University.
#
# refdata is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Unit tests for the dataset handle."""

import pytest

from refdata.dataset.base import DatasetHandle
from refdata.db import local_time

import refdata.error as err


def test_format_error():
    """Ensure that the proper error is raised when initializing a dataset
    handle with an invalid format identifier.
    """
    doc = {
        'id': '0000',
        'url': 'countries.json',
        "checksum": "889c264f2ac4629b4998aa8b8b1d4de45890c39c10e24cfd8a017e9924e805c7",
        "schema": [{"id": "name"}, {"id": "alpha2Code"}],
        "format": {
            "type": "unknown",
            "parameters": {}
        }
    }
    with pytest.raises(err.InvalidFormatError):
        DatasetHandle(
            descriptor=doc,
            package_name='test',
            package_version='0',
            created_at=local_time(),
            datafile='/dev/null'
        )
