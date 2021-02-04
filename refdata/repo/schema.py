# This file is part of the Reference Data Repository (refdata).
#
# Copyright (C) 2021 New York University.
#
# refdata is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Schema validator for the repository index file.

The validator is inteded as a tool for developers and data publishers to
validate their data indexes before publishing them. The validator is currently
not used to validate the schema of an index structure that is passed to a
repository manager.
"""

from jsonschema import Draft7Validator, RefResolver
from typing import Dict

import importlib.resources as pkg_resources
import os
import yaml


# Make sure that the path to the schema file is a valid URI. Otherwise, errors
# occur (at least on MS Windows environments). Changed based on:
# https://github.com/Julian/jsonschema/issues/398#issuecomment-385130094
schemafile = 'file:///{}'.format(os.path.abspath(os.path.join(__file__, 'schema.yaml')))
schema = yaml.safe_load(pkg_resources.open_text(__package__, 'schema.yaml'))
resolver = RefResolver(schemafile, schema)


def validate(doc: Dict) -> Draft7Validator:
    """Validate the schema for a repository index document.

    The given document is a dictionary containing the repository index. An
    error is raised if the referenced document does not satisfy the defined
    repository index schema.


    Parameters
    ----------
    doc: dict
        Repository index document.

    Raises
    ------
    jsonschema.exceptions.ValidationError
    """
    validator = Draft7Validator(
        schema=schema['definitions']['RepositoryIndex'],
        resolver=resolver
    )
    validator.validate(doc)
