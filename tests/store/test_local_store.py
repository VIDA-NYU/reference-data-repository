# This file is part of the Reference Data Repository (refdata).
#
# Copyright (C) 2021 New York University.
#
# refdata is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Unit tests for the local datastore."""

import os
import pytest

from refdata.db import Dataset
from refdata.store import LocalStore, RefStore, download_file
from refdata.version import __version__

import refdata
import refdata.error as err


def test_download_dataset(store):
    """Test downloading datasets to the local store."""
    dataset_id, descriptor = store.download(key='cities')
    assert dataset_id is not None
    assert descriptor['id'] == 'cities'
    assert os.path.isfile(store._datafile(dataset_id))
    # No issue downloading the datset again.
    dataset_id, descriptor = store.download(key='cities')
    assert dataset_id is not None
    assert descriptor['id'] == 'cities'
    assert os.path.isfile(store._datafile(dataset_id))
    # Error when downloading unkown file.
    with pytest.raises(err.UnknownDatasetError):
        store.download(key='unknown')


def test_download_invalid_checksum(store, tmpdir):
    """Test downloading a dataset with an invalid checksum."""
    # Hack: Modify checksum value for dataset 'cities' before attempting to
    # download it.
    ds = store.repository().get('cities')
    ds.doc['checksum'] = '0000'
    with pytest.raises(ValueError):
        download_file(dataset=ds, dst=os.path.join(tmpdir, 'test.dat'))


def test_listing_dataset_in_local_store(store):
    """Test listing the dataset in the local store."""
    store.download(key='cities')
    assert len(store.list()) == 1
    store.download(key='countries')
    datasets = [ds.identifier for ds in store.list()]
    assert len(datasets) == 2
    assert 'cities' in datasets
    assert 'countries' in datasets


def test_local_store_init(tmpdir):
    """Test different scenarios for database creation when initializing the
    local store.
    """
    # First without connection url and no existing database.
    basedir = os.path.join(tmpdir, 'test')
    store = LocalStore(package_name='test', package_version='test.1', basedir=basedir)
    assert store.package_name == 'test'
    assert store.package_version == 'test.1'
    assert os.path.join(basedir, 'refdata.db')
    # A seocond call should not re-create the database. To validate this we
    # create a new dataset and ensure that after re-creating the store that
    # the database is not empty.
    with store.db.session() as session:
        session.add(
            Dataset(
                key='my_key',
                descriptor={'id': 'my_key'},
                package_name='test',
                package_version='1',
                filesize=0
            )
        )
    store = RefStore(basedir=basedir)
    assert store.package_name == refdata.__name__.split('.')[0]
    assert store.package_version == __version__
    with store.db.session() as session:
        datasets = session.query(Dataset).all()
        assert len(datasets) == 1
        ds = datasets[0]
        assert ds.key == 'my_key'
        assert ds.descriptor == {'id': 'my_key'}
        assert ds.package_name == 'test'
        assert ds.package_version == '1'
        assert ds.filesize == 0
        assert ds.created_at is not None
    # Create the store with a connection string that points to the created
    # database.
    dbfile = os.path.join(basedir, 'refdata.db')
    store = RefStore(basedir=basedir, connect_url='sqlite:///{}'.format(dbfile))
    with store.db.session() as session:
        datasets = session.query(Dataset).all()
        assert len(datasets) == 1


def test_local_store_repo_manager(mock_response, tmpdir):
    """Ensure that the repository manager is created when first accessed.
    """
    # First without connection url and no existing database.
    basedir = os.path.join(tmpdir, 'test')
    store = RefStore(basedir=basedir)
    # Ensure that the default test repository was created.
    assert len(store.repository().find()) == 3
    # Hack to ensure that the manager is created only once.
    store.repository().datasets = dict()
    assert len(store.repository().find()) == 0


def test_open_dataset(store):
    """Test opening a downloaded dataset."""
    store.download(key='cities')
    assert store.open('cities').identifier == 'cities'
    # Error when opening a dataset that has not been downloaded and is not
    # downloaded automatically.
    with pytest.raises(err.NotDownloadedError):
        store.open('countries')
    with pytest.raises(err.NotDownloadedError):
        store.open('countries', auto_download=False)
    # The dataset can be opened if the auto_download flag is True.
    assert store.open('countries', auto_download=True).identifier == 'countries'


def test_remove_dataset(store):
    """Test deleting a datasets from the local store."""
    store.download(key='cities')
    # A first attempt to remove the dataset return True.
    assert store.remove(key='cities')
    # The second attempt returns False since the dataset no longer exists
    # in the local store.
    assert not store.remove(key='cities')
