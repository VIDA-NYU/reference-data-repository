# This file is part of the Reference Data Repository (refdata).
#
# Copyright (C) 2021 New York University.
#
# refdata is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Unit tests for the local datastore."""

import os

from refdata.db import Dataset
from refdata.store import LocalStore


def test_local_store_init(tmpdir):
    """Test different scenarios for database creation when initializing the
    local store.
    """
    # First without connection url and no existing database.
    basedir = os.path.join(tmpdir, 'test')
    store = LocalStore(basedir=basedir)
    assert os.path.join(basedir, 'refdata.db')
    # A seocond call should not re-create the database. To validate this we
    # create a new dataset and ensure that after re-creating the store that
    # the database is not empty.
    with store.db.session() as session:
        session.add(Dataset(key='my_key', descriptor={'id': 'my_key'}))
    store = LocalStore(basedir=basedir)
    with store.db.session() as session:
        datasets = session.query(Dataset).all()
        assert len(datasets) == 1
    # Create the store with a connection string that points to the created
    # database.
    dbfile = os.path.join(basedir, 'refdata.db')
    store = LocalStore(basedir=basedir, connect_url='sqlite:///{}'.format(dbfile))
    with store.db.session() as session:
        datasets = session.query(Dataset).all()
        assert len(datasets) == 1


def test_local_store_repo_manager(mock_response, tmpdir):
    """Ensure that the repository manager is created when first accessed.
    """
    # First without connection url and no existing database.
    basedir = os.path.join(tmpdir, 'test')
    store = LocalStore(basedir=basedir)
    # Ensure that the default test repository was created.
    assert len(store.repository().find()) == 3
    # Hack to ensure that the manager is created only once.
    store.repository().datasets = dict()
    assert len(store.repository().find()) == 0
