import bibrecord.record
import numpy as np
import unittest

from ocdb import database


class TestMaterial(unittest.TestCase):
    def setUp(self):
        self.material = database.Material()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "name",
            "symbol",
            "reference",
            "metadata",
        ]
        for attribute in attributes:
            self.assertTrue(hasattr(self.material, attribute))

    def test_name_is_string(self):
        self.assertIsInstance(self.material.name, str)

    def test_symbol_is_string(self):
        self.assertIsInstance(self.material.symbol, str)

    def test_reference_is_bibrecord_record(self):
        self.assertIsInstance(
            self.material.reference, bibrecord.record.Record
        )

    def test_metadata_is_metadata(self):
        self.assertIsInstance(self.material.metadata, database.Metadata)

    def test_n_returns_two_numpy_arrays(self):
        n = self.material.n()
        self.assertIsInstance(n, tuple)
        self.assertIsInstance(n[0], np.ndarray)
        self.assertIsInstance(n[1], np.ndarray)

    def test_k_returns_two_numpy_arrays(self):
        k = self.material.k()
        self.assertIsInstance(k, tuple)
        self.assertIsInstance(k[0], np.ndarray)
        self.assertIsInstance(k[1], np.ndarray)

    def test_index_of_refraction_returns_real_and_complex_numpy_array(self):
        nk = self.material.index_of_refraction()
        self.assertIsInstance(nk, tuple)
        self.assertIsInstance(nk[0], np.ndarray)
        self.assertIsInstance(nk[1], np.ndarray)
        self.assertTrue(all(np.iscomplex(nk[1])))

    def test_n_with_uncertainties_returns_four_numpy_arrays(self):
        n = self.material.n(uncertainties=True)
        self.assertEquals(4, len(n))
        self.assertIsInstance(n[0], np.ndarray)
        self.assertIsInstance(n[1], np.ndarray)
        self.assertIsInstance(n[2], np.ndarray)
        self.assertIsInstance(n[3], np.ndarray)

    def test_k_with_uncertainties_returns_four_numpy_arrays(self):
        k = self.material.k(uncertainties=True)
        self.assertEquals(4, len(k))
        self.assertIsInstance(k[0], np.ndarray)
        self.assertIsInstance(k[1], np.ndarray)
        self.assertIsInstance(k[2], np.ndarray)
        self.assertIsInstance(k[3], np.ndarray)

    def test_index_of_refr_with_uncertainties_returns_six_numpy_arrays(self):
        nk = self.material.index_of_refraction(uncertainties=True)
        self.assertEquals(6, len(nk))
        self.assertIsInstance(nk[0], np.ndarray)
        self.assertIsInstance(nk[1], np.ndarray)
        self.assertIsInstance(nk[2], np.ndarray)
        self.assertIsInstance(nk[3], np.ndarray)
        self.assertIsInstance(nk[4], np.ndarray)
        self.assertIsInstance(nk[5], np.ndarray)


class TestMetadata(unittest.TestCase):
    def setUp(self):
        self.metadata = database.Metadata()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "layer_thickness",
            "substrate",
            "layer_stack",
            "date_of_measurement",
        ]
        for attribute in attributes:
            self.assertTrue(hasattr(self.metadata, attribute))


class TestCollection(unittest.TestCase):
    def setUp(self):
        self.collection = database.Collection()
        self.item = database.Material
        self.item.symbol = "Co"

    def test_instantiate_class(self):
        pass

    def test_add_item_sets_property_identical_to_item_symbol(self):
        self.collection.add_item(self.item)
        self.assertTrue(hasattr(self.collection, self.item.symbol))

    def test_iterate_over_collection_yields_material(self):
        self.collection.add_item(self.item)
        for element in self.collection:
            self.assertIsInstance(element, database.Material)
