import os
import unittest
import yaml

from ocdb import io, material


class TestDataImporter(unittest.TestCase):
    def setUp(self):
        self.importer = io.DataImporter()
        self.data_filename = "foo.txt"
        self.metadata_filename = "foo.yaml"

    def tearDown(self):
        for file in [self.data_filename, self.metadata_filename]:
            if os.path.exists(file):
                os.remove(file)

    def create_files(self):
        with open(self.data_filename, "w+", encoding="utf8") as f:
            f.write("")

        metadata = {
            "file": {"name": self.data_filename},
            "material": {"name": "Cobalt", "symbol": "Co"},
        }
        with open(self.metadata_filename, "w+", encoding="utf8") as f:
            f.write(yaml.dump(metadata))

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "data_filename",
            "metadata_filename",
        ]
        for attribute in attributes:
            self.assertTrue(hasattr(self.importer, attribute))

    def test_import_without_metadata_filename_raises(self):
        self.importer.data_filename = self.data_filename
        with self.assertRaises(ValueError):
            self.importer.import_data()

    def test_import_without_data_filename_raises(self):
        with self.assertRaises(ValueError):
            self.importer.import_data()

    def test_import_data_returns_material(self):
        self.create_files()
        self.importer.metadata_filename = self.metadata_filename
        self.assertIsInstance(self.importer.import_data(), material.Material)

    def test_import_with_nonexisting_data_file_raises(self):
        self.importer.metadata_filename = self.metadata_filename
        with self.assertRaises(FileNotFoundError):
            self.importer.import_data()

    def test_import_with_nonexisting_metadata_file_raises(self):
        self.create_files()
        os.remove(self.metadata_filename)
        self.importer.metadata_filename = self.metadata_filename
        with self.assertRaises(FileNotFoundError):
            self.importer.import_data()

    def test_setting_metadata_filename_on_instantiation(self):
        importer = io.DataImporter(metadata=self.metadata_filename)
        self.assertEqual(self.metadata_filename, importer.metadata_filename)

    def test_import_reads_metadata(self):
        self.create_files()
        self.importer.metadata_filename = self.metadata_filename
        self.importer.import_data()
        self.assertTrue(self.importer.metadata)

    def test_import_maps_name(self):
        self.create_files()
        self.importer.metadata_filename = self.metadata_filename
        material_ = self.importer.import_data()
        self.assertTrue(material_.name)

    def test_import_maps_symbol(self):
        self.create_files()
        self.importer.metadata_filename = self.metadata_filename
        material_ = self.importer.import_data()
        self.assertTrue(material_.name)


DATA_WITH_UNCERTAINTIES = """
# Optical constants for Co created by PTB
# Reconstructed from reflection measurements in the wavelength range 8 - 25 nm
# 40 nm Co thin film in a multilayer on Si (C/ Co/ Ru/ Si) (measured 4/2022)
# n = (1-delta) - (i*beta)
# The values are provided with their 3-sigma uncertainty bounds. HB: Higher Bound. LB: Lower Bound.
#lambda/nm	1-delta	beta	1-delta_LB	1-delta_HB	beta_LB	beta_HB
# ------------------------
8.0	0.96788	0.02267	0.96772	0.96804	0.02253	0.0228
8.1	0.96713	0.02328	0.96697	0.96729	0.02315	0.02341
8.2	0.96639	0.02393	0.96623	0.96656	0.0238	0.02407
8.3	0.96564	0.02463	0.96546	0.96581	0.0245	0.02477
8.4	0.96491	0.02536	0.96474	0.96508	0.02523	0.0255
"""

DATA_WITHOUT_UNCERTAINTIES = """
# Optical constants for Ni created by PTB
# Reconstructed from reflection measurements in the wavelength range 10 - 16 nm
# 25 nm Ni thin film on Si (measured 04/2016)
# n = (1-delta) - (i*beta)
# 
# lambda/nm 1-delta beta
# ------------------------
10.00	 0.95861	 0.04855
10.10	 0.95888	 0.04955
10.20	 0.95915	 0.05041
10.30	 0.95940	 0.05113
"""


class TestTxtDataImporter(unittest.TestCase):
    def setUp(self):
        self.importer = io.TxtDataImporter()
        self.data_filename = "foo.txt"
        self.metadata_filename = "foo.yaml"

    def tearDown(self):
        for file in [self.data_filename, self.metadata_filename]:
            if os.path.exists(file):
                os.remove(file)

    def create_files(self):
        with open(self.data_filename, "w+", encoding="utf8") as f:
            f.write(DATA_WITH_UNCERTAINTIES)

        metadata = {
            "file": {"name": self.data_filename},
            "material": {"name": "Cobalt", "symbol": "Co"},
        }
        with open(self.metadata_filename, "w+", encoding="utf8") as f:
            f.write(yaml.dump(metadata))

    def test_instantiate_class(self):
        pass

    def test_import_data_sets_wavelength_in_n(self):
        self.create_files()
        self.importer.metadata_filename = self.metadata_filename
        material_ = self.importer.import_data()
        self.assertTrue(material_.n()[0][0])

    def test_import_data_sets_data_in_n(self):
        self.create_files()
        self.importer.metadata_filename = self.metadata_filename
        material_ = self.importer.import_data()
        self.assertTrue(material_.n()[1][0])

    def test_import_data_sets_wavelength_in_k(self):
        self.create_files()
        self.importer.metadata_filename = self.metadata_filename
        material_ = self.importer.import_data()
        self.assertTrue(material_.k()[0][0])

    def test_import_data_sets_data_in_k(self):
        self.create_files()
        self.importer.metadata_filename = self.metadata_filename
        material_ = self.importer.import_data()
        self.assertTrue(material_.k()[1][0])

    def test_import_data_sets_wavelength_metadata_in_n(self):
        self.create_files()
        self.importer.metadata_filename = self.metadata_filename
        material_ = self.importer.import_data()
        self.assertEqual("wavelength", material_.n_data.axes[0].quantity)
        self.assertEqual(r"\lambda", material_.n_data.axes[0].symbol)
        self.assertEqual("nm", material_.n_data.axes[0].unit)

    def test_import_data_sets_wavelength_metadata_in_k(self):
        self.create_files()
        self.importer.metadata_filename = self.metadata_filename
        material_ = self.importer.import_data()
        self.assertEqual("wavelength", material_.k_data.axes[0].quantity)
        self.assertEqual(r"\lambda", material_.k_data.axes[0].symbol)
        self.assertEqual("nm", material_.k_data.axes[0].unit)

    def test_import_data_with_uncertainties_sets_uncertainties(self):
        self.create_files()
        self.importer.metadata_filename = self.metadata_filename
        material_ = self.importer.import_data()
        self.assertTrue(material_.n_data.has_uncertainties())
        self.assertTrue(material_.k_data.has_uncertainties())

    def test_import_data_without_uncertainties_doesnt_set_uncertainties(self):
        self.create_files()
        with open(self.data_filename, "w", encoding="utf8") as f:
            f.write(DATA_WITHOUT_UNCERTAINTIES)
        self.importer.metadata_filename = self.metadata_filename
        material_ = self.importer.import_data()
        self.assertFalse(material_.n_data.has_uncertainties())
        self.assertFalse(material_.k_data.has_uncertainties())


class TestCreateMetadataFile(unittest.TestCase):
    def setUp(self):
        self.filename = "foo.yaml"

    def tearDown(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def test_crate_metadata_file_creates_file(self):
        io.create_metadata_file(filename=self.filename)
        self.assertTrue(os.path.exists(self.filename))

    def test_create_metadata_file_without_filename_raises(self):
        with self.assertRaises(ValueError):
            io.create_metadata_file()
