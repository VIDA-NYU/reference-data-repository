# This file is part of the Reference Data Repository (refdata).
#
# Copyright (C) 2021 New York University.
#
# refdata is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Unit tests for the local store database."""

from sqlalchemy.exc import IntegrityError

import pytest

from refdata.db import DB, Dataset


"""Database connection Url for test purposes."""
TEST_URL = 'sqlite:///:memory:'


def test_database_init():
    """Test creating a fresh instance of the database."""
    db = DB(connect_url=TEST_URL)
    db.init()


def test_database_session():
    """Test manipulating data in the database."""
    # -- Setup ----------------------------------------------------------------
    db = DB(connect_url=TEST_URL)
    db.init()
    # -- Tests ----------------------------------------------------------------
    with db.session() as session:
        session.add(Dataset(key='my_key', descriptor={'id': 'my_key'}))
    with db.session() as session:
        session.add(Dataset(key='a_key', descriptor={'id': 'a_key'}))
    with db.session() as session:
        datasets = session.query(Dataset).all()
        assert len(datasets) == 2
    # Error when creating an entry with duplicate key.
    with pytest.raises(IntegrityError):
        with db.session() as session:
            session.add(Dataset(key='my_key', descriptor={'id': 'my_key'}))
