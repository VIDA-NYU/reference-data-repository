# This file is part of the Reference Data Repository (refdata).
#
# Copyright (C) 2021 New York University.
#
# refdata is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Manager for downloaded dataset files on the local file system."""

from pathlib import Path
from pooch.core import stream_download
from pooch.downloaders import choose_downloader

from typing import Dict, List, Optional, Set, Union

import os
import pandas as pd

from refdata.base import DatasetDescriptor
from refdata.dataset.base import DatasetHandle
from refdata.db import Dataset, DATASET_ID, DB, SessionScope
from refdata.repo.loader import RepositoryIndexLoader, UrlLoader
from refdata.repo.manager import RepositoryManager
from refdata.version import __version__

import refdata.config as config
import refdata.error as err


class LocalStore:
    """The local dataset store maintains downloaded datasets on the file system.
    All datasets are maintained in subfolders of a base directory. By default,
    the base directory is in the users cache directory under the package name.

    Information about downloaded datasets is maintaind in an SQLite database
    `refdata.db` that is created in the base directory. The data file for
    each downloaded dataset is maintained in a separate subfolder.
    """
    def __init__(
        self, package_name: str, package_version: str,
        basedir: Optional[str] = None, loader: Optional[RepositoryIndexLoader] = None,
        auto_download: Optional[bool] = None, connect_url: Optional[str] = None
    ):
        """Initialize the base directory on the file system where downloaded
        datasets are stored, the database for storing information about the
        downloaded datasets, the repository manager, and set the auto download
        option.

        Parameters
        ----------
        package_name: string
            Name of the package that created the instance of the local store.
            This name is used to associated downloaded datasets in the local
            database with the packages that downloaded them.
        package_version: string
            Version information for the package that created the local store
            instance.
        basedir: string, default=None
            Path to the directory for downloaded datasets. By default, the
            directory that is specified in the environment variable REFDATA_BASEDIR
            is used. If the environment variable is not set an directory under
            the OS-specific users cache data directory is used.
        loader: refdata.repo.loader.RepositoryIndexLoader, default=None
            Loader for a dataset repository index. the loaded index is used to
            create an instance of the repository manager that is associated with
            the local data store for downloading datasets.
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
        self.package_name = package_name
        self.package_version = package_version
        # Create the base directory if it does not exist.
        self.basedir = basedir if basedir else config.BASEDIR()
        os.makedirs(self.basedir, exist_ok=True)
        # Set the repository loader. The repository manager will be instantiated
        # when it is first accessed. If no loader is given the default dataset
        # index will be loaded for the associated repository manager instance.
        self.loader = loader if loader is not None else UrlLoader()
        self.repo = None
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
        return os.path.abspath(os.path.join(self.basedir, '{}.{}'.format(dataset_id, 'dat')))

    def distinct(
        self, key: str, columns: Optional[Union[str, List[str]]] = None,
        auto_download: Optional[bool] = None
    ) -> Set:
        """Shortcut to get the set of distinct values in one or more columns
        for a downloaded dataset with the given identifier.

        Parameters
        ----------
        key: string
            External unique dataset identifier.
        columns: list of string, default=None
            Column identifier defining the content and returned distinct value
            set.
        auto_download: bool, default=None
            Override the class global auto download flag.

        Returns
        -------
        set
        """
        dataset = self.open(key=key, auto_download=auto_download)
        return dataset.distinct(columns=columns)

    def download(self, key: str) -> DatasetHandle:
        """Download the dataset with the given (external) identifier.

        Returns the handle for the downloaded dataset. If no dataset with that
        given key exists an error is raised. If the dataset had been downloaded
        before the data file is downloaded again.

        Returns the internal identifier and the descriptor (serialization) for
        the downloaded dataset.

        Parameters
        ----------
        key: string
            External unique dataset identifier.

        Returns
        -------
        refdata.dataset.base.DatasetHandle

        Raises
        ------
        refdata.error.UnknownDatasetError
        """
        # Get the dataset descriptor from the repository.
        descriptor = self.repository().get(key=key)
        if descriptor is None:
            raise err.UnknownDatasetError(key=key)
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
        # Download the dataset files into the dataset target directory. This
        # will raise an error if the checksum for the downloaded file does not
        # match the expected checksum from the repository index.
        dst = self._datafile(dataset_id)
        download_file(dataset=descriptor, dst=dst)
        # Create entry for the downloaded dataset if it was downloaded for
        # the first time.
        if not ds_exists:
            with self.db.session() as session:
                dataset = Dataset(
                    dataset_id=dataset_id,
                    key=key,
                    descriptor=descriptor.to_dict(),
                    package_name=self.package_name,
                    package_version=self.package_version
                )
                session.add(dataset)
        return self.open(key=key)

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

    def list(self) -> List[DatasetHandle]:
        """Get the descriptors for all datasets that have been downloaded and
        are available from the local dataset store.

        Returns
        -------
        list of refdata.dataset.base.DatasetHandle
        """
        with self.db.session() as session:
            datasets = session.query(Dataset).all()
            return [
                DatasetHandle(
                    descriptor=d.descriptor,
                    package_name=d.package_name,
                    package_version=d.package_version,
                    created_at=d.created_at,
                    datafile=self._datafile(d.dataset_id)
                ) for d in datasets
            ]

    def load(
        self, key: str, columns: Optional[List[str]] = None,
        auto_download: Optional[bool] = None
    ) -> pd.DataFrame:
        """Load the dataset with the given identifier as a pandas data frame.

        This is a shortcut to open the dataset with the given identifier (and
        optionally download it first) and then reading data from the downloaded
        file into a data frame.

        Parameters
        ----------
        key: string
            External unique dataset identifier.
        columns: list of string, default=None
            Column identifier defining the content and the schema of the
            returned data frame.
        auto_download: bool, default=None
            Override the class global auto download flag.

        Returns
        -------
        pd.DataFrame
        """
        dataset = self.open(key=key, auto_download=auto_download)
        return dataset.data_frame(columns=columns)

    def mapping(
        self, key: str, lhs: Union[str, List[str]], rhs: Union[str, List[str]],
        ignore_equal: Optional[bool] = True, auto_download: Optional[bool] = None
    ) -> Dict:
        """Generate a mapping from values in dataset rows.

        This is a shortcut to open the dataset with the given identifier (and
        optionally download it first) and the generae a mapping from the
        downloaded dataset for the given columns.

        Parameters
        ----------
        key: string
            External unique dataset identifier.
        lhs: string or list of string
            Columns defining the source of values for the left-hand side of the
            mapping.
        rhs: string or list of string
            Columns defining the source of values for the right-hand side of the
            mapping.
        ignore_equal: bool, default=True
            Exclude mappings from a value to itself from the created mapping.
        auto_download: bool, default=None
            Override the class global auto download flag.

        Returns
        -------
        set
        """
        dataset = self.open(key=key, auto_download=auto_download)
        return dataset.mapping(lhs=lhs, rhs=rhs, ignore_equal=ignore_equal)

    def open(self, key: str, auto_download: Optional[bool] = None) -> DatasetHandle:
        """Get handle for the specified dataset. If the dataset does not exist
        in the local store it will be downloaded if the given auto_download
        flag is True or if the class global auto_download flag is True. Note
        that the auto_download argument will override the class global one.

        If the dataset is not available in the local store (and not automatically
        downloaded) an error is raised.

        Parameters
        ----------
        key: string
            External unique dataset identifier.
        auto_download: bool, default=None
            Override the class global auto download flag.

        Returns
        -------
        refdata.dataset.base.DatasetHandle

        Raises
        ------
        refdata.error.NotDownloadedError
        """
        # Return the dataset handle if the dataset has been downloaded before.
        with self.db.session() as session:
            dataset = self._get(session=session, key=key)
            if dataset is not None:
                return DatasetHandle(
                    descriptor=dataset.descriptor,
                    package_name=dataset.package_name,
                    package_version=dataset.package_version,
                    created_at=dataset.created_at,
                    datafile=self._datafile(dataset.dataset_id)
                )
        # Attempt to download if it does not exist in the local store and either
        # of the given auto_download flag or the class global auto_download is
        # True. Raises error if dataset has not been downloaded and
        # auto_download is False.
        download = auto_download if auto_download is not None else self.auto_download
        if download:
            return self.download(key=key)
        else:
            raise err.NotDownloadedError(key=key)

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
            self.repo = RepositoryManager(doc=self.loader.load())
        return self.repo


class RefStore(LocalStore):
    """Default local store for the refdata package. Uses the module name and
    package version to set the respective properties of the created local store
    instance.
    """
    def __init__(
        self, basedir: Optional[str] = None, loader: Optional[RepositoryIndexLoader] = None,
        auto_download: Optional[bool] = None, connect_url: Optional[str] = None
    ):
        """Initialize the store properties.

        Parameters
        ----------
        basedir: string, default=None
            Path to the directory for downloaded datasets. By default, the
            directory that is specified in the environment variable REFDATA_BASEDIR
            is used. If the environment variable is not set an directory under
            the OS-specific users cache data directory is used.
        loader: refdata.repo.loader.RepositoryIndexLoader, default=None
            Loader for a dataset repository index. the loaded index is used to
            create an instance of the repository manager that is associated with
            the local data store for downloading datasets.
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
        super(RefStore, self).__init__(
            package_name=__name__.split('.')[0],
            package_version=__version__,
            basedir=basedir,
            loader=loader,
            auto_download=auto_download,
            connect_url=connect_url
        )


# -- Helper Functions ---------------------------------------------------------

def download_file(dataset: DatasetDescriptor, dst: str):
    """Download data file for the given dataset.

    Computes the checksum for the downloaded file during download. Raises an
    error if the checksum of the downloaded file does not match the value in
    the given dataset descriptor.

    Parameters
    ----------
    url: string
        Url for downloaded resource.
    dst: string
        Path to destination file on disk.

    Raises
    ------
    ValueError
    """
    url = dataset.url
    stream_download(
        url=url,
        fname=Path(dst),
        known_hash=dataset.checksum,
        downloader=choose_downloader(url),
        pooch=None
    )
