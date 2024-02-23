import matplotlib.figure
import matplotlib.axes
import matplotlib.pyplot as plt
import unittest

import numpy as np

from ocdb import material, plotting


class TestPlotterFactory(unittest.TestCase):
    def setUp(self):
        self.factory = plotting.PlotterFactory()
        self.material = material.Material()
        self.material.n_data.data = np.ones(10)
        self.material.n_data.axes[0].values = np.linspace(10, 12, 10)
        self.material.k_data.data = np.ones(10)
        self.material.k_data.axes[0].values = np.linspace(10, 12, 10)
        self.factory.material = self.material

    def test_instantiate_class(self):
        pass

    def test_is_abstract_plotter_factory(self):
        self.assertIsInstance(self.factory, material.AbstractPlotterFactory)

    def test_get_plotter_returns_plotter(self):
        self.assertIsInstance(
            self.factory.get_plotter(), plotting.BasePlotter
        )

    def test_get_plotter_without_values_returns_single_plotter(self):
        self.assertIsInstance(
            self.factory.get_plotter(), plotting.SinglePlotter
        )

    def test_get_plotter_with_values_n_or_k_returns_single_plotter(self):
        self.assertIsInstance(
            self.factory.get_plotter(values="n"), plotting.SinglePlotter
        )
        self.assertIsInstance(
            self.factory.get_plotter(values="k"), plotting.SinglePlotter
        )

    def test_get_plotter_with_values_n_sets_value_in_plotter(self):
        plotter = self.factory.get_plotter(values="n")
        self.assertEqual(plotter.parameters["values"], "n")

    def test_get_plotter_with_values_k_sets_value_in_plotter(self):
        plotter = self.factory.get_plotter(values="k")
        self.assertEqual(plotter.parameters["values"], "k")

    def test_get_plotter_with_values_both_returns_twin_plotter(self):
        self.assertIsInstance(
            self.factory.get_plotter(values="both"), plotting.TwinPlotter
        )

    def test_get_plotter_without_values_with_uncertainties(self):
        self.material.n_data.lower_bounds = np.zeros(10)
        self.material.n_data.upper_bounds = np.zeros(10)
        self.material.k_data.lower_bounds = np.zeros(10)
        self.material.k_data.upper_bounds = np.zeros(10)
        self.assertIsInstance(
            self.factory.get_plotter(uncertainties=True),
            plotting.SingleUncertaintiesPlotter,
        )

    def test_get_plotter_with_values_n_with_uncertainties(self):
        self.material.n_data.lower_bounds = np.zeros(10)
        self.material.n_data.upper_bounds = np.zeros(10)
        self.material.k_data.lower_bounds = np.zeros(10)
        self.material.k_data.upper_bounds = np.zeros(10)
        plotter = self.factory.get_plotter(values="n", uncertainties=True)
        self.assertIsInstance(
            plotter,
            plotting.SingleUncertaintiesPlotter,
        )
        self.assertEqual(plotter.parameters["values"], "n")

    def test_get_plotter_with_values_k_with_uncertainties(self):
        self.material.n_data.lower_bounds = np.zeros(10)
        self.material.n_data.upper_bounds = np.zeros(10)
        self.material.k_data.lower_bounds = np.zeros(10)
        self.material.k_data.upper_bounds = np.zeros(10)
        plotter = self.factory.get_plotter(values="k", uncertainties=True)
        self.assertIsInstance(
            plotter,
            plotting.SingleUncertaintiesPlotter,
        )
        self.assertEqual(plotter.parameters["values"], "k")

    def test_get_plotter_with_values_both_with_uncertainties(self):
        self.material.n_data.lower_bounds = np.zeros(10)
        self.material.n_data.upper_bounds = np.zeros(10)
        self.material.k_data.lower_bounds = np.zeros(10)
        self.material.k_data.upper_bounds = np.zeros(10)
        self.assertIsInstance(
            self.factory.get_plotter(values="both", uncertainties=True),
            plotting.TwinUncertaintiesPlotter,
        )

    def test_without_values_with_na_uncertainties_returns_single_plotter(
        self,
    ):
        self.assertIsInstance(
            self.factory.get_plotter(uncertainties=True),
            plotting.SinglePlotter,
        )
        self.assertNotIsInstance(
            self.factory.get_plotter(uncertainties=True),
            plotting.SingleUncertaintiesPlotter,
        )

    def test_n_with_na_uncertainties_returns_single_plotter(self):
        plotter = self.factory.get_plotter(values="n", uncertainties=True)
        self.assertIsInstance(
            plotter,
            plotting.SinglePlotter,
        )
        self.assertNotIsInstance(
            plotter,
            plotting.SingleUncertaintiesPlotter,
        )
        self.assertEqual(plotter.parameters["values"], "n")

    def test_k_with_na_uncertainties_returns_single_plotter(self):
        plotter = self.factory.get_plotter(values="k", uncertainties=True)
        self.assertIsInstance(
            plotter,
            plotting.SinglePlotter,
        )
        self.assertNotIsInstance(
            plotter,
            plotting.SingleUncertaintiesPlotter,
        )
        self.assertEqual(plotter.parameters["values"], "k")

    def test_plot_both_with_na_uncertainties_returns_twin_plotter(self):
        self.assertIsInstance(
            self.factory.get_plotter(values="both", uncertainties=True),
            plotting.TwinPlotter,
        )
        self.assertNotIsInstance(
            self.factory.get_plotter(values="both", uncertainties=True),
            plotting.TwinUncertaintiesPlotter,
        )


class TestBasePlotter(unittest.TestCase):
    def setUp(self):
        self.plotter = plotting.BasePlotter()

    def tearDown(self):
        plt.close()

    def test_instantiate_class(self):
        pass

    def test_is_abstract_plotter(self):
        self.assertIsInstance(self.plotter, material.AbstractPlotter)

    def test_has_attributes(self):
        attributes = [
            "fig",
            "figure",
            "ax",
            "axes",
            "dataset",
            "parameters",
        ]
        for attribute in attributes:
            self.assertTrue(hasattr(self.plotter, attribute))

    def test_figure_is_identical_with_fig(self):
        self.plotter.figure = "Foo"
        self.assertEqual(self.plotter.figure, self.plotter.fig)

    def test_axes_is_identical_with_ax(self):
        self.plotter.axes = "Foo"
        self.assertEqual(self.plotter.axes, self.plotter.ax)

    def test_plot_sets_figure_to_matplotlib_figure(self):
        self.plotter.plot()
        self.assertIsInstance(self.plotter.figure, matplotlib.figure.Figure)

    def test_plot_sets_axes_to_matplotlib_axes(self):
        self.plotter.plot()
        self.assertIsInstance(self.plotter.axes, matplotlib.axes.Axes)


class TestSinglePlotter(unittest.TestCase):
    def setUp(self):
        self.plotter = plotting.SinglePlotter()
        self.material = material.Material()
        self.material.n_data.data = np.ones(10)
        self.material.n_data.axes[0].values = np.linspace(10, 12, 10)
        self.material.n_data.axes[0].symbol = r"\lambda"
        self.material.n_data.axes[0].quantity = "wavelength"
        self.material.n_data.axes[0].unit = "nm"
        self.material.k_data.data = np.ones(10) * 2
        self.material.k_data.axes[0].values = np.linspace(10, 12, 10)
        self.material.k_data.axes[0].symbol = r"\lambda"
        self.material.k_data.axes[0].quantity = "wavelength"
        self.material.k_data.axes[0].unit = "nm"

    def tearDown(self):
        plt.close()

    def test_instantiate_class(self):
        pass

    def test_plot_with_values_n_plots_n(self):
        self.plotter.dataset = self.material
        self.plotter.parameters["values"] = "n"
        self.plotter.plot()
        np.testing.assert_array_equal(
            self.plotter.axes.get_lines()[0].get_ydata(),
            self.material.n_data.data,
        )

    def test_plot_with_values_k_plots_k(self):
        self.plotter.dataset = self.material
        self.plotter.parameters["values"] = "k"
        self.plotter.plot()
        np.testing.assert_array_equal(
            self.plotter.axes.get_lines()[0].get_ydata(),
            self.material.k_data.data,
        )

    def test_plot_n_values_labels_x_axis(self):
        self.plotter.dataset = self.material
        self.plotter.parameters["values"] = "n"
        self.plotter.plot()
        self.assertEqual(
            self.plotter.axes.get_xlabel(),
            self.material.n_data.axes[0].get_label(),
        )

    def test_plot_n_values_labels_y_axis(self):
        self.plotter.dataset = self.material
        self.plotter.parameters["values"] = "n"
        self.plotter.plot()
        self.assertEqual(
            self.plotter.axes.get_ylabel(),
            self.material.n_data.axes[1].get_label(),
        )

    def test_plot_k_values_labels_x_axis(self):
        self.plotter.dataset = self.material
        self.plotter.parameters["values"] = "k"
        self.plotter.plot()
        self.assertEqual(
            self.plotter.axes.get_xlabel(),
            self.material.k_data.axes[0].get_label(),
        )

    def test_plot_k_values_labels_y_axis(self):
        self.plotter.dataset = self.material
        self.plotter.parameters["values"] = "k"
        self.plotter.plot()
        self.assertEqual(
            self.plotter.axes.get_ylabel(),
            self.material.k_data.axes[1].get_label(),
        )


class TestTwinPlotter(unittest.TestCase):
    def setUp(self):
        self.plotter = plotting.TwinPlotter()
        self.material = material.Material()
        self.material.n_data.data = np.linspace(0.98, 0.99, 10)
        self.material.n_data.axes[0].values = np.linspace(10, 12, 10)
        self.material.n_data.axes[0].symbol = r"\lambda"
        self.material.n_data.axes[0].quantity = "wavelength"
        self.material.n_data.axes[0].unit = "nm"
        self.material.k_data.data = np.linspace(0.02, 0.01, 10)
        self.material.k_data.axes[0].values = np.linspace(10, 12, 10)
        self.material.k_data.axes[0].symbol = r"\lambda"
        self.material.k_data.axes[0].quantity = "wavelength"
        self.material.k_data.axes[0].unit = "nm"

    def tearDown(self):
        plt.close()

    def test_instantiate_class(self):
        pass

    def test_has_additional_axes_attributes(self):
        attributes = [
            "ax2",
            "axes2",
        ]
        for attribute in attributes:
            self.assertTrue(hasattr(self.plotter, attribute))

    def test_axes2_is_identical_with_ax2(self):
        self.plotter.axes = object()
        self.assertIs(self.plotter.axes2, self.plotter.ax2)

    def test_plot_plots_n(self):
        self.plotter.dataset = self.material
        self.plotter.plot()
        np.testing.assert_array_equal(
            self.plotter.axes.get_lines()[0].get_ydata(),
            self.material.n_data.data,
        )

    def test_plot_sets_axes2_to_matplotlib_axes(self):
        self.plotter.dataset = self.material
        self.plotter.plot()
        self.assertIsInstance(self.plotter.axes2, matplotlib.axes.Axes)

    def test_plot_plots_k(self):
        self.plotter.dataset = self.material
        self.plotter.plot()
        np.testing.assert_array_equal(
            self.plotter.axes2.get_lines()[0].get_ydata(),
            self.material.k_data.data,
        )

    def test_plot_labels_x_axis(self):
        self.plotter.dataset = self.material
        self.plotter.plot()
        self.assertEqual(
            self.plotter.axes.get_xlabel(),
            self.material.n_data.axes[0].get_label(),
        )

    def test_plot_labels_first_y_axis(self):
        self.plotter.dataset = self.material
        self.plotter.plot()
        self.assertEqual(
            self.plotter.axes.get_ylabel(),
            self.material.n_data.axes[1].get_label(),
        )

    def test_plot_labels_second_y_axis(self):
        self.plotter.dataset = self.material
        self.plotter.plot()
        self.assertEqual(
            self.plotter.axes2.get_ylabel(),
            self.material.k_data.axes[1].get_label(),
        )

    def test_plot_sets_color_for_n_values(self):
        prop_cycle = plt.rcParams["axes.prop_cycle"]
        colors = prop_cycle.by_key()["color"]
        self.plotter.dataset = self.material
        self.plotter.plot()
        self.assertEqual(
            self.plotter.axes.get_lines()[0].get_color(),
            colors[0],
        )

    def test_plot_sets_color_for_k_values(self):
        prop_cycle = plt.rcParams["axes.prop_cycle"]
        colors = prop_cycle.by_key()["color"]
        self.plotter.dataset = self.material
        self.plotter.plot()
        self.assertEqual(
            self.plotter.axes2.get_lines()[0].get_color(),
            colors[1],
        )

    def test_plot_sets_tick_color_for_first_axis(self):
        prop_cycle = plt.rcParams["axes.prop_cycle"]
        colors = prop_cycle.by_key()["color"]
        self.plotter.dataset = self.material
        self.plotter.plot()
        self.assertEqual(
            self.plotter.axes.get_yaxis().get_tick_params()["labelcolor"],
            colors[0],
        )

    def test_plot_sets_tick_color_for_second_axis(self):
        prop_cycle = plt.rcParams["axes.prop_cycle"]
        colors = prop_cycle.by_key()["color"]
        self.plotter.dataset = self.material
        self.plotter.plot()
        self.assertEqual(
            self.plotter.axes2.get_yaxis().get_tick_params()["labelcolor"],
            colors[1],
        )


class TestSingleUncertaintiesPlotter(unittest.TestCase):
    def setUp(self):
        self.plotter = plotting.SingleUncertaintiesPlotter()
        self.material = material.Material()
        self.material.n_data.data = np.linspace(0.98, 0.99, 10)
        self.material.n_data.lower_bounds = (
            self.material.n_data.data
            - np.random.normal(0.005, 0.002, size=10)
        )
        self.material.n_data.upper_bounds = (
            self.material.n_data.data
            + np.random.normal(0.005, 0.002, size=10)
        )
        self.material.n_data.axes[0].values = np.linspace(10, 12, 10)
        self.material.n_data.axes[0].symbol = r"\lambda"
        self.material.n_data.axes[0].quantity = "wavelength"
        self.material.n_data.axes[0].unit = "nm"
        self.material.k_data.data = np.linspace(0.02, 0.01, 10)
        self.material.k_data.lower_bounds = (
            self.material.k_data.data - np.random.normal(0.01, 0.002, size=10)
        )
        self.material.k_data.upper_bounds = (
            self.material.k_data.data
            + np.random.normal(0.005, 0.002, size=10)
        )
        self.material.k_data.axes[0].values = np.linspace(10, 12, 10)
        self.material.k_data.axes[0].symbol = r"\lambda"
        self.material.k_data.axes[0].quantity = "wavelength"
        self.material.k_data.axes[0].unit = "nm"

    def tearDown(self):
        plt.close()

    def test_instantiate_class(self):
        pass

    def test_plot_with_values_n_plots_n(self):
        self.plotter.dataset = self.material
        self.plotter.parameters["values"] = "n"
        self.plotter.plot()
        np.testing.assert_array_equal(
            self.plotter.axes.get_lines()[0].get_ydata(),
            self.material.n_data.data,
        )

    def test_plot_with_values_n_plots_n_uncertainties(self):
        self.plotter.dataset = self.material
        self.plotter.parameters["values"] = "n"
        self.plotter.plot()
        np.testing.assert_array_equal(
            self.plotter.axes.get_children()[1]
            .get_paths()[0]
            .to_polygons()[0][1:11, 1],
            self.material.n_data.lower_bounds,
        )
        np.testing.assert_array_equal(
            self.plotter.axes.get_children()[1]
            .get_paths()[0]
            .to_polygons()[0][12:, 1],
            self.material.n_data.upper_bounds[::-1],
        )

    def test_plot_with_values_k_plots_k(self):
        self.plotter.dataset = self.material
        self.plotter.parameters["values"] = "k"
        self.plotter.plot()
        np.testing.assert_array_equal(
            self.plotter.axes.get_lines()[0].get_ydata(),
            self.material.k_data.data,
        )

    def test_plot_with_values_k_plots_k_uncertainties(self):
        self.plotter.dataset = self.material
        self.plotter.parameters["values"] = "k"
        self.plotter.plot()
        np.testing.assert_array_equal(
            self.plotter.axes.get_children()[1]
            .get_paths()[0]
            .to_polygons()[0][1:11, 1],
            self.material.k_data.lower_bounds,
        )
        np.testing.assert_array_equal(
            self.plotter.axes.get_children()[1]
            .get_paths()[0]
            .to_polygons()[0][12:, 1],
            self.material.k_data.upper_bounds[::-1],
        )

    def test_plot_sets_alpha_value_for_uncertainties(self):
        self.plotter.dataset = self.material
        self.plotter.parameters["values"] = "k"
        self.plotter.plot()
        self.assertTrue(self.plotter.axes.get_children()[1].get_alpha())
        self.assertLessEqual(
            self.plotter.axes.get_children()[1].get_alpha(),
            0.3,
        )


class TestTwinUncertaintiesPlotter(unittest.TestCase):
    def setUp(self):
        self.plotter = plotting.TwinUncertaintiesPlotter()
        self.material = material.Material()
        self.material.n_data.data = np.linspace(0.98, 0.99, 10)
        self.material.n_data.lower_bounds = (
            self.material.n_data.data
            - np.random.normal(0.005, 0.002, size=10)
        )
        self.material.n_data.upper_bounds = (
            self.material.n_data.data
            + np.random.normal(0.005, 0.002, size=10)
        )
        self.material.n_data.axes[0].values = np.linspace(10, 12, 10)
        self.material.n_data.axes[0].symbol = r"\lambda"
        self.material.n_data.axes[0].quantity = "wavelength"
        self.material.n_data.axes[0].unit = "nm"
        self.material.k_data.data = np.linspace(0.02, 0.01, 10)
        self.material.k_data.lower_bounds = (
            self.material.k_data.data - np.random.normal(0.01, 0.002, size=10)
        )
        self.material.k_data.upper_bounds = (
            self.material.k_data.data
            + np.random.normal(0.005, 0.002, size=10)
        )
        self.material.k_data.axes[0].values = np.linspace(10, 12, 10)
        self.material.k_data.axes[0].symbol = r"\lambda"
        self.material.k_data.axes[0].quantity = "wavelength"
        self.material.k_data.axes[0].unit = "nm"

    def tearDown(self):
        plt.close()

    def test_instantiate_class(self):
        pass

    def test_has_additional_axes_attributes(self):
        attributes = [
            "ax2",
            "axes2",
        ]
        for attribute in attributes:
            self.assertTrue(hasattr(self.plotter, attribute))

    def test_axes2_is_identical_with_ax2(self):
        self.plotter.axes = object()
        self.assertIs(self.plotter.axes2, self.plotter.ax2)

    def test_plot_plots_n(self):
        self.plotter.dataset = self.material
        self.plotter.plot()
        np.testing.assert_array_equal(
            self.plotter.axes.get_lines()[0].get_ydata(),
            self.material.n_data.data,
        )

    def test_plot_sets_axes2_to_matplotlib_axes(self):
        self.plotter.dataset = self.material
        self.plotter.plot()
        self.assertIsInstance(self.plotter.axes2, matplotlib.axes.Axes)

    def test_plot_plots_k(self):
        self.plotter.dataset = self.material
        self.plotter.plot()
        np.testing.assert_array_equal(
            self.plotter.axes2.get_lines()[0].get_ydata(),
            self.material.k_data.data,
        )

    def test_plot_plots_n_uncertainties(self):
        self.plotter.dataset = self.material
        self.plotter.plot()
        np.testing.assert_array_equal(
            self.plotter.axes.get_children()[1]
            .get_paths()[0]
            .to_polygons()[0][1:11, 1],
            self.material.n_data.lower_bounds,
        )
        np.testing.assert_array_equal(
            self.plotter.axes.get_children()[1]
            .get_paths()[0]
            .to_polygons()[0][12:, 1],
            self.material.n_data.upper_bounds[::-1],
        )

    def test_plot_plots_k_uncertainties(self):
        self.plotter.dataset = self.material
        self.plotter.plot()
        np.testing.assert_array_equal(
            self.plotter.axes2.get_children()[1]
            .get_paths()[0]
            .to_polygons()[0][1:11, 1],
            self.material.k_data.lower_bounds,
        )
        np.testing.assert_array_equal(
            self.plotter.axes2.get_children()[1]
            .get_paths()[0]
            .to_polygons()[0][12:, 1],
            self.material.k_data.upper_bounds[::-1],
        )

    def test_plot_sets_color_for_n_uncertainties(self):
        prop_cycle = plt.rcParams["axes.prop_cycle"]
        colors = prop_cycle.by_key()["color"]
        self.plotter.dataset = self.material
        self.plotter.plot()
        np.testing.assert_allclose(
            self.plotter.axes.get_children()[1].get_facecolor()[0][0:3],
            matplotlib.colors.to_rgb(colors[0]),
        )

    def test_plot_sets_color_for_k_values(self):
        prop_cycle = plt.rcParams["axes.prop_cycle"]
        colors = prop_cycle.by_key()["color"]
        self.plotter.dataset = self.material
        self.plotter.plot()
        np.testing.assert_allclose(
            self.plotter.axes2.get_children()[1].get_facecolor()[0][0:3],
            matplotlib.colors.to_rgb(colors[1]),
        )
