# This file is part of the Reference Data Repository (refdata).
#
# Copyright (C) 2021 New York University.
#
# refdata is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Definition of environment variables that are used to configure components of
the reference data repository package. For each defined variable a helper
function is defined to provide easy access to the environment variable and its
default value.
"""

from appdirs import user_cache_dir

import os


"""Environment variables to configure the reference data manager and local data
store.
"""
ENV_AUTODOWNLOAD = 'REFDATA_AUTODOWNLOAD'
ENV_BASEDIR = 'REFDATA_BASEDIR'
ENV_URL = 'REFDATA_URL'


"""Default directory name for the local store."""
DEFAULT_DIR = '.refdata'

"""Default Url for the repository index file."""
DEFAULT_URL = 'https://raw.githubusercontent.com/VIDA-NYU/reference-data-repository/master/data/index.json'


# -- Helper Functions for Accessing Configuration Values ----------------------

def AUTO_DOWNLOAD() -> bool:
    """Get the value for the auto_download flag from the environment variable
    REFDATA_AUTODOWNLOAD.

    Casts the current value for the environment variable to Boolean. Only if
    the value equals 'true' (ignoring case) will the result be True. The
    default value is False.

    Returns
    -------
    bool
    """
    value = os.environ.get(ENV_AUTODOWNLOAD)
    if value:
        return True if value.lower() == 'true' else False
    return False


def BASEDIR() -> str:
    """Get the current value for the environment variable REFDATA_BASEDIR.

    If the value is not set (missing or empty) the folder `.refdata` in the
    OS-specific data cache directory for the current user is used as the
    default.

    Returns
    -------
    string
    """
    basedir = os.environ.get(ENV_BASEDIR)
    if not basedir:
        basedir = os.path.join(user_cache_dir(appname=__name__.split('.')[0]), DEFAULT_DIR)
    return basedir


def URL() -> str:
    """Get the Url for the repository index file that is specified in the
    environment variable REFDATA_URL or the default Url if the variable is
    not set or empty.

    Returns
    -------
    string
    """
    url = os.environ.get(ENV_URL)
    if not url:
        url = DEFAULT_URL
    return url
