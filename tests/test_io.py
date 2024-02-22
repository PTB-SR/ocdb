import datetime
import os
import unittest

import bibrecord.record
import yaml

from ocdb import io, material


class TestDataImporterFactory(unittest.TestCase):
    def setUp(self):
        self.factory = io.DataImporterFactory()
        self.metadata = io.Metadata()
        self.metadata.file["format"] = "text"

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "references",
        ]
        for attribute in attributes:
            self.assertTrue(hasattr(self.factory, attribute))

    def test_references_contain_actual_references(self):
        self.assertTrue(self.factory.references.records)

    def test_get_importer_returns_data_importer(self):
        self.assertIsInstance(
            self.factory.get_importer(metadata=self.metadata), io.DataImporter
        )

    def test_get_importer_without_metadata_raises(self):
        with self.assertRaisesRegex(ValueError, "Missing metadata"):
            self.factory.get_importer()

    def test_get_importer_with_unknown_format_raises(self):
        self.metadata.file["format"] = "unknown"
        with self.assertRaisesRegex(
            NotImplementedError, "Importer for format .* not implemented"
        ):
            self.factory.get_importer(metadata=self.metadata)

    def test_get_importer_sets_metadata_in_importer(self):
        importer = self.factory.get_importer(metadata=self.metadata)
        self.assertTrue(importer.metadata)

    def test_get_importer_sets_references_in_importer(self):
        importer = self.factory.get_importer(metadata=self.metadata)
        self.assertTrue(importer.references)


class TestDataImporter(unittest.TestCase):
    def setUp(self):
        self.importer = io.DataImporter()
        self.data_filename = "foo.txt"
        self.metadata = io.Metadata()
        self.metadata.file["name"] = self.data_filename
        self.metadata.material = {"name": "Cobalt", "symbol": "Co"}
        self.references = io.References()
        self.references.load()

    def tearDown(self):
        if os.path.exists(self.data_filename):
            os.remove(self.data_filename)

    def create_data_file(self):
        with open(self.data_filename, "w+", encoding="utf8") as f:
            f.write("")

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "data_filename",
            "metadata",
            "material",
            "references",
        ]
        for attribute in attributes:
            self.assertTrue(hasattr(self.importer, attribute))

    def test_import_without_metadata_raises(self):
        self.importer.data_filename = self.data_filename
        with self.assertRaises(ValueError):
            self.importer.import_data()

    def test_import_without_data_filename_raises(self):
        with self.assertRaises(ValueError):
            self.importer.import_data()

    def test_import_data_returns_material(self):
        self.create_data_file()
        self.importer.metadata = self.metadata
        self.assertIsInstance(self.importer.import_data(), material.Material)

    def test_import_with_nonexisting_data_file_raises(self):
        self.importer.metadata = self.metadata
        with self.assertRaises(FileNotFoundError):
            self.importer.import_data()

    def test_instantiating_with_metadata_sets_metadata(self):
        importer = io.DataImporter(metadata=self.metadata)
        self.assertTrue(importer.metadata)

    def test_import_maps_name(self):
        self.create_data_file()
        self.importer.metadata = self.metadata
        material_ = self.importer.import_data()
        self.assertTrue(material_.name)

    def test_import_maps_symbol(self):
        self.create_data_file()
        self.importer.metadata = self.metadata
        material_ = self.importer.import_data()
        self.assertTrue(material_.name)

    def test_import_maps_comment(self):
        self.create_data_file()
        self.metadata.comment = "Lorem ipsum"
        self.importer.metadata = self.metadata
        material_ = self.importer.import_data()
        self.assertEqual(self.metadata.comment, material_.metadata.comment)

    def test_import_maps_uncertainties(self):
        self.create_data_file()
        self.metadata.uncertainties["confidence_interval"] = "3 sigma"
        self.importer.metadata = self.metadata
        material_ = self.importer.import_data()
        self.assertEqual(
            self.metadata.uncertainties["confidence_interval"],
            material_.metadata.uncertainties.confidence_interval,
        )

    def test_import_maps_date(self):
        self.create_data_file()
        self.metadata.date = datetime.date.fromisoformat("2022-04-01")
        self.importer.metadata = self.metadata
        material_ = self.importer.import_data()
        self.assertEqual(
            self.metadata.date,
            material_.metadata.date,
        )

    def test_import_with_reference_adds_reference(self):
        self.create_data_file()
        self.metadata.references.append("ciesielski-zenodo-5602719")
        self.importer.metadata = self.metadata
        self.importer.references = self.references
        material_ = self.importer.import_data()
        self.assertTrue(material_.references)

    def test_import_with_reference_adds_reference_as_reference(self):
        self.create_data_file()
        self.metadata.references.append("ciesielski-zenodo-5602719")
        self.importer.metadata = self.metadata
        self.importer.references = self.references
        material_ = self.importer.import_data()
        self.assertIsInstance(
            material_.references[0], bibrecord.record.Record
        )


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
        self.metadata = io.Metadata()
        self.metadata.file["name"] = self.data_filename
        self.metadata.material = {"name": "Cobalt", "symbol": "Co"}

    def tearDown(self):
        if os.path.exists(self.data_filename):
            os.remove(self.data_filename)

    def create_data_file(self):
        with open(self.data_filename, "w+", encoding="utf8") as f:
            f.write(DATA_WITH_UNCERTAINTIES)

    def test_instantiate_class(self):
        pass

    def test_import_data_sets_wavelength_in_n(self):
        self.create_data_file()
        self.importer.metadata = self.metadata
        material_ = self.importer.import_data()
        self.assertTrue(material_.n()[0][0])

    def test_import_data_sets_data_in_n(self):
        self.create_data_file()
        self.importer.metadata = self.metadata
        material_ = self.importer.import_data()
        self.assertTrue(material_.n()[1][0])

    def test_import_data_sets_wavelength_in_k(self):
        self.create_data_file()
        self.importer.metadata = self.metadata
        material_ = self.importer.import_data()
        self.assertTrue(material_.k()[0][0])

    def test_import_data_sets_data_in_k(self):
        self.create_data_file()
        self.importer.metadata = self.metadata
        material_ = self.importer.import_data()
        self.assertTrue(material_.k()[1][0])

    def test_import_data_sets_wavelength_metadata_in_n(self):
        self.create_data_file()
        self.importer.metadata = self.metadata
        material_ = self.importer.import_data()
        self.assertEqual("wavelength", material_.n_data.axes[0].quantity)
        self.assertEqual(r"\lambda", material_.n_data.axes[0].symbol)
        self.assertEqual("nm", material_.n_data.axes[0].unit)

    def test_import_data_sets_wavelength_metadata_in_k(self):
        self.create_data_file()
        self.importer.metadata = self.metadata
        material_ = self.importer.import_data()
        self.assertEqual("wavelength", material_.k_data.axes[0].quantity)
        self.assertEqual(r"\lambda", material_.k_data.axes[0].symbol)
        self.assertEqual("nm", material_.k_data.axes[0].unit)

    def test_import_data_with_uncertainties_sets_uncertainties(self):
        self.create_data_file()
        self.importer.metadata = self.metadata
        material_ = self.importer.import_data()
        self.assertTrue(material_.n_data.has_uncertainties())
        self.assertTrue(material_.k_data.has_uncertainties())

    def test_import_data_without_uncertainties_doesnt_set_uncertainties(self):
        self.create_data_file()
        with open(self.data_filename, "w", encoding="utf8") as f:
            f.write(DATA_WITHOUT_UNCERTAINTIES)
        self.importer.metadata = self.metadata
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

    def test_create_metadata_writes_correct_metadata(self):
        metadata = io.Metadata()
        metadata.versions.append(io.VersionMetadata())
        metadata.references.append("")
        io.create_metadata_file(filename=self.filename)
        with open(self.filename, "r", encoding="utf8") as file:
            metadata_dict = yaml.safe_load(file)
        self.assertDictEqual(metadata_dict, metadata.to_dict())


class TestMetadata(unittest.TestCase):
    def setUp(self):
        self.metadata = io.Metadata()
        metadata = io.Metadata()
        metadata.versions.append(io.VersionMetadata())
        metadata.references.append("")
        self.metadata_dict = metadata.to_dict()
        # self.metadata_dict = copy.deepcopy(io.METADATA_DICT)
        self.filename = "test.yaml"

    def tearDown(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def create_metadata_file(self):
        with open(self.filename, "w+", encoding="utf8") as file:
            file.write(yaml.dump(self.metadata_dict))

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "format",
            "file",
            "material",
            "uncertainties",
            "references",
            "date",
            "versions",
            "comment",
        ]
        for attribute in attributes:
            self.assertTrue(hasattr(self.metadata, attribute))

    def test_format_is_readonly_property(self):
        with self.assertRaises(AttributeError):
            # noinspection PyPropertyAccess
            self.metadata.format = {}

    def test_from_dict_maps_comment(self):
        self.metadata_dict["comment"] = "Lorem ipsum"
        self.metadata.from_dict(metadata=self.metadata_dict)
        self.assertEqual(self.metadata_dict["comment"], self.metadata.comment)

    def test_from_dict_does_not_map_nonexisting_attribute(self):
        self.metadata_dict["foo"] = "bar"
        self.metadata.from_dict(metadata=self.metadata_dict)
        self.assertFalse(hasattr(self.metadata, "foo"))

    def test_from_dict_updates_dict_attributes(self):
        self.metadata_dict["file"] = {"name": "bar.dat"}
        self.metadata.from_dict(metadata=self.metadata_dict)
        file_metadata = {"name": "bar.dat", "format": ""}
        self.assertDictEqual(file_metadata, self.metadata.file)

    def test_from_dict_with_missing_format_key_raises(self):
        self.metadata_dict.pop("format")
        with self.assertRaisesRegex(KeyError, "Wrong metadata schema"):
            self.metadata.from_dict(metadata=self.metadata_dict)

    def test_from_dict_with_wrong_format_raises(self):
        self.metadata_dict["format"]["type"] = "Wrong format"
        with self.assertRaisesRegex(ValueError, "Wrong metadata format"):
            self.metadata.from_dict(metadata=self.metadata_dict)

    def test_from_dict_with_versions_adds_version_object(self):
        self.metadata.from_dict(metadata=self.metadata_dict)
        self.assertIsInstance(self.metadata.versions[0], io.VersionMetadata)

    def test_from_file_maps_comment(self):
        self.metadata_dict["comment"] = "Lorem ipsum"
        self.create_metadata_file()
        self.metadata.from_file(self.filename)
        self.assertEqual(self.metadata_dict["comment"], self.metadata.comment)

    def test_from_file_maps_date(self):
        self.metadata_dict["date"] = "2022-01-01"
        self.create_metadata_file()
        self.metadata.from_file(self.filename)
        self.assertEqual(
            datetime.date.fromisoformat(self.metadata_dict["date"]),
            self.metadata.date,
        )

    def test_to_dict_returns_dict(self):
        self.assertIsInstance(self.metadata.to_dict(), dict)

    def test_to_dict_returns_dict_with_correct_keys(self):
        keys = [
            "format",
            "file",
            "material",
            "uncertainties",
            "references",
            "date",
            "versions",
            "comment",
        ]
        self.assertListEqual(keys, list(self.metadata.to_dict().keys()))

    def test_to_dict_converts_version_in_dict(self):
        self.metadata.versions.append(io.VersionMetadata())
        self.assertIsInstance(self.metadata.to_dict()["versions"][0], dict)

    def test_to_dict_converts_date_in_dict(self):
        self.assertEqual(
            str(self.metadata.date), self.metadata.to_dict()["date"]
        )

    def test_instantiate_with_filename_reads_from_file(self):
        self.metadata_dict["comment"] = "Lorem ipsum"
        self.create_metadata_file()
        metadata = io.Metadata(filename=self.filename)
        self.assertEqual(self.metadata_dict["comment"], metadata.comment)


class TestVersionMetadata(unittest.TestCase):
    def setUp(self):
        self.metadata = io.VersionMetadata()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "identifier",
            "description",
            "metadata",
        ]
        for attribute in attributes:
            self.assertTrue(hasattr(self.metadata, attribute))

    def test_from_dict_maps_attribute(self):
        metadata_dict = {"identifier": "foo"}
        self.metadata.from_dict(metadata=metadata_dict)
        self.assertEqual(
            metadata_dict["identifier"], self.metadata.identifier
        )

    def test_from_dict_does_not_map_nonexisting_attribute(self):
        metadata_dict = {"foo": "bar"}
        self.metadata.from_dict(metadata=metadata_dict)
        self.assertFalse(hasattr(self.metadata, "foo"))

    def test_to_dict_returns_dict(self):
        self.assertIsInstance(self.metadata.to_dict(), dict)

    def test_to_dict_returns_dict_with_correct_keys(self):
        self.assertListEqual(
            ["identifier", "description", "metadata"],
            list(self.metadata.to_dict().keys()),
        )


class TestReferences(unittest.TestCase):
    def setUp(self):
        self.references = io.References()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "records",
        ]
        for attribute in attributes:
            self.assertTrue(hasattr(self.references, attribute))

    def test_load_populates_entries(self):
        self.references.load()
        self.assertTrue(self.references.records)

    def test_entries_are_bibrecord_records(self):
        self.references.load()
        for key in self.references.records:
            self.assertIsInstance(
                self.references.records[key], bibrecord.record.Record
            )
