# This file is part of the Reference Data Repository (refdata).
#
# Copyright (C) 2021 New York University.
#
# refdata is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Unit tests for version information."""

from refdata.version import __version__


def test_package_version():
    """Test accessing package version information (for completion)."""
    assert __version__ is not None
