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
    sample:
      thickness: 40 nm
      substrate: Si
      layer_stack: Si (C/ Co/ Ru/ Si)
      morphology: amorphous
    measurement:
      facility: BESSY-II
      beamline: SX700
      date: 2022-04-01
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

sample
    Crucial information concerning the sample, such as (layer) thickness,
    substrate, and layer stack.

    More information may be added here in the future.

    thickness
        Thickness of the sample (the actual layer of the material of interest),
        most probably in nanometres. Nevertheless, the unit should be
        explicitly given, with (numerical) value and unit separated by a space.

    substrate
        The substrate used as basis. Typically a single material, such as Si.

        This is different from the layer stack.

    layer_stack
        The full layer stack, including the substrate and the material of
        interest.

        .. todo::
            Most probably, we need an agreement and a convention here how to
            write the information of the layer stack.

    morphology
        Morphology of the sample.

        Ideally this should be a controlled vocabulary. Possible entries would
        be "amorphous", "crystalline", "microcrystalline" -- what else?

measurement
    Basic information on the measurement, such as facility used and date the
    data were obtained.

    facility
        The name of the facility the data were recorded at.

    beamline
        The name of the actual beamline used to record the data.

    date
        The date (in YYYY-MM-DD format) the data were recorded at.

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
        A concise description of the characteristics of this version.

        Please *do not* simply state "old data" or "data from 20xx", as this
        does not help the users of the package at all, but describe/mention the
        *characteristics* of this version. This may be the wavelength range or
        a different layer stack or else.

    metadata
        The filename of the metadata file (without path).

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
    :obj:`ocdb.database.Material` is not complete.

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

The metadata schema for the metadata files is currently contained in the
:attr:`METADATA` attribute of the :mod:`io` module (at the very top, straight
after the import statements). This is the (only) place to change the version
number of the format, and the function :func:`create_metadata_file` makes use
of the :attr:`METADATA` attribute to populate the template file.


Module documentation
====================

"""
import os.path

import numpy as np
import oyaml as yaml

from ocdb import database


METADATA = {
    "format": {
        "type": "OCDB metadata",
        "version": "1.0.rc-1",
    },
    "filename": {
        "name": "",
        "format": "text",
    },
    "material": {
        "name": "",
        "symbol": "",
    },
    "sample": {
        "thickness": "xx nm",
        "substrate": "",
        "layer_stack": "",
        "morphology": "amorphous",
    },
    "measurement": {
        "facility": "BESSY-II",
        "beamline": "SX700",
        "date": "2022-04-01",
    },
    "references": [""],
    "versions": [
        {
            "identifier": "",
            "description": "",
            "metadata": "",
        },
    ],
    "comment": "",
}


class DataImporter:
    """
    Base class for data importer.

    Data and metadata need always to be imported together, and in case of data
    for the ocdb package, the relevant metadata are stored in a separate file.

    The structure and contents of the metadata file are described above, and
    this class takes care of both, importing the metadata file and mapping the
    contents to the :obj:`ocdb.database.Material` object eventually returned.

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
        :obj:`ocdb.database.Material` object.

    material : :class:`ocdb.database.Material`
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
    the actual material, an object of class :class:`ocdb.database.Material`.

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
        self.material = database.Material()

    def import_data(self):
        """
        Import data from given data and metadata files.

        The material, an object of class :class:`ocdb.database.Material`,
        is directly returned by the method, but accessible as well via the
        :attr:`material` attribute of the importer.

        .. important::

            All actual importing of the (numerical) data is delegated to the
            non-public method :meth:`_import_data`. Hence, importers inheriting
            from :class:`DataImporter` usually *only* need to implement this
            method.

            The :class:`DataImporter` class takes care of the metadata and
            their mapping to the :obj:`ocdb.database.Material` object.

        Returns
        -------
        material : :class:`ocdb.database.Material`
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
    with open(filename, "w+", encoding="utf8") as file:
        file.write(yaml.dump(METADATA))
