# This file is part of the Reference Data Repository (refdata).
#
# Copyright (C) 2021 New York University.
#
# refdata is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Fixtures for local datastore unit tests."""

import pytest

from refdata.repo import RepositoryManager, download_index
from refdata.store import LocalStore


@pytest.fixture
def store(mock_response, tmpdir):
    return LocalStore(
        basedir=tmpdir,
        repo=RepositoryManager(doc=download_index('index.json')),
        auto_download=False
    )
