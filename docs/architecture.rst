============
Architecture
============

Each software has some kind of architecture, and this is the place to describe it in broad terms, to make it easier for developers to get around the code. Following the scheme of a layered architecture as featured by the "Clean Architecture" (Robert Martin) or the "hexagonal architecture", alternatively known as "ports and adapters" (Alistair Cockburn), the different layers are described successively from the inside out.


Core domain
===========

The core domain contains the central entities and their abstract interactions, or, in terms of the "Domain Driven Design" (Eric Evans), the implementation of the abstract model of the application.

The central entity of the ocdb package is the :class:`ocdb.material.Material` class containing both, data and metadata, of a material, *i.e.* the optical constants and the relevant information regarding their determination.

Materials are organised into collections, each of type :class:`ocdb.material.Collection`. Different collections can exist, *e.g.* for elements, compositions, and "materials" as a general collection containing all datasets. Each collection contains its items as attributes that are themselves objects of :class:`ocdb.material.Material`. Thus, you can directly access a material, its optical constants and accompanying metadata, from within a collection.

Besides these two core classes, the core domain contains abstract factories and corresponding abstract base classes for plotters and alike, such as to decouple the core domain entirely from the outer layers. The adjacent layer outside implements concrete factories as well as concrete base classes and their descendants, all inheriting from the abstract classes implemented in the core domain. Currently, despite their name, the abstract base classes are *not* implemented in strict sense as Python ABC, although functionally they serve this purpose.


Business rules
==============

Having data is one thing, but working on and with the data requires more than simply getting the raw data. Things coming immediately to mind are interpolation of values and conversion of units. As those tasks operate on and modify the data of a :obj:`ocdb.material.Material` object, but otherwise yield a modified :obj:`ocdb.material.Material` object rather than something else, they are best referred to as "processing steps" and hence be part of the :mod:`ocdb.processing` module.

Plotting data is another issue (see the :mod:`ocdb.plotting` module for details), as is generating well-formatted reports providing an overview of the data and metadata for either single materials or entire collections (details can be found in the :mod:`ocdb.report` module.). Whether these two use cases are part of the business rules or rather of the interfaces is a matter of debate, as both require external libraries -- Matplotlib and Jinja -- that the ocdb package otherwise does not depend on and does not have as a strict requirement.

Plotting is done using descendants of the :class:`ocdb.plotting.BasePlotter` class, and the correct plotter for a given task is determined by the :class:`ocdb.plotting.PlotterFactory` class. While users of the ocdb package will directly call the :meth:`ocdb.material.Material.plot` method rather than manually instantiating plotter factories and obtain plotters, dependency inversin is implemented by means of the :class:`ocdb.material.AbstractPlotterFactory` and :class:`ocdb.material.AbstractPlotter` classes.

In any case, dependency inversion between the different layers, *i.e.* decoupling the core domain entirely from the business rules, is done via the abstract factory pattern. These abstract factories are defined within the core domain, and concrete factory classes that inherit from the abstract counterpart implemented in the modules relating to the business rules.


Interfaces
==========

Eventually, data need to come from somewhere. Hence the need for importers of actual data and accompanying metadata. This is the realm of the :mod:`ocdb.io` module, and in particular the :class:`ocdb.io.DataImporter` class and its descendants for specific data formats.

Similarly, collections ought to be created and filled for the users of the package. These housekeeping and management tasks are located in a :mod:`ocdb.management` module, and this machinery is most likely eventually called from the package ``__init__.py`` file, such that importing ocdb by means of a simple ``import ocdb`` will make the collections accessible from within the ``ocdb`` namespace immediately. If loading data becomes a time-critical issue, deferred loading of the actual data needs to be implemented.

Last but not least, management utils, *e.g.* for creating metadata files for new entries, can come in quite handy. The latter is taken care of by the :func:`ocdb.io.create_metadata_file` function.
