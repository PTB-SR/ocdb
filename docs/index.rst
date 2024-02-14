
.. _OCDB: https://www.ocdb.ptb.de/

====
ocdb
====

*Optical constants for elements and various materials in the EUV and VUV wavelengths.*

Welcome! This is the documentation for ocdb, a **Python package** for easily accessing the X-ray/EUV/VUV **scattering and absorption data** contained in the `Optical Constants Database (OCDB) <OCDB_>`_  provided by the German National Metrology Institute, the `Physikalisch-Technische Bundesanstalt, PTB <https://www.ptb.de/>`_.


Features
========

A list of (planned) features:

* Access to X-ray/EUV/VUV scattering and absorption coefficients (*n* and *k*)

* Interface compatible to the `periodictable Python package <https://pypi.org/project/periodictable/>`_

* Provides data *and* uncertainties

* FAIR and linked data: citable, reliable, and reproducible

* Community-driven: easy to contribute


And to make it even more convenient for users and future-proof:

* Open source project written in Python (>= 3.7)

* Developed fully test-driven

* Extensive user and API documentation



.. warning::
    ocdb is currently under active development and still considered in Alpha development state. Therefore, expect frequent changes in features and public APIs that may break your own code. Nevertheless, feedback as well as feature requests are highly welcome.


Installation
============

To install the ocdb package on your computer (sensibly within a Python virtual environment), open a terminal (activate your virtual environment), and type in the following:

.. code-block:: bash

    pip install ocdb


License
=======

This program is free software: you can redistribute it and/or modify it under the terms of the **GPLv3 License**.


OCDB funding
============

Development of the `Optical Constants Database (OCDB) <OCDB_>`_ containing the data the ocdb Python package provides convenient access to has been funded by the `EMPIR project 20IND04-ATMOC <https://www.atmoc.ptb.de/>`_.


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
