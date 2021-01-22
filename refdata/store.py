# This file is part of the Reference Data Repository (refdata).
#
# Copyright (C) 2021 New York University.
#
# refdata is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Manager for downloaded dataset files on the local file system."""

from typing import Dict, List, Optional, Tuple

import os
import requests

from refdata.base import DatasetDescriptor
from refdata.checksum import hash_file
from refdata.dataset import DatasetHandle
from refdata.db import Dataset, DATASET_ID, DB, SessionScope
from refdata.repo import RepositoryManager

import refdata.config as config
import refdata.error as err


class LocalStore:
    """The local dataset store maintains downloaded datasets on the file system.
    All datasets are maintained in subfolders of a base directory. By default,
    the base directory is in the users home directory under `.refdata`.

    Information about downloaded datasets is maintaind in an SQLite database
    `refdata.db` that is created in the base directory. The data file for
    each downloaded dataset is maintained in a separate subfolder.
    """
    def __init__(
        self, basedir: Optional[str], repo: Optional[RepositoryManager] = None,
        auto_download: Optional[bool] = None, connect_url: Optional[str] = None
    ):
        """Initialize the base directory on the file system where downloaded
        datasets are stored, the database for storing information about the
        downloaded datasets, the repository manager, and set the auto download
        option.

        Parameters
        ----------
        basedir: string, default=None
            Path to the directory for downloaded datasets. By default, the
            directory that is specified in the environment variable REFDATA_BASEDIR
            is used or $HOME/.refdata if the environment variable is not set.
        repo: refdata.repo.RepositoryManager, default=None
            Repository manager that is used to access dataset metadata for
            downloading datasets.
        auto_download: bool, default=None
            If auto download is enabled (True) datasets are downloaded automatically
            when they are first accessed via `.open()`. If this option is not
            enabled and an attempt is made to open a datasets that has not yet
            been downloaded to the local file syste, an error is raised. If this
            argument is not given the value from the environment variable
            REFDATA_AUTODOWNLOAD is used or False if the variable is not set.
        connect_url: string, default=None
            SQLAlchemy database connect Url string. If a value is given it is
            assumed that the database exists and has been initialized. If no
            value is given the default SQLite database is used. If the respective
            database file does not exist a new database will be created.
        """
        # Create the base directory if it does not exist.
        self.basedir = basedir if basedir else config.BASEDIR()
        os.makedirs(self.basedir, exist_ok=True)
        # Set the repository manager. If none was given the default manager will
        # be used when it is first accessed.
        self.repo = repo
        # Set the auto download option. Read REFDATA_AUTODOWNLOAD if not no
        # argument value was given. The default is False.
        self.auto_download = auto_download if auto_download is not None else config.AUTO_DOWNLOAD()
        # Initialize the metadata database if it does not exist.
        if connect_url is None:
            dbfile = os.path.join(self.basedir, 'refdata.db')
            create_db = not os.path.isfile(dbfile)
            self.db = DB(connect_url='sqlite:///{}'.format(dbfile))
            # Create fresh database if the database file does not exist.
            if create_db:
                self.db.init()
        else:
            self.db = DB(connect_url=connect_url)

    def _datafile(self, dataset_id: str) -> str:
        """Helper method to get the path to the data file in the store base
        directory that contains the download for the dataset with the given
        (internal) identifier.

        Parameters
        ----------
        dataset_id: string
            Internal unique dataset identifier.

        Returns
        -------
        string
        """
        return os.path.join(self.basedir, '{}.{}'.format(dataset_id, 'dat'))

    def download(self, key: str) -> Tuple[str, Dict]:
        """Download the dataset with the given (external) identifier. If no
        dataset with that given key exists a ValueError is raised. If the
        dataset had been downloaded before the existing data file is
        downloaded again.

        Returns the internal identifier and the descriptor (serialization) for
        the downloaded dataset.

        Parameters
        ----------
        key: string
            External unique dataset identifier.

        Returns
        -------
        string, dict
        """
        # Get the dataset descriptor from the repository.
        ds = self.repository().get(key=key)
        if ds is None:
            raise ValueError("unknown dataset '{}'".format(key))
        # Get the internal dataset identifier if the dataset had been
        # downloaded before. If the dataset had not been downloaded an new
        # entry is created in the database.
        with self.db.session() as session:
            dataset = self._get(session=session, key=key)
            if dataset is None:
                dataset_id = DATASET_ID()
                ds_exists = False
            else:
                dataset_id = dataset.dataset_id
                ds_exists = True
        # Download the dataset files into the dataset target directory
        dst = self._datafile(dataset_id)
        download_file(dataset=ds, dst=dst)
        # Create entry for the downloaded dataset if it was downloaded for
        # the first time.
        if not ds_exists:
            with self.db.session() as session:
                dataset = Dataset(
                    dataset_id=dataset_id,
                    key=key,
                    descriptor=ds.to_dict()
                )
                session.add(dataset)
        return dataset_id, ds.to_dict()

    def _get(self, session: SessionScope, key: str) -> Dataset:
        """Get the database object for the dataset with the given key. If
        the dataset does not exist in the database the result is None.

        Parameters
        ----------
        key: string
            External unique dataset identifier.

        Returns
        -------
        string
        """
        return session.query(Dataset).filter(Dataset.key == key).one_or_none()

    def list(self) -> List[DatasetDescriptor]:
        """Get the descriptors for all datasets that have been downloaded and
        are available from the local dataset store.

        Returns
        -------
        list of refdata.base.DatasetDescriptor
        """
        with self.db.session() as session:
            datasets = session.query(Dataset).all()
            return [DatasetDescriptor(ds.descriptor) for ds in datasets]

    def open(self, key: str, auto_download: Optional[bool] = None) -> DatasetHandle:
        """Get handle for the specified dataset. If the dataset does not exist
        in the local store it will be downloaded if the given auto_download
        flag is True or if the class global auto_download flag is True. Note
        that the auto_download argument will override the class global one.

        If the dataset is not available in the local store (and not automatically
        downloaded) a ValueError is raised.

        Parameters
        ----------
        key: string
            External unique dataset identifier.
        auto_download: bool, default=None
            Override the class global auto download flag.

        Returns
        -------
        refdata.dataset.DatasetHandle
        """
        # Get the identifier and descriptor for the dataset. Raises ValueError
        # if dataset has not been downloaded and auto_download is False.
        dataset_id, descriptor = None, None
        with self.db.session() as session:
            dataset = self._get(session=session, key=key)
            if dataset is not None:
                dataset_id = dataset.dataset_id
                descriptor = dataset.descriptor
        # Attempt to download if it does not exist in the local store and either
        # of the given auto_download flag or the class global auto_download is
        # True.
        if dataset_id is None:
            download = auto_download if auto_download is not None else self.auto_download
            if download:
                dataset_id, descriptor = self.download(key=key)
            else:
                raise ValueError("dataset '{}' not available in local data store")
        # Return handle for the dataset.
        return DatasetHandle(doc=descriptor, datafile=self._datafile(dataset_id))

    def remove(self, key: str) -> bool:
        """Remove the dataset with the given (external) identifier from the
        local store. Returns True if the dataset was removed and False if the
        dataset had not been downloaded before.

        Parameters
        ----------
        key: string
            External unique dataset identifier.

        Returns
        -------
        bool
        """
        with self.db.session() as session:
            dataset = self._get(session=session, key=key)
            if dataset is None:
                return False
            # Delete dataset entry from database first.
            dataset_id = dataset.dataset_id
            session.delete(dataset)
        # Delete the downloaded file from disk.
        os.unlink(self._datafile(dataset_id))
        return True

    def repository(self) -> RepositoryManager:
        """Get a reference to the associated repository manager.

        Returns
        -------
        refdata.repo.RepositoryManager
        """
        # Create an instance of the default repository manager if none was
        # given when the store was created and this is the firat access to
        # the manager.
        if self.repo is None:
            self.repo = RepositoryManager()
        return self.repo


# -- Helper Functions ---------------------------------------------------------

def download_file(dataset: DatasetDescriptor, dst: str):
    """Download data file for the given dataset. Raises an error if the checksum
    of the downloaded file does not match the value in the given dataset
    descriptor.

    Parameters
    ----------
    url: string
        Url for downloaded resource.
    dst: string
        Path to destination file on disk.

    Raises
    ------
    refdata.error.InvalidChecksumError
    """
    with requests.get(dataset.url, stream=True) as r:
        r.raise_for_status()
        with open(dst, 'wb') as f:
            for buf in r.iter_content(chunk_size=8192):
                f.write(buf)
    # Raise error if the checksum for the downloaded file is invalid.
    if hash_file(filename=dst) != dataset.checksum:
        raise err.InvalidChecksumError(dataset)
