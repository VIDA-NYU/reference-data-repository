# This file is part of the Reference Data Repository (refdata).
#
# Copyright (C) 2021 New York University.
#
# refdata is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

from refdata.loader.base import DatasetLoader

from typing import IO

import pandas as pd


class CSVLoader(DatasetLoader):
    def __init__(self, format):
        pass

    def read(self, file: IO) -> pd.DataFrame:
        """Read data from file and returna data frame containing the dataset.

        Parameters
        ----------
        file: file object
            Open file object.

        Returns
        -------
        pd.DataFrame
        """
        raise NotImplementedError()
