=======
Roadmap
=======

A few ideas how to develop the project further, currently a list as a reminder for the main developers themselves, in no particular order, though with a tendency to list more important aspects first:


For version 0.1.rc-1
====================

* Examples section, including Jupyter notebooks?


For version 0.1
===============

* Finalise metadata schema and remove "rc-1" suffix in version number in metadata files

* DOI via Zenodo

* Initial Python package on GitHub and PyPI

* Plotting with range and different *x* axis unit?


For later versions
==================

* Integration with ``periodictable`` package

  * Bidirectional integration? Accessing data from CXRO via ``periodictable`` from within ``ocdb`` package if no data are available from OCDB; accessing OCDB data from within ``periodictable`` via extension mechanism provided by the latter.

* Consolidate structure for relevant metadata

* Support for user contributions

  * Decide upon sensible file format for data and metadata
  * Supporting packages/functionality helping to create the data in the respective format


Todos
=====

A list of todos, extracted from the code and documentation itself, and only meant as convenience for the main developers. Ideally, this list will be empty at some point.

.. todolist::

