=======
Roadmap
=======

A few ideas how to develop the project further, currently a list as a reminder for the main developers themselves, in no particular order, though with a tendency to list more important aspects first:


For version 0.3
===============

* Plotting

  * Range and different *x* axis unit
  * Semilog and loglog plots

* Consolidate structure for relevant metadata


For later versions
==================

* Examples section, including Jupyter notebooks?

* Integration with ``periodictable`` package

  * Bidirectional integration? Accessing data from CXRO via ``periodictable`` from within ``ocdb`` package if no data are available from OCDB; accessing OCDB data from within ``periodictable`` via extension mechanism provided by the latter.

* Deferred loading of data

  * Currently, the ocdb package imports *all* data on importing the package. With more data, this will become increasingly time-consuming.

* Support for user contributions

  * Decide upon sensible file format for data and metadata
  * Supporting packages/functionality helping to create the data in the respective format


Todos
=====

A list of todos, extracted from the code and documentation itself, and only meant as convenience for the main developers. Ideally, this list will be empty at some point.

.. todolist::

