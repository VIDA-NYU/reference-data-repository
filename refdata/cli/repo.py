# This file is part of the Reference Data Repository (refdata).
#
# Copyright (C) 2021 New York University.
#
# refdata is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Commands that interact with a repository index."""

import click

from refdata.cli.util import read_index
from refdata.repo import RepositoryManager


@click.group()
def cli_repo():
    """Data Repository Index."""
    pass


# -- Commands -----------------------------------------------------------------

@cli_repo.command(name='list')
@click.option('-i', '--index', required=False, help='Repository index file')
def list_repository(index):
    """List repository content."""
    # Read the index of given.
    doc = None
    if index is not None:
        doc = read_index(index)
    datasets = RepositoryManager(doc=doc).find()
    # Compute max. length for dataset identifier, name and description.
    id_len = max([len(d.identifier) for d in datasets] + [10])
    name_len = max([len(d.name) for d in datasets] + [4])
    desc_len = max([len(d.description) for d in datasets if d.description is not None] + [11])
    template = '{:>' + str(id_len) + '} | {:<' + str(name_len) + '} | {:<' + str(desc_len) + '}'
    click.echo(template.format('Identifier', 'Name', 'Description'))
    click.echo(template.format('-' * id_len, '-' * name_len, '-' * desc_len))
    for dataset in sorted(datasets, key=lambda d: d.name):
        click.echo(template.format(dataset.identifier, dataset.name, dataset.description))
