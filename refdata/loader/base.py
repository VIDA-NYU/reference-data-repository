# This file is part of the Reference Data Repository (refdata).
#
# Copyright (C) 2021 New York University.
#
# refdata is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Interface for format-specific dataset loaders."""

from abc import ABCMeta, abstractmethod
from typing import IO

import pandas as pd


class DatasetLoader(metaclass=ABCMeta):
    """The dataset loader reads a given opened file and returns a pandas data
    frame containing the dataset in the file.
    """
    @abstractmethod
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
        raise NotImplementedError()  # pragma: no cover
