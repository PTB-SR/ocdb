import unittest

import ocdb.material
import ocdb.plotting
import ocdb.processing
from ocdb import management


class TestCollectionCreator(unittest.TestCase):
    def setUp(self):
        self.collection_creator = management.CollectionCreator()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "name",
        ]
        for attribute in attributes:
            self.assertTrue(hasattr(self.collection_creator, attribute))

    def test_create_collection_creates_collection(self):
        self.collection_creator.name = "elements"
        collection = self.collection_creator.create()
        self.assertIsInstance(collection, ocdb.material.Collection)

    def test_create_without_name_raises(self):
        with self.assertRaisesRegex(
            ValueError, "No name provided for collection"
        ):
            self.collection_creator.create()

    def test_create_collection_with_name_creates_collection(self):
        collection = self.collection_creator.create(name="elements")
        self.assertIsInstance(collection, ocdb.material.Collection)

    def test_create_with_wrong_name_raises(self):
        self.collection_creator.name = "nonexistent_collection"
        with self.assertRaisesRegex(ValueError, "No data for"):
            self.collection_creator.create()

    def test_create_adds_actual_material(self):
        self.collection_creator.name = "elements"
        collection = self.collection_creator.create()
        self.assertTrue(hasattr(collection, "Co"))

    def test_with_versions_adds_version(self):
        self.collection_creator.name = "elements"
        collection = self.collection_creator.create()
        self.assertTrue(collection.Ta.versions)

    def test_added_version_is_version(self):
        self.collection_creator.name = "elements"
        collection = self.collection_creator.create()
        self.assertIsInstance(
            collection.Ta.versions[0], ocdb.material.Version
        )

    def test_added_version_has_material(self):
        self.collection_creator.name = "elements"
        collection = self.collection_creator.create()
        self.assertTrue(collection.Ta.versions[0].material)

    def test_added_version_has_description(self):
        self.collection_creator.name = "elements"
        collection = self.collection_creator.create()
        self.assertTrue(collection.Ta.versions[0].description)

    def test_create_adds_processing_step_factory_to_material(self):
        self.collection_creator.name = "elements"
        collection = self.collection_creator.create()
        self.assertIsInstance(
            collection.Co.processing_step_factory,
            ocdb.processing.ProcessingStepFactory,
        )

    @unittest.skipUnless(
        hasattr(ocdb.plotting, "plt"), "Matplotlib not loaded"
    )
    def test_create_adds_plotter_factory_to_material(self):
        self.collection_creator.name = "elements"
        collection = self.collection_creator.create()
        self.assertIsInstance(
            collection.Co.plotter_factory,
            ocdb.plotting.PlotterFactory,
        )
