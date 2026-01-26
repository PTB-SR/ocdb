# noqa: D405 D407
"""
Interfaces to the persistence layer, *i.e.* importers and exporters.

Data need to come from somewhere (and sometimes need to be persisted). This
module provides general facilities for reading data from different sources.

From a software architecture perspective, this module belongs to the
periphery.


Data in the ocdb package
========================

Data and corresponding context (*i.e.*, metadata) are stored in files in
the ``db`` directory of the ocdb package. The format of data and metadata
files is nothing users of the ocdb package should be concerned with.
Contributors and developers, however, need a bit more details.

Data in the OCDB are currently provided as plain text files with a short
(human-readable) header containing some information. For the ocdb package,
reading the actual numerical data from these files is rather straight-forward.
However, this does not help with the relevant metadata. Therefore, a different
approach is used, based on additional, separate metadata files that contain
all relevant information, including the filename of the actual data file
(and its format). These metadata files are YAML files, due to this format
being quite human-writable, while retaining the necessary machine-readability.


Importing data
==============

When importing data, the actual file format does not matter, as this is
been taken care of by the :class:`DataImporterFactory`. Hence, all you
need is the name of the metadata file(s). These can be imported via the
:meth:`Metadata.from_file` method of the :class:`Metadata` class. The
latter represents the metadata in code. For details, see below. All we
care about for now is to get the metadata and to use them to get the
matching importer.

For a single metadata file ``Co.yaml`` containing the relevant metadata for
the Cobalt dataset in the OCDB, this may look like:

.. code-block::

    metadata = ocdb.io.Metadata()
    metadata.from_file("Co.yaml")

    importer_factory = ocdb.io.DataImporterFactory()
    importer = importer_factory.get_importer(metadata=metadata)

    Co = importer.import_data()

Here, ``Co`` will be an :obj:`ocdb.material.Material` object containing
both, data and metadata for Cobalt.

To import a whole bunch of data in one go, assuming you have a list of
metadata filenames, things could be made a bit smoother. Let's assume for
the moment that we would want to create a dictionary `materials` with the
symbol of the individual material contained in the metadata as key:

.. code-block::

    importer_factory = ocdb.io.DataImporterFactory()
    materials = {}

    for filename in metadata_filenames:
        metadata = ocdb.io.Metadata(filename=filename)
        importer = importer_factory.get_importer(metadata=metadata)

        materials[metadata.material["symbol"]] = importer.import_data()

This is what basically happens behind the scenes when you import the ocdb
package.


Metadata
========

A key concept of the ocdb package is to provide sensible context for the
data, *i.e.* metadata. As mentioned above, these metadata are stored within
separate files in YAML format. The format is described in more detail below,
as well as the ways to create those files and how the metadata are represented
within the ocdb package.


Metadata files
--------------

The current state of affairs regarding the structure of metadata files used to
both, provide metadata and the name of the file containing the actual data is
documented below. The metadata files are in YAML format, and a data importer
needs nothing else than the name of an existing metadata file to start with.

The metadata file as created by the :func:`create_metadata_file` function
looks as follows:

.. literalinclude:: ../metadata-schema.yaml
   :language: yaml


For convenience, below is an additional example with some hand-crafted
example content. However, keep in mind that the schema shown above is
automatically generated and should always be up to date. Hence, if there
are differences between the schema shown above and the example below,
the former should be more authoritative.

.. code-block:: yaml

    format:
      type: OCDB metadata
      version: 1.0
    file:
      name: Ta.txt
      format: text
    material:
      name: Tantalum
      symbol: Ta
    uncertainties:
      confidence_interval: "3 sigma"
    references:
      - "saadeh-ao-33-10032"
    date: "2020-12-01"
    versions:
      - identifier: Ta_2019
        description: "wavelength range 10-20 nm"
        metadata: Ta_2019.yaml
    comment: >
      Lorem ipsum


A few comments on the format:

format
    This is an identifier of the file format. As a user, just never change.

    The version number will only be set/incremented by the ocb package
    maintainers.

file
    Name and format of the file containing the actual numerical data.

    name:
        Name of the file containing the data.

        Only the file name without path. Due to the "convention over
        configuration" approach of the ocdb package, all data reside in one
        location. Furthermore, data are accessed as package data, not via
        the file system, due to the way Python packages are handled internally.

    format:
        Identifier of the file format the data are provided in.

        The format string is an entry of a controlled vocabulary. This
        string gets used by the :class:`DataImporterFactory` to decide which
        importer to instantiate and return.

material
    Basic information on the material.

    name
        Full name of the material.

    symbol
        Common abbreviation, in case of elements the generic IUPAC element
        symbol. For compositions, typically the molecular formula.

        .. important::
            This string is used to access the data from within the ocdb
            package. Hence, it should be short and needs to be a valid Python
            variable name.

uncertainties
    Relevant information about the uncertainties, if present.

    confidence_interval
        The value the uncertainties are provided for.

references
    BibTeX keys of citable reference(s) for the data.

    The corresponding BibTeX records are stored in the file ``literature.bib``
    in the ``db/`` directory of the ocdb package.

date
    Date the dataset has been created, in the form ``YYYY-MM-DD``.

    Due to the internal representation as :class:`datetime.date` object, the
    date must be a full date including valid values for month and day.
    However, if you cannot or do not want to give a precise date, you may
    specify something like ``2018-01-01``, *i.e.* January 1st of a given year.

    Make sure to surround the date with quotation marks in the YAML file to
    explicitly make it a string.

    Dates are used to sort versions of a dataset. For versions, see below.

versions
    List of entries for additional datasets for the same material.

    Over time, different datasets will be available for the same material.
    Hence, it may be of interest to access the older datasets that are
    superset by a new one, at least get the information that there are
    some and where they are located in the ocdb.

    To be able to sensibly address those additional datasets from within the
    ocdb package, they need a (unique) identifier, a (short) description and
    the information where to find the data and metadata.

    identifier
        Unique identifier for the dataset.

        The identifier behaves similar to the field symbol (in ``material``)
        above. In particular, it needs to be a valid Python variable name.

    description
        Concise description of the characteristics of this version.

        Please *do not* simply state "old data" or "data from 20xx", as this
        does not help the users of the package at all, but describe/mention
        the *characteristics* of this version. This may be the wavelength
        range or a different layer stack or else.

    metadata
        Filename of the metadata file (without path).

        The logic of the ocdb package requires only the name of a metadata
        file to figure out by itself where the data are located.


    .. todo::

        How to deal with versions/history in older datasets? Generally there
        would be two strategies possible: (i) Keep it simple: Only the
        most current dataset has a list of versions. In case of a new
        version, not only will the metadata file be moved, but its version
        list deleted as well. (ii) Keep references in both directions: Each
        dataset potentially has a list of versions, with indication which of
        them are newer than the current dataset and which are older. This
        would require a much more complicated handling of the versions,
        but would allow to keep the version information in superseded
        metadata files. Probably for starters start with the simple option.

comment
    Textual description of whatever additional information.

    There is nearly always the need to store some information that just
    doesn't fit into any of the fields. However, use with care and expand
    the data structure if you realise that you repeatedly store the same
    (kind of) information in the comment.

    .. note::

        The ``>`` sign shown in the hand-crafted example above is the YAML
        syntax for a multiline text field where where each line break is
        folded to a space unless it ends an empty or a more-indented line.
        For more details, see the `YAML specification
        <http://yaml.org/spec/1.2.2/#23-scalars>`_.



Creating metadata files
-----------------------

Rather than creating the metadata YAML files by hand, (data) contributors to
the ocdb package should use the :func:`create_metadata_file` function. This
function will always use the latest metadata scheme to write the template.
See the :func:`create_metadata_file` documentation for further details.


Representing metadata in code
-----------------------------

Metadata are represented as classes within the :mod:`ocdb.io` module.
Currently, the following classes are implemented:

* :class:`Metadata`

    Metadata for a given dataset as read from a metadata file.

* :class:`VersionMetadata`

    Metadata for an individual version of a dataset contained in the OCDB.

Note that these classes only belong to the :mod:`ocdb.io` module. Metadata
of the :class:`ocdb.material.Material` class are entirely separate and
described in more detail in the :mod:`ocdb.material` module.


Data files
==========

Data files reside in a directory separate from the metadata. The reason of
this "convention over configuration" approach is simply to allow the
machinery importing all the data for the user to iterate over all files in
a directory and import the accompanying (meta)data.

As described above, for one material, there can (and will) be several
datasets, each with their data (and metadata) files. Where the additional
metadata files are stored is still under discussion, for details see the
section on metadata above.

Data files are, for the time being, simply text files as those currently
available from the OCDB. Those data files can be read using the
:class:`TxtDataImporter` class. Users typically do not care about data import,
as the ocdb package handles all this transparently and automatically for them.


Notes for developers
====================

Adding importers for data file formats
--------------------------------------

Currently, there is only one importer for plain text files available. To
implement importers for other data file formats requires these steps:

* Decide upon a format specifier used in the metadata schema as well.

* Implement the importer class, inheriting from :class:`DataImporter`

* Add the logic to the :class:`DataImporterFactory` to select the new
  importer given the format string in the metadata.


Updating the metadata schema
----------------------------

The metadata schema for the metadata files is implemented in the
:class:`Metadata` class. Hence, all changes should be applied there,
and with each change incrementing the version number of the schema as well.

To create the YAML listing of the schema shown above, use the Python script
``create_metadata_schema.py`` located in the ``docs`` directory of the ocdb
package.

.. important::

    Whenever you change the schema, don't forget to update the schema file
    included in the documentation as well.

If the metadata schema evolves and hence the need exists to deal with
different versions of the schema, appropriate functionality needs to be
implemented, most probably in the :meth:`Metadata.from_dict` method.


Module documentation
====================

"""
import datetime
import importlib.resources
import os.path

import bibrecord.bibtex
import bibrecord.database
import numpy as np
import oyaml as yaml

from ocdb import material


class DataImporterFactory:
    """
    Factory for data importer.

    Data containing the actual optical constants for a given material can be
    stored in different formats. While for each format supported, there exists
    a dedicated importer class inheriting from :class:`DataImporter`, the
    factory is the one place deciding which importer object to return.


    Attributes
    ----------
    references : :class:`References`
        Database of bibliographic records.

        The references are loaded from the BibTeX database upon
        instantiating the :class:`DataImporterFactory` class and passed on to
        the :obj:`DataImporter` objects returned by the :meth:`get_importer`
        method. Thus, the BibTeX database is typically only loaded once.


    Examples
    --------
    Getting a data importer object from the factory is straight-forward:
    Create an instance of the factory and call its :meth:`get_importer`
    method:

    .. code-block::

        metadata = Metadata(filename=<my_metadata.yaml>)

        importer_factory = DataImporterFactory()
        importer_factory.get_importer(metadata=metadata)

    """

    def __init__(self):
        self.references = References()
        self.references.load()

    def get_importer(self, metadata=None):
        """
        Return data importer given the information provided in the metadata.

        Parameters
        ----------
        metadata : :class:`Metadata`
            Metadata describing the data to be imported.

        Returns
        -------
        importer : :class:`DataImporter`
            Data importer object best fitting the criteria provided

        Raises
        ------
        ValueError
            Raised if no metadata are provided

        NotImplementedError
            Raised if no importer for the given format is implemented.

        """
        if not metadata:
            raise ValueError("Missing metadata")
        if metadata.file["format"] == "text":
            importer = TxtDataImporter()
        else:
            raise NotImplementedError(
                f"Importer for format '{metadata.file['format']}' "
                f"not implemented"
            )
        importer.metadata = metadata
        importer.references = self.references
        return importer


class DataImporter:
    """
    Base class for data importer.

    Data and metadata need always to be imported together, and in case of data
    for the ocdb package, the relevant metadata are stored in a separate file.

    The structure and contents of the metadata file are described above, and
    this class takes care of both, importing the metadata file and mapping the
    contents to the :obj:`ocdb.material.Material` object eventually returned.

    .. important::

        Actual importer for different file formats should always inherit from
        this class. Furthermore, all they usually need to do is to implement
        :meth:`_import_data`. All actual importing should go into this
        non-public method. Basic sanity checks, such as existing filenames for
        data and metadata and whether these files actually exist, are taken
        care of by this base class and hence should be no concern for
        implementers of actual importers.

    Attributes
    ----------
    data_filename : :class:`str`
        Name of the file containing the actual (numerical) data

    metadata : :class:`Metadata`
        Metadata as read from the metadata file.

        These metadata are automatically mapped to the resulting
        :obj:`ocdb.material.Material` object.

    material : :class:`ocdb.material.Material`
        Optical constants and relevant metadata for a single material.

        The object data and metadata are imported into upon calling
        :meth:`import_data`.

    references : :class:`References`
        Database of bibliographic records.

    Examples
    --------
    Importing data is a two-step process: (i) create an importer object
    and set the metadata and references, and (ii) call the import method:

    .. code-block::

        importer = ocdb.io.DataImporter()
        importer.metadata = ocdb.io.Metadata(filename="metadata/foo.yaml")
        importer.references = ocdb.io.References()
        importer.references.load()
        material = importer.import_data()

    As you can see from the example, the :meth:`import_data` method will
    return the actual material, an object of class
    :class:`ocdb.material.Material`.

    For convenience, you can set the metadata upon instantiating the importer
    object:

    .. code-block::

        metadata = ocdb.io.Metadata(filename="metadata/foo.yaml")
        importer = ocdb.io.DataImporter(metadata=metadata)
        importer.references = ocdb.io.References()
        importer.references.load()
        material = importer.import_data()

    Furthermore, there is no need to catch the return value of the
    :meth:`import_data` method, as the resulting material can be accessed via
    the :attr:`material` attribute of the importer:

    .. code-block::

        metadata = ocdb.io.Metadata(filename="metadata/foo.yaml")
        importer = ocdb.io.DataImporter(metadata=metadata)
        importer.references = ocdb.io.References()
        importer.references.load()
        importer.import_data()
        foo = importer.material

    For examples how to import "real" data, you may have a look at the
    documentation of classes inheriting from this base class.

    """

    def __init__(self, metadata=None):
        self.data_filename = ""
        self.metadata = metadata
        self.material = material.Material()
        self.references = None

    def import_data(self):
        """
        Import data from given data and metadata files.

        The material, an object of class :class:`ocdb.material.Material`,
        is directly returned by the method, but accessible as well via the
        :attr:`material` attribute of the importer.

        .. important::

            All actual importing of the (numerical) data is delegated to the
            non-public method :meth:`_import_data`. Hence, importers
            inheriting from :class:`DataImporter` usually *only* need to
            implement this method.

            The :class:`DataImporter` class takes care of the metadata and
            their mapping to the :obj:`ocdb.material.Material` object.

        Returns
        -------
        material : :class:`ocdb.material.Material`
            Optical constants and relevant metadata for a single material.

        """
        self._check_for_metadata()
        self._map_metadata()
        self._load_references()
        self._check_for_data()
        self._import_data()
        return self.material

    def _check_for_metadata(self):
        if not self.metadata:
            raise ValueError("No metadata provided")

    def _map_metadata(self):
        # Note: This is currently hard-coded, but a more general mapping is
        #       complicated and seems not worth it for the time being.
        self.data_filename = self.metadata.file["name"]
        self.material.name = self.metadata.material["name"]
        self.material.symbol = self.metadata.material["symbol"]
        self.material.metadata.comment = self.metadata.comment
        self.material.metadata.uncertainties.confidence_interval = (
            self.metadata.uncertainties["confidence_interval"]
        )
        self.material.metadata.date = self.metadata.date

    def _load_references(self):
        for reference in self.metadata.references:
            self.material.references.append(
                self.references.records[reference]
            )

    def _check_for_data(self):
        if not self.data_filename:
            raise ValueError("No filename for data provided")
        if not os.path.exists(self.data_filename):
            raise FileNotFoundError(f"Could not find {self.data_filename}")

    def _import_data(self):
        pass


class TxtDataImporter(DataImporter):
    """
    Import data from (plain) text files.

    Currently, the OCDB provides the data as (plain) text files with a small
    header with a bit of metadata (in non-standardised formatting). Hence,
    data are read using :func:`numpy.loadtxt` and metadata entirely read
    from the YAML metadata file accompanying the data.

    Examples
    --------
    The basic operation of the :class:`TxtDataImporter` is the same as that of
    the base importer :class:`DataImporter`:

    .. code-block::

        metadata = ocdb.io.Metadata(filename="metadata/foo.yaml")
        importer = ocdb.io.TxtDataImporter(metadata=metadata)
        importer.references = ocdb.io.References()
        importer.references.load()
        importer.import_data()
        foo = importer.material

    Typical users of the ocdb package, however, should regularly not be
    concerned with importing data, as the package transparently and
    automatically takes care of that for the users.

    """

    def _import_data(self):
        data = np.loadtxt(self.data_filename)
        self.material.n_data.axes[0].values = data[:, 0]
        self.material.n_data.axes[0].quantity = "wavelength"
        self.material.n_data.axes[0].symbol = r"\lambda"
        self.material.n_data.axes[0].unit = "nm"
        self.material.n_data.data = data[:, 1]
        self.material.k_data.axes[0] = self.material.n_data.axes[0]
        self.material.k_data.data = data[:, 2]
        if data.shape[1] > 3:  # uncertainties are present
            self.material.n_data.lower_bounds = data[:, 3]
            self.material.n_data.upper_bounds = data[:, 4]
            self.material.k_data.lower_bounds = data[:, 5]
            self.material.k_data.upper_bounds = data[:, 6]


def create_metadata_file(filename=""):
    """
    Create a metadata template file in YAML format.

    The metadata accompanying the data of the OCDB in the ocdb package are
    stored in metadata files in YAML format. To help (data) contributors to
    create these metadata files, this function takes a metadata file name and
    creates a YAML template file with the current metadata structure.

    All that is left to do to the data contributors is to fill out the fields
    of the metadata file and to submit both, metadata and data file to the
    ocdb package maintainers.

    Parameters
    ----------
    filename : :class:`str`
        Name of the metadata file that should be created

    """
    if not filename:
        raise ValueError("Missing filename")
    metadata = Metadata()
    metadata.versions.append(VersionMetadata())
    metadata.references.append("")
    with open(filename, "w+", encoding="utf8") as file:
        file.write(yaml.dump(metadata.to_dict()))


class Metadata:
    """
    Metadata for a given dataset as read from a metadata file.

    Data without context (*i.e.*, metadata) are mostly useless. Hence, for the
    ocdb package, metadata accompanying the actual data (*i.e.*, optical
    constants) are stored in separate metadata files for each dataset.

    This class provides the code representation of all the information
    contained in these files.


    Attributes
    ----------
    file : :class:`dict`
        Metadata describing the data file

    material : :class:`dict`
        Metadata describing the material

    uncertainties : :class:`dict`
        Metadata describing the uncertainties provided

    references : :class:`list`
        List of references related to the dataset

        If you use the data for your own work, consider citing these
        references.

    versions : :class:`list`
        List of related datasets

        Each element in the list is an object of type :obj:`VersionMetadata`.

    comment : :class:`str`
        Any additional relevant information of the dataset.

        There is nearly always the need to store some information that just
        doesn't fit into any of the fields. However, use with care and expand
        the data structure if you realise that you repeatedly store the same
        (kind of) information in the comment.


    Parameters
    ----------
    filename : :class:`str`
        Name of a metadata file to import the metadata from.

    Examples
    --------
    There are several ways to populate a :obj:`Metadata` object: from a
    dictionary conforming to the schema, or from a YAML file. Usually,
    you will have a YAML file conforming to the metadata schema that you
    want to import the metadata from:

    .. code-block::

        metadata = Metadata()
        metadata.from_file(<my_metadata.yaml>)

    For convenience, there is a shortcut, directly providing the filename
    when instantiating the object:

    .. code-block::

        metadata = Metadata(filename=<my_metadata.yaml>)

    If you would like to get the current metadata schema as dictionary,
    this is possible as well:

    .. code-block::

        metadata = Metadata()
        metadata_dict = metadata.to_dict()

    Or, again even shorter:

    .. code-block::

        metadata_dict = Metadata().to_dict()

    However, if you would like to create a metadata YAML file from this
    template, simply use the :func:`create_metadata_file` function provided
    by the module as well.

    """

    def __init__(self, filename=""):
        self.file = {
            "name": "",
            "format": "",
        }
        self.material = {
            "name": "",
            "symbol": "",
        }
        self.uncertainties = {
            "confidence_interval": "",
        }
        self.references = []
        self.date = datetime.date.today()
        self.versions = []
        self.comment = ""

        self._format = {
            "type": "OCDB metadata",
            "version": "1.0",
        }
        if filename:
            self.from_file(filename=filename)

    @property
    def format(self):
        """
        Metadata describing the metadata schema itself.

        Returns
        -------
        metadata : :class:`dict`

        """
        return self._format

    def from_dict(self, metadata=None):
        """
        Set metadata from dictionary.

        Parameters
        ----------
        metadata : :class:`dict`
            Metadata to be set


        .. note::

            As soon as there are different versions of the metadata schema,
            this is the place to implement the logic mapping the contents
            of the dictionary to the class attributes. The version can be
            accessed from the ``format`` section of the metadata dictionary.

        """
        if "format" not in metadata.keys():
            raise KeyError("Wrong metadata schema")
        metadata_format = metadata.pop("format")
        if metadata_format["type"] != self.format["type"]:
            raise ValueError("Wrong metadata format")
        for key, value in metadata.items():
            if key == "versions":
                for version_dict in value:
                    version = VersionMetadata()
                    version.from_dict(version_dict)
                    self.versions.append(version)
            elif key == "date":
                self.date = datetime.date.fromisoformat(value)
            elif hasattr(self, key):
                if isinstance(value, dict):
                    getattr(self, key).update(value)
                else:
                    setattr(self, key, value)

    def to_dict(self):
        """
        Return metadata as dictionary.

        Returns
        -------
        metadata : :class:`dict`

        """
        output = {}
        keys = [
            "format",
            "file",
            "material",
            "uncertainties",
            "references",
            "date",
            "versions",
            "comment",
        ]
        for key in keys:
            if key == "versions":
                output["versions"] = []
                for version in self.versions:
                    output["versions"].append(version.to_dict())
            elif key == "date":
                output["date"] = str(self.date)
            else:
                output[key] = getattr(self, key)
        return output

    def from_file(self, filename=""):
        """
        Set metadata from file.

        Metadata are stored in YAML files.

        Internally, the method :meth:`from_dict` will be called after the YAML
        file has been read (and converted into a :class:`dict`).

        Parameters
        ----------
        filename : :class:`str`
            File the metadata should be imported from.

        """
        with open(filename, "r", encoding="utf8") as file:
            metadata = yaml.safe_load(file.read())
        self.from_dict(metadata=metadata)


class VersionMetadata:
    """
    Metadata for an individual version of a dataset contained in the OCDB.

    Over time, different datasets will be available for the same material.
    Hence, it may be of interest to access the older datasets that are
    superset by a new one, at least get the information that there are
    some and where they are located in the ocdb.

    To be able to sensibly address those additional datasets from within the
    ocdb package, they need a (unique) identifier, a (short) description and
    the information where to find the data and metadata.


    Attributes
    ----------
    identifier : :class:`str`
        Unique identifier for the dataset.

        Typically, this is the name of the "base" dataset with a suffix,
        *e.g.* ``Co_2018`` in case of a dataset containing data for cobalt
        created in 2018.

        .. important::
            This string is used to access the data from within the ocdb
            package. Hence, it should be short and needs to be a valid Python
            variable name.

    description : :class:`str`
        Concise description of the characteristics of this version.

        Please *do not* simply state "old data" or "data from 20xx", as this
        does not help the users of the package at all, but describe/mention
        the *characteristics* of this version. This may be the wavelength
        range or a different layer stack or else.

    metadata : :class:`str`
        Filename of the metadata file (without path).

        The logic of the ocdb package requires only the name of a metadata
        file to figure out by itself where the data are located.

    """

    def __init__(self):
        self.identifier = ""
        self.description = ""
        self.metadata = ""

    def from_dict(self, metadata=None):
        """
        Set metadata from dictionary.

        Parameters
        ----------
        metadata : :class:`dict`
            Metadata to be set

        """
        for key, value in metadata.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def to_dict(self):
        """
        Return metadata as dictionary.

        Returns
        -------
        metadata : :class:`dict`

        """
        output = {}
        for key in ["identifier", "description", "metadata"]:
            output[key] = getattr(self, key)
        return output


class References:
    """
    Database of bibliographic records.

    Each record is of type :class:`bibrecord.record.Record` (actually, it is
    a subtype corresponding to the actual BibTeX entry type). Records are
    stored in the :attr:`records` attribute as a dictionary whose keys are
    the BibTeX keys used to cite the bibliographic record and the
    corresponding value the instance of the corresponding
    :class:`bibrecord.record.Record` subclass.

    The bibliographic data are read from a BibTeX file residing in
    ``db/literature.bib`` in the ``ocdb`` package directory. Reading of this
    file is done using the :mod:`importlib_resources` library to not depend
    on the way how the ocdb package is installed.

    Attributes
    ----------
    records : :class:`dict`
        Bibliographic records

        The keys are the BibTeX keys used to cite the bibliographic record and
        the value the instance of the corresponding
        :class:`bibrecord.record.Record` subclass.


    Examples
    --------
    Users of the :mod:`ocdb` package will not have to deal with this class,
    as everything is magically been taken care of. Nevertheless, some code
    within the :mod:`ocdb` package needs to use this class. Two lines are
    all there is to it:

    .. code-block::

        references = References()
        references.load()

    Afterwards, all bibliographic records are contained in the
    :attr:`References.records` attribute.

    """

    def __init__(self):
        self.records = {}
        self._bibliography_file = "db/literature.bib"

    def load(self):
        """
        Load references from BibTeX bibliography.

        References are stored in a BibTeX file that is loaded as package
        resource via the :mod:`importlib_resources` library.

        """
        bibtex = (
            importlib.resources.files(__package__)
            .joinpath(self._bibliography_file)
            .read_text(encoding="utf8")
        )
        bibliography = bibrecord.bibtex.Bibliography()
        bibliography.from_bib(bibtex)
        database = bibrecord.database.Database()
        database.from_bibliography(bibliography)
        self.records = database.records
