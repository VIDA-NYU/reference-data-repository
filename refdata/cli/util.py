# This file is part of the Reference Data Repository (refdata).
#
# Copyright (C) 2021 New York University.
#
# refdata is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Collection of helper functions for the Reference Data Repository command
line interface.
"""

from typing import Dict

import click
import json

from refdata.base import DatasetDescriptor
from refdata.repo.loader import FileLoader, UrlLoader


class TPrinter:
    """Wrapper around `click.echo` for table printing."""
    def write(self, s):
        click.echo(s)

    def flush(self):
        pass


def print_dataset(dataset: DatasetDescriptor, raw: bool):
    """Output the given dataset.

    If the raw flag is True the output is the formated dictionary serialization
    of the descriptor.

    Parameters
    ----------
    dataset: refdata.base.DatasetDescriptor
        Descriptor for output dataset.
    raw: bool
        Print dictionary serialization of the descriptor.
    """
    # Print dictionary serialization if raw flag is set to True.
    if raw:
        click.echo(json.dumps(dataset.to_dict(), indent=4))
        return
    # Dataset properties.
    template = '{:>11}: {}'
    click.echo()
    click.echo(template.format('Identifier', dataset.identifier))
    click.echo(template.format('Name', dataset.name))
    click.echo(template.format('Description', dataset.description))
    click.echo(template.format('URL', dataset.url))
    click.echo(template.format('Checksum', dataset.checksum))
    click.echo(template.format('Compression', dataset.compression))
    click.echo(template.format('Author', dataset.author))
    click.echo(template.format('License', dataset.license))
    click.echo(template.format('Web', dataset.webpage))
    click.echo(template.format('Tags', ', '.join(dataset.tags)))
    # Schema
    click.echo('\nAttributes\n----------')
    for col in dataset.columns:
        click.echo()
        click.echo(template.format('Identifier', col.identifier))
        click.echo(template.format('Name', col.name))
        click.echo(template.format('Description', col.description))
        click.echo(template.format('Datatype', col.dtype))
        click.echo(template.format('Tags', ', '.join(col.tags)))


def read_index(filename: str) -> Dict:
    """Read a repository index file.

    The filename may either reference a file on the local file system or is
    expected to be an Url. Attempts to read a file first and then load the
    Url if an error occured while loading the file.

    Parameters
    ----------
    filename: string
        Path to file on the local file system or Url.

    Returns
    -------
    dict
    """
    try:
        return FileLoader(filename).load()
    except (IOError, OSError):
        pass
    return UrlLoader(url=filename).load()
