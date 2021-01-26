# This file is part of the Reference Data Repository (refdata).
#
# Copyright (C) 2021 New York University.
#
# refdata is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Unit test for the command line interface of the local data store."""

from refdata.cli.base import cli


def test_dataset_lifecycle(refdata_cli, index_file, mock_response):
    """Test listing the content of the local data store."""
    # Empty store content at the beginning.
    cmd = ['store', 'list', '-i', index_file]
    result = refdata_cli.invoke(cli, cmd)
    assert 'cities' not in result.output
    assert result.exit_code == 0
    # Download dataset.
    cmd = ['store', 'download', '-i', index_file, 'cities']
    result = refdata_cli.invoke(cli, cmd)
    assert result.exit_code == 0
    # List store content again.
    cmd = ['store', 'list', '-i', index_file]
    result = refdata_cli.invoke(cli, cmd)
    assert 'cities' in result.output
    assert result.exit_code == 0
    # Print dataset descriptor.
    cmd = ['store', 'show', '-i', index_file, '-r', 'cities']
    result = refdata_cli.invoke(cli, cmd)
    assert result.exit_code == 0
    # Remove dataset.
    cmd = ['store', 'remove', '-i', index_file, 'cities']
    result = refdata_cli.invoke(cli, cmd)
    assert result.exit_code == 0
    # Empty store content at the end.
    cmd = ['store', 'list', '-i', index_file]
    result = refdata_cli.invoke(cli, cmd)
    assert 'cities' not in result.output
    assert result.exit_code == 0
