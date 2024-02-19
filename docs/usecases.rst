.. _use_cases:

.. _periodictable: https://pypi.org/project/periodictable/

.. _OCDB: https://www.ocdb.ptb.de/

=========
Use cases
=========

.. sidebar:: Contents

    .. contents::
        :local:
        :depth: 1


For the time being, the following description of use cases serves as **user manual**: it showcases specific usage scenarios focussing on those interested in the data provided by the `Optical Constants Database (OCDB) <OCDB_>`_ and provides an idea how working with the ocdb package may look like. Those interested in the details may have a look at the :doc:`API documentation <api/index>`.


General usage
=============

The ocdb package is meant to provide easy access to the values contained in the `Optical Constants Database (OCDB) <OCDB_>`_ provided by the German National Metrology Institute, the `Physikalisch-Technische Bundesanstalt, PTB <https://www.ptb.de/>`_. Furthermore it should seamlessly integrate in the `periodictable package <periodictable_>`_, at least provide an interface similar to this package.

For starters, you should import the ocdb package for further use:

.. code-block::

    import ocdb


Do not, however, import all symbols from the ocdb package (such as ``from ocdb import *``), as this messes up with your global namespace and is generally discouraged.


Exploring the database contents
===============================

The `OCDB <OCDB_>`_ contains optical constants for both, elements and compositions. Hence, three different :class:`collections <ocdb.material.Collection>` are provided at the top level of the ocdb package and are available upon importing the package:

* ``ocdb.elements``

    Optical constants for all elements data are available for in the `OCDB <OCDB_>`_.

* ``ocdb.compositions``

    Optical constants for all compositions data are available for in the `OCDB <OCDB_>`_.

* ``ocdb.materials``

    Optical constants for all elements and compositions data are available for in the `OCDB <OCDB_>`_, hence the combination of ``ocdb.elements`` and ``ocdb.materials``.

If you want to get a first overview of what data are available from the `OCDB <OCDB_>`_, you may want to get a list of all elements and compositions:

.. code-block::

    for element in ocdb.elements:
        print(element.symbol)

    for composition in ocdb.compositions:
        print(composition.symbol)


This would print the chemical symbols (or molecular formulae) for those elements and compositions data are available for in the `OCDB <OCDB_>`_.


For the elements, this should output something like:

.. code-block:: text

    Co
    Ni
    Mo
    Ru
    Te
    Ta
    Pt


How about getting all information for both, elements and compositions, at once?

.. code-block::

    for material in ocdb.materials:
        print(material.symbol)


Accessing a single element or composition
=========================================

Following the user interface of the `periodictable package <https://pypi.org/project/periodictable/>`_, accessing a single element or composition should be possible by using its name:


.. code-block::

    cobalt = ocdb.elements.Co

    taten = ocdb.compositions.TaTeN


.. note::

    Names of the individual entries (datasets) follow the convention used in  the periodictable package and are capitalised. Given the rather complicated names of the composites, capitalisation ("camel case") as used in the chemical formulae is most probably the only sensible choice, although this runs against PEP8 conventions in this particular case.


Accessing *n* and *k* values
============================

For each material/substance a database record is present in the `OCDB <OCDB_>`_, the ocdb package provides access to the data. The available data are:

* dispersion coefficient *n* (:math:`1-{\delta}`)
* extinction coefficient *k* (:math:`-{\beta}`)
* [uncertainties for *n* (lower and upper boundary)]
* [uncertainties for *k* (lower and upper boundary)]
* metadata

  * uncertainty information (if uncertainties are present, *e.g.* "3 sigma")
  * references (`bibrecord <https://bibrecord.docs.till-biskup.de/>`_ entries)

Within the ocdb package, we can directly access the data, not needing the additional ``xray`` property as an intermediate level, as in the `periodictable package <periodictable_>`_. Given the different ways of accessing the same information, following is a list of different method calls asking for the entire information (*i.e.*, returning a numpy array with two columns):

.. code-block::

    ocdb.elements.Co.n()  # -> [np.array(dtype=float), np.array(dtype=float)]

    ocdb.elements.Co.k()  # -> [np.array(dtype=float), np.array(dtype=float)]

    ocdb.elements.Co.index_of_refraction()  # -> [np.array(dtype=float), np.array(dtype=complex)]


All these will return the complete list of available values and provide wavelength values (in nm) in the first array (as this is currently the way the data are provided by the `OCDB <OCDB_>`_).


.. important::

    The values are not accessed as a property/attribute, but as a method, and without any further parameters will return an array/list of all values (to be exact: they will return a list of numpy arrays: wavelength/energy and optical constants).

    While using a method with a name that rather reflects a property (and besides that does not conform to PEP8 due to its short name) is unusual, it seems justified here, as it makes for an intuitive user interface.


.. important::

    Calling :meth:`ocdb.material.Material.index_of_refraction()` returns a complex value with both, *n* and *k* contained. Hence, we need to clearly define which convention we follow regarding signs. ;-)


.. note::

    The data contained in the `OCDB <OCDB_>`_ are not strictly X-ray data. In a long run, there will be data all the way to the far IR. Hence, summarising these values under ``xray`` (as in the `periodictable package <periodictable_>`_) would be misleading. Therefore, a much more general name needs to be found, such as "optical constants" or "fundamental parameters", when creating the extension for the `periodictable package <periodictable_>`_. For the ocdb package, we simply leave out this additional level.


Asking for uncertainties
------------------------

Users may want to get uncertainties together with the values for *n* or *k*. After all, this is one of the :doc:`essential concepts <concepts>` of the `OCDB <OCDB_>`_ and hence the ocdb package. How about this?


.. code-block::

    [co_wl, co_n, co_n_lb, co_n_ub] = ocdb.elements.Co.n(uncertainties=True)


This would return a list of *four* one-dimensional numpy arrays: wavelength, *n* lower bound, and upper bound. How lower and upper bound are defined can be looked up in the metadata.


.. note::

    If you ask for uncertainties, but no uncertainties are available from the `OCDB <OCDB_>`_, empty arrays will be returned. To check for uncertainties being present for a given material, you best use its method :meth:`ocdb.material.Material.has_uncertainties`. This method will return a Boolean value.


Asking for a specific value
---------------------------

If a user is interested in the value for a given wavelength/energy only, they may simply provide this value (hence the method call rather than accessing a property in the first place):


.. code-block::

    _, co_13_5 = ocdb.elements.Co.n(13.5)


Note that here, again, technically speaking the return value is a tuple of two numpy arrays: wavelength and optical constant. As you are usually not interested in the first if you explicitly provide only *one* specific value, you can omit it using the Pythonic ``_`` as variable name for the first return value.


.. important::

    If the user asks for a value that is no exact hit on the axis, **no interpolation** will be performed and an exception thrown. In case the user explicitly enables interpolation, as long as the value is within the overall axis range of data available from the OCDB, this will perform a *linear* interpolation. Otherwise, again an exception will be thrown. For further details, see the documentation for the :class:`ocdb.processing.Interpolation` class.


In case a user wants to get interpolated values, they need to be explicit about this. The reason for this design decision is to make users aware of the actual measured data.


.. code-block::

    ocdb.elements.Co.n(12.123, interpolation=True)


Asking for a range of values
----------------------------

A single value or all available values for a material are nice, but how about a certain range of values (perhaps with a user-defined spacing)?


.. code-block::

    range_ = np.linspace(10, 12, 21)  # [10.0, 10.1, 10.2, ..., 12.0]
    ocdb.elements.Co.n(range_)


As with single values (see above), this will throw an exception if (some of) the values provided are no direct hits on the axis. In order to get interpolated values, the user needs to be explicit about this:

.. code-block::

    range_ = np.linspace(10, 12, 201)  # [10.00, 10.01, 10.02, ..., 12.00]
    ocdb.elements.Co.n(range_, interpolation=True)


Asking for explicit units
-------------------------

Although the primary data currently available from the `OCDB <OCDB_>`_ provide a wavelength scale (in nm), users may want to get other units (such as eV) as well:


.. code-block::

    ocdb.elements.Co.n(unit="eV")


.. todo::
    Unit conversion is not yet implemented, but planned for the first release (version 0.1) for "eV".


References for values
=====================

One idea behind the ocdb package, besides providing uncertainties for the values, is to have "FAIR" and citable values/data. Hence, for each material/substance, there are references for the values that allows for citing the correct paper/source.

Thanks to the `bibrecord package <https://bibrecord.docs.till-biskup.de/>`_, accessing the bibliographic data of the relevant references should be straight-forward:

.. code-block::

    print(ocdb.elements.Co.references[0].to_string())

would result in the following string:

.. code-block:: text

    Qais Saadeh, Philipp Naujok, Devesh Thakare, Meiyi Wu, Vicky Philipsen, Frank Scholze, Christian Buchholz, Zanyar Salami, Yasser Abdulhadi, Danilo Ocaña García, Heiko Mentzel, Anja Babuschkin, Christian Laubis, Victor Soltwisch: On the optical constants of cobalt in the M-absorption edge region. Optik 273:17045, 2023.

For more options, *e.g.* a full BibTeX record, see the `bibrecord package <https://bibrecord.docs.till-biskup.de/>`_. Usually, a DOI will be available for each reference. Those interested in a quick and easy way to retrieve the reference may use something like:

.. code-block::

    print(ocdb.elements.Co.references[0].doi)

resulting (currently) in:

.. code-block:: text

    10.1016/j.ijleo.2022.170455

ready for copy&paste into your preferred literature search and retrieval tool.


Plotting values
===============

Plotting values should be straight-forward. However it is sometimes convenient to have plot methods for each material readily available. The following plots are immediately obvious:

* plot of *n* vs. wavelength
* plot of *k* vs. wavelength
* plot of both, *n* and *k*, vs. wavelength in one plot

  * two axes left and right, for *n* and *k*, respectively, and colour-coded for easily assigning the values to the axes.

* plot of *n* or *k* vs. wavelength with uncertainties
* plot of both, *n* and *k*, vs. wavelength with uncertainties in one plot

All plots should automatically provide correct axis labels and perhaps a title displaying the material the data are plotted for. In case of plotting both, *n* and *k* values, the two separate *y* axes are colour-coded to allow for easily assigning the data to their axes.


.. important::

    The ocdb package purposefully does *not* depend on Matplotlib, due to its many dependencies. Therefore, if you install ocdb without further explicit dependencies, you may not have Matplotlib available and plotting will not work. However, as soon as Matplotlib is available from within your Python installation/virtual environment, plotting as shown below will work.


In the simplest form, plotting data of a given substance is as easy as:

.. code-block::

    ocdb.elements.Co.plot()

This will simply plot the *n* values of the given dataset, in our case that of Cobalt.

Plots can be customised and controlled in quite some detail by specifying additional key--value pairs to the :meth:`ocdb.material.Material.plot` method:

.. code-block::

    ocdb.elements.Co.plot(values="both", uncertainties=True)

This would plot both, *n* and *k* values and graphically depict their uncertainties (if available). If no uncertainties are available, a warning should be issued.

Similarly, we may want to provide a range and unit for the *x* axis:

.. code-block::

    ocdb.elements.Co.plot(range=[80, 124], unit="eV")

    ocdb.elements.Co.plot(values="both", uncertainties=True, range=[80, 124], unit="eV")


.. todo::

    Plotting ranges and different units for the *x* axis are not yet implemented.

