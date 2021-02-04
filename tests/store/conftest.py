# This file is part of the Reference Data Repository (refdata).
#
# Copyright (C) 2021 New York University.
#
# refdata is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Fixtures for local datastore unit tests."""

import pytest

from refdata.repo.loader import UrlLoader
from refdata.store.base import LocalStore
from refdata.version import __version__


@pytest.fixture
def store(mock_response, tmpdir):
    return LocalStore(
        package_name='refdata_test',
        package_version=__version__,
        basedir=tmpdir,
        loader=UrlLoader(url='index.json'),
        auto_download=False
    )
