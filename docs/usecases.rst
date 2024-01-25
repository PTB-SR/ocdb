.. _use_cases:

=========
Use cases
=========

.. sidebar:: Contents

    .. contents::
        :local:
        :depth: 1


For the time being, the following description of use cases is rather an idea how working with the ocdb package may look like than a description of what actually can be achieved.


General usage
=============

The ocdb package is meant to provide easy access to the values contained in the `Optical Constants Database (OCDB) <https://www.ocdb.ptb.de/>`_ provided by the German National Metrology Institute, the `Physikalisch-Technische Bundesanstalt, PTB <https://www.ptb.de/>`_. Furthermore it should seamlessly integrate in the `periodictable package <https://pypi.org/project/periodictable/>`_, at least provide an interface similar to this package.

For starters, you should import the ocdb package for further use:

.. code-block::

    import ocdb


Do not, however, import all symbols from the ocdb package (such as ``from ocdb import *``), as this messes up with your global namespace and is generally discouraged.


Exploring the DB contents
=========================

If you want to get a first overview of what data are available from the OCDB, you may want to get a list of all elements and compositions:

.. code-block::

    for element in ocdb.elements:
        print(element.symbol)

    for composition in ocdb.compositions:
        print(composition.symbol)


This would print the chemical symbols for those elements and compositions data are available for in the OCDB.


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


.. todo::

    Decide whether ``materials`` is the right name here, or whether we would rather like to go with ``substance``. In any case, the name should be general enough and intuitive enough to cover the concept that both, elements and compositions are covered.

    **Answer:** ``materials`` is probably the better name in the given (local) context of the OCDB, where people deal with materials.


Accessing a single element or composition
=========================================

Following the user interface of the `periodictable package <https://pypi.org/project/periodictable/>`_, accessing a single element or composition should be possible by using its name:


.. code-block::

    cobalt = ocdb.elements.Co

    taten = ocdb.compositions.TaTeN


.. todo::

    Decide whether to use capitalised names, as in the periodictable package, or to stick with PEP8 naming conventions. Probably, capitalised names are much more intuitive and easier to read.

    **Answer:** Given the rather complicated names of the composites, capitalisation as used in the chemical formulae is most probably the only sensible choice, although this runs against PEP8 conventions in this particular case.


Accessing *n* and *k* values
============================

For each material/substance a database record is present in the OCDB, the ocdb package provides access to the data. The available data are:

* *n* (:math:`1-{\delta}`)
* *k* (:math:`-{\beta}`)
* [uncertainties for *n* (lower and upper boundary)]
* [uncertainties for *k* (lower and upper boundary)]
* metadata

  * sample information
  * measurement information (at least date)
  * uncertainty information (if uncertainties are present, *e.g.* "3 sigma")
  * reference (`bibrecord <https://bibrecord.docs.till-biskup.de/>`_ entry if citable reference)


.. todo::

    *n* and *k* values are available for different wavelength ranges and with different sampling of the wavelength axis for the different elements and compositions. Furthermore, the wavelength axes are not necessarily equidistant. How to deal with a user wanting to access the value for a certain wavelength (or energy)? Interpolate, and if so, how (linear, cubic, spline, ...)?

    Raw data as provided by OCDB seem to provide *n* and *k* values. Provide methods for getting delta and beta instead?

    Provide data as complex float? Or *n* and *k* separately?

    **Answer:** Both, *n* and *k* separately (and uncertainties with them), and a property ``index_of_refraction`` (note: ``refractive_index`` would be an alternative, though ``index_of_refraction`` would be compatible to ``periodictable``) as complex float. Uncertainties need to be both, lower and upper boundary, as the distribution might not be strictly symmetric.

    Generally, the wavelength axis should be either a separate property or the first row/column in a matrix.


.. todo::

    How to provide uncertainties? Matrix with two columns/rows for lower and upper bound for each wavelength entry? Add wavelength as first row/column (only if wavelength is not a separate property)?


If no uncertainties are available, return simply ``None`` ("principle of least surprise").


.. todo::

    Decide upon a structure for the metadata. Currently, this information is contained in a somewhat human-readable (though not strictly machine-readable) form in the header of the data files.

    Important metadata (VS):

    * layer thickness
    * substrate
    * date of measurement
    * sample preparation details (ideally eventually a DOI)


Within the ocdb package, we could directly access the data, and we would not need to have an additional ``xray`` property as an intermediate level. Hence, there would be two ways to access all *n* values of an element/substance:

.. code-block::

    ocdb.elements.Co.n()

    ocdb.elements.xray.n()


.. important::

    The values are not accessed as a property/attribute, but as a method, and without any further parameters will return an array/list of all values (to be exact: they will return a list of numpy arrays: wavelength/energy and optical constant).

    While using a method with a name that rather reflects a property (and besides that does not conform to PEP8 due to its short name) is unusual, it seems justified here, as it makes for an intuitive user interface.


.. todo::

    Are the data contained in the OCDB strictly X-ray data? If not (and at least VUV probably does not count as X-ray any more), summarising these values under ``xray`` may be misleading. Is there a better general name for this wavelength range?

    **Answer** In a long run, there will be data all the way to the far IR. Hence, a much more general name needs to be found, such as "optical constants" or "fundamental parameters". For the time being, perhaps simply leave out this additional level.


Given the different ways of accessing the same information, following is a list of different method calls asking for the entire information (*i.e.*, returning a numpy array with two columns):

.. code-block::

    ocdb.elements.Co.n()  # [np.array(dtype=float), np.array(dtype=float)]

    ocdb.elements.Co.k()  # [np.array(dtype=float), np.array(dtype=float)]

    ocdb.elements.Co.index_of_refraction()  # [np.array(dtype=float), np.array(dtype=complex)]


All these will return the complete list of available values and provide wavelength values (in nm) in the first array (as this is currently the way the data are provided by the OCDB).


.. important::

    Calling ``index_of_refraction()`` returns a complex value with both, *n* and *k* contained. Hence, we need to clearly define which convention we follow regarding signs. ;-)


Asking for explicit units
-------------------------

Although the primary data currently available from the OCDB provide a wavelength scale (in nm), users may want to get other units (such as eV) as well:


.. code-block::

    ocdb.elements.Co.n(unit="eV")


Asking for uncertainties
------------------------

Users may want to get uncertainties together with the values for *n* or *k*. How about this?


.. code-block::

    ocdb.elements.Co.n(uncertainties=True)


This would return a list of *three* numpy arrays, the first two one-dimensional, the third two-dimensional with lower and upper bound. How lower and upper bound are defined can be looked up in the metadata.

And of course, this could be combined with asking for an explicit unit for the energy/wavelength axis:


.. code-block::

    ocdb.elements.Co.n(uncertainties=True, unit="eV")


Asking for a specific value
---------------------------

If a user is interested in the value for a given wavelength/energy only, they may simply provide this value (hence the method call rather than accessing a property in the first place):


.. code-block::

    ocdb.elements.Co.n(10.0)


And if users like energies (in eV) more than wavelengths (in nm):


.. code-block::

    ocdb.elements.Co.n(91.84, unit="eV")  # 91.84 ~= 13.5 nm


.. note::

    As long as the value is within the overall axis range of data available from the OCDB, this will perform a *linear* interpolation (allow for other interpolation methods later?). Otherwise, ``np.nan`` will be returned.


Asking for a range of values
----------------------------

A single value or all available values for a material are nice, but how about a certain range of values (perhaps with a user-defined spacing)?


.. code-block::

    range_ = np.linspace(10, 12, 21)  # [10.0, 10.1, 10.2, ..., 12.0]
    ocdb.elements.Co.n(range_)


.. note::

    As long as the range is within the overall axis range of data available from the OCDB, this will perform a *linear* interpolation (allow for other interpolation methods later?). Otherwise, ``np.nan`` will be returned.


Reference for values
====================

One idea behind the ocdb package, besides providing uncertainties for the values, is to have "FAIR" and citable values/data. Hence, for each material/substance, there should be a reference for the values that allows for citing the correct paper/source.

Thanks to the `bibrecord package <https://bibrecord.docs.till-biskup.de/>`_, this should be straight-forward:

.. code-block::

    print(ocdb.elements.Co.reference.to_string())

would result in the following string:

.. code-block:: text

    Qais Saadeh, Philipp Naujok, Devesh Thakare, Meiyi Wu, Vicky Philipsen, Frank Scholze, Christian Buchholz, Zanyar Salami, Yasser Abdulhadi, Danilo Ocaña García, Heiko Mentzel, Anja Babuschkin, Christian Laubis, Victor Soltwisch: On the optical constants of cobalt in the M-absorption edge region. Optik 273:17045, 2023.

For more options, *e.g.* a full BibTeX record, see the `bibrecord package <https://bibrecord.docs.till-biskup.de/>`_.

In case of no separate reference for a substance/material, a general reference to the OCDB should be returned, probably https://zenodo.org/doi/10.5281/zenodo.5602718.


Accessing relevant metadata
===========================

A key aspect of the ocdb package and a strict requirement from a scientific point of view is access to relevant metadata. Those metadata include (but may not be limited to):

* layer thickness
* substrate
* date of measurement
* sample preparation details (ideally eventually a DOI)
* information regarding the uncertainty values (such as ":math:`3\sigma`")

For the time being, just providing a :class:`dict` with respective fields is probably the most sensible solution. However, this interface should be regarded as unstable and not for general use.

It might be interesting though to provide a method displaying a summary of the available information in textual format:


.. code-block::

    ocdb.elements.Co.metadata.to_string()


This would require ``metadata`` to be a class rather than a plain :class:`dict`. Alternatively, one could provide the same information by just using ``print`` on the metadata as such:


.. code-block::

    print(ocdb.elements.Co.metadata)


Again, this requires ``metadata`` to be a class rather than a plain :class:`dict`.


Plotting values
===============

Plotting values should be straight-forward, however it might be convenient to provide plot methods for each material. The following plots would be immediately obvious:

* plot of *n* vs. wavelength
* plot of *k* vs. wavelength
* plot of both, *n* and *k*, vs. wavelength in one plot

  * one joint *y* axis? or two axes left and right, for *n* and *k*, respectively?

* plot of *n* or *k* vs. wavelength with uncertainties
* plot of both, *n* and *k*, vs. wavelength with uncertainties in one plot

All plots should automatically provide correct axis labels and perhaps a title displaying the material the data are plotted for. In case of plotting both, *n* and *k* values, a legend would be nice to have as well.

In the simplest form, plotting should be as easy as:

.. code-block::

    ocdb.elements.Co.plot()


We may want to parametrise the plot by specifying additional key--value pairs:

.. code-block::

    ocdb.elements.Co.plot(values="both", uncertainties=True)

This would plot both, *n* and *k* values and graphically depict their uncertainties (if available). If no uncertainties are available, a warning should be issued.

Similarly, we may want to provide a range and unit for the *x* axis:

.. code-block::

    ocdb.elements.Co.plot(range=[80, 124], unit="eV")

    ocdb.elements.Co.plot(values="both", uncertainties=True, range=[80, 124], unit="eV")
