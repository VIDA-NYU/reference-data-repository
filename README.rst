=========================
Reference Data Repository
=========================

.. image:: https://img.shields.io/badge/License-MIT-yellow.svg
    :target: https://github.com/VIDA-NYU/reference-data-repository/blob/master/LICENSE


.. image:: https://github.com/VIDA-NYU/reference-data-repository/workflows/build/badge.svg
    :target: https://github.com/VIDA-NYU/reference-data-repository/actions?query=workflow%3A%22build%22


.. image:: https://codecov.io/gh/VIDA-NYU/reference-data-repository/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/VIDA-NYU/reference-data-repository


About
=====

The **Reference Data Repository** provides access to reference data sets (e.g., controlled vocabularies, gazetteers, etc.) that are accessible on the Web and that are useful for data cleaning and data profiling tools like `openclean <https://github.com/VIDA-NYU/openclean-core/>`_ and `Auctus <https://gitlab.com/ViDA-NYU/auctus/auctus>`_.


Data Hosting
------------
Individual datasets are hosted by data maintainers on different platforms. The only requirement is that the datasets (or individual dataset versions) are accessible via HTTP GET requests. Information about dataset is maintained in a central index (as a Json file) that is hosted on the Web (see for example the `openclean reference data collection <https://github.com/VIDA-NYU/openclean-reference-data/blob/master/data/index.json>`_).



Datasets and Data Formats
-------------------------
Each dataset has a unique identifier. Different file formats are supported for the datasets, e.g., csv files, Json, SQLIte database files, etc.. Format information for each dataset is stored as part of its entry in the global index.

Datasets are considered tabular (or sets of columns). Users may access only a single column from a dataset (e.g., country_name), multiple columns (e.b., country_name, captial_city) or the full dataset.

Below is an example dataset descriptor.

.. code-block:: json

    {
        "id": "encyclopaedia_britannica:us_cities",
        "name": "Cities in the U.S.",
        "description": "Names of cities in the U.S. from the Encyclopaedia Britannica.",
        "url": "https://raw.githubusercontent.com/VIDA-NYU/openclean-reference-data/master/data/us_cities.tsv",
        "checksum": "d361873f13b867805628d7db63987392835114f13da9ead0e11ccff2946631d2",
        "webpage": "https://www.britannica.com/topic/list-of-cities-and-towns-in-the-United-States-2023068",
        "schema": [
            {"id": "city", "name": "City", "description": "City Name", "dtype": "text"},
            {"id": "state", "name": "State", "description": "U.S. State Name", "dtype": "text"}
        ],
        "format": {
            "type": "csv",
            "parameters": {
                "delim": "\t"
            }
        }
    }


The full schema for the data repository index content is defined in `schema.yaml <https://github.com/VIDA-NYU/reference-data-repository/blob/master/refdata/schema.yaml>`_.


Local Data Repository
---------------------
Users maintain copies of the datasets for local access. By default, datasets are stored in a subfolder `.refdata` in the users home directory.
