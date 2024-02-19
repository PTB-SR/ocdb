
.. _OCDB: https://www.ocdb.ptb.de/

====
ocdb
====

*Optical constants for elements and various materials in the EUV and VUV wavelengths.*

Welcome! This is the documentation for ocdb, a **Python package** for easily accessing the X-ray/EUV/VUV **scattering and absorption data** contained in the `Optical Constants Database (OCDB) <OCDB_>`_  provided by the German National Metrology Institute, the `Physikalisch-Technische Bundesanstalt, PTB <https://www.ptb.de/>`_.

This is a first glimpse on how working with the ocdb package may look like:

.. code-block::

    import ocdb

    # All available values for n
    [co_wl, co_n] = ocdb.elements.Co.n()

    # Complex index of refraction for a given wavelength
    _, co_13_5 = ocdb.elements.Co.index_of_refraction(13.5)

    # All available values for k with uncertainties
    [co_wl, co_k, co_k_lb, co_k_ub] = ocdb.elements.Co.k(uncertainties=True)

For further details, have a look at the :doc:`use cases <usecases>` section.


Features
========

A list of (planned) features:

* Access to X-ray/EUV/VUV scattering and absorption coefficients (*n* and *k*)

* Interface compatible to the `periodictable Python package <https://pypi.org/project/periodictable/>`_

* Provides data *and* uncertainties

* FAIR and linked data: citable, reliable, and reproducible

* Community-driven: easy to contribute


And to make it even more convenient for users and future-proof:

* Open source project written in Python (>= 3.9)

* Developed fully test-driven

* Extensive user and API documentation


.. warning::
    The ocdb package is currently under active development and still considered in beta development state. Therefore, expect frequent changes in features and public APIs that may break your own code. Nevertheless, feedback as well as feature requests are highly welcome.


Requirements
============

The ocdb package comes with a rather minimal set of requirements:

* Python >= 3.9
* numpy, oyaml, and bibrecord packages

In case you would like to make use of the optional plotting and report generating capabilities, you would need to install additional dependencies, namely Matplotlib (with all its dependencies) and Jinja. Have a look at the :doc:`installation instructions <installing>` for further details.


.. _sec-how_to_cite:

How to cite
===========

The Python ocdb package is free software. However, if you use it for your own research, please consider to cite it appropriately:

  * Till Biskup. The ocdb Python package (2024). `doi:10.5281/zenodo.######## <https://doi.org/10.5281/zenodo.########>`_

Furthermore, if you use the data the ocdb package provides access to for your own research, use the appropriate references for each individual dataset, as available from its metadata. Have a look at the documentation of the :class:`ocdb.material.Material` class for details how to conveniently obtain the relevant bibliographic data, either as string or as BibTeX record.


Installation
============

To install the ocdb package on your computer (sensibly within a Python virtual environment), open a terminal (activate your virtual environment), and type in the following:

.. code-block:: bash

    pip install ocdb


Have a look at the more detailed :doc:`installation instructions <installing>` as well.


License
=======

This program is free software: you can redistribute it and/or modify it under the terms of the **GPLv3 License**. Please note that this license only applies to the ocdb Python package, *not* to the data contained in the `Optical Constants Database (OCDB) <OCDB_>`_. The data themselves are licensed under CC BY 4.0, if not explicitly stated otherwise. If you use the ocdb Python package or the data contained in the OCDB, please cite the relevant references. See the :ref:`How to cite <sec-how_to_cite>` section for further details.


OCDB funding
============

Development of the `Optical Constants Database (OCDB) <OCDB_>`_ containing the data the ocdb Python package provides convenient access to has been funded by the `EMPIR project 20IND04-ATMOC <https://www.atmoc.ptb.de/>`_.


Logo
====

The copyright of the logo of the `Optical Constants Database (OCDB) <OCDB_>`_ used here for the Python ocdb package belongs to Victor Soltwisch.


.. toctree::
   :maxdepth: 2
   :caption: User Manual:
   :hidden:

   audience
   concepts
   usecases
   installing

.. toctree::
   :maxdepth: 2
   :caption: Developers:
   :hidden:

   people
   contributing
   architecture
   changelog
   roadmap
   api/index
