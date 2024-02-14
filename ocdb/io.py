# noqa: D405 D407
"""
Interfaces to the persistence layer, *i.e.* importers and eventually exporters.

Data need to come from somewhere (and sometimes need to be persisted). This
module provides general facilities for reading data from different sources.

From a software architecture perspective, this module belongs to the periphery.


Importing data
==============

Data in the OCDB are currently provided as plain text files with a short
(human-readable) header containing some information. For the ocdb package,
reading the actual numerical data from these files is rather straight-forward.
However, this does not help with the relevant metadata. Therefore, a different
approach will be used, based on additional, separate metadata files that
contain all relevant information, including the filename of the actual data
file (and perhaps its format). These metadata files are YAML
files, due to this format being quite human-writable, while retaining the
necessary machine-readability.


Metadata files
--------------

The current state of affairs regarding the structure of metadata files used to
both, provide metadata and the name of the file containing the actual data is
documented below. The metadata files are in YAML format, and a data importer
needs nothing else than the name of an existing metadata file to start with.

.. code-block:: yaml

    format:
      type: ODCB metadata
      version: 1.0.rc-1
    file:
      name: foo.txt
      format: text
    material:
      name: Cobalt
      symbol: Co
    uncertainties:
      confidence_interval: 3 sigma
    references:
      - saadeh-optik-273-170455
    versions:
      - identifier: Co_2018
        description: Lorem ipsum...
        metadata: foo-1.yaml
    comment: >
      Lorem ipsum


A few comments on the format:

format
    This is an identifier of the file format. As a user, just never change.

    The version number will only be set/incremented by the ocb package
    maintainers.

file
    Name and format of the file containing the actual numerical data.

    The format string should ideally be from a controlled vocabulary. As soon
    as there are several formats, an ImporterFactory will be in place, and
    there, this string may be used to decide which importer to instantiate
    and return.

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

versions
    List of entries for additional datasets for the same material.

    Over time, different datasets will be available for the same material.
    Hence, it may be of interest to access the older datasets that are superset
    by a new one, at least get the information that there are some and where
    they are located in the ocdb.

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
        does not help the users of the package at all, but describe/mention the
        *characteristics* of this version. This may be the wavelength range or
        a different layer stack or else.

    metadata
        Filename of the metadata file (without path).

        The logic of the ocdb package requires only the name of a metadata file
        to figure out by itself where the data are located.

    .. todo::

        How to discriminate between current and old/superseded versions? One
        possibility would be to have only the metadata files of the most
        current datasets in the ``metadata`` directory, and the metadata of the
        superseded/alternative datasets in a separate (parallel) directory (or
        simply the ``data`` directory). This "convention over configuration"
        approach would allow the ocdb package to import all data from a given
        location, without need to first check for each metadata file whether it
        has been superseded or not.

comment
    Textual description of whatever additional information.

    There is nearly always the need to store some information that just doesn't
    fit into any of the fields. However, use with care and expand the data
    structure if you realise that you repeatedly store the same (kind of)
    information in the comment.


Rather than creating the metadata YAML files by hand, (data) contributors to
the ocdb package should use the :func:`create_metadata_file` function. This
function will always use the latest metadata scheme to write the template.
See the :func:`create_metadata_file` documentation for further details.


.. warning::

    The format/contents of the metadata file is/are currently still under
    development. Furthermore, the automatic mapping of metadata to the
    :obj:`ocdb.material.Material` is not complete.

.. todo::

    Complete format of the metadata file and implement the missing mapping of
    metadata in :meth:`DataImporter._import_metadata`.


Data files
----------

Data files reside in a directory separate from the metadata. The reason of this
"convention over configuration" approach is simply to allow the machinery
importing all the data for the user to iterate over all files in a directory
and import the accompanying (meta)data.

As described above, for one material, there can (and will) be several datasets,
each with their data (and metadata) files. Where the additional metadata files
are stored is still under discussion, for details see the section on metadata
above.

Data files are, for the time being, simply text files as those currently
available from the OCDB. Those data files can be read using the
:class:`TxtDataImporter` class. Users typically do not care about data import,
as the ocdb package handles all this transparently and automatically for them.


Note for developers
===================

The metadata schema for the metadata files is implemented in the
:class:`Metadata` class. To create the schema, you may use the
:meth:`Metadata.to_dict` method.


Module documentation
====================

"""
import os.path

import numpy as np
import oyaml as yaml

from ocdb import material


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

    metadata_filename : :class:`str`
        Name of the file containing the corresponding metadata

    metadata : :class:`dict`
        Metadata as read from the metadata file.

        These metadata are automatically mapped to the resulting
        :obj:`ocdb.material.Material` object.

    material : :class:`ocdb.material.Material`
        Optical constants and relevant metadata for a single material.

        The object data and metadata are imported into upon calling
        :meth:`import_data`.

    Examples
    --------
    Importing data is a two-step process: (i) create an importer object and set
    the metadata filename, and (ii) call the import method:

    .. code-block::

        importer = ocdb.io.DataImporter()
        importer.metadata_filename = "metadata/foo.yaml"

        material = importer.import_data()

    As you can see from the example, the :meth:`import_data` method will return
    the actual material, an object of class :class:`ocdb.material.Material`.

    For convenience, you can set the metadata filename upon instantiating the
    importer object:

    .. code-block::

        importer = ocdb.io.DataImporter(metadata="metadata/foo.yaml")
        material = importer.import_data()

    Furthermore, there is no need to catch the return value of the
    :meth:`import_data` method, as the resulting material can be accessed via
    the :attr:`material` attribute of the importer:

    .. code-block::

        importer = ocdb.io.DataImporter(metadata="metadata/foo.yaml")
        importer.import_data()
        foo = importer.material

    For examples how to import "real" data, you may have a look at the
    documentation of classes inheriting from this base class.

    """

    def __init__(self, metadata=""):
        self.data_filename = ""
        self.metadata_filename = metadata
        self.metadata = None
        self.material = material.Material()

    def import_data(self):
        """
        Import data from given data and metadata files.

        The material, an object of class :class:`ocdb.material.Material`,
        is directly returned by the method, but accessible as well via the
        :attr:`material` attribute of the importer.

        .. important::

            All actual importing of the (numerical) data is delegated to the
            non-public method :meth:`_import_data`. Hence, importers inheriting
            from :class:`DataImporter` usually *only* need to implement this
            method.

            The :class:`DataImporter` class takes care of the metadata and
            their mapping to the :obj:`ocdb.material.Material` object.

        Returns
        -------
        material : :class:`ocdb.material.Material`
            Optical constants and relevant metadata for a single material.

        """
        self._check_for_metadata()
        self._import_metadata()
        self._check_for_data()
        self._import_data()
        return self.material

    def _check_for_metadata(self):
        if not self.metadata_filename:
            raise ValueError("No filename for metadata provided")
        if not os.path.exists(self.metadata_filename):
            raise FileNotFoundError("Could not find {self.metadata_filename}")

    def _import_metadata(self):
        with open(self.metadata_filename, "r+", encoding="utf8") as file:
            self.metadata = yaml.safe_load(file.read())
        self.data_filename = self.metadata["file"]["name"]
        mappings = {
            "material.name": "name",
            "material.symbol": "symbol",
        }
        for metadata_value, material_attribute in mappings.items():
            first, second = metadata_value.split(".")
            value = self.metadata[first][second]
            setattr(self.material, material_attribute, value)

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
    header with a bit of metadata (in non-standardised formatting). Hence, data
    are read using :func:`numpy.loadtxt` and metadata entirely read from the
    YAML metadata file accompanying the data.

    Examples
    --------
    The basic operation of the :class:`TxtDataImporter` is the same as that of
    the base importer :class:`DataImporter`:

    .. code-block::

        importer = ocdb.io.TxtDataImporter(metadata="metadata/foo.yaml")
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
    of the metadata file and to submit both, metadata and data file to the ocdb
    package maintainers.

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


class DataImporterFactory:
    """
    Factory for data importer.

    Data containing the actual optical constants for a given material can be
    stored in different formats. While for each format supported, there exists
    a dedicated importer class inheriting from :class:`DataImporter`, the
    factory is the one place deciding which importer object to return.


    Examples
    --------
    Getting a data importer object from the factory is straight-forward: Create
    an instance of the factory and call its :meth:`get_importer` method:

    .. code-block::

        importer_factory = DataImporterFactory()
        importer_factory.get_importer()

    """

    # noinspection PyMethodMayBeStatic
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

        """
        if not metadata:
            raise ValueError("Missing metadata")
        if metadata.file["format"] == "text":
            return TxtDataImporter()
        raise NotImplementedError(
            f"Importer for format '{metadata.file['format']}' not implemented"
        )


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

        If you use the data for your own work, consider citing these references.

    versions : :class:`list`
        List of related datasets

        Each element in the list is an object of type :obj:`VersionMetadata`.

    comment : :class:`str`
        Any additional relevant information of the dataset.

        There is nearly always the need to store some information that just
        doesn't fit into any of the fields. However, use with care and expand
        the data structure if you realise that you repeatedly store the same
        (kind of) information in the comment.

    """

    def __init__(self):
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
        self.versions = []
        self.comment = ""

        self._format = {
            "type": "OCDB metadata",
            "version": "1.0.rc-1",
        }

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
            "versions",
            "comment",
        ]
        for key in keys:
            if key == "versions":
                output["versions"] = []
                for version in self.versions:
                    output["versions"].append(version.to_dict())
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
        with open(filename, "r+", encoding="utf8") as file:
            metadata = yaml.safe_load(file.read())
        self.from_dict(metadata=metadata)


class VersionMetadata:
    """
    Metadata for an individual version of a dataset contained in the OCDB.

    Over time, different datasets will be available for the same material.
    Hence, it may be of interest to access the older datasets that are superset
    by a new one, at least get the information that there are some and where
    they are located in the ocdb.

    To be able to sensibly address those additional datasets from within the
    ocdb package, they need a (unique) identifier, a (short) description and
    the information where to find the data and metadata.


    Attributes
    ----------
    identifier : :class:`str`
        Unique identifier for the dataset.

        Typically, this is the name of the "base" dataset with a suffix, *e.g.*
        ``Co_2018`` in case of a dataset containing data for cobalt created in
        2018.

        .. important::
            This string is used to access the data from within the ocdb
            package. Hence, it should be short and needs to be a valid Python
            variable name.

    description : :class:`str`
        Concise description of the characteristics of this version.

        Please *do not* simply state "old data" or "data from 20xx", as this
        does not help the users of the package at all, but describe/mention the
        *characteristics* of this version. This may be the wavelength range or
        a different layer stack or else.

    metadata : :class:`str`
        Filename of the metadata file (without path).

        The logic of the ocdb package requires only the name of a metadata file
        to figure out by itself where the data are located.

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
