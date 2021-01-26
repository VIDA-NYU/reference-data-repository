# This file is part of the Reference Data Repository (refdata).
#
# Copyright (C) 2021 New York University.
#
# refdata is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Collection of helper functions for the Reference Data Repository command
line interface.
"""

from typing import Dict, List

import click
import json
import os

from refdata.base import DatasetDescriptor
from refdata.repo import download_index


def print_datasets(datasets: List[DatasetDescriptor]):
    """Print a listing of datasets to the console.

    Outputs the identifier, name and description for each dataset in the given
    list. Datasets are sorted by their name.

    Parameters
    ----------
    datasets: list of refdata.base.DatasetDescriptor
        List of dataset descriptors.
    """
    # Compute maximal length of values for the dataset identifier, name and
    # description. The length values are used to align the output.
    id_len = max([len(d.identifier) for d in datasets] + [10])
    name_len = max([len(d.name) for d in datasets] + [4])
    desc_len = max([len(d.description) for d in datasets if d.description is not None] + [11])
    # Create the output template with all values left aligned.
    template = '{:<' + str(id_len) + '} | {:<' + str(name_len) + '} | {:<' + str(desc_len) + '}'
    click.echo()
    click.echo(template.format('Identifier', 'Name', 'Description'))
    click.echo(template.format('-' * id_len, '-' * name_len, '-' * desc_len))
    # Sort datasets by name before output.
    for dataset in sorted(datasets, key=lambda d: d.name):
        desc = dataset.description if dataset.description is not None else ''
        click.echo(template.format(dataset.identifier, dataset.name, desc))


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
    """Read a repository index file. The filename may either reference a file
    on the local file system or is expected to be an Url.

    Parameters
    ----------
    filename: string
        Path to file on the local file system or Url.

    Returns
    -------
    dict
    """
    if os.path.isfile(filename):
        with open(filename, 'r') as f:
            doc = json.load(f)
    else:
        doc = download_index(url=filename)
    return doc
