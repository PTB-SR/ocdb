import matplotlib.figure
import matplotlib.axes
import unittest

from ocdb import database, plotting


class TestPlotterFactory(unittest.TestCase):
    def setUp(self):
        self.factory = plotting.PlotterFactory()

    def test_instantiate_class(self):
        pass

    def test_is_abstract_plotter_factory(self):
        self.assertIsInstance(self.factory, database.AbstractPlotterFactory)

    def test_get_plotter_returns_plotter(self):
        self.assertIsInstance(
            self.factory.get_plotter(), plotting.BasePlotter
        )


class TestBasePlotter(unittest.TestCase):
    def setUp(self):
        self.plotter = plotting.BasePlotter()

    def test_instantiate_class(self):
        pass

    def test_is_abstract_plotter(self):
        self.assertIsInstance(self.plotter, database.AbstractPlotter)

    def test_has_attributes(self):
        attributes = [
            "fig",
            "figure",
            "ax",
            "axes",
            "dataset",
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
