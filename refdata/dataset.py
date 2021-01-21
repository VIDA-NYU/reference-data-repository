# This file is part of the Reference Data Repository (refdata).
#
# Copyright (C) 2021 New York University.
#
# refdata is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

from typing import Dict

from refdata.base import DatasetDescriptor


class DatasetHandle(DatasetDescriptor):
    """
    """
    def __init__(self, doc: Dict, datafile: str):
        """
        """
        super(DatasetHandle, self).__init__(doc=doc)
        self.datafile = datafile
