# This file is part of the Reference Data Repository (refdata).
#
# Copyright (C) 2021 New York University.
#
# refdata is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Fixtures for testing the command-line interface."""

import os
import pytest

from click.testing import CliRunner

from refdata.db import DB

import refdata.config as config


@pytest.fixture
def refdata_cli(tmpdir):
    """Initialize the environment and the database for the local store."""
    basedir = os.path.abspath(str(tmpdir))
    connect_url = 'sqlite:///{}'.format(os.path.join(basedir, 'test.db'))
    DB(connect_url=connect_url).init()
    os.environ[config.ENV_BASEDIR] = basedir
    os.environ[config.ENV_URL] = connect_url
    # Make sure to reset the database.
    yield CliRunner()
    # Clear environment variables that were set for the test runner.
    del os.environ[config.ENV_BASEDIR]
    del os.environ[config.ENV_URL]
