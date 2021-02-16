# This file is part of the Reference Data Repository (refdata).
#
# Copyright (C) 2021 New York University.
#
# refdata is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Commands that interact with a repository index."""

import click
import tableprint as tp

from refdata.repo.loader import DictLoader, UrlLoader
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
    # Read the index from the optional file or Url. By default, the index that
    # is specified in the environment is loaded.
    loader = DictLoader(util.read_index(index)) if index is not None else UrlLoader()
    datasets = RepositoryManager(doc=loader.load()).find()
    headers = ['Identifier', 'Name', 'Description']
    data = list()
    # Maintain the maximum with for each columns.
    widths = [len(h) + 1 for h in headers]
    # Sort datasets by name before output.
    for dataset in sorted(datasets, key=lambda d: d.name):
        desc = dataset.description if dataset.description is not None else ''
        row = [dataset.identifier, dataset.name, desc]
        for i in range(len(row)):
            w = len(row[i]) + 1
            if w > widths[i]:
                widths[i] = w
        data.append(row)
    tp.table(data, headers=headers, width=widths, style='grid', out=util.TPrinter())


@cli_repo.command(name='show')
@click.option('-i', '--index', required=False, help='Repository index file')
@click.option('-r', '--raw', is_flag=True, default=False, help='Print JSON format')
@click.argument('key')
def show_dataset(index, raw, key):
    """Show dataset descriptor from repository index."""
    # Read the index from the optional file or Url. By default, the index that
    # is specified in the environment is loaded.
    loader = DictLoader(util.read_index(index)) if index is not None else UrlLoader()
    util.print_dataset(dataset=RepositoryManager(doc=loader.load()).get(key), raw=raw)


@cli_repo.command(name='validate')
@click.argument('file')
def validate_index_file(file):
    """Validate repository index file."""
    validate(doc=util.read_index(file))
    click.echo('Document is valid.')
