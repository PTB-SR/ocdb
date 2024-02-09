import numpy as np
import unittest

from ocdb import material


class TestMaterial(unittest.TestCase):
    def setUp(self):
        self.material = material.Material()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "name",
            "symbol",
            "references",
            "metadata",
        ]
        for attribute in attributes:
            self.assertTrue(hasattr(self.material, attribute))

    def test_name_is_string(self):
        self.assertIsInstance(self.material.name, str)

    def test_symbol_is_string(self):
        self.assertIsInstance(self.material.symbol, str)

    def test_references_is_list(self):
        self.assertIsInstance(self.material.references, list)

    def test_metadata_is_metadata(self):
        self.assertIsInstance(self.material.metadata, material.Metadata)

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
        self.assertEqual(4, len(n))
        self.assertIsInstance(n[0], np.ndarray)
        self.assertIsInstance(n[1], np.ndarray)
        self.assertIsInstance(n[2], np.ndarray)
        self.assertIsInstance(n[3], np.ndarray)

    def test_k_with_uncertainties_returns_four_numpy_arrays(self):
        k = self.material.k(uncertainties=True)
        self.assertEqual(4, len(k))
        self.assertIsInstance(k[0], np.ndarray)
        self.assertIsInstance(k[1], np.ndarray)
        self.assertIsInstance(k[2], np.ndarray)
        self.assertIsInstance(k[3], np.ndarray)

    def test_index_of_refr_with_uncertainties_returns_six_numpy_arrays(self):
        nk = self.material.index_of_refraction(uncertainties=True)
        self.assertEqual(6, len(nk))
        self.assertIsInstance(nk[0], np.ndarray)
        self.assertIsInstance(nk[1], np.ndarray)
        self.assertIsInstance(nk[2], np.ndarray)
        self.assertIsInstance(nk[3], np.ndarray)
        self.assertIsInstance(nk[4], np.ndarray)
        self.assertIsInstance(nk[5], np.ndarray)

    def test_n_has_correct_symbol_set_in_axis(self):
        self.assertEqual("n", self.material.n_data.axes[1].symbol)

    def test_k_has_correct_symbol_set_in_axis(self):
        self.assertEqual("k", self.material.k_data.axes[1].symbol)

    def test_n_has_correct_quantity_set_in_axis(self):
        self.assertEqual(
            "dispersion coefficient", self.material.n_data.axes[1].quantity
        )

    def test_k_has_correct_quantity_set_in_axis(self):
        self.assertEqual(
            "extinction coefficient", self.material.k_data.axes[1].quantity
        )

    def test_has_plotter_factory(self):
        self.assertIsInstance(
            self.material.plotter_factory, material.AbstractPlotterFactory
        )

    def test_plot_returns_plotter(self):
        self.assertIsInstance(self.material.plot(), material.AbstractPlotter)

    def test_plot_calls_plotter(self):
        class Plotter(material.AbstractPlotter):
            def __init__(self):
                self.called = False

            def plot(self):
                self.called = True

        class PlotterFactory(material.AbstractPlotterFactory):
            def get_plotter(self, **kwargs):
                return Plotter()

        self.material.plotter_factory = PlotterFactory()
        plotter = self.material.plot()
        self.assertTrue(plotter.called)

    def test_plot_sets_dataset_in_plotter(self):
        plotter = self.material.plot()
        self.assertIs(plotter.dataset, self.material)

    def test_plot_calls_plotter_factory_with_kwargs(self):
        class PlotterFactory(material.AbstractPlotterFactory):
            def __init__(self):
                self.kwargs = None

            def get_plotter(self, **kwargs):
                self.kwargs = kwargs
                return super().get_plotter(**kwargs)

        self.material.plotter_factory = PlotterFactory()
        kwargs = {"values": "k", "uncertainties": True}
        self.material.plot(**kwargs)
        self.assertDictEqual(self.material.plotter_factory.kwargs, kwargs)

    def test_has_processing_step_factory(self):
        self.assertIsInstance(
            self.material.processing_step_factory,
            material.AbstractProcessingStepFactory,
        )


class TestData(unittest.TestCase):
    def setUp(self):
        self.data = material.Data()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "data",
            "axes",
            "lower_bounds",
            "upper_bounds",
        ]
        for attribute in attributes:
            self.assertTrue(hasattr(self.data, attribute))

    def test_has_uncertainties_returns_true_if_lb_and_ub_present(self):
        self.data.lower_bounds = np.zeros(10)
        self.data.upper_bounds = np.ones(10)
        self.assertTrue(self.data.has_uncertainties())

    def test_has_uncertainties_returns_false_if_lb_is_missing(self):
        self.data.upper_bounds = np.ones(10)
        self.assertFalse(self.data.has_uncertainties())

    def test_has_uncertainties_returns_false_if_ub_is_missing(self):
        self.data.lower_bounds = np.zeros(10)
        self.assertFalse(self.data.has_uncertainties())

    def test_has_uncertainties_returns_false_if_lb_and_ub_are_missing(self):
        self.assertFalse(self.data.has_uncertainties())


class TestAxis(unittest.TestCase):
    def setUp(self):
        self.axis = material.Axis()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "values",
            "quantity",
            "unit",
            "symbol",
        ]
        for attribute in attributes:
            self.assertTrue(hasattr(self.axis, attribute))

    def test_get_label_returns_string(self):
        self.assertIsInstance(self.axis.get_label(), str)

    def test_get_label_with_quantity_only_returns_quantity(self):
        self.axis.quantity = "foo"
        self.assertEqual(self.axis.quantity, self.axis.get_label())

    def test_get_label_with_quantity_and_unit_returns_both_with_slash(self):
        self.axis.quantity = "foo"
        self.axis.unit = "bar"
        self.assertEqual(
            f"{self.axis.quantity} / {self.axis.unit}", self.axis.get_label()
        )

    def test_get_label_with_symbol_and_quantity_returns_symbol(self):
        self.axis.symbol = r"\delta"
        self.axis.quantity = "foo"
        self.assertEqual(f"${self.axis.symbol}$", self.axis.get_label())

    def test_get_label_with_symbol_quantity_unit_returns_symbol_unit(self):
        self.axis.symbol = r"\delta"
        self.axis.quantity = "foo"
        self.axis.unit = "bar"
        self.assertEqual(
            f"${self.axis.symbol}$ / {self.axis.unit}", self.axis.get_label()
        )


class TestMetadata(unittest.TestCase):
    def setUp(self):
        self.metadata = material.Metadata()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "sample",
            "measurement",
            "comment",
        ]
        for attribute in attributes:
            self.assertTrue(hasattr(self.metadata, attribute))

    def test_sample_is_correct_class(self):
        self.assertIsInstance(self.metadata.sample, material.Sample)

    def test_measurement_is_correct_class(self):
        self.assertIsInstance(self.metadata.measurement, material.Measurement)


class TestSample(unittest.TestCase):
    def setUp(self):
        self.sample = material.Sample()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "thickness",
            "substrate",
            "layer_stack",
            "morphology",
        ]
        for attribute in attributes:
            self.assertTrue(hasattr(self.sample, attribute))


class TestMeasurement(unittest.TestCase):
    def setUp(self):
        self.measurement = material.Measurement()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "type",
            "facility",
            "beamline",
            "date",
        ]
        for attribute in attributes:
            self.assertTrue(hasattr(self.measurement, attribute))


class TestCollection(unittest.TestCase):
    def setUp(self):
        self.collection = material.Collection()
        self.item = material.Material
        self.item.symbol = "Co"

    def test_instantiate_class(self):
        pass

    def test_add_item_sets_property_identical_to_item_symbol(self):
        self.collection.add_item(self.item)
        self.assertTrue(hasattr(self.collection, self.item.symbol))

    def test_iterate_over_collection_yields_material(self):
        self.collection.add_item(self.item)
        for element in self.collection:
            self.assertIsInstance(element, material.Material)


class TestAbstractPlotter(unittest.TestCase):
    def setUp(self):
        self.plotter = material.AbstractPlotter()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "dataset",
        ]
        for attribute in attributes:
            self.assertTrue(hasattr(self.plotter, attribute))

    def test_has_plot_method(self):
        self.assertTrue(hasattr(self.plotter, "plot"))
        self.assertTrue(callable(self.plotter.plot))


class TestAbstractPlotterFactory(unittest.TestCase):
    def setUp(self):
        self.factory = material.AbstractPlotterFactory()

    def test_instantiate_class(self):
        pass

    def test_get_plotter_returns_plotter(self):
        self.assertIsInstance(
            self.factory.get_plotter(), material.AbstractPlotter
        )

    def test_get_plotter_accepts_keyword_arguments(self):
        self.factory.get_plotter(foo=None, bar="foobar")


class TestAbstractProcessingStep(unittest.TestCase):
    def setUp(self):
        self.processing_step = material.AbstractProcessingStep()

    def test_instantiate_class(self):
        pass

    def test_has_attributes(self):
        attributes = [
            "data",
        ]
        for attribute in attributes:
            self.assertTrue(hasattr(self.processing_step, attribute))

    def test_has_process_method(self):
        self.assertTrue(hasattr(self.processing_step, "process"))
        self.assertTrue(callable(self.processing_step.process))


class TestAbstractProcessingStepFactory(unittest.TestCase):
    def setUp(self):
        self.factory = material.AbstractProcessingStepFactory()

    def test_instantiate_class(self):
        pass

    def test_get_processing_step_returns_processing_step(self):
        self.assertIsInstance(
            self.factory.get_processing_step(),
            material.AbstractProcessingStep,
        )

    def test_get_processing_step_accepts_keyword_arguments(self):
        self.factory.get_processing_step(foo=None, bar="foobar")
