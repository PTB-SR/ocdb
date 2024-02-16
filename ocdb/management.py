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
        importer_factory = ocdb.io.DataImporterFactory()
        for file in (
            importlib.resources.files(__package__)
            .joinpath(self._metadata_path)
            .joinpath(self.name)
            .iterdir()
        ):
            metadata = ocdb.io.Metadata(filename=file)
            metadata.file["name"] = (
                importlib.resources.files(__package__)
                .joinpath(self._data_path)
                .joinpath(metadata.file["name"])
            )
            importer = importer_factory.get_importer(metadata)
            material = importer.import_data()
            material.processing_step_factory = (
                ocdb.processing.ProcessingStepFactory()
            )
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
