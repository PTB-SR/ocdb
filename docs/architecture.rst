============
Architecture
============

Each software has some kind of architecture, and this is the place to describe it in broad terms, to make it easier for developers to get around the code.


Core domain
===========

The central entity of the ocdb package is the :class:`ocdb.database.Material` class containing both, data and metadata, of a material, *i.e.* the optical constants and the relevant information regarding their determination.

Materials are organised into collections, each of type :class:`ocdb.database.Collection`. Different collections can exist, *e.g.* for elements, compositions, and "materials" as a general collection containing all datasets. Each collection contains its items as attributes that are themselves objects of :class:`ocdb.database.Material`. Thus, you can directly access a material, its optical constants and accompanying metadata, from within a collection.


Business rules
==============

Having data is one thing, but working on and with the data requires more than simply getting the raw data. Things coming immediately to mind are interpolation of values and conversion of units.

Plotting data is another issue, as is generating well-formatted reports providing an overview of the data and metadata for either single materials or entire collections.


Interfaces
==========

Eventually, data need to come from somewhere. Hence the need for importers of actual data and accompanying metadata. Similarly, collections ought to be created and filled for the users of the package. Last but not least, management utils, *e.g.* for creating metadata files for new entries, can come in quite handy.
