# This file is part of the Reference Data Repository (refdata).
#
# Copyright (C) 2021 New York University.
#
# refdata is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Commands that interact with a repository index."""

import click

from refdata.repo.manager import RepositoryManager
from refdata.repo.schema import validate

import refdata.cli.util as util


@click.group()
def cli_repo():
    """Data Repository Index."""
    pass


# -- Commands -----------------------------------------------------------------

@cli_repo.command(name='list')
@click.option('-i', '--index', required=False, help='Repository index file')
def list_repository(index):
    """List repository index content."""
    # Read the index of given.
    doc = util.read_index(index) if index is not None else None
    util.print_datasets(RepositoryManager(doc=doc).find())


@cli_repo.command(name='show')
@click.option('-i', '--index', required=False, help='Repository index file')
@click.option('-r', '--raw', is_flag=True, default=False, help='Print JSON format')
@click.argument('key')
def show_dataset(index, raw, key):
    """Show dataset descriptor from repository index."""
    # Read the index of given.
    doc = util.read_index(index) if index is not None else None
    util.print_dataset(dataset=RepositoryManager(doc=doc).get(key), raw=raw)


@cli_repo.command(name='validate')
@click.argument('file')
def validate_index_file(file):
    """Validate repository index file."""
    validate(doc=util.read_index(file))
    click.echo('Document is valid.')
