"""
Core entities of the ocdb package forming a database of optical constants.

From a software architecture perspective, the classes in the database module of
the ocdb package are part of the core domain. That does not imply by any means
that users of the ocdb package will instantiate these classes by themselves.
Nevertheless, they will directly interact with instances of the core classes.


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

import bibrecord.record
import numpy as np


class Material:
    """
    Optical constants and relevant metadata for a single material.

    This is a base class for materials of all kinds, be it elements or
    compositions, and it is at the core of the ocdb package and architecture.
    Key aspects are data *and* metadata in a single unit, the latter including
    a full bibliographic record for proper citation.


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

    reference : :class:`bibrecord.record.Record`
        Bibliographic record for the data of the optical constants.

        One central idea of the ocdb package is to provide not only data, but
        the relevant metadata as well. Hence, the reference of the dataset, be
        it an actual dataset or a publication describing the underlying
        measurements, is fairly essential.

    metadata : :class:`Metadata`
        Relevant metadata for the data of the optical constants.

        Data are only as good as their accompanying metadata. Reproducibility
        as well as sensible use of the data requires access to all relevant
        metadata.


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

    # pylint: disable=too-many-instance-attributes
    def __init__(self):
        self.name = ""
        self.symbol = ""
        self.reference = bibrecord.record.Record()
        self.metadata = Metadata()

        # TODO: Shall at least n, k, and uncertainties be one matrix "data"?
        self._wavelengths = np.ndarray(0)
        self._n = np.ndarray(0)
        self._n_lb = np.ndarray(0)
        self._n_ub = np.ndarray(0)
        self._k = np.ndarray(0)
        self._k_lb = np.ndarray(0)
        self._k_ub = np.ndarray(0)

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
        if uncertainties:
            output = (self._wavelengths, self._n, self._n_lb, self._n_ub)
        else:
            output = (self._wavelengths, self._n)
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
        if uncertainties:
            output = (self._wavelengths, self._k, self._k_lb, self._k_ub)
        else:
            output = (self._wavelengths, self._k)
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
            wavelength and *n* + i\ *k* as :class:`numpy.ndarray`

        """
        n_k = self._n + 1j * self._k
        if uncertainties:
            output = (
                self._wavelengths,
                n_k,
                self._n_lb,
                self._n_ub,
                self._k_lb,
                self._k_ub,
            )
        else:
            output = self._wavelengths, n_k

        return output


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
    layer_thickness : :class:`None`
        Thickness of the layer of the actual material of interest.

        The materials whose optical constants are contained in the OCDB have
        been measured on thin films in reflection, not as free-standing thin
        films in transmission. Therefore, the material of interest is a (thin)
        film supported by a substrate and in many cases a more complex stack of
        different layers.

        .. todo::
            Decide upon the type of this attribute.
            PhysicalConstant with at least value and unit?

    substrate : :class:`str`
        Name of the substrate supporting the actual material of interest.

        Note that the substrate is typically different from the (more complex)
        layer stack. For the latter, see the :attr:`layer_stack` attribute.

    layer_stack : :class:`str`
        Description of the (complex) layer stack of the sample.

        The materials whose optical constants are contained in the OCDB have
        been measured on thin films in reflection, not as free-standing thin
        films in transmission. Therefore, the material of interest is a (thin)
        film supported by a substrate and in many cases a more complex stack of
        different layers.

        A brief description of this layer stack, *e.g.* "Si (C/ Co/ Ru/ Si)",
        should be provided here.

    date_of_measurement : :class:`None`
        Date of the measurement.

        .. todo::
            Decide upon the type of this attribute. Python date object?

    """

    def __init__(self):
        self.layer_thickness = None
        self.substrate = ""
        self.layer_stack = ""
        self.date_of_measurement = None


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
