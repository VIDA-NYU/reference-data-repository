# This file is part of the Reference Data Repository (refdata).
#
# Copyright (C) 2021 New York University.
#
# refdata is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Unit tests for the configuration helper methods."""

from pathlib import Path

import os
import pytest

import refdata.config as config


@pytest.mark.parametrize(
    'value,result',
    [
        (None, False),
        ('', False),
        ('TRUE', True),
        ('True', True),
        ('true', True),
        ('False', False),
        ('123', False)
    ]
)
def test_auto_download_flag(value, result):
    """Test getting the value for the auto download option from the environment."""
    # -- Setup ----------------------------------------------------------------
    if value is not None:
        os.environ[config.ENV_AUTODOWNLOAD] = value
    elif config.ENV_AUTODOWNLOAD in os.environ:
        del os.environ[config.ENV_AUTODOWNLOAD]
    # -- Test -----------------------------------------------------------------
    assert config.AUTO_DOWNLOAD() == result
    # -- Cleanup --------------------------------------------------------------
    if config.ENV_AUTODOWNLOAD in os.environ:
        del os.environ[config.ENV_AUTODOWNLOAD]


def test_basedir_config():
    """Test getting the configuration value for the local store base direcory."""
    os.environ[config.ENV_BASEDIR] = '/dev/null'
    assert config.BASEDIR() == '/dev/null'
    os.environ[config.ENV_BASEDIR] = ''
    assert config.BASEDIR() == os.path.join(str(Path.home()), config.DEFAULT_DIR)
    del os.environ[config.ENV_BASEDIR]
    assert config.BASEDIR() == os.path.join(str(Path.home()), config.DEFAULT_DIR)


def test_repository_url():
    """Test getting the configuration value for the repository index Url."""
    os.environ[config.ENV_URL] = 'http://some.host'
    assert config.URL() == 'http://some.host'
    os.environ[config.ENV_URL] = ''
    assert config.URL() == config.DEFAULT_URL
    del os.environ[config.ENV_URL]
    assert config.URL() == config.DEFAULT_URL
