============
Contributing
============

You want to contribute to the ocdb package? Excellent! Here, you will get some important background information regarding the necessary and available tools, the code formatting and organisation, tests, static code analysis, and how to build the documentation.


Virtual environment
===================

The whole development should take place inside a virtual python environment that should be located *outside* the project directory.

To create a new virtual python environment, open a terminal and change to a a directory where the virtual environment should reside. Then type something like:

.. code-block:: bash

    python3 -m venv ocdb

This will create a virtual environment in the directory "ocdb". To activate this virtual environment, use:

.. code-block:: bash

    source ocdb/bin/activate

To deactivate, the command would simply be:

.. code-block:: bash

    deactivate


Autoincrementing version numbers
================================

The version number is contained in the file ``VERSION`` in the project root directory. To automatically increment the version number with every commit, use a git hook that calls the file ``bin/incrementVersion.sh``. Git hooks reside in the directory ``.git/hooks``. The simplest would be to create a new file ``pre-commit`` in this directory with the following content:


.. code-block:: bash

    #!/bin/sh
    ./bin/incrementVersion.sh


Make sure to set it to executable and have a line break (aka: new or empty line) at the end of the file. Otherwise, you man run into trouble, i.e., not having your version number updated automatically with each commit.


Directory layout
================

The ocdb package follows good practice of the Python community regarding directory layout. As there will be several subpackages available, these reside each in a separate directory containing its own ``__init__.py`` file. All packages/modules reside below the ``ocdb`` directory of the project root. The ``tests`` directory follows the same structure and contains all the module tests. Generally, the ocdb package should be developed test-driven (test-first) as much as possible.

(This) documentation resides inside the ``docs`` directory of the project root. The auto-generated :doc:`API documentation <api/index>` is in its own directory.

A general overview of the overall package structure:

.. code-block:: bash

    bin/
    ocdb/
    docs/
        api/
    tests/


Code formatting
===============

Generally, code formatting follows :pep:`8` guidelines.

A consistent code formatting is enforced using `Black <https://black.readthedocs.io/>`_, with the only change to the default settings being the line width of 78 characters (as compared to the standard of 88 characters). Use ``black -l 78`` on the command line, or, preferably, configure Black in your IDE. For PyCharm (starting with 2023.2), the settings can be found in ``Preferences`` | ``Settings`` > ``Tools`` > ``Black``. Here, set ``-l 78`` as command-line options via the ``Settings`` edit field. For older PyCharm versions or other IDEs/editors see the `official Black documentation <https://black.readthedocs.io/en/stable/integrations/editors.html>`_.

To use Black, it needs to be installed. Either install it separately

.. code-block:: bash

    pip install black

or install the ocdb package with the appropriate dependencies:

.. code-block:: bash

    pip install ocdb[dev]

In case you are installing the ocdb package in editable fashion (as usual for development purposes), use the following command from *within* the package directory (*i.e.*, the one containing the ``setup.py`` file):

.. code-block::

    pip install -e .[dev]

To automatically format your Python code with every commit, use a git hook that calls the file ``bin/formatPythonFile.sh``. Git hooks reside in the directory ``.git/hooks``. The simplest would be to create a new file ``pre-commit`` with/add to the existing file in this directory the following content:

.. code-block:: bash

    ./bin/formatPythonFile.sh

For static code analysis using Prospector, see the respective :ref:`section <sec_prospector>`.


Docstring format
================

The Docstring format used within the code of the ocdb package is "NumPy". For convenience, set your IDE accordingly.

For PyCharm, the settings can be found in ``Preferences`` > ``Tools`` > ``Python Integrated Tools``. Here, you find a section "Docstrings" where you can select the Docstring format from a number of different formats.


Unittests and test driven development
=====================================

Developing the ocdb package code should be done test-driven wherever possible. The tests reside in the ``tests`` directory in the respective subpackage directory (see above).

Tests should be written using the Python :mod:`unittest` framework. Make sure that tests are independent of the respective local environment and clean up afterwards (using appropriate ``teardown`` methods).


Metacode: Conveniently adding features
======================================

The ocdb package is maintained using the `pymetacode Python package <https://python.docs.meta-co.de/>`_. In short, use the pymetacode ``pymeta`` command from the command line/terminal whenever you want to add modules, classes, or functions. This will ensure both a consistent overall style and organisation and automatically create the respective unittest stubs for you.


Setting up the documentation build system
=========================================

The documentation is built using `Sphinx <https://sphinx-doc.org/>`_, `Python <https://python.org/>`_. Building requires using a shell, for example ``bash``.


To install the necessary Python dependencies, create a virtual environment, e.g., with ``virtualenv <environment>``, and activate it afterwards with ``<environment>/bin/activate``. Then install the dependencies using ``pip``:

.. code-block:: bash

    pip install sphinx
    pip install sphinx-rtd-theme
    pip install sphinx-multiversion


Alternatively, you may simply install ocdb with the required dependencies:

.. code-block:: bash

    pip install ocdb[docs]

In case you are installing the ocdb package in editable fashion (as usual for development purposes), use the following command from *within* the package directory (*i.e.*, the one containing the ``setup.py`` file):

.. code-block::

    pip install -e .[docs]


To build the documentation:

    * Activate the virtual environment where the necessary dependencies are installed in.
    * ``cd`` to ``docs/``, then run ``make html``. (To clean previously built documentation, run ``make clean`` first).


To build the documentation for all releases and the current master branch:

  * Activate the virtual environment where the necessary dependencies are installed in.
  * ``cd`` to ``docs/``, then run ``make multiversion``. (To clean previously built documentation, run ``make clean`` first).


.. _sec_prospector:

Static code analysis with Prospector
====================================

Static code analysis can be performed using `Prospector <http://prospector.landscape.io/en/master/>`_. First, install the necessary tools into the virtual environment created for the ocdb package:

.. code-block:: bash

    pip install prospector[with_pyroma]

The optional arguments ensure that all necessary dependencies are installed as well.

Afterwards, simply run Prospector from a terminal from within your project root:

.. code-block:: bash

    prospector

It will display the results of the static code analysis within the terminal. Settings can be changed in the ``.prospector.yaml`` file in the project root, but please be very careful changing settings here. Often, it is better to (temporarily) silence warnings in the code itself.

