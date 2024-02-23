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


A :obj:`Material` object is basically a composition of objects for data and
metadata that are described in the next section.

Interfaces to other modules -- pointing outwards in terms of a layered
architecture, as described in the :doc:`architecture section
<../architecture>` -- is provided by means of abstract factories and
described in a separate section below as well.


Data and metadata
=================

As mentioned above, a :obj:`Material` object is basically a composition of
objects for data and metadata:

* :class:`Data`

    Unit containing both, numeric data and corresponding axes.

* :class:`Axis`

    Data and metadata for an axis.

* :class:`Metadata`

    Relevant metadata for the optical constants of a given material.


Abstract interfaces
===================

Currently, interfaces to two other modules are provided:
:mod:`ocdb.processing` and :mod:`ocdb.plotting`. Interfacing is done
according to the "dependency inversion principle" using abstract factories:

* :class:`AbstractProcessingStepFactory`

    Abstract factory for processing steps.

* :class:`AbstractPlotterFactory`

    Abstract factory for plotter.

Those abstract factories create the relevant objects whose (abstract) base
classes are defined here as well:

* :class:`AbstractProcessingStep`

    Abstract base class for processing steps.

* :class:`AbstractPlotter`

    Abstract base class for plotter.

The concrete factories and base classes are implemented in the respective
modules: :mod:`ocdb.processing` and :mod:`ocdb.plotting`.


Module documentation
====================

"""

import copy
import datetime
import warnings

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

    n_data : :class:`Data`
        Data for the real part (dispersion) of the refractive index.

        To access the data, you will usually use the method :meth:`n`,
        as this provides you with additional options, such as getting a
        specific value or an (interpolated) range of values as well as
        uncertainties (if available in the dataset).

        To obtain *n* and *k* values simultaneously, use the
        :meth:`index_of_refraction` method.

    k_data : :class:`Data`
        Data for the complex part (extinction) of the refractive index.

        To access the data, you will usually use the method :meth:`k`,
        as this provides you with additional options, such as getting a
        specific value or an (interpolated) range of values as well as
        uncertainties (if available in the dataset).

        To obtain *n* and *k* values simultaneously, use the
        :meth:`index_of_refraction` method.

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

    versions : :class:`list`
        Previous versions of the dataset for the given material.

        Over time, different datasets will be available for the same material.
        Hence, it may be of interest to access the older datasets that are
        superset by a new one, at least get the information that there are
        some and where they are located in the ocdb.

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

    processing_step_factory : :class:`AbstractProcessingStepFactory`
        Factory for creating processing step objects on request.


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
    Hence, the :attr:`reference` and :attr:`metadata` attributes.

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

    For details regarding the metadata, have a look at the documentation of
    the :class:`Metadata` class.

    """

    def __init__(self):
        self.name = ""
        self.symbol = ""
        self.references = []
        self.metadata = Metadata()
        self.versions = []

        self.plotter_factory = AbstractPlotterFactory()
        self.processing_step_factory = AbstractProcessingStepFactory()

        self.n_data = Data()
        self.n_data.axes[1].quantity = "dispersion coefficient"
        self.n_data.axes[1].symbol = "n"
        self.k_data = Data()
        self.k_data.axes[1].quantity = "extinction coefficient"
        self.k_data.axes[1].symbol = "k"

    def n(
        self, values=None, interpolation=None, uncertainties=False, unit=""
    ):  # pylint: disable=invalid-name
        """
        Return real part *n* of the index of refraction.

        Parameters
        ----------
        values : :class:`float` or :class:`numpy.ndarray`
            Wavelengths/energies to get *n* for.

            If no values are provided, the entire data contained in the
            dataset are returned.

        interpolation : :class:`str`, default None
            Kind of interpolation to perform to get data.

            If no interpolation is provided, just a table lookup will be
            performed and if that fails, a :class:`ValueError` raised.

        uncertainties : :class:`bool`
            Whether to return uncertainties as separate arrays in output

        unit : :class:`str`
            Unit to convert the *x* axis values to

        Returns
        -------
        n : :class:`tuple`
            wavelength and *n* as :class:`numpy.ndarray`

            In case of uncertainties set to True, two additional arrays with
            lower and upper bound.

        See Also
        --------
        :meth:`k`, :meth:`index_of_refraction`

        """
        processing_steps = self.processing_step_factory.get_processing_steps(
            values=values, interpolation=interpolation, unit=unit
        )
        data = copy.deepcopy(self.n_data)
        for processing_step in processing_steps:
            processing_step.data = data
            data = processing_step.process()
        wavelengths = data.axes[0].values
        if uncertainties:
            output = (
                wavelengths,
                data.data,
                data.lower_bounds,
                data.upper_bounds,
            )
        else:
            output = (wavelengths, data.data)
        return output

    def k(
        self, values=None, interpolation=None, uncertainties=False, unit=""
    ):
        """
        Return imaginary part *k* of the index of refraction.

        Parameters
        ----------
        values : :class:`float` or :class:`numpy.ndarray`
            Wavelengths/energies to get *n* for.

            If no values are provided, the entire data contained in the
            dataset are returned.

        interpolation : :class:`str`, default None
            Kind of interpolation to perform to get data.

            If no interpolation is provided, just a table lookup will be
            performed and if that fails, a :class:`ValueError` raised.

        uncertainties : :class:`bool`
            Whether to return uncertainties as separate arrays in output

        unit : :class:`str`
            Unit to convert the *x* axis values to

        Returns
        -------
        k : :class:`tuple`
            wavelength and *k* as :class:`numpy.ndarray`

        See Also
        --------
        :meth:`n`, :meth:`index_of_refraction`

        """
        processing_steps = self.processing_step_factory.get_processing_steps(
            values=values, interpolation=interpolation, unit=unit
        )
        data = copy.deepcopy(self.k_data)
        for processing_step in processing_steps:
            processing_step.data = data
            data = processing_step.process()
        wavelengths = data.axes[0].values
        if uncertainties:
            output = (
                wavelengths,
                data.data,
                data.lower_bounds,
                data.upper_bounds,
            )
        else:
            output = (wavelengths, data.data)
        return output

    def index_of_refraction(
        self, values=None, interpolation=None, uncertainties=False, unit=""
    ):
        r"""
        Return complex index of refraction

        Parameters
        ----------
        values : :class:`float` or :class:`numpy.ndarray`
            Wavelengths/energies to get *n* for.

            If no values are provided, the entire data contained in the
            dataset are returned.

        interpolation : :class:`str`, default None
            Kind of interpolation to perform to get data.

            If no interpolation is provided, just a table lookup will be
            performed and if that fails, a :class:`ValueError` raised.

        uncertainties : :class:`bool`
            Whether to return uncertainties as separate arrays in output

        unit : :class:`str`
            Unit to convert the *x* axis values to

        Returns
        -------
        index_of_refraction : :class:`tuple`
            wavelength and *n* - i\ *k* as :class:`numpy.ndarray`

        See Also
        --------
        :meth:`n`, :meth:`k`

        """
        processing_steps = self.processing_step_factory.get_processing_steps(
            values=values, interpolation=interpolation, unit=unit
        )
        n_data = copy.deepcopy(self.n_data)
        for processing_step in processing_steps:
            processing_step.data = n_data
            n_data = processing_step.process()
        k_data = copy.deepcopy(self.k_data)
        for processing_step in processing_steps:
            processing_step.data = k_data
            k_data = processing_step.process()
        wavelengths = n_data.axes[0].values
        n_k = n_data.data - 1j * k_data.data
        if uncertainties:
            output = (
                wavelengths,
                n_k,
                n_data.lower_bounds,
                n_data.upper_bounds,
                k_data.lower_bounds,
                k_data.upper_bounds,
            )
        else:
            output = wavelengths, n_k
        return output

    def plot(self, **kwargs):
        """
        Plot data.

        Although not the primary concern of the ocdb package, getting an
        overview of the data contained in the database is always a good
        idea. Hence, for convenience, graphical representations of the
        optical constants for a material are quite helpful.


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


        Parameters
        ----------
        kwargs
            Parameters controlling the type of resulting plot.

            A list of key--value pairs, either as :class:`dict` or
            separate, *i.e.* the Python ``**kwargs`` argument.

            Currently, the following keys are understood:

            values : :class:`str`
                Values to plot: *n* or *k* or both.

                Allowed values are: ``n``, ``k``, ``both``

            uncertainties : :class:`bool`
                Whether to plot uncertainties.

            For the most up-to-date list of possible parameters, have a look
            at the :meth:`ocdb.plotting.PlotterFactory.get_plotter` method
            as well.


        Examples
        --------
        Plotting is rather straight-forward. Assuming an object of class
        :class:`Material` and named ``stuff``, plotting the optical data
        of "stuff" is as simple as:

        .. code-block::

            stuff.plot()

        This would plot only the *n* values for the given material. If you
        are instead interested in the *k* values, you would need to be
        explicit about this:

        .. code-block::

            stuff.plot(values="k")

        If you want to see both values, *n* and *k*, in one graph, and for
        obvious reasons with two independent axes left and right, this is
        possible as well:

        .. code-block::

            stuff.plot(values="both")

        How about uncertainties? These can be plotted as well, and you can
        combine all of the above with uncertainties: only *n* with
        uncertainties, only *k* with uncertainties, or both, *n* and *k*
        with their respective uncertainties:

        .. code-block::

            # The following two lines are equivalent
            stuff.plot(uncertainties=True)
            stuff.plot(values="n", uncertainties=True)

            # Plotting k instead of n
            stuff.plot(values="k", uncertainties=True)

            # Plotting n & k with uncertainties
            stuff.plot(values="both", uncertainties=True)

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
        self.plotter_factory.material = self
        plotter = self.plotter_factory.get_plotter(**kwargs)
        plotter.dataset = self
        plotter.plot()
        return plotter

    def has_uncertainties(self):
        """
        Indicate whether uncertainties are present.

        Only in case of both, lower *and* upper boundary being present for
        both, *n* and *k* values, will the answer be "True".

        Returns
        -------
        answer : :class:`bool`
            Whether dataset contains uncertainties

        """
        return bool(
            self.n_data.has_uncertainties()
            and self.k_data.has_uncertainties()
        )


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

        Could be an empty array. Use :meth:`has_uncertainties` for a
        convenient check.

    upper_bounds : :class:`numpy.ndarray`
        Upper bounds for uncertainty of the values stored in :attr:`data`.

        Could be an empty array. Use :meth:`has_uncertainties` for a
        convenient check.

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
        return bool(self.lower_bounds.size and self.upper_bounds.size)


class Axis:
    """
    Data and metadata for an axis.

    Data (stored in :class:`Data`) will always have at least two axes (except
    single points). One axis contains both, values (the independent variable)
    and metadata for the corresponding label, the second axis will only
    contain the metadata.


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
        least a standard subset of LaTeX math commands. If in doubt, have a
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

    Data are only as good as their accompanying metadata. Hence, metadata
    are a prerequisite for both, reproducibility and correct use of the data.

    This class provides a structure and hence access to the relevant metadata
    for optical constants of materials from the OCDB database. These metadata
    should be as machine-actionable as possible, allowing for automatic
    processing of information wherever sensible.


    Attributes
    ----------
    uncertainties : :class:`Uncertainties`
        Metadata regarding the uncertainties of the optical constants.

    date : :class:`datetime.date`
        Date the dataset was created.

        This date may be something like January 1st of a given year if no
        further information is available but the year the dataset was created.

    comment : :class:`str`
        Any relevant information that does not (yet) fit into anywhere else.

        There is nearly always the need to store some information that
        just does not fit into any of the fields. However, use with care
        and expand the data structure if you realise that you repeatedly
        store the same (kind of) information in the comment.

    """

    def __init__(self):
        self.uncertainties = Uncertainties()
        self.date = datetime.date.today()
        self.comment = ""


class Uncertainties:
    """
    Relevant information about the uncertainties, if present.

    Data are only as good as their accompanying metadata. Hence, metadata
    are a prerequisite for both, reproducibility and correct use of the data.

    This class provides a structure and hence access to the relevant metadata
    regarding the uncertainties of the values of the optical constants.

    .. note::
        Currently, there is not much information contained in this class. But
        this will change in the future, providing more detailed information on
        how the uncertainties have been determined.

    Attributes
    ----------
    confidence_interval : :class:`str`
        The value the uncertainties are provided for.

        A typical example would be "3 sigma".

    """

    def __init__(self):
        self.confidence_interval = ""


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
            PhysicalQuantity with at least value and unit?

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

        Controlled vocabulary, currently with "amorphous", "crystalline",
        "microcrystalline", "polycrystalline", "unknown" as entries.

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

        Controlled vocabulary, currently with "reflection", "transmission" as
        entries.

    facility : :class:`str`
        Name of the facility the measurement was carried out at.

        Typically, this will be the name the facility is known with. In
        case of the data in the OCDB recorded by the PTB in Germany,
        this will usually either be "BESSY-II" or "MLS".

    beamline : :class:`str`
        Name of the beamline the measurement was performed at.

        The name of the beamline typically requires detailed knowledge
        about the facility it is located at to make sense of the
        information provided.

    date : :class:`datetime.date`
        Date of the measurement.


    .. todo::
        How to deal with datasets spanning multiple wavelength ranges,
        hence are measured at more than one beamline and possibly at more
        than one facility (if we count BESSY-II and MLS as different
        facilities, as would make sense to me)?

        Two possibilities are immediately obvious: omit the fields
        ``facility`` and ``beamline``, or make them lists (of strings).
        A third possibility would be to make it a list of :class:`Setup`
        objects, where :class:`Setup` would have (at least) the two
        attributes ``facility`` and ``beamline``. The last option would
        have the advantage that facility and beamline are always
        explicitly together.

        Would it eventually make sense to change the name ``beamline`` to
        ``setup`` or ``instrument``? We may not always have beamlines at
        synchrotrons...

    """

    def __init__(self):
        self.type = ""
        self.facility = ""
        self.beamline = ""
        self.date = datetime.date.today()


class Version:
    """
    Metadata for a version of a dataset for a single material.

    Over time, different datasets will be available for the same material.
    Hence, it may be of interest to access the older datasets that are
    superset by a new one, at least get the information that there are
    some and where they are located in the ocdb.

    In case that there are multiple versions of a dataset for one material,
    each such version is represented by an object of class :obj:`Version` and
    contained in the :attr:`Material.versions` list.

    Attributes
    ----------
    material : :class:`Material`
        Optical constants and relevant metadata for a single material.

    description : :class:`str`
        Concise description of the characteristics of this version.

    current : :class:`bool`
        Flag determining whether the dataset version is the current one

    """

    def __init__(self):
        self.material = None
        self.description = ""
        self.current = False


class Collection:
    # noinspection PyUnresolvedReferences
    """
    Collection of materials whose data are part of the OCDB.

    While each material, be it an element or composition, will be accessed by
    means of an :obj:`Material` object, users of the ocdb package will
    typically operate on the properties of a collection that are
    :obj:`Material` objects.

    This allows for different collections, *e.g.* elements and compositions.
    Similarly, a general collection such as "materials" would be possible,
    containing all materials data are available for in the OCDB.


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
    interested in just getting a list of all items, either by name or by
    symbol (or both):

    .. code-block::

        for item in collection:
            print(item.symbol, item.name)

    If you know the items of your collection, you can access them as
    attributes of the collection itself. To be exact, each item added to a
    collection using the :meth:`add_item` method gets added as a attribute
    to the collection with the symbol of the item being the name of the
    attribute.

    Suppose you know that Cobalt (with symbol Co) is part of the items of your
    collection. In this case, you can access it as a property of the
    collection:

    .. code-block::

        collection.Co

    In the same way, you can access all properties of this item. For details,
    have a look at the documentation of the underlying :class:`Material`
    class.

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
        self._items[item.symbol] = item


class AbstractPlotter:
    """
    Abstract base class for plotters.

    Although not the primary concern of the ocdb package, getting an overview
    of the data contained in the database is always a good idea. Hence, for
    convenience, graphical representations of the optical constants for a
    material are quite helpful.

    Plotting as such is provided in the :mod:`ocdb.plotting` module, but the
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
        warnings.warn("Not plotting... probably Matplotlib is not installed.")


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
    :class:`AbstractPlotterFactory` are implemented in the
    :mod:`ocdb.plotting` module. Only if you ever import this module would
    you need to have a plotting framework (Matplotlib) installed.


    Attributes
    ----------
    material : :class:`Material`
        Material the plotter should be found for.

        Sometimes, which plotter to return depends on the settings of the
        material: Uncertainties can only be plotted if data for uncertainties
        are present in the material. However, this shall not be the
        responsibility of the uncertainties-aware plotter, but of the factory
        to return the fitting plotter in the first place.

        The material will be set from within the material.


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
    be found in the :mod:`ocdb.plotting` documentation.

    The actual users of the ocdb package will not see much of the factory,
    as they will usually just call the :meth:`Material.plot` method that
    will take care of the rest.

    """

    def __init__(self):
        self.material = None

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


class AbstractProcessingStep:
    """
    Abstract base class for processing steps.

    Often, data need to be processed before they are returned, be it the user
    asking for an explicit value that needs to be interpolated, be it a unit
    conversion.


    Parameters
    ----------
    data : :class:`Data`
        Data of a :class:`Material` that should be processed


    Attributes
    ----------
    data : :class:`Data`
        Data of a :class:`Material` that should be processed

    parameters : :class:`dict`
        All parameters necessary to perform the processing step

    """

    def __init__(self, data=None):
        self.data = data or Data()
        self.parameters = {}

    def process(self):
        """Perform the actual processing."""
        return self.data


class AbstractProcessingStepFactory:
    """
    Abstract factory for processing steps.

    Different types of data and different situations require different
    types of processing steps. A simple example: Asking for a particular
    value of *n* or *k*, *i.e.*, for a given wavelength, usually requires
    interpolating this value, except of the lucky situation of the user
    asking for a value that is an exact match.

    In any case, all the material wants and needs to know is that it
    requires a processing step in order to get its data processed. The
    abstract interface of the processing step itself is described in the
    :class:`AbstractProcessingStep` class, and the
    :class:`AbstractProcessingStepFactory` is the one place to ask for the
    correct processing step.

    Concrete instances of both, :class:`AbstractProcessingStep` and
    :class:`AbstractProcessingStepFactory` are implemented in the
    :mod:`ocdb.processing` module.

    For a given list of keyword arguments, there may be more than one
    processing step that needs to be applied sequentially to the data.

    The factory is responsible for returning the individual processing
    steps in the correct order. Assigning the correct data to the
    processing step, however, is the duty of the calling code, as
    otherwise, processing would not be sequentially applied to the result
    of the previous processing step, respectively.


    Examples
    --------
    A factory usually has exactly one duty: Given a list of criteria,
    return the object that fits these criteria. Hence, getting a processing
    step from the factory is as simple as:

    .. code-block::

        processing_step_factory = AbstractProcessingStepFactory()
        processing_steps = processing_step_factory.get_processing_steps()

    The criteria for getting the *correct* processing step will be some
    key-value pairs, hence the :meth:`get_processing_step` method supports
    arbitrary key-value pair (``**kwargs`` in Python speak):

    .. code-block::

        processing_step_factory = AbstractProcessingStepFactory()
        processing_steps = processing_step_factory.get_processing_steps(
            values=13.5
        )

    This may get you a processing step extracting (and interpolating,
    where necessary) the values for *n* and *k* for the given wavelength.
    Details of the available processing steps can be found in the
    :mod:`ocdb.processing` documentation.

    The actual users of the ocdb package will not see much of the factory,
    as they will usually just call the :meth:`Material.n`,
    :meth:`Material.k`, or :meth:`Material.index_of_refraction` methods that
    will take care of the rest.

    """

    # noinspection PyMethodMayBeStatic
    # pylint: disable=unused-argument
    def get_processing_steps(self, **kwargs):
        """
        Return processing steps given the criteria in the keyword arguments.

        For a given list of keyword arguments, there may be more than one
        processing step that needs to be applied sequentially to the data.

        The factory is responsible for returning the individual processing
        steps in the correct order. Assigning the correct data to the
        processing step, however, is the duty of the calling code, as
        otherwise, processing would not be sequentially applied to the result
        of the previous processing step, respectively.

        Parameters
        ----------
        kwargs
            All parameters relevant to decide upon a correct processing step.

            A list of key--value pairs, either as :class:`dict` or
            separate, *i.e.* the Python ``**kwargs`` argument.

        Returns
        -------
        processing_steps : :class:`list`
            Processing steps fitting to the criteria provided by parameters.

            Each element in the list is an object of type
            :class:`AbstractProcessingStep`.

        """
        return [AbstractProcessingStep()]
