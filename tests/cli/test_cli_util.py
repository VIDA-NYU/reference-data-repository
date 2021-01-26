# This file is part of the Reference Data Repository (refdata).
#
# Copyright (C) 2021 New York University.
#
# refdata is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Unit test for the helper commands and functions for the command line
interface.
"""

from refdata.cli.base import cli
from refdata.cli.util import read_index
from refdata.store.checksum import hash_file


def test_compute_checksum(refdata_cli, countries_file):
    """Test computing the checksum for a local file via the command line
    interface.
    """
    cmd = ['checksum', countries_file]
    result = refdata_cli.invoke(cli, cmd)
    assert hash_file(countries_file) in result.output
    assert result.exit_code == 0


def test_read_remote_index(mock_response):
    doc = read_index(filename='index.json')
    assert doc is not None
