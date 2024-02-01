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
      date: 2022-04-00
    references:
      - saadeh-optik-273-170455
    versions:
      - name: foo-1.txt
        format: text
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
    Basic information on the material: name is the full name, symbol the common
    abbreviation, in case of elements the generic IUPAC element symbol. For
    compositions, typically the molecular formula.

sample
    Crucial information concerning the sample, such as (layer) thickness,
    substrate, and layer stack.

    More information may be added here in the future.

measurement
    Basic information on the measurement, such as facility used and date the
    data were obtained.

references
    BibTeX keys of citable reference(s) for the data.

    The corresponding BibTeX records are stored in the file ``literature.bib``
    in the ``db/`` directory of the ocdb package.

versions
    List of name/format entries for additional datasets for the same material.

    Over time, different datasets will be available for the same material.
    Hence, it may be of interest to access the older datasets that are superset
    by a new one, at least get the information that there are some and where
    they are located in the ocdb.

comment
    Textual description of whatever additional information.

    There is nearly always the need to store some information that just doesn't
    fit into any of the fields. However, use with care and expand the data
    structure if you realise that you repeatedly store the same (kind of)
    information in the comment.


.. warning::

    The format/contents of the metadata file is/are currently still under
    development. Furthermore, the automatic mapping of metadata to the
    :obj:`ocdb.database.Material` is not complete.

.. todo::

    Complete format of the metadata file and implement the missing mapping of
    metadata in :meth:`DataImporter._import_metadata`.


Module documentation
====================

"""
import os.path

import numpy as np
import yaml

from ocdb import database


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
        self.material.n_data.axes[0].symbol = "\lambda"
        self.material.n_data.axes[0].unit = "nm"
        self.material.n_data.data = data[:, 1]
        self.material.k_data.axes[0] = self.material.n_data.axes[0]
        self.material.k_data.data = data[:, 2]
        if data.shape[1] > 3:  # uncertainties are present
            self.material.n_data.lower_bounds = data[:, 3]
            self.material.n_data.upper_bounds = data[:, 4]
            self.material.k_data.lower_bounds = data[:, 5]
            self.material.k_data.upper_bounds = data[:, 6]
