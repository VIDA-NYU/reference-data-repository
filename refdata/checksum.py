# This file is part of the Reference Data Repository (refdata).
#
# Copyright (C) 2021 New York University.
#
# refdata is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Functions for computing a secure hash checksum for data files in the
repository. Used to validate that downloaded files have a checksum that
matches the hash that is included in the repository index.
"""

from typing import Optional

import hashlib


"""Default block size when reading input files."""
BLOCK_SIZE = 65536


def hash_file(filename: str, chunk_size: Optional[int] = None) -> str:
    """Compute checksum for a given input file using the SHA-256 algorithm.

    Parameters
    ----------
    filename: str
        Path to file on the local file system.
    chunk_size: int, default=None
        Size of blocks that are read from the input file. Reading the file in
        chunks avoids having to read the whole file into memory before computing
        the checksum.

    Returns
    -------
    string
    """
    # Ensure that the chunk size is set.
    chunk_size = chunk_size if chunk_size is not None else BLOCK_SIZE
    m = hashlib.sha256()
    # Read file in chunks of XXX to avoid loading large files completely into
    # memory.
    with open(filename, 'rb') as f:
        while True:
            data = f.read(chunk_size)
            if not data:
                break
            m.update(data)
    # Return the checksum for the read file. Use hexdigest to get a string that
    # contains only hexadecimal digits (to include in Json documents).
    return m.hexdigest()
