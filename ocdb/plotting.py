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

  Plot either *n* or *k* together with its uncertainties as shaded area.

  A subclass of :class:`SinglePlotter`.

* :class:`TwinUncertaintiesPlotter`

  Plot *n* and *k* together in one axes, with different scaling of the
  left and right *y* axis, and both with their respective uncertainties as
  shaded areas.

  A subclass of :class:`TwinPlotter`.


For developers
==============

How does plotting actually work? The user interface for plotting values of
:obj:`ocdb.material.Material` objects is the
:meth:`ocdb.material.Material.plot` method. For all the magic contained
therein to work, the :obj:`ocdb.material.Material` object needs to contain an
instance of :class:`PlotterFactory` (rather than
:class:`ocdb.material.AbstractPlotterFactory`) in its
:attr:`ocdb.material.Material.plotter_factory` attribute. This
:obj:`PlotterFactory` object will take care of creating the correct
plotter object based on the criteria provided when calling
:meth:`ocdb.material.Material.plot`.


Module documentation
====================

"""

try:
    # noinspection PyUnresolvedReferences
    import matplotlib.pyplot as plt
except ImportError:
    pass

from ocdb import material


class PlotterFactory(material.AbstractPlotterFactory):
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

    In actual :obj:`ocdb.material.Material` objects containing real data,
    the :attr:`ocdb.material.Material.plotter_factory` will be set to an
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
    as they will usually just call the :meth:`ocdb.material.Material.plot`
    method that will take care of the rest.

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

            Currently, the following keys are understood:

            values : :class:`str`
                Values to plot: *n* or *k* or both.

                Allowed values are: ``n``, ``k``, ``both``

            uncertainties : :class:`bool`
                Whether to plot uncertainties.

        Returns
        -------
        plotter : :class:`BasePlotter`
            Plotter that best fits the criteria provided by the parameters.

        """
        plotter = BasePlotter()
        if "values" in kwargs:
            if kwargs["values"] in ("n", "k"):
                if (
                    "uncertainties" in kwargs
                    and kwargs["uncertainties"]
                    and self.material.has_uncertainties()
                ):
                    plotter = SingleUncertaintiesPlotter()
                else:
                    plotter = SinglePlotter()
                plotter.parameters["values"] = kwargs["values"]
            elif kwargs["values"] == "both":
                if (
                    "uncertainties" in kwargs
                    and kwargs["uncertainties"]
                    and self.material.has_uncertainties()
                ):
                    plotter = TwinUncertaintiesPlotter()
                else:
                    plotter = TwinPlotter()
        else:
            if (
                "uncertainties" in kwargs
                and kwargs["uncertainties"]
                and self.material.has_uncertainties()
            ):
                plotter = SingleUncertaintiesPlotter()
            else:
                plotter = SinglePlotter()
        return plotter


class BasePlotter(material.AbstractPlotter):
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
    :class:`ocdb.material.AbstractPlotterFactory`.

    Attributes
    ----------
    dataset : :class:`Material`
        Source of data to plot.

    figure : :class:`matplotlib.figure.Figure`
        Matplotlib figure containing the actual plot

        For convenience, the shorthand :attr:`fig` does also work.

    axes : :class:`matplotlib.axes.Axes`
        Matplotlib axes containing the actual plot

        For convenience, the shorthand :attr:`ax` does also work.

    parameters : :class:`dict`
        Parameters relevant for the plot.

        Which parameters are actually understood by the respective subclass
        may be different from case to case. See the documentation of the
        plotter class used.


    Examples
    --------
    Actual plotting will always be performed using descendants of this
    :class:`BasePlotter` class, and the normal user of the ocdb package
    will not instantiate plotter objects directly, but rather call
    :meth:`ocdb.material.Material.plot`. Nevertheless, you can do the
    whole work manually:

    .. code-block::

        material = ocdb.material.Material()
        plotter = BasePlotter()
        plotter.dataset = material
        plotter.plot()

    For the typical use case, see the documentation of the
    :meth:`ocdb.material.Material.plot` method.

    """

    def __init__(self):
        super().__init__()
        self.figure = None
        self.axes = None
        self.parameters = {}

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

        The actual plotting is performed in the non-public method
        :meth:`_create_plot`, such as not to interfere with the
        necessary settings done by the base class.
        """
        self.figure, self.axes = plt.subplots()
        self._create_plot()

    def _create_plot(self):
        pass


class SinglePlotter(BasePlotter):
    """
    Graphical display of either *n* or *k* values.

    In its simplest form, a line plotter plotting either *n* or *k* values vs.
    wavelength. Which of the two to plot is a matter of the parameter
    ``values``. For details, see below.

    If you are interested in seeing both, *n* and *k* values in one plot,
    have a look at :class:`TwinPlotter`. If you instead want to plot either
    *n* or *k*, but with uncertainties, :class:`SingleUncertaintiesPlotter`
    would be the plotter of your choosing.


    Attributes
    ----------
    parameters : :class:`dict`
        Parameters relevant for the plot.

        The following keys are currently interpreted:

        values : :class:`str`
            Values to plot: either *n* or *k*.

            Possible values are ``n`` and ``k``.

            The default value is ``n``.

    Examples
    --------
    The normal user of the ocdb package will not instantiate plotter objects
    directly, but rather call :meth:`ocdb.material.Material.plot`.
    Nevertheless, you can do the whole work manually:

    .. code-block::

        material = ocdb.material.Material()
        plotter = SinglePlotter()
        plotter.dataset = material
        plotter.parameters["values"] = "n"
        plotter.plot()

    This would plot the *n* values of the given material. Generally,
    you would achieve the same much easier by using directly the
    :meth:`ocdb.material.Material.plot` method:

    .. code-block::

        ocdb.elements.Co.plot()

    Note that the default is to always plot *n*. If you want to plot *k*
    instead, you need to be explicit about it:

    .. code-block::

        ocdb.elements.Co.plot(values="k")

    For the typical use case, see the documentation of the
    :meth:`ocdb.material.Material.plot` method.

    """

    def __init__(self):
        super().__init__()
        self.parameters["values"] = "n"

    def _create_plot(self):
        if self.parameters["values"] == "k":
            data = self.dataset.k_data
        else:
            data = self.dataset.n_data
        self.axes.plot(data.axes[0].values, data.data)
        self.axes.set_xlabel(data.axes[0].get_label())
        self.axes.set_ylabel(data.axes[1].get_label())


class TwinPlotter(BasePlotter):
    """
    Graphical display of both, *n* and *k* values.

    In its simplest form, a line plotter plotting both, *n* or *k* values vs.
    wavelength.

    Due to the values of *n* and *k* being on an entirely different scale,
    two independent *y* axes are used and labelled appropriately. The *x*
    axis, however, is obviously shared by both and typically the wavelength
    in nm.

    To optically assign the values to the respective axes, the plotted values
    as well as the corresponding *y* axis appear with the same colour. The
    colours used are the first and second colour of the currently set colour
    cycle. See the Matplotlib documentation for further details.

    If you are interested in seeing either *n* or *k* values in one plot,
    have a look at :class:`SinglePlotter`. If you instead want to plot *n* and
    *k* together with their respective uncertainties,
    :class:`TwinUncertaintiesPlotter` would be the plotter of your choosing.


    Attributes
    ----------
    axes2 : :class:`matplotlib.axes.Axes`
        Matplotlib axes containing the actual plot for *k* values

        For convenience, the shorthand :attr:`ax2` does also work.


    Examples
    --------
    The normal user of the ocdb package will not instantiate plotter objects
    directly, but rather call :meth:`ocdb.material.Material.plot`.
    Nevertheless, you can do the whole work manually:

    .. code-block::

        material = ocdb.material.Material()
        plotter = TwinPlotter()
        plotter.dataset = material
        plotter.plot()

    This would plot both, *n* and *k* values of the given material. Generally,
    you would achieve the same much easier by using directly the
    :meth:`ocdb.material.Material.plot` method:

    .. code-block::

        ocdb.elements.Co.plot(values="both")

    For the typical use case, see the documentation of the
    :meth:`ocdb.material.Material.plot` method.

    """

    def __init__(self):
        super().__init__()
        self.axes2 = None

    @property
    def ax2(self):
        """
        Convenience shorthand for the :attr:`axes2` attribute.

        Returns
        -------
        figure : :class:`matplotlib.axes.Axes`
            Matplotlib axes containing the actual plot for *k* values

        """
        return self.axes2

    def _create_plot(self):
        prop_cycle = plt.rcParams["axes.prop_cycle"]
        colors = prop_cycle.by_key()["color"]

        self.axes.plot(
            self.dataset.n_data.axes[0].values,
            self.dataset.n_data.data,
            color=colors[0],
        )
        self.axes.set_xlabel(self.dataset.n_data.axes[0].get_label())
        self.axes.set_ylabel(
            self.dataset.n_data.axes[1].get_label(),
            color=colors[0],
        )
        self.axes.tick_params(axis="y", labelcolor=colors[0])

        self.axes2 = self.axes.twinx()
        self.axes2.plot(
            self.dataset.k_data.axes[0].values,
            self.dataset.k_data.data,
            color=colors[1],
        )
        self.axes2.set_ylabel(
            self.dataset.k_data.axes[1].get_label(),
            color=colors[1],
        )
        self.axes2.tick_params(axis="y", labelcolor=colors[1])


class SingleUncertaintiesPlotter(SinglePlotter):
    """
    Graphical display of either *n* or *k* values together with uncertainties.

    In its simplest form, a line plotter plotting either *n* or *k* values vs.
    wavelength, but together with their uncertainties as shaded area. Which of
    the two to plot is a matter of the parameter ``values``. For details,
    see below.

    If you are interested in seeing both, *n* and *k* values in one plot,
    have a look at :class:`TwinUncertaintiesPlotter`. If you instead want to
    plot either *n* or *k*, but without uncertainties, :class:`SinglePlotter`
    would be the plotter of your choosing.


    Attributes
    ----------
    parameters : :class:`dict`
        Parameters relevant for the plot.

        The following keys are currently interpreted:

        values : :class:`str`
            Values to plot: either *n* or *k*.

            Possible values are ``n`` and ``k``.

            The default value is ``n``.

    Examples
    --------
    The normal user of the ocdb package will not instantiate plotter objects
    directly, but rather call :meth:`ocdb.material.Material.plot`.
    Nevertheless, you can do the whole work manually:

    .. code-block::

        material = ocdb.material.Material()
        plotter = SingleUncertaintiesPlotter()
        plotter.dataset = material
        plotter.parameters["values"] = "n"
        plotter.plot()

    This would plot the *n* values of the given material together with the
    uncertainties. Generally, you would achieve the same much easier by
    using directly the :meth:`ocdb.material.Material.plot` method:

    .. code-block::

        ocdb.elements.Co.plot(uncertainties=True)

    Note that the default is to always plot *n*. If you want to plot *k*
    instead, together with their uncertainties, you need to be explicit
    about it:

    .. code-block::

        ocdb.elements.Co.plot(values="k", uncertainties=True)

    For the typical use case, see the documentation of the
    :meth:`ocdb.material.Material.plot` method.

    """

    def _create_plot(self):
        super()._create_plot()
        if self.parameters["values"] == "k":
            data = self.dataset.k_data
        else:
            data = self.dataset.n_data
        self.axes.fill_between(
            data.axes[0].values,
            data.lower_bounds,
            data.upper_bounds,
            alpha=0.3,
        )


class TwinUncertaintiesPlotter(TwinPlotter):
    """
    Graphical display of both, *n* and *k* values with uncertainties.

    In its simplest form, a line plotter plotting both, *n* or *k* values vs.
    wavelength, but together with their uncertainties as shaded areas.

    Due to the values of *n* and *k* being on an entirely different scale,
    two independent *y* axes are used and labelled appropriately. The *x*
    axis, however, is obviously shared by both and typically the wavelength
    in nm.

    To optically assign the values to the respective axes, the plotted values
    as well as the corresponding *y* axis appear with the same colour. The
    colours used are the first and second colour of the currently set colour
    cycle. See the Matplotlib documentation for further details.

    If you are interested in seeing either *n* or *k* values in one plot,
    have a look at :class:`SingleUncertaintiesPlotter`. If you instead want to
    plot *n* and *k*, but without their respective uncertainties,
    :class:`TwinPlotter` would be the plotter of your choosing.


    Attributes
    ----------
    axes2 : :class:`matplotlib.axes.Axes`
        Matplotlib axes containing the actual plot for *k* values

        For convenience, the shorthand :attr:`ax2` does also work.


    Examples
    --------
    The normal user of the ocdb package will not instantiate plotter objects
    directly, but rather call :meth:`ocdb.material.Material.plot`.
    Nevertheless, you can do the whole work manually:

    .. code-block::

        material = ocdb.material.Material()
        plotter = TwinUncertaintiesPlotter()
        plotter.dataset = material
        plotter.plot()

    This would plot both, *n* and *k* values of the given material together
    with their uncertainties. Generally, you would achieve the same much
    easier by using directly the :meth:`ocdb.material.Material.plot` method:

    .. code-block::

        ocdb.elements.Co.plot(values="both", uncertainties=True)

    For the typical use case, see the documentation of the
    :meth:`ocdb.material.Material.plot` method.

    """

    def _create_plot(self):
        super()._create_plot()
        prop_cycle = plt.rcParams["axes.prop_cycle"]
        colors = prop_cycle.by_key()["color"]
        self.axes.fill_between(
            self.dataset.n_data.axes[0].values,
            self.dataset.n_data.lower_bounds,
            self.dataset.n_data.upper_bounds,
            alpha=0.3,
            facecolor=colors[0],
        )
        self.axes2.fill_between(
            self.dataset.k_data.axes[0].values,
            self.dataset.k_data.lower_bounds,
            self.dataset.k_data.upper_bounds,
            alpha=0.3,
            facecolor=colors[1],
        )
