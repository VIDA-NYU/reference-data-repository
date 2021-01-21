# This file is part of the Reference Data Repository (refdata).
#
# Copyright (C) 2021 New York University.
#
# refdata is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Define the classes in the Object-Relational Mapping for the local store's
metadata management.
"""

import json
import uuid

from sqlalchemy import Column, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.types import TypeDecorator, Unicode


# -- Helper Functions ---------------------------------------------------------

def DATASET_ID() -> str:
    """Create a new unique identifier.

    Returns
    -------
    string
    """
    return str(uuid.uuid4()).replace('-', '')


# -- ORM Base -----------------------------------------------------------------

"""Base class for all database tables."""
Base = declarative_base()


# -- Database Schema ----------------------------------------------------------

class JsonObject(TypeDecorator):
    """Decorator for objects that are stored as serialized JSON strings."""

    impl = Unicode

    def process_literal_param(self, value, dialect):
        """Expects a JSON serializable object."""
        return json.dumps(value)

    process_bind_param = process_literal_param

    def process_result_value(self, value, dialect):
        """Create JSON object from string serialization."""
        return json.loads(value)


class Dataset(Base):
    """Descriptor for dataset that has been downloaded to the local data store.
    Each dataset has two identifier, (i) the identifier that is part of the
    dataset descriptor (`key`), and (ii) an internal identifier (`dataset_id`).
    Users will reference datasets by their key. The internal dataset identifier
    specifies the subfolder under which the dataset files are stored.
    """
    # -- Schema ---------------------------------------------------------------
    __tablename__ = 'dataset'

    dataset_id = Column(String(32), default=DATASET_ID, primary_key=True)
    key = Column(String(1024), nullable=False, unique=True)
    descriptor = Column(JsonObject, nullable=False)


# -- Database Object ----------------------------------------------------------

class DB(object):
    """Wrapper to establish a database connection and create the database
    schema.
    """
    def __init__(self, connect_url: str):
        """Initialize the database for a given connection Url.

        Parameters
        ----------
        connect_url: string
            SQLAlchemy database connect Url string.
        """
        self._engine = create_engine(connect_url)
        self._session = sessionmaker(bind=self._engine)

    def init(self):
        """Create all tables in the database model schema."""
        # Drop all tables first before creating them.
        Base.metadata.drop_all(self._engine)
        Base.metadata.create_all(self._engine)

    def session(self):
        """Create a new database session instance. The sessoin is wrapped by a
        context manager to properly manage the session scope.

        Returns
        -------
        refdata.db.SessionScope
        """
        return SessionScope(self._session())


class SessionScope(object):
    """Context manager for providing transactional scope around a series of
    database operations.
    """
    def __init__(self, session):
        """Initialize the database session.

        Parameters
        ----------
        session: sqlalchemy.orm.session.Session
            Database session.
        """
        self.session = session

    def __enter__(self):
        """Return the managed database session object.

        Returns
        -------
        sqlalchemy.orm.session.Session
        """
        return self.session

    def __exit__(self, exc_type, exc_value, exc_traceback):
        """Commit or rollback transaction depending on the exception type.
        Does not surpress any exceptions.
        """
        if exc_type is None:
            try:
                self.session.commit()
            except Exception:
                self.session.rollback()
                raise
            finally:
                self.session.close()
        else:  # pragma: no cover
            try:
                self.session.rollback()
            finally:
                self.session.close()
