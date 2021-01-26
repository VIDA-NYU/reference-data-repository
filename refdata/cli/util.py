# This file is part of the Reference Data Repository (refdata).
#
# Copyright (C) 2021 New York University.
#
# refdata is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Collection of helper functions for the Reference Data Repository command
line interface.
"""

from typing import Dict

import json
import os

from refdata.repo import download_index


def read_index(filename: str) -> Dict:
    """Read a repository index file. The filename may either reference a file
    on the local file system or is expected to be an Url.

    Parameters
    ----------
    filename: string
        Path to file on the local file system or Url.

    Returns
    -------
    dict
    """
    if os.path.isfile(filename):
        with open(filename, 'r') as f:
            doc = json.load(f)
    else:
        doc = download_index(url=filename)
    return doc
