# This file is part of the Reference Data Repository (refdata).
#
# Copyright (C) 2021 New York University.
#
# refdata is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Commands that interact with the local data store."""

import click

from refdata.repo import RepositoryManager
from refdata.store.base import RefStore

import refdata.cli.util as util


@click.group()
def cli_store():
    """Local Data Store."""
    pass


# -- Commands -----------------------------------------------------------------

@cli_store.command(name='download')
@click.option('-b', '--basedir', required=False, help='Local store directory')
@click.option('-d', '--db', required=False, help='Database connect URL')
@click.option('-i', '--index', required=False, help='Repository index file')
@click.argument('key')
def download_dataset(basedir, db, index, key):
    """List local store content."""
    # Read the index of given.
    doc = util.read_index(index) if index is not None else None
    store = RefStore(basedir=basedir, repo=RepositoryManager(doc=doc), connect_url=db)
    store.download(key)


@cli_store.command(name='list')
@click.option('-b', '--basedir', required=False, help='Local store directory')
@click.option('-d', '--db', required=False, help='Database connect URL')
@click.option('-i', '--index', required=False, help='Repository index file')
def list_datasets(basedir, db, index):
    """List local store content."""
    # Read the index of given.
    doc = util.read_index(index) if index is not None else None
    store = RefStore(basedir=basedir, repo=RepositoryManager(doc=doc), connect_url=db)
    util.print_datasets(store.list())


@cli_store.command(name='remove')
@click.option('-b', '--basedir', required=False, help='Local store directory')
@click.option('-d', '--db', required=False, help='Database connect URL')
@click.option('-i', '--index', required=False, help='Repository index file')
@click.option('-f', '--force', is_flag=True, default=False, help='Remove without confirmation')
@click.argument('key')
def remove_dataset(basedir, db, index, force, key):
    """Remove dataset from local store."""
    # Confirm that the user wants to remove the dataset from the local store.
    if not force:  # pragma: no cover
        msg = "Do you really want to remove dataset '{}'".format(key)
        click.confirm(msg, default=True, abort=True)
    # Read the index of given.
    doc = util.read_index(index) if index is not None else None
    store = RefStore(basedir=basedir, repo=RepositoryManager(doc=doc), connect_url=db)
    store.remove(key)


@cli_store.command(name='show')
@click.option('-b', '--basedir', required=False, help='Local store directory')
@click.option('-d', '--db', required=False, help='Database connect URL')
@click.option('-i', '--index', required=False, help='Repository index file')
@click.option('-r', '--raw', is_flag=True, default=False, help='Print JSON format')
@click.argument('key')
def show_dataset(basedir, db, index, raw, key):
    """Show descriptor for downloaded dataset."""
    # Read the index of given.
    doc = util.read_index(index) if index is not None else None
    store = RefStore(basedir=basedir, repo=RepositoryManager(doc=doc), connect_url=db)
    util.print_dataset(dataset=store.open(key), raw=raw)
