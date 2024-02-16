import unittest

import ocdb
import ocdb.material


class TestPackageImport(unittest.TestCase):
    def setUp(self):
        self.collections = ["elements", "compositions"]

    def test_ocdb_has_collections(self):
        for collection in self.collections:
            self.assertTrue(hasattr(ocdb, collection))

    def test_collections_are_collections(self):
        for collection in self.collections:
            self.assertIsInstance(
                getattr(ocdb, collection), ocdb.material.Collection
            )

    def test_remove_unnecessary_symbols(self):
        symbols = ["collection_creator", "collection", "collection_name"]
        for symbol in symbols:
            self.assertFalse(hasattr(ocdb, symbol))
