# This file is part of the Reference Data Repository (refdata).
#
# Copyright (C) 2021 New York University.
#
# refdata is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Main module for the Reference Data Repository command line interface."""

import click

from refdata.cli.repo import cli_repo
from refdata.cli.store import cli_store
from refdata.cli.util import read_index
from refdata.repo import validate
from refdata.store.checksum import hash_file


@click.group()
def cli():
    """Command line interface for the Reference Data Repository."""
    pass


# -- Commands -----------------------------------------------------------------

@cli.command(name='checksum')
@click.argument('file')
def print_checksum(file):
    """Print file checksum."""
    click.echo(hash_file(file))


@cli.command(name='validate')
@click.argument('file')
def validate_index_file(file):
    """Validate repository index."""
    validate(doc=read_index(file))
    click.echo('Document is valid.')


cli.add_command(cli_repo, name="repo")
cli.add_command(cli_store, name="store")
