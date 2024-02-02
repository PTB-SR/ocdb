"""
Graphical representations of the data contained in the ocdb package.

Although not the primary concern of the ocdb package, getting an overview
of the data contained in the database is always a good idea. Hence, for
convenience, graphical representations of the optical constants for a
material are quite helpful.


.. important::

    In order to access the plotting capabilities, you do need to have
    Matplotlib installed, although it is not a hard requirement of
    the ocdb package, to keep things clean and simple. The convenient
    way to install the necessary requirements would be to use pip with
    the optional requirements, such as:

     .. code-block:: bash

         pip install ocdb[presentation]

    This will install all necessary dependencies for you. Note that
    this step is only necessary if you ever want to access the
    plotting capabilities. Using the ocdb package without Matplotlib
    is entirely possible.


Plotter types
=============

The following list is for the being just a documentation of plotter types
that seem sensible:

* :class:`SinglePlotter`

    Plot either *n* or *k*. Basically a line plot.

* :class:`TwinPlotter`

    Plot *n* and *k* together in one axes, with different scaling of the
    left and right *y* axis due to the disjunctive values for *n* and *k*,
    one close to 1 and the other close to 0.

* :class:`SingleUncertaintiesPlotter`

    Plot either *n* or *k* together with its uncertainties.

    Most probably a subclass of :class:`SinglePlotter`.

* :class:`TwinUncertaintiesPlotter`

    Plot *n* and *k* together in one axes, with different scaling of the
    left and right *y* axis, and both with their respective uncertainties.

    Most probably a subclass of :class:`TwinPlotter`.


For developers
==============

How does plotting actually work? The user interface for plotting values of
:obj:`ocdb.database.Material` objects is the
:meth:`ocdb.database.Material.plot` method. For all the magic contained
therein to work, the :obj:`ocdb.database.Material` object needs to contain an
instance of :class:`PlotterFactory` (rather than
:class:`ocdb.database.AbstractPlotterFactory`) in its
:attr:`ocdb.database.Material.plotter_factory` attribute. This
:obj:`PlotterFactory` object will take care of creating the correct
plotter object based on the criteria provided when calling
:meth:`ocdb.database.Material.plot`.

.. todo::

    How to deal with the dependency on Matplotlib, though? If we
    instantiate an object of :class:`PlotterFactory` upon creating the
    actual :obj:`odcb.database.Material` objects, we would have to have
    Matplotlib at hand...

    One idea would be to check for the availability of the matplotlib package
    when creating all the :obj:`odcb.database.Material` objects and only
    in case it is available to load the plotting module and to replace the
    :obj:`ocdb.database.AbstractPlotterFactory` object with a
    :obj:`PlotterFactory` object. If Matplotlib is not available, probably
    a warning should be issued that plotting is not possible.


Module documentation
====================

"""

import matplotlib.pyplot as plt

from ocdb import database


class PlotterFactory(database.AbstractPlotterFactory):
    """
    Factory for plotter.

    Different types of data and different situations require different
    types of plotters. A simple example: Plotting either *n* or *k* is
    usually a very simple line plot. Plotting both, *n* and *k* in one
    axes requires two different axes left and right due to the
    dramatically different ranges of the values (for *n* close to 1,
    for *k* close to zero). Plotting values together with their
    uncertainties is yet a different matter.

    Getting the appropriate plotter for the task at hand is the
    responsibility of this plotter factory.

    In actual :obj:`database.Material` objects containing real data,
    the :attr:`database.Material.plotter_factory` will be set to an
    instance of this class.

    Examples
    --------
    A factory usually has exactly one duty: Given a list of criteria,
    return the object that fits these criteria. Hence, getting a plotter
    from the factory is as simple as:

    .. code-block::

        plotter_factory = PlotterFactory()
        plotter = plotter_factory.get_plotter()

    The criteria for getting the *correct* plotter will be some key-value
    pairs, hence the :meth:`get_plotter` method supports arbitrary
    key-value pair (``**kwargs`` in Python speak):

    .. code-block::

        plotter_factory = PlotterFactory()
        plotter = plotter_factory.get_plotter(uncertainties="True")

    This may get you a plotter capable of plotting not only the values,
    but the uncertainties as well. Details of the available plotters can
    be found in the :mod:`plotting` documentation.

    The actual users of the ocdb package will not see much of the factory,
    as they will usually just call the :meth:`database.Materials.plot` method
    that will take care of the rest.

    """

    def get_plotter(self, **kwargs):
        """
        Return plotter object given the criteria in the keyword arguments.

        Parameters
        ----------
        kwargs
            All parameters relevant to decide upon the correct plotter.

            A list of key--value pairs, either as :class:`dict` or
            separate, *i.e.* the Python ``**kwargs`` argument.

        Returns
        -------
        plotter : :class:`BasePlotter`
            Plotter that best fits the criteria provided by the parameters.

        """
        return BasePlotter()


class BasePlotter(database.AbstractPlotter):
    """
    Base class for all concrete plotters of the ocdb package.

    A concrete plot depends strongly on what shall actually be
    plotted, be it only *n* or only *k*, or each of them with their
    respective uncertainties, or *n* and *k* together in one plot,
    with and without their uncertainties. Nevertheless, all these types of
    plots share a common base, and this is implemented in this class.

    Real plots will always be performed by a descendant of this class.
    Which plotter to actually use is in the realm of the
    :class:`PlotterFactory` that itself descends from the
    :class:`ocdb.database.AbstractPlotterFactory`.

    Attributes
    ----------
    figure : :class:`matplotlib.figure.Figure`
        Matplotlib figure containing the actual plot

        For convenience, the shorthand :attr:`fig` does also work.

    axes : :class:`matplotlib.axes.Axes`
        Matplotlib axes containing the actual plot

        For convenience, the shorthand :attr:`ax` does also work.


    Examples
    --------
    Actual plotting will always be performed using descendants of this
    :class:`BasePlotter` class, and the normal user of the ocdb package
    will not instantiate plotter objects directly, but rather call
    :meth:`ocdb.database.Material.plot`. Nevertheless, you can do the
    whole work manually:

    .. code-block::

        material = ocdb.database.Material()
        plotter = BasePlotter()
        plotter.dataset = material
        plotter.plot()

    For the typical use case, see the documentaiton of the
    :meth:`ocdb.database.Material.plot` method.

    """

    def __init__(self):
        super().__init__()
        self.figure = None
        self.axes = None

    @property
    def fig(self):
        """
        Convenience shorthand for the :attr:`figure` attribute.

        Returns
        -------
        figure : :class:`matplotlib.figure.Figure`
            Matplotlib figure containing the actual plot

        """
        return self.figure

    @property
    def ax(self):  # pylint: disable=invalid-name
        """
        Convenience shorthand for the :attr:`axes` attribute.

        Returns
        -------
        figure : :class:`matplotlib.axes.Axes`
            Matplotlib axes containing the actual plot

        """
        return self.axes

    def plot(self):
        """
        Perform the actual plotting.

        First of all, the :attr:`figure` and :attr:`axes` properties of the
        plotter are set.
        """
        self.figure, self.axes = plt.subplots()
