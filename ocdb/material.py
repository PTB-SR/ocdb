"""
Core entities of the ocdb package forming a database of optical constants.

From a software architecture perspective, the classes in the material
module of the ocdb package are part of the core domain. That does not
imply by any means that users of the ocdb package will instantiate these
classes by themselves. Nevertheless, they will directly interact with
instances of the core classes.


Core entities
=============

Two abstractions form the core entities of the ocdb package:

* :class:`Material`

    Optical constants and relevant metadata for a single material.

* :class:`Collection`

    Collection of materials whose data are part of the OCDB.


Module documentation
====================

"""

import numpy as np


class Material:
    """
    Optical constants and relevant metadata for a single material.

    This is a base class for materials of all kinds, be it elements or
    compositions, and it is at the core of the ocdb package and architecture.
    Key aspects are data *and* metadata in a single unit, the latter including
    full bibliographic records for proper citation.


    Attributes
    ----------
    name : :class:`str`
        The human-readable name of the material.

        Usually, you want to use English common names.

    symbol : :class:`str`
        The symbol typically used to refer to the material.

        In case of elements, the element symbol.

        In case of compositions, typically the molecular formula.

        This is used, *i.a.*, to refer to the material from within the ocdb
        package and the :class:`Collection` class. Hence, the symbol needs to
        be *unique* within the ocdb package.

    references : :class:`list`
        Bibliographic records for the data of the optical constants.

        One central idea of the ocdb package is to provide not only data, but
        the relevant metadata as well. Hence, the reference of the dataset, be
        it an actual dataset or a publication describing the underlying
        measurements, is fairly essential.

        Each entry of the list is a :obj:`bibrecord.record.Record` object.

    metadata : :class:`Metadata`
        Relevant metadata for the data of the optical constants.

        Data are only as good as their accompanying metadata. Reproducibility
        as well as sensible use of the data requires access to all relevant
        metadata.

    plotter_factory : :class:`AbstractPlotterFactory`
        Factory for creating plotter objects on request.

        Concrete Plotter are descendants of the :class:`AbstractPlotter`
        class and reside in the :mod:`plotting` module. The :meth:`plot`
        method of this class first calls the plotter factory to obtain the
        appropriate plotter, and afterwards calls the
        :meth:`AbstractPlotter.plot` method on this plotter object.

        In case you wonder: in all practical cases, the actual plotter is a
        descendant of the :class:`AbstractPlotter` class. See the
        :mod:`plotting` module for details.)


    Examples
    --------
    Although typical users of the ocdb package will not directly instantiate
    objects of this class, they will usually operate on these objects that are
    part of a :class:`Collection`. In the following examples, we will always
    use the data for the element Cobalt (symbol: Co) as an example.

    Getting the object from a :class:`Collection`, in case you don't want to
    operate on the collection (what would be preferable):

    .. code-block::

        Co = ocdb.elements.Co

    Getting values for *n*, *k*, or the complex index of refraction:

    .. code-block::

        wavelength, n = ocdb.elements.Co.n()
        wavelength, k = ocdb.elements.Co.k()
        wavelength, nk = ocdb.elements.Co.index_of_refraction()

    For further details, have a look at the documentation of the respective
    methods, *i.e.* :meth:`n`, :meth:`k`, and :meth:`index_of_refraction`.

    A key aspect of the ocdb package is available metadata and citable data.
    Hence the :attr:`reference` and :attr:`metadata` attributes.

    Suppose you are interested in a human-readable representation of the
    reference:

    .. code-block::

        ocdb.elements.Co.reference.to_string()

    This returns the reference as you would typically find it in the reference
    section of a publication.

    If you are interested in the BibTeX record for further use in own
    publications, try:

    .. code-block::

        ocdb.elements.Co.reference.to_bib()

    This will return a multiline string with the BibTeX entry. To actually see
    the BibTeX entry, use:

    .. code-block::

        print(ocdb.elements.Co.reference.to_bib())

    For details regarding the metadata, have a look at the documentation of the
    :class:`Metadata` class.

    """

    def __init__(self):
        self.name = ""
        self.symbol = ""
        self.references = []
        self.metadata = Metadata()

        self.plotter_factory = AbstractPlotterFactory()

        self.n_data = Data()
        self.n_data.axes[1].quantity = "dispersion coefficient"
        self.n_data.axes[1].symbol = "n"
        self.k_data = Data()
        self.k_data.axes[1].quantity = "extinction coefficient"
        self.k_data.axes[1].symbol = "k"

    def n(self, uncertainties=False):  # pylint: disable=invalid-name
        """
        Return real part *n* of the index of refraction.

        Parameters
        ----------
        uncertainties : :class:`bool`
            Whether to return uncertainties as separate arrays in output

        Returns
        -------
        n : :class:`tuple`
            wavelength and *n* as :class:`numpy.ndarray`

            In case of uncertainties set to True, two additional arrays with
            lower and upper bound.

        """
        wavelengths = self.n_data.axes[0].values
        if uncertainties:
            output = (
                wavelengths,
                self.n_data.data,
                self.n_data.lower_bounds,
                self.n_data.upper_bounds,
            )
        else:
            output = (wavelengths, self.n_data.data)
        return output

    def k(self, uncertainties=False):
        """
        Return imaginary part *k* of the index of refraction.

        Parameters
        ----------
        uncertainties : :class:`bool`
            Whether to return uncertainties as separate arrays in output

        Returns
        -------
        k : :class:`tuple`
            wavelength and *k* as :class:`numpy.ndarray`

        """
        wavelengths = self.k_data.axes[0].values
        if uncertainties:
            output = (
                wavelengths,
                self.k_data.data,
                self.k_data.lower_bounds,
                self.k_data.upper_bounds,
            )
        else:
            output = (wavelengths, self.k_data.data)
        return output

    def index_of_refraction(self, uncertainties=False):
        r"""
        Return complex index of refraction

        Parameters
        ----------
        uncertainties : :class:`bool`
            Whether to return uncertainties as separate arrays in output

        Returns
        -------
        index_of_refraction : :class:`tuple`
            wavelength and *n* - i\ *k* as :class:`numpy.ndarray`

        """
        n_k = self.n_data.data - 1j * self.k_data.data
        wavelengths = self.k_data.axes[0].values
        if uncertainties:
            output = (
                wavelengths,
                n_k,
                self.n_data.lower_bounds,
                self.n_data.upper_bounds,
                self.k_data.lower_bounds,
                self.k_data.upper_bounds,
            )
        else:
            output = wavelengths, n_k

        return output

    def plot(self):
        """
        Plot data.

        Although not the primary concern of the ocdb package, getting an
        overview of the data contained in the database is always a good
        idea. Hence, for convenience, graphical representations of the
        optical constants for a material are quite helpful.

        Examples
        --------
        Plotting is rather straight-forward. Assuming an object of class
        :class:`Material` and named ``stuff``, plotting the optical data
        of "stuff" is as simple as:

        .. code-block::

            stuff.plot()

        All the magic happens inside the plot method. For those interested
        in more details: a plotter factory stored in
        :attr:`plotter_factory` is asked for the appropriate plotter
        object, and afterwards first the current :obj:`Material` object
        whose :meth:`plot` method is called is set to the
        :attr:`AbstractPlotter.dataset` property and after that the
        :meth:`AbstractPlotter.plot` method of this plotter is called. As
        you may be interested in the plotter object itself, it is returned
        upon request.

        Returns
        -------
        plotter : :class:`AbstractPlotter`
            Plotter used for plotting the data.

        """
        plotter = self.plotter_factory.get_plotter()
        plotter.dataset = self
        plotter.plot()
        return plotter


class Data:
    """
    Unit containing both, numeric data and corresponding axes.

    Attributes
    ----------
    data : :class:`numpy.ndarray`
        Actual numerical data.

    axes : :class:`list`
        List of :obj:`Axis` objects corresponding to the data.

        Note that there are always two axes, one with the independent values,
        the other without values, but with the relevant metadata to create
        appropriate axis labels, *i.e.* at least measure/symbol.

    lower_bounds : :class:`numpy.ndarray`
        Lower bounds for uncertainty of the values stored in :attr:`data`.

        Could be an empty array. Use :meth:`has_uncertainties` for a convenient
        check.

    upper_bounds : :class:`numpy.ndarray`
        Upper bounds for uncertainty of the values stored in :attr:`data`.

        Could be an empty array. Use :meth:`has_uncertainties` for a convenient
        check.

    """

    def __init__(self):
        self.data = np.ndarray(0)
        self.axes = [Axis(), Axis()]
        self.lower_bounds = np.ndarray(0)
        self.upper_bounds = np.ndarray(0)

    def has_uncertainties(self):
        """
        Indicate whether uncertainties are present.

        Only in case of both, lower *and* upper boundary being present will
        the answer be "True".

        Returns
        -------
        answer : :class:`bool`
            Whether data contain uncertainties

        """
        return self.lower_bounds.size and self.upper_bounds.size


class Axis:
    """
    Data and metadata for an axis.

    Data (stored in :class:`Data`) will always have at least two axes (except
    single points). One axis contains both, values (the independent variable)
    and metadata for the corresponding label, the second axis will only contain
    the metadata.


    Attributes
    ----------
    values : :class:`numpy.ndarray`
        Values of the independent variable data are available for

    quantity : :class:`str`
        Textual description of the quantity of the axis

        This will usually be a name. For the (mathematical) symbol, use
        :attr:`symbol` (and see there).

        Usually used as first part of an automatically generated axis label.
        For automatically generated axis labels, see :meth:`get_label`.

    symbol : :class:`str`
        Symbol for the quantity of the numerical data.

        Usually used as first part of an automatically generated axis label.
        For automatically generated axis labels, see :meth:`get_label`.

        Symbols are treated as mathematical variables, hence you can use at
        least a standard subset of LaTeX math commands. If in doubt, havw a
        look at the corresponding section of the `Matplotlib documentation
        <https://matplotlib.org/stable/users/explain/text/mathtext.html>`_
        what subset of LaTeX markup is supported without having to use a
        full LaTeX engine. At the very least, Greek letters and sub- and
        superscript work as expected.

    unit : :class:`str`
        unit of the numerical data

        Usually used as second part of an automatically generated axis label,
        separated with a slash from the quantity or symbol.
        For automatically generated axis labels, see :meth:`get_label`.

    """

    def __init__(self):
        self.values = np.ndarray(0)
        self.quantity = ""
        self.unit = ""
        self.symbol = ""

    def get_label(self):
        """
        Get axis label according to IUPAC conventions.

        .. note::

            There are three alternative ways of writing axis labels, one with
            using the quantity name and the unit, one with using the quantity
            symbol and the unit, and one using both, quantity name and symbol,
            usually separated by comma. Quantity and unit shall always be
            separated by a slash. Which way you prefer is a matter of personal
            taste and given context.


        Returns
        -------
        label : :class:`str`
            Axis label that can be used for a plot.

        """
        if self.symbol:
            measure = f"${self.symbol}$"
        else:
            measure = self.quantity
        if self.unit:
            label = f"{measure} / {self.unit}"
        else:
            label = measure
        return label


class Metadata:
    """
    Relevant metadata for the optical constants of a given material.

    Data are only as good as their accompanying metadata. Hence, metadata are a
    prerequisite for both, reproducibility and correct use of the data.

    This class provides a structure and hence access to the relevant metadata
    for optical constants of materials from the OCDB database. These metadata
    should be as machine-actionable as possible, allowing for automatic
    processing of information wherever sensible.


    Attributes
    ----------
    sample : :class:`Sample`
        Metadata regarding the sample used to obtain the optical constants.

    measurement : :class:`Measurement`
        Metadata regarding the actual measurement.

    comment : :class:`str`
        Any relevant information that does not (yet) fit into anywhere else.

        There is nearly always the need to store some information that
        just does not fit into any of the fields. However, use with care
        and expand the data structure if you realise that you repeatedly
        store the same (kind of) information in the comment.

    """

    def __init__(self):
        self.sample = Sample()
        self.measurement = Measurement()
        self.comment = ""


class Sample:
    """
    Relevant metadata of the sample measured to get its optical constants.

    Data are only as good as their accompanying metadata. Hence, metadata
    are a prerequisite for both, reproducibility and correct use of the data.

    This class provides a structure and hence access to the relevant metadata
    regarding the sample that was measured to obtain the optical constants
    of a given material. These metadata should be as machine-actionable as
    possible, allowing for automatic processing of information wherever
    sensible.


    Attributes
    ----------
    thickness : :class:`None`
        Thickness of the layer of the actual material of interest.

        The materials whose optical constants are contained in the OCDB have
        usually been measured on thin films in reflection, not as
        free-standing thin films in transmission. Therefore, the material
        of interest is a (thin) film supported by a substrate and in many
        cases a more complex stack of different layers.

        .. todo::
            Decide upon the type of this attribute.
            PhysicalConstant with at least value and unit?

    substrate : :class:`str`
        Name of the substrate supporting the actual material of interest.

        Note that the substrate is typically different from the (more
        complex) layer stack. For the latter, see the :attr:`layer_stack`
        attribute.

    layer_stack : :class:`str`
        Description of the (complex) layer stack of the sample.

        The materials whose optical constants are contained in the OCDB have
        been measured on thin films in reflection, not as free-standing thin
        films in transmission. Therefore, the material of interest is a
        (thin) film supported by a substrate and in many cases a more
        complex stack of different layers.

        A brief description of this layer stack, *e.g.* "C/Co/Ru@Si",
        should be provided here.

    morphology : :class:`str`
        Morphology of the sample.

    """

    def __init__(self):
        self.thickness = None
        self.substrate = ""
        self.layer_stack = ""
        self.morphology = ""


class Measurement:
    """
    Metadata regarding the actual measurement.

    The data contained in the optical constants database are usually
    recorded at a synchrotron and in reflection mode. Basic metadata
    describing the setup used and the measurement performed are stored in
    this class in a machine-actioable form.


    Attributes
    ----------
    type : :class:`str`
        Type of measurement.

        There are two types of measurements usually performed: reflection
        or transmission. Currently, all data contained in the OCDB are
        obtained using reflection-type measurements.

    facility : :class:`str`
        Name of the facility the measurement was carried out at.

    beamline : :class:`str`
        Name of the beamline the measurement was performed at.

    date : :class:`datetime.date`
        Date of the measurement.

    """

    def __init__(self):
        self.type = ""
        self.facility = ""
        self.beamline = ""
        self.date = None


class Collection:
    # noinspection PyUnresolvedReferences
    """
    Collection of materials whose data are part of the OCDB.

    While each material, be it an element or composition, will be accessed by
    means of an :obj:`Material` object, users of the ocdb package will typically
    operate on the properties of a collection that are :obj:`Material` objects.

    This allows for different collections, *e.g.* elements and compositions.
    Similarly, a general collection such as "materials" would be possible,
    containing all materials data are availabe for in the OCDB.


    Attributes
    ----------
    item : :class:`Material`
        Item of a collection

        All items added to a collection using the method :meth:`add_item` will
        appear as attribute of the object. As this is dynamic, however, no
        concrete attributes can be described here.


    .. todo::

        May a collection eventually have some more attributes controlling,
        *e.g.*, the type of interpolation used? May be sensible to
        implement/store on this level and passed down to the individual
        materials. Probably we need the information on the materials
        level, but from the users perspective, usually interacting with
        collections, additionally having the attribute here and pass it
        down may make some sense.


    Examples
    --------
    Given a collection with items, here termed ``collection``, we may be
    interested in just getting a list of all items, either by name or by symbol
    (or both):

    .. code-block::

        for item in collection:
            print(item.symbol, item.name)

    If you know the items of your collection, you can access them as attributes
    of the collection itself. To be exact, each item added to a collection using
    the :meth:`add_item` method gets added as a attribute to the collection with
    the symbol of the item being the name of the attribute.

    Suppose you know that Cobalt (with symbol Co) is part of the items of your
    collection. In this case, you can access it as a property of the collection:

    .. code-block::

        collection.Co

    In the same way, you can access all properties of this item. For details,
    have a look at the documentation of the underlying :class:`Material` class.

    """

    def __init__(self):
        self._items = {}

    def __iter__(self):
        """
        Iterate over the items of the collection.

        Returns
        -------
        item : :class:`Material`
            Material of the collection

        """
        for item in self._items.values():
            yield item

    def add_item(self, item):
        """
        Add an item to the collection.

        Parameters
        ----------
        item : :class:`Material`
            The item to be added to the collection.

            The item will be accessible as attribute of the collection, using
            the symbol of the material in :attr:`Material.symbol` as name for
            the attribute.

            Hence, symbols for materials need to be unique within the ocdb
            package.

        """
        setattr(self, item.symbol, item)


class AbstractPlotter:
    """
    Abstract base class for plotters.

    Although not the primary concern of the ocdb package, getting an overview
    of the data contained in the database is always a good idea. Hence, for
    convenience, graphical representations of the optical constants for a
    material are quite helpful.

    Plotting as such is provided in the :mod:`plotting` module, but the
    abstract plotter class resides here, according to the dependency
    inversion principle. To not have the hard dependency of the ocdb
    package from the Matplotlib stack (as this will require a lot of other
    packages to be present as well), no direct dependency on Matplotlib
    exists at this stage.

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

    Attributes
    ----------
    dataset : :class:`Material`
        Source of data to plot.

    """

    def __init__(self):
        self.dataset = None

    def plot(self):
        """Perform the actual plotting."""


class AbstractPlotterFactory:
    """
    Abstract factory for plotter.

    Different types of data and different situations require different
    types of plotters. A simple example: Plotting either *n* or *k* is
    usually a very simple line plot. Plotting both, *n* and *k* in one
    axes requires two different axes left and right due to the
    dramatically different ranges of the values (for *n* close to 1,
    for *k* close to zero). Plotting values together with their
    uncertainties is yet a different matter.

    In any case, all the material wants and needs to know is that it
    requires a plotter in order to get its data plotted. The abstract
    interface of the plotter itself is described in the
    :class:`AbstractPlotter` class, and the
    :class:`AbstractPlotterFactory` is the one place to ask for the
    correct plotter.

    Concrete instances of both, :class:`AbstractPlotter` and
    :class:`AbstractPlotterFactory` are implemented in the :mod:`plotting`
    module. Only if you ever import this module would you need to have a
    plotting framework (Matplotlib) installed.


    Examples
    --------
    A factory usually has exactly one duty: Given a list of criteria,
    return the object that fits these criteria. Hence, getting a plotter
    from the factory is as simple as:

    .. code-block::

        plotter_factory = AbstractPlotterFactory()
        plotter = plotter_factory.get_plotter()

    The criteria for getting the *correct* plotter will be some key-value
    pairs, hence the :meth:`get_plotter` method supports arbitrary
    key-value pair (``**kwargs`` in Python speak):

    .. code-block::

        plotter_factory = AbstractPlotterFactory()
        plotter = plotter_factory.get_plotter(uncertainties="True")

    This may get you a plotter capable of plotting not only the values,
    but the uncertainties as well. Details of the available plotters can
    be found in the :mod:`plotting` documentation.

    The actual users of the ocdb package will not see much of the factory,
    as they will usually just call the :meth:`Materials.plot` method that
    will take care of the rest.

    """

    # noinspection PyMethodMayBeStatic
    # pylint: disable=unused-argument
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
        plotter : :class:`AbstractPlotter`
            Plotter that best fits the criteria provided by the parameters.

        """
        return AbstractPlotter()
