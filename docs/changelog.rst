
.. _OCDB: https://www.ocdb.ptb.de/

.. _GITHUB_REPO: https://github.com/PTB-SR/ocdb

.. _PYPI: https://pypi.org/project/ocdb/

=========
Changelog
=========

This page contains a summary of changes between the official ocdb releases. Only the biggest changes are listed here. A complete and detailed log of all changes is available through the `GitHub Repository Browser <GITHUB_REPO_>`_.


Version 0.2.0
=============

Not yet released

New features
------------

* :class:`ocdb.io.TxtDataExporter` for data


Changes
-------

* New header format for the data files

    * Formalised header with consistent content.
    * Header format does not impact the importer.


Version 0.1.2
=============

Released 2024-06-11


Fixes
-----

* Dependency in ``docs/requirements.txt`` to build API docs


Version 0.1.1
=============

Released 2024-02-29


Fixes
-----

* Dependency in ``setup.py``: ``jinja2`` rather than ``jinja``
* Date in metadata of old Ru dataset


Version 0.1.0
=============

Released 2024-02-23

* First public release

* Package available via `PyPI <PYPI_>`_, code via `GitHub <GITHUB_REPO_>`_

* DOI via Zenodo: https://doi.org/10.5281/zenodo.10697496


Version 0.1.0.rc-1
==================

Released 2024-02-23

* First public pre-release

* General user interface for accessing optical constants contained in the `Optical Constants database <OCDB_>`_.

* Package available via `PyPI <PYPI_>`_, code via `GitHub <GITHUB_REPO_>`_
