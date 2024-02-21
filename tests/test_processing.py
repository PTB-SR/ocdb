import numpy as np
import unittest

from ocdb import material, processing


class TestProcessingStepFactory(unittest.TestCase):
    def setUp(self):
        self.factory = processing.ProcessingStepFactory()

    def test_instantiate_class(self):
        pass

    def test_is_abstract_processing_step_factory(self):
        self.assertIsInstance(
            self.factory, material.AbstractProcessingStepFactory
        )

    def test_get_processing_step_returns_list(self):
        self.assertIsInstance(self.factory.get_processing_steps(), list)

    def test_get_processing_step_returns_processing_step_in_list(self):
        self.assertIsInstance(
            self.factory.get_processing_steps()[0], processing.ProcessingStep
        )

    def test_get_processing_step_with_values_returns_interpolation(self):
        self.assertIsInstance(
            self.factory.get_processing_steps(values=13.5)[0],
            processing.Interpolation,
        )
        self.assertIsInstance(
            self.factory.get_processing_steps(values=np.linspace(1, 2, 11))[
                0
            ],
            processing.Interpolation,
        )

    def test_get_processing_step_with_values_sets_interpolation_kind(self):
        interpolation = self.factory.get_processing_steps(
            values=13.5, interpolation="foo"
        )[0]
        self.assertEqual(interpolation.parameters["kind"], "foo")

    def test_get_processing_step_with_values_sets_values(self):
        interpolation = self.factory.get_processing_steps(values=13.5)[0]
        self.assertEqual(interpolation.parameters["values"], 13.5)

    def test_get_processing_step_with_values_none_omits_interpolation(self):
        processing_step = self.factory.get_processing_steps(values=None)[0]
        self.assertNotIsInstance(
            processing_step,
            processing.Interpolation,
        )

    def test_get_processing_step_with_unit_returns_unit_conversion(self):
        self.assertIsInstance(
            self.factory.get_processing_steps(unit="eV")[0],
            processing.UnitConversion,
        )

    def test_get_processing_step_with_unit_sets_unit(self):
        unit_conversion = self.factory.get_processing_steps(unit="eV")[0]
        self.assertEqual(unit_conversion.parameters["unit"], "eV")

    def test_unit_conversion_comes_before_interpolation(self):
        processing_steps = self.factory.get_processing_steps(
            values=13.5, unit="eV"
        )
        self.assertIsInstance(processing_steps[0], processing.UnitConversion)
        self.assertIsInstance(processing_steps[1], processing.Interpolation)


class TestProcessingStep(unittest.TestCase):
    def setUp(self):
        self.processing_step = processing.ProcessingStep()

    def test_instantiate_class(self):
        pass

    def test_is_abstract_processing_step(self):
        self.assertIsInstance(
            self.processing_step, material.AbstractProcessingStep
        )

    def test_has_attributes(self):
        attributes = [
            "data",
        ]
        for attribute in attributes:
            self.assertTrue(hasattr(self.processing_step, attribute))

    def test_process_returns_data(self):
        self.assertIsInstance(self.processing_step.process(), material.Data)


class TestInterpolation(unittest.TestCase):
    def setUp(self):
        self.interpolation = processing.Interpolation()
        self.data = material.Data()
        self.data.data = np.linspace(2, 3, 11)
        self.data.axes[0].values = np.linspace(10, 20, 11)
        self.data.lower_bounds = np.linspace(1, 2, 11)
        self.data.upper_bounds = np.linspace(3, 4, 11)

    def test_instantiate_class(self):
        pass

    def test_interpolate_single_value_returns_data_with_one_value(self):
        self.interpolation.data = self.data
        self.interpolation.parameters["values"] = 13.5
        self.interpolation.process()
        self.assertEqual(self.interpolation.data.data.size, 1)
        self.assertEqual(self.interpolation.data.axes[0].values.size, 1)
        self.assertEqual(self.interpolation.data.lower_bounds.size, 1)
        self.assertEqual(self.interpolation.data.upper_bounds.size, 1)

    def test_interpolate_scalar_int_returns_data_with_one_value(self):
        self.interpolation.data = self.data
        self.interpolation.parameters["values"] = 13
        self.interpolation.process()
        self.assertEqual(self.interpolation.data.data.size, 1)
        self.assertEqual(self.interpolation.data.axes[0].values.size, 1)
        self.assertEqual(self.interpolation.data.lower_bounds.size, 1)
        self.assertEqual(self.interpolation.data.upper_bounds.size, 1)

    def test_interpolate_single_value_returns_correct_value_in_data(self):
        self.interpolation.data = self.data
        value = np.interp(13.5, self.data.axes[0].values, self.data.data)
        self.interpolation.parameters["values"] = 13.5
        self.interpolation.process()
        self.assertAlmostEqual(self.interpolation.data.data, value, 1e-5)

    def test_interpolate_single_value_returns_correct_value_in_axes(self):
        self.interpolation.data = self.data
        self.interpolation.parameters["values"] = 13.5
        self.interpolation.process()
        self.assertAlmostEqual(
            self.interpolation.data.axes[0].values,
            self.interpolation.parameters["values"],
            1e-5,
        )

    def test_interpolate_single_value_returns_correct_value_in_lb(self):
        self.interpolation.data = self.data
        value = np.interp(
            13.5, self.data.axes[0].values, self.data.lower_bounds
        )
        self.interpolation.parameters["values"] = 13.5
        self.interpolation.process()
        self.assertAlmostEqual(
            self.interpolation.data.lower_bounds,
            value,
            1e-5,
        )

    def test_interpolate_single_value_returns_correct_value_in_ub(self):
        self.interpolation.data = self.data
        value = np.interp(
            13.5, self.data.axes[0].values, self.data.upper_bounds
        )
        self.interpolation.parameters["values"] = 13.5
        self.interpolation.process()
        self.assertAlmostEqual(
            self.interpolation.data.upper_bounds,
            value,
            1e-5,
        )

    def test_interpolate_range_returns_data_with_correct_size(self):
        self.interpolation.data = self.data
        self.interpolation.parameters["values"] = np.linspace(13, 14, 11)
        self.interpolation.process()
        self.assertEqual(self.interpolation.data.data.size, 11)
        self.assertEqual(self.interpolation.data.axes[0].values.size, 11)
        self.assertEqual(self.interpolation.data.lower_bounds.size, 11)
        self.assertEqual(self.interpolation.data.upper_bounds.size, 11)

    def test_interpolate_without_uncertainties(self):
        self.data.lower_bounds = np.ndarray(0)
        self.data.upper_bounds = np.ndarray(0)
        self.interpolation.data = self.data
        self.interpolation.parameters["values"] = 13.5
        self.interpolation.process()
        self.assertEqual(self.interpolation.data.data.size, 1)
        self.assertEqual(self.interpolation.data.axes[0].values.size, 1)

    def test_interpolate_single_value_below_axis_range_raises(self):
        self.interpolation.data = self.data
        self.interpolation.parameters["values"] = -13.5
        message = f"Requested range not within data range. Available range:"
        with self.assertRaisesRegex(ValueError, message):
            self.interpolation.process()

    def test_interpolate_single_value_above_axis_range_raises(self):
        self.interpolation.data = self.data
        self.interpolation.parameters["values"] = 135.0
        with self.assertRaises(ValueError):
            self.interpolation.process()

    def test_interpolate_range_with_start_below_axis_range_raises(self):
        self.interpolation.data = self.data
        self.interpolation.parameters["values"] = np.linspace(5, 15, 11)
        with self.assertRaises(ValueError):
            self.interpolation.process()

    def test_interpolate_range_with_start_above_axis_range_raises(self):
        self.interpolation.data = self.data
        self.interpolation.parameters["values"] = np.linspace(25, 35, 11)
        with self.assertRaises(ValueError):
            self.interpolation.process()

    def test_interpolate_range_with_end_above_axis_range_raises(self):
        self.interpolation.data = self.data
        self.interpolation.parameters["values"] = np.linspace(15, 25, 11)
        with self.assertRaises(ValueError):
            self.interpolation.process()

    def test_interpolate_range_with_end_below_axis_range_raises(self):
        self.interpolation.data = self.data
        self.interpolation.parameters["values"] = np.linspace(-5, 5, 11)
        with self.assertRaises(ValueError):
            self.interpolation.process()

    def test_interpolate_single_value_with_data_provided_in_constructor(self):
        interpolation = processing.Interpolation(self.data)
        interpolation.parameters["values"] = 13.5
        interpolation.process()
        self.assertEqual(interpolation.data.data.size, 1)
        self.assertEqual(interpolation.data.axes[0].values.size, 1)
        self.assertEqual(interpolation.data.lower_bounds.size, 1)
        self.assertEqual(interpolation.data.upper_bounds.size, 1)

    def test_interpolate_single_na_value_with_kind_none_raises(self):
        self.interpolation.data = self.data
        self.interpolation.parameters["values"] = 13.4
        self.interpolation.parameters["kind"] = None
        with self.assertRaisesRegex(ValueError, r"Value\(s\) not available"):
            self.interpolation.process()

    def test_interpolate_range_na_value_with_kind_none_raises(self):
        self.interpolation.data = self.data
        self.interpolation.parameters["values"] = np.linspace(13.2, 13.6, 3)
        self.interpolation.parameters["kind"] = None
        with self.assertRaisesRegex(ValueError, r"Value\(s\) not available"):
            self.interpolation.process()

    def test_interpolate_range_na_value_with_kind_none_raises(self):
        self.interpolation.data = self.data
        self.interpolation.parameters["values"] = np.linspace(10, 20, 21)
        self.interpolation.parameters["kind"] = None
        with self.assertRaisesRegex(ValueError, r"Value\(s\) not available"):
            self.interpolation.process()


class TestUnitConversion(unittest.TestCase):
    def setUp(self):
        self.unit_conversion = processing.UnitConversion()
        self.data = material.Data()
        self.data.axes[0].values = np.linspace(10, 20, 11)
        # Note: c_0, eV, h_planck are all *exact* starting 2019 according to SI
        self.constants = {
            "c_0": 299792458,
            "eV": 1.602176634e-19,
            "h_planck": 6.62607015e-34,
        }

    def test_instantiate_class(self):
        pass

    def test_convert_without_unit_does_not_change_axis_values(self):
        self.data.axes[0].unit = "nm"
        self.unit_conversion.data = self.data
        processed_data = self.unit_conversion.process()
        np.testing.assert_allclose(
            processed_data.axes[0].values, self.data.axes[0].values
        )

    def test_convert_with_empty_unit_does_not_change_axis_values(self):
        self.data.axes[0].unit = "nm"
        self.unit_conversion.data = self.data
        self.unit_conversion.parameters["unit"] = ""
        processed_data = self.unit_conversion.process()
        np.testing.assert_allclose(
            processed_data.axes[0].values, self.data.axes[0].values
        )

    def test_convert_with_unknown_unit_raises(self):
        self.unit_conversion.data = self.data
        self.unit_conversion.parameters["unit"] = "unknown"
        with self.assertRaisesRegex(ValueError, "not supported"):
            self.unit_conversion.process()

    def test_convert_from_nm_to_ev(self):
        self.data.axes[0].unit = "nm"
        self.unit_conversion.data = self.data
        self.unit_conversion.parameters["unit"] = "eV"
        ev_values = (
            self.constants["h_planck"]
            / self.constants["eV"]
            * self.constants["c_0"]
            * 1e9
            / self.data.axes[0].values
        )
        processed_data = self.unit_conversion.process()
        np.testing.assert_allclose(processed_data.axes[0].values, ev_values)

    def test_convert_from_ev_to_nm(self):
        nm_values = self.data.axes[0].values
        self.data.axes[0].values = (
            self.constants["h_planck"]
            / self.constants["eV"]
            * self.constants["c_0"]
            * 1e9
            / self.data.axes[0].values
        )
        self.data.axes[0].unit = "ev"
        self.unit_conversion.data = self.data
        self.unit_conversion.parameters["unit"] = "nm"
        processed_data = self.unit_conversion.process()
        np.testing.assert_allclose(processed_data.axes[0].values, nm_values)

    def test_unit_is_case_insensitive(self):
        self.data.axes[0].unit = "nm"
        self.unit_conversion.data = self.data
        self.unit_conversion.parameters["unit"] = "ev"
        ev_values = (
            self.constants["h_planck"]
            / self.constants["eV"]
            * self.constants["c_0"]
            * 1e9
            / self.data.axes[0].values
        )
        processed_data = self.unit_conversion.process()
        np.testing.assert_allclose(processed_data.axes[0].values, ev_values)
