"""
Processing steps for data contained in the OCDB.

Data processing can be quite different, from interpolating values to
converting between units.

For the time being, users of the ocdb package will not use the classes
implemented in this module directly, but only indirectly while accessing the
values for *n* and *k*.

"""

import numpy as np

from ocdb import material


class ProcessingStepFactory(material.AbstractProcessingStepFactory):
    """
    Factory for processing steps.

    Different types of data and different situations require different
    types of processing steps. A simple example: Asking for a particular
    value of *n* or *k*, *i.e.*, for a given wavelength, usually requires
    interpolating this value, except of the lucky situation of the user
    asking for a value that is an exact match.

    Getting the appropriate processing step for the task at hand is the
    responsibility of this processing step factory.

    In actual :obj:`ocdb.material.Material` objects containing real data,
    the :attr:`ocdb.material.Material.processing_step_factory` will be set
    to an instance of this class.

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

        processing_step_factory = ProcessingStepFactory()
        processing_steps = processing_step_factory.get_processing_steps()

    The criteria for getting the *correct* processing step will be some
    key-value pairs, hence the :meth:`get_processing_step` method supports
    arbitrary key-value pair (``**kwargs`` in Python speak):

    .. code-block::

        processing_step_factory = ProcessingStepFactory()
        processing_steps = processing_step_factory.get_processing_steps(
            values=13.5
        )

    This may get you a processing step extracting (and interpolating,
    where necessary) the values for *n* and *k* for the given wavelength.

    .. note::

        As depending on the keyword arguments there may be more than one
        processing step, :meth:`get_processing_steps` will always return a
        list of :obj:`ProcessingStep` objects.

    The actual users of the ocdb package will not see much of the factory,
    as they will usually just call the :meth:`ocdb.material.Material.n`,
    :meth:`ocdb.material.Material.k`,
    or :meth:`ocdb.material.Material.index_of_refraction` methods that will
    take care of the rest.

    """

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
            All parameters relevant to decide on the correct processing step.

            A list of key--value pairs, either as :class:`dict` or
            separate, *i.e.* the Python ``**kwargs`` argument.

        Returns
        -------
        processing_steps : :class:`list`
            Processing steps fitting to the parameters.

            Each element in the list is an object of type
            :class:`ProcessingStep`.

        """
        processing_steps = []
        if "unit" in kwargs:
            unit_conversion = UnitConversion()
            unit_conversion.parameters["unit"] = kwargs["unit"]
            processing_steps.append(unit_conversion)
        if "values" in kwargs and kwargs["values"] is not None:
            interpolation = Interpolation()
            interpolation.parameters["values"] = kwargs["values"]
            if "interpolation" in kwargs:
                interpolation.parameters["kind"] = kwargs["interpolation"]
            processing_steps.append(interpolation)
        if not processing_steps:
            processing_steps.append(ProcessingStep())
        return processing_steps


class ProcessingStep(material.AbstractProcessingStep):
    """
    Base class for all concrete processing steps of the ocdb package.

    A concrete processing step depends strongly on what shall actually be
    processed, be it interpolating values for *n* or *k*, be it converting
    units. Nevertheless, all these types of processing steps share a common
    base, and this is implemented in this class.

    Real processing steps will always be performed by a descendant of this
    class. Which processing step to actually use is in the realm of the
    :class:`ProcessingStepFactory` that itself descends from the
    :class:`ocdb.material.AbstractProcessingStepFactory`.

    """

    def process(self):
        """
        Perform the actual processing.

        The actual processing is performed in the non-public method
        :meth:`_process`, such as not to interfere with the
        necessary settings done by the base class.
        """
        self._process()
        return self.data

    def _process(self):
        pass


class Interpolation(ProcessingStep):
    """
    Interpolate data for a given value or range of values.

    For the time being, only linear interpolation is supported, as this seems
    to be the physically most plausible way.


    Attributes
    ----------
    parameters : :class:`dict`
        All parameters necessary to perform the processing step

        values : :class:`float` or :class:`numpy.ndarray`
            Values to perform the interpolation for

        kind : :class:`str`
            Kind of interpolation used.

            If :class:`None`, no interpolation will be performed and a
            :class:`ValueError` raised if the value is not in the axis.

    Raises
    ------
    ValueError
        Raised if the values are not within the data range.

        Data will only be interpolated, not extrapolated.

    ValueError
        Raised if kind of interpolation is None and values are not in axis.


    Examples
    --------
    Interpolation operates on :obj:`ocdb.material.Data` objects. Hence, you
    need to have such a data object, most probably from a material. The result
    will be stored in the :attr:`data` attribute of the :class:`Interpolation`
    class, but will be returned by the method :meth:`process` as well:

    .. code-block::

        interpolation = Interpolation()
        interpolation.data = ocdb.elements.Co.n_data
        interpolation.parameters["values"] = 13.5
        interpolated_data = interpolation.process()

    Or a bit simpler, directly instantiating the interpolation object with the
    data to interpolate:

    .. code-block::

        interpolation = Interpolation(ocdb.elements.Co.n_data)
        interpolation.parameters["values"] = 13.5
        interpolated_data = interpolation.process()

    Typically, users will not directly interact with the class, but rather ask
    for a given value or range of values:

    .. code-block::

        ocdb.elements.Co.n(13.5, interpolation="linear")

    See the documentation of :meth:`ocdb.material.Material.n` for details.

    """

    def __init__(self, data=None):
        super().__init__(data=data)
        self.parameters["values"] = None
        self.parameters["kind"] = "linear"

    def _process(self):
        self._sanitise_parameters()
        self._check_range()
        self._interpolate_data()

    def _sanitise_parameters(self):
        if isinstance(self.parameters["values"], (float, int)):
            # noinspection PyTypedDict
            self.parameters["values"] = np.asarray(
                [self.parameters["values"]]
            )

    def _check_range(self):
        axes_values = self.data.axes[0].values
        if (
            min(self.parameters["values"]) < min(axes_values)
            or max(self.parameters["values"]) > max(axes_values)
            # This line is here to satisfy Black...
        ):
            message = (
                f"Requested range not within data range. "
                f"Available range: [{min(axes_values)}, {max(axes_values)}]"
            )
            raise ValueError(message)

    def _interpolate_data(self):
        if self.data.has_uncertainties():
            data_arrays = ["data", "lower_bounds", "upper_bounds"]
        else:
            data_arrays = ["data"]
        for data_array in data_arrays:
            # noinspection PyTypeChecker
            if self.parameters["kind"]:
                interpolated = np.interp(
                    self.parameters["values"],
                    self.data.axes[0].values,
                    getattr(self.data, data_array),
                )
                setattr(self.data, data_array, interpolated)
            else:
                index = [
                    np.where(self.data.axes[0].values == value)[0]
                    for value in self.parameters["values"]
                    if any(np.where(self.data.axes[0].values == value)[0])
                ]
                if not index:
                    raise ValueError("Value(s) not available")
                if len(index) != len(self.parameters["values"]):
                    raise ValueError("Value(s) not available")
                setattr(
                    self.data,
                    data_array,
                    getattr(self.data, data_array)[index],
                )
        self.data.axes[0].values = self.parameters["values"]


class UnitConversion(ProcessingStep):
    """
    Conversion between units for the wavelength/energy axis.

    Optical constants are generally energy-dependent, and energy can be given
    in a diverse set of units. Typical units are "nm" and "eV".


    Attributes
    ----------
    parameters : :class:`dict`
        All parameters necessary to perform the processing step

        unit : :class:`str`
            Unit to convert the *x* axis values into.

            Default: ``nm``

            Possible values: ``nm``, ``eV``

            If the value is identical with the unit of the *x* axis of the
            data to convert, the data are returned as is. Values are handled
            case-insensitive.

    constants : :class:`dict`
        All (physical) constants used for the unit conversions.

        c_0 : :class:`float`
            Speed of light in vacuum.

            Value: 299792458 m/s (exact)

        eV : :class:`float`
            Electron volt

            Value: 1.602176634e-19 J (exact)

        h_planck : :class:`float`
            Planck constant

            Value: 6.62607015e-34 J s (exact)


    Raises
    ------
    ValueError
        Raised if unit to convert to is not supported.


    Examples
    --------
    Unit conversion operates on :obj:`ocdb.material.Data` objects. Hence, you
    need to have such a data object, most probably from a material. The result
    will be stored in the :attr:`data` attribute of the
    :class:`UnitConversion` class, but will be returned by the method
    :meth:`process` as well:

    .. code-block::

        unit_conversion = UnitConversion()
        unit_conversion.data = ocdb.elements.Co.n_data
        unit_conversion.parameters["unit"] = "eV"
        converted_data = unit_conversion.process()

    Or a bit simpler, directly instantiating the unit conversion object with
    the data to convert the axis for:

    .. code-block::

        unit_conversion = UnitConversion(ocdb.elements.Co.n_data)
        unit_conversion.parameters["unit"] = "eV"
        converted_data = unit_conversion.process()

    Typically, users will not directly interact with the class, but rather ask
    for a given unit:

    .. code-block::

        ocdb.elements.Co.n(unit="eV")

    See the documentation of :meth:`ocdb.material.Material.n` for details.

    """

    def __init__(self, data=None):
        super().__init__(data=data)
        self.parameters["unit"] = "nm"

        self._supported_units = ["nm", "eV"]
        # Note: c_0, eV, h_planck are all exact starting 2019 according to SI
        self.constants = {
            "c_0": 299792458,
            "eV": 1.602176634e-19,
            "h_planck": 6.62607015e-34,
        }

    def _process(self):
        if not self.parameters["unit"]:
            return
        self._sanitise_parameters()
        if self.data.axes[0].unit.lower() == self.parameters["unit"].lower():
            return
        conversion_method = (
            f"_{self.data.axes[0].unit.lower()}_to_"
            f"{self.parameters['unit'].lower()}"
        )
        getattr(self, conversion_method)()

    def _sanitise_parameters(self):
        supported_units = [unit.lower() for unit in self._supported_units]
        if self.parameters["unit"].lower() not in supported_units:
            raise ValueError(
                f"Conversion to {self.parameters['unit']} not supported"
            )

    def _nm_to_ev(self):
        self.data.axes[0].values = (
            self.constants["h_planck"]
            / self.constants["eV"]
            * self.constants["c_0"]
            * 1e9
            / self.data.axes[0].values
        )

    def _ev_to_nm(self):
        self._nm_to_ev()
