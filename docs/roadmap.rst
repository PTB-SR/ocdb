=======
Roadmap
=======

A few ideas how to develop the project further, currently a list as a reminder for the main developers themselves, in no particular order, though with a tendency to list more important aspects first:


For version 0.1
===============

* Design data structures and user interface

  * For starters, only ``ocdb`` user interface, not yet integrated into ``periodictable``.
  * User interface is described in the :doc:`Use cases <usecases>` section.

* Decide upon a data file format for the actual data

  * For starters, probably simply the text files from the OCDB, accompanied by YAML files with the relevant metadata and a BibTeX file with the references.

* Initial Python package on GitHub and PyPI


For later versions
==================

* Integration with ``periodictable`` package

  * Bidirectional integration? Accessing data from CXRO via ``periodictable`` from within ``ocdb`` package if no data are available from OCDB; accessing ODCB data from within ``periodictable`` via extension mechanism provided by the latter.

* Consolidate structure for relevant metadata

* Support for user contributions

  * Decide upon sensible file format for data and metadata
  * Supporting packages/functionality helping to create the data in the respective format


Todos
=====

A list of todos, extracted from the code and documentation itself, and only meant as convenience for the main developers. Ideally, this list will be empty at some point.

.. todolist::

