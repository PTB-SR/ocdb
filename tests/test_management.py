import unittest

import ocdb.material
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
