=========================
Reference Data Repository
=========================




About
=====

The aim of the Reference Data Repository is to provide access to reference data sets (e.g., controlled vocabularies, gazetteers, etc.) that are accessible on the Web and that are useful for tools like `openclean <https://github.com/VIDA-NYU/openclean-core/>`_.


Data Hosting
------------
Individual datasets may be hosted by data maintainers on different platforms. The only requirement is that the datasets (or individual dataset versions) are accessible via HTTP (single GET request). Information about all the available dataset is maintained in a central index (as a Json file) that is hosted on a version control system (e.g., GitHub, GitLab, ...).



Datasets and Data Formats
-------------------------
Each dataset has a unique identifier. Different file formats are supported for the datasets, e.g., csv files, Json, SQLIte database files, etc.. Format information for each dataset is stored as part of its entry in the global index.

Datasets are considered tabular (or sets of columns). Users may access only a single column from a dataset (e.g., country_name), multiple columns (e.b., country_name, captial_city) or the full dataset.



Local Data Repository
---------------------
Users maintain copies of the datasets for local access. By default, datasets are stored in a subfolder `.refdata` in the users home directory.
