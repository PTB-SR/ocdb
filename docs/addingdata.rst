
.. _OCDB: https://www.ocdb.ptb.de/

===========
Adding data
===========

The purpose of the ocdb package is to provide easy access to the data for optical constants contained in the `Optical Constants Database (OCDB) <OCDB_>`_. As detailed in the section on :doc:`essential concepts <concepts>`, uncertainties, transparency and reproducibility as well as a history of records are the crucial aspects the ocdb package contributes to the community.

While the ocdb Python package will be further developed (if you are interested in contributing, see the :doc:`guide how to contribute to the package development <contributing>`), the data available from the `Optical Constants Database (OCDB) <OCDB_>`_ will continuously being updated and expanded. How to add data from the OCDB to the ocdb package will be described here, covering the necessary details of package and data organisation.


.. note::

    The ocdb package provides an interface to the data available from the `Optical Constants Database (OCDB) <OCDB_>`_. However, the package developers and maintainers are not responsible for the quality and validity of the data. For each dataset there will be references covering necessary details on how the optical constants have been determined. Nevertheless, a gap-less protocol of the data processing and analysis starting with the raw data from measurements all the way to the final *n* and *k* values is out of scope of the ocdb package. See the :ref:`discrimination between dataset and measurement <sec-dataset_vs_measurement>` for a bit more details.


Overview: How to add data
=========================

Adding data to the ocdb package consists basically of three steps that can be separated and even be carried out by different persons:

#. Obtaining the relevant information (data and metadata)
#. Creating the relevant files (for data and metadata)
#. Adding the files to the ocdb package

This section will briefly go through each of these steps and explain the necessary details.


.. important::

    This section assumes familiarity with the ocdb package and its organisation and is only meant as a reminder for routine management tasks, and *not* as a replacement for the detailed reading of the other sections below.


Obtaining the relevant information
----------------------------------

The OCDB contains optical constants and their uncertainties for different materials. Where these data come from is *not* the responsibility of the ocdb package maintainers and out of scope of this package. Nevertheless, the important part from the ocdb package point of view is to have the complete set of necessary information at hand, as there is:

* numerical data for the optical constants (*n* and *k*)

* uncertainties for *n* and *k* (if available)

* citable reference(s) for the data

  * all information necessary for a full bibliographic record eventually stored in BibTeX format

* metadata

  * date the dataset has been created (*not* necessarily the date of measurement)
  * details on the uncertainties (if uncertainties are available)

Once all this information is available, you can proceed to the next step.


Creating the relevant files
---------------------------

Two files need to be created:

#. the metadata file in YAML format, and
#. the data file (currently in text format).


Creating the metadata file
~~~~~~~~~~~~~~~~~~~~~~~~~~

Creating the scaffold for the metadata file in YAML format is straight-forward, and assuming the ocdb package installed effectively a two-liner:


.. code-block::

    import ocdb.io
    ocdb.io.create_metadata_file("<name>.yaml")


This will create the file ``<name>.yaml`` in the current directory. Make sure to replace ``<name>`` with a sensible string. Typically, this is the element symbol in case of an element or the molecular formula in case of compositions. Use the text editor of your liking afterwards to add the relevant metadata to this file.


Creating the data file
~~~~~~~~~~~~~~~~~~~~~~

Creating the data file is similarly straight-forward once you have an :obj:`ocdb.material.Material` object with all its fields set appropriately:

#. Create an exporter
#. Set its ``material`` attribute to the material created
#. Call the ``export`` method

In code, this looks like:


.. code-block::

    import ocdb.io
    import ocdb.material

    material = ocdb.material.Material()
    # Provide relevant content, including data and metadata

    exporter = ocdb.io.TxtDataExporter()
    exporter.material = material
    exporter.export()

This will create the appropriate text file with the symbol of the given
material as the file basename and ``.txt`` as file extension in the current directory.

The crucial part, however, is to set all the relevant attributes in the :obj:`ocdb.material.Material` object. For *n* and *k* values and their uncertainties, this should be rather straight-forward, assuming a basic familiarity with the organisation of the :class:`ocdb.material.Material` class and its attributes. Adding the reference(s) is slightly more involved.


Adding reference(s)
~~~~~~~~~~~~~~~~~~~

References are eventually stored in a BibTeX file in the ocdb package data. As adding data to the package requires the source code of the package to be available, you will find the BibTeX file as ``ocdb/db/literature.bib``. Make sure the reference you need for your new dataset is already contained in this BibTeX database and has an appropriate unique key. You need to know this BibTeX key in the next step. If the BibTeX entry for the reference for your new dataset exists in the BibTeX database file, things are comparably straight-forward:

#. Create an :obj:`ocdb.io.References` object, and
#. add the approriate reference to your :obj:`ocdb.material.Material` object.

In code, this looks like:


.. code-block::

    import ocdb.io
    import ocdb.material

    material = ocdb.material.Material()
    # Provide relevant content, including data and metadata

    references = ocdb.io.References()
    material.references.append(references.records[<BibTeX-key>])


Assuming again, as above, that you have added all the other data and metadata to your :obj:`ocdb.material.Material` object, this will add the relevant citable reference to your material. Of course, if there is more than one reference, you can add multiple references as well. Just make sure that the number and sequence of references you set manually in this step is identical to the metadata (*i.e.* BibTeX keys) provided in the metadata file you've created as discussed above.


Adding the files to the ocdb package
------------------------------------

.. note::

    This should usually only be done by the package maintainers, as adding data involves, *i.a.*, making a new release. You are, however, welcome to fork the official repository, add the data to your local fork, and create a pull request.


Once you have both, data and metadata files, created and with correct content, it is time to add the files (and hence the data) to the ocdb package. Again, this requires the source code of the ocdb package to be available. The data file goes into the ``ocdb/db/data`` directory, and the metadata file in either of the subdirectories of ``ocdb/db/metadata``, depending on whether your newly created dataset describes an element or a composition. For details, see the (next) section on :ref:`package organisation <sec-package_organisation>`. If you want to add a *new version* of an existing dataset, things get a bit more complicated. For details, see the respective section on :ref:`versions of datasets <sec-versions_of_datasets>` below.



.. _sec-package_organisation:

Package organisation
====================

Data and corresponding metadata are contained as "package data" within the ocdb Python package. As adding data means that you need to have access to the source code of the package, it does not matter that package data in Python packages are not paths in the file system, strictly speaking.

A brief overview of the overall package structure -- in terms of the directories of its source code:

.. code-block:: text

    .
    ├── bin
    ├── docs
    ├── ocdb
    │   └── db
    │       ├── data
    │       └── metadata
    │           ├── compositions
    │           └── elements
    └── tests

The crucial part here is the directory ``db`` (shorthand for "database") residing in the ``ocdb`` subdirectory where all the Python code of the package can be found. As you can see, the database is organised into ``data`` and ``metadata`` subdirectories, where the latter is partly misleading, strictly speaking. But more on this (and the reason why) later. Two important rules:

* All data, *i.e.* files containing the actual optical constants of the diverse materials, reside in the ``data`` directory.

* The subdirectories of the ``metadata`` directory contain *only* metadata, with an organisational separation between (chemical) elements and compositions, *i.e.* all materials that are *not* (chemical) elements.

That means, in short: If you add a new dataset to the ocdb package, you will add the data file to the ``ocdb/db/data`` directory, while the metadata file goes into one of the subdirectories of the ``ocdb/db/metadata/`` directory, depending on whether it is an element or not.

Furthermore, in the ``db`` directory resides a BibTeX file ``literature.bib`` containing the BibTeX records for all citable references.


Metadata
========

Data without context are usually useless. One of the promises of the ocdb package is to provide its users not only with easy access to the optical constants contained in the `Optical Constants Database (OCDB) <OCDB_>`_, but with relevant (minimal) metadata, including a citable reference with further details.

To this end, each and every dataset in the ocdb package consists of two files: a metadata file in YAML format, and a data file. For the format of the latter, see below. The **format of the metadata files** is described in greater detail in the :mod:`ocdb.io` module documentation. See there for details.

Important to note here is: You do not need to create such a metadata file by yourself, but can get it created for you. The full sequence of steps, assuming a working Python installation and the ocdb package installed (typically within a virtual environment, see the :doc:`installation instructions <installing>` for details), looks like:

.. code-block::

    import ocdb.io
    ocdb.io.create_metadata_file("<name>.yaml")

This will create the file ``<name>.yaml`` in the current directory. Make sure to replace ``<name>`` with a sensible string. Typically, this is the element symbol in case of an element or the molecular formula in case of compositions.


References
==========

One key concept of the OCDB and hence the ocdb package is to provide citable references for each individual dataset. To this end, there exists a BibTeX database containing all relevant references. The BibTeX database is stored in the file ``literature.bib`` in the ``db`` directory.

If you add datasets to the ocdb package, make sure to add the references to the BibTeX database as well, and adhere to the overall structure and formatting of the bibliographic records found in the file. The references are processed using the `bibrecord package <https://bibrecord.docs.till-biskup.de/>`_, and this package is currently not meant as a general BibTeX parser. Hence, not everything allowed in BibTeX is allowed in the BibTeX database used by the ocdb package.


Data format
===========

Data files are currently provided as plain text files in the `Optical Constants Database (OCDB) <OCDB_>`_. The same file format is used inside the ocdb Python package. This file format may change in the future, but this is of no concern for any user of the ocdb package. As long as for each individual file format, there exists an implemented importer class, and each file format can be addressed by a unique name within the metadata file, everything should work as expected.

To give you an idea how such a data file looks like, below are the first few lines of one dataset from the `Optical Constants Database (OCDB) <OCDB_>`_:

.. code-block:: text

    # Optical constants for Co created by PTB
    # Reconstructed from reflection measurements in the wavelength range 8 - 25 nm
    # 40 nm Co thin film in a multilayer on Si (C/ Co/ Ru/ Si) (measured 4/2022)
    # n = (1-delta) - (i*beta)
    # The values are provided with their 3-sigma uncertainty bounds. HB: Higher Bound. LB: Lower Bound.
    #lambda/nm	1-delta	beta	1-delta_LB	1-delta_HB	beta_LB	beta_HB
    # ------------------------
    8.0	0.96788	0.02267	0.96772	0.96804	0.02253	0.0228
    8.1	0.96713	0.02328	0.96697	0.96729	0.02315	0.02341
    8.2	0.96639	0.02393	0.96623	0.96656	0.0238	0.02407
    8.3	0.96564	0.02463	0.96546	0.96581	0.0245	0.02477

As you can see, there is a series of header lines marked with ``#`` and describing in some detail the following data, and the actual data appear in seven columns, separated by tabulators. Uncertainties are provided as lower and upper bound for both, *n* and *k*. Hence, if no uncertainties are contained in the dataset, the data file will consist of only three columns.

While this text format may not be the final format of the data in the OCDB and in the ocdb package, it is the format for the time being. Hence, a few more details will be given below. Plain text formats have one clear advantage over any binary format: they are generally and even human readable without need for any special program. The biggest disadvantage in the given context is their potentially limited accuracy of the numeric values.


Header
------

Generally, header lines start with ``#``. This makes it simple to read the files with many generic programs and routines. The header should contain minimal information on the material, who (institution) measured it when (date accurate to a month) and how (reflection, absorption, ...), how the optical constants are defined, what the data columns mean, and if present, how to interpret the values for the uncertainties. The overall aim of the header is to provide all relevant context for a person having only this data file to make reasonable sense of it.

Details of a given sample, as can be seen in the example above, are purely optional and will probably be removed in the future, as datasets will span a broad range of wavelengths/energies measured at different setups with (slightly) different samples.


.. note::

    A more formal definition of the header contents and its structure will probably come together with implementing a data exporter.


Restructuring the header
~~~~~~~~~~~~~~~~~~~~~~~~

The current header of the text files contained in the OCDB is not really specified, and it contains information that is obsolete given the scope of the OCDB (datasets that will soon span more than one individual sample and measurement, hence sample and measurement-specific information), while missing other relevant information (such as a link to the OCDB, to the PTB, and the reference).

Hence, for the time being this section will discuss and present ideas how to restructure the header. Once this converges, the result will be documented, probably on this page and in the exporter to be written. Furthermore, once we arrive at a reasonable header format, we can reexport all available data of the OCDB from within the ocdb package.

Necessary information in the header:

* Reference to the OCDB and perhaps the PTB

* Version identifier of the file format

* Material the optical constants are provided for

* Date (at least accurate to a month) the dataset has been created (the dataset, *not* the measurements)

* Definition of the complex refractive index, and accordingly *n* and *k* as provided

* Definition of the uncertainties if present

* Reference that shall be cited when using the data (yes, people will usually use the ocdb package, but as the data will be provided as text files via the OCDB webpage, this independent information is relevant and should be contained *in* the actual data file)

* License

  Whether we can apply licenses to data at all is highly debated, but as soon as you submit something to Zenodo, it will need a license, and this is usually CC-By 4.0. This is what is currently stated in the ocdb package as license for the data, and it is in line with good scientific practice to cite appropriately (and it does *not* matter that people don't do that -- too many scientists do not adhere to the standards of good scientific practice).

* Header of the data columns

How could all that look like? Here is a first example. Values in brackets ``[]`` are optional, values in angle brackets ``<>`` need to be replaced by actual values:

.. code-block:: text

    # OCDB data - format: 1.1
    #
    # Optical Constants Database (OCDB) - https://www.ocdb.ptb.de/
    # operated by the Physikalisch-Technische Bundesanstalt (PTB),
    # the German National Metrology Institute: https://www.ptb.de/
    #
    # For easy access to these data, check out the Python ocdb package:
    # https://pypi.org/project/ocdb/
    #
    # Optical constants for <material>
    # Determined from reflection measurements
    #
    # Created: [DD/]MM/YYYY
    # License: CC BY 4.0 <http://creativecommons.org/licenses/by/4.0/>
    # Reference: https://doi.org/<DOI>
    #
    # Complex refractive index defined as: n = (1-delta) - (i*beta)
    #
    # [The values are provided with their 3-sigma uncertainty bounds.]
    # [LB: lower bound, UB: upper bound.]
    #
    # Columns are separated by tabulator (\t).
    #
    # wavelength/nm	1-delta	beta	1-delta_LB	1-delta_UB	beta_LB	beta_UB
    # ------------------------
    8.00	0.96788	0.02267	0.96772	0.96804	0.02253	0.0228

For the time being, all *n* and *k* values will be determined from reflection measurements.


Data
----

While the primary axis of datasets can be both, wavelength (in nm) and energy (in eV), datasets contained in the OCDB will always have wavelength as their primary axis, to an accuracy of 0.01 nm. In case data were recorded with a primary energy axis (in eV), they will be converted to a wavelength axis with the given accuracy of 0.01 nm. This is justified by the given energy range and instrument resolution.

Data columns are separated by tabulators (``\t``), the accuracy of the numeric values may differ for different datasets, but should be reasonable.


.. _sec-versions_of_datasets:

Versions of datasets
====================

The data provided by the `OCDB <OCDB_>`_ and the ocdb Python package in turn will change over time. Reasons for change are manifold: extending the available wavelength range (from the EUV to the VUV and eventually all the way to the IR), improved setup to measure the primary data, an enhanced understanding of the factors influencing the measurements and in turn an improved sample preparation and measurement strategies, and more advanced algorithms and strategies to obtain optical constants from the measured data, to name but the most important aspects.

The ocdb Python package aims at creating a **full transparency how the datasets for a given substance have been evolved**, besides providing access to previous versions of the data for the same substance if there are any.

In any case, there will always be one primary version of a dataset for a given material, usually the most current one.  This is the one version the metadata file is stored in the ``ocdb/db/metadata/`` tree. All other metadata files referring to older (superseded) versions of the dataset are located in the ``ocdb/db/data/`` directory. This is the reason for the above statement, that the ``data`` directory is partly misleading, as strictly speaking, it does contain both, data *and* some metadata, although the latter only for versions of datasets. The reason for this organisation (and for the subdirectories in the ``metadata`` tree): It is fairly straight-forward to iterate over all metadata files in the ``metadata`` tree to populate the collections (see :class:`ocdb.material.Collection` for details) the ocdb package provides.


Adding a new version of a dataset
---------------------------------

What does all that mean for adding a new version of a dataset? Adding a new *version* means that there is already an existing dataset. Hence, this existing dataset needs to be moved and its files usually be renamed, adding a sensible suffix to the file basename, such as the year. This is typically a two-step process:

* Rename the data file residing in the ``ocdb/db/data`` directory, adding a suffix.
* Move the corresponding metadata file from the ``ocdb/db/metadata`` tree to the ``ocdb/db/data`` directory and append the same suffix as done for the data file above.

Afterwards, you can create a new metadata file for the new version of the dataset and place it in the appropriate place in the ``ocdb/db/metadata`` tree. Don't forget to add the reference to the previous (and moved) dataset in the ``version`` block of the metadata file. If there were older versions already present in the dataset just moved, these should be added as well.

