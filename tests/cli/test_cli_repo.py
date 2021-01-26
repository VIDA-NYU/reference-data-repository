# This file is part of the Reference Data Repository (refdata).
#
# Copyright (C) 2021 New York University.
#
# refdata is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Unit test for the repository index command line interface."""

from refdata.cli.base import cli


def test_list_repository(refdata_cli, index_file):
    """Test listing the content of a repository index file."""
    cmd = ['index', 'list', '-i', index_file]
    result = refdata_cli.invoke(cli, cmd)
    assert result.exit_code == 0


def test_show_dataset(refdata_cli, index_file):
    """Test printing descriptor for dataset in repository index file."""
    cmd = ['index', 'show', '-i', index_file, 'cities']
    result = refdata_cli.invoke(cli, cmd)
    assert result.exit_code == 0


def test_validate_index(refdata_cli, index_file):
    """Test validating a repository index file."""
    cmd = ['index', 'validate', index_file]
    result = refdata_cli.invoke(cli, cmd)
    assert result.exit_code == 0
