# Reference Data Repository - Changelog

### 0.1.0 - 2020-01-27

* Initial release.


### 0.1.1 - 2020-02-03

* Use `appdirs.user_cache_dir` as parent directory for the default target directory for downloaded files (\#5).


### 0.2.0 - 2020-02-04

* Repository index loader for different data sources. It is now possible to load the repository index from an Url, a locak file, or directly from a given dictionary.
* Support loading index files in Json or YAML format.
* Add package information and timestamp for downloaded datasets.
