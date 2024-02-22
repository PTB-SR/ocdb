"""
General management of the ocdb package.

There is one place to define the interplay of the whole machinery importing
the data and creating the collections used as user interface of the ocdb
package. To not clutter the package ``__init__.py`` file, this module
provides all the necessary functionality that is in turn used in the ocdb
package ``__init__.py`` file to create the collections upon importing the
package.

"""

import importlib.resources

import ocdb.io
import ocdb.material
import ocdb.plotting
import ocdb.processing


class CollectionCreator:
    """
    Creator of collections for the ocdb package.

    The main user interface of the ocdb package are collections, objects of
    type :class:`ocdb.material.Collection`, containing the individual
    materials as properties. Each material in turn is an object of type
    :class:`ocdb.material.Material`.

    Attributes
    ----------
    name : :class:`str`
        Name of the collection to create.

        Note that there needs to be a corresponding resource in the package
        data containing the metadata for this collection.

    Raises
    ------
    ValueError
        Raised if no name for a collection is provided.

    ValueError
        Raised if there exists no corresponding resource in the package data.


    Examples
    --------
    The "magic" of creating collections happens upon importing the ocdb
    package. Nevertheless, this is *how* the magic happens:

    .. code-block::

        for collection_name in ["elements", "compositions"]:
            collection_creator = CollectionCreator()
            collection = collection_creator.create(name=collection_name)


    """

    def __init__(self):
        self.name = ""
        self._metadata_path = "db/metadata"
        self._data_path = "db/data"

        self._importer_factory = ocdb.io.DataImporterFactory()
        self._processing_step_factory = (
            ocdb.processing.ProcessingStepFactory()
        )
        self._plotter_factory = ocdb.plotting.PlotterFactory()

    def create(self, name=""):
        """
        Create a collection.

        Parameters
        ----------
        name : :class:`str`
            Name of the collection to create.

            If not given, but the attribute :attr:`name` is set, the attribute
            will be used. Otherwise, the attribute :attr:`name` will be set
            from the parameter.

        Returns
        -------
        collection : :class:`ocdb.material.Collection`
            Collection containing the individual materials.

        Raises
        ------
        ValueError
            Raised if no name for a collection is provided.

        ValueError
            Raised if no corresponding resource exists in the package data.

        """
        if name:
            self.name = name
        self._check_prerequisites()
        collection = ocdb.material.Collection()
        for file in (
            importlib.resources.files(__package__)
            .joinpath(self._metadata_path)
            .joinpath(self.name)
            .iterdir()
        ):
            # noinspection PyTypeChecker
            metadata = ocdb.io.Metadata(filename=file)
            metadata.file["name"] = self._replace_filename_with_resource(
                metadata.file["name"]
            )
            material = self._import_material(metadata)
            self._add_versions(material, metadata)
            collection.add_item(material)
        return collection

    def _check_prerequisites(self):
        if not self.name:
            raise ValueError("No name provided for collection")
        if (
            not importlib.resources.files(__package__)
            .joinpath(self._metadata_path)
            .joinpath(self.name)
            .is_dir()
        ):
            raise ValueError(f"No data for '{self.name}'")

    def _replace_filename_with_resource(self, filename):
        """
        Return a package resource (from package data) for a given filename.

        Parameters
        ----------
        filename : :class:`str`
            Name of the file the package resource shall be returned for

        Returns
        -------
        resource : :class:`pathlib.PosixPath`
            Package resource accessible from within a Python package

        """
        resource = (
            importlib.resources.files(__package__)
            .joinpath(self._data_path)
            .joinpath(filename)
        )
        return resource

    def _import_material(self, metadata):
        """
        Import data and metadata for a given material.

        Parameters
        ----------
        metadata : :class:`ocdb.io.Metadata`
            Metadata for the dataset.

        Returns
        -------
        material : :class:`ocdb.material.Material`
            Data and metadata for the given material

        """
        importer = self._importer_factory.get_importer(metadata)
        material = importer.import_data()
        material.processing_step_factory = self._processing_step_factory
        if hasattr(ocdb.plotting, "plt"):
            material.plotter_factory = self._plotter_factory
        return material

    def _add_versions(self, material, metadata):
        """
        Add versions of a dataset for a given material.

        Only in case that the metadata for a given dataset contain versions
        will additional versions of this dataset be imported. Versions are
        represented as :obj:`ocdb.material.Version` objects and appended to
        the :attr:`ocdb.material.Material.versions` list.

        .. note::

            Currently, only the current version of a dataset gets versions
            added to its metadata. Hence, there is no way to see from the
            versions that are themselves :obj:`ocdb.material.Material` objects
            if there are other versions. This may change in the future.

        Parameters
        ----------
        material : :class:`ocdb.material.Material`
            Material the versions should be imported and added for.

        metadata : :class:`ocdb.io.Metadata`
            Metadata of the material versions should be added for.

        """
        for version in metadata.versions:
            metadata_file = self._replace_filename_with_resource(
                version.metadata
            )
            # noinspection PyTypeChecker
            version_metadata = ocdb.io.Metadata(filename=metadata_file)
            version_metadata.file["name"] = (
                self._replace_filename_with_resource(
                    version_metadata.file["name"]
                )
            )
            dataset_version = ocdb.material.Version()
            dataset_version.material = self._import_material(version_metadata)
            dataset_version.description = version.description
            material.versions.append(dataset_version)
