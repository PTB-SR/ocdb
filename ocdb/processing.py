"""
Processing steps for data contained in the OCDB.

Data processing can be quite different, from interpolating values to
converting between units.

For the time being, users of the ocdb package will not use the classes
implemented in this module directly, but only indirectly while accessing the
values for *n* and *k*.

"""

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


    Examples
    --------
    A factory usually has exactly one duty: Given a list of criteria,
    return the object that fits these criteria. Hence, getting a processing
    step from the factory is as simple as:

    .. code-block::

        processing_step_factory = ProcessingStepFactory()
        processing_step = processing_step_factory.get_processing_step()

    The criteria for getting the *correct* processing step will be some
    key-value pairs, hence the :meth:`get_processing_step` method supports
    arbitrary key-value pair (``**kwargs`` in Python speak):

    .. code-block::

        processing_step_factory = ProcessingStepFactory()
        processing_step = processing_step_factory.get_processing_step(
            values=13.5
        )

    This may get you a processing step extracting (and interpolating,
    where necessary) the values for *n* and *k* for the given wavelength.

    The actual users of the ocdb package will not see much of the factory,
    as they will usually just call the :meth:`ocdb.material.Material.n`,
    :meth:`ocdb.material.Material.k`,
    or :meth:`ocdb.material.Material.index_of_refraction` methods that will
    take care of the rest.

    """

    def get_processing_step(self, **kwargs):
        """
        Return processing step given the criteria in the keyword arguments.

        Parameters
        ----------
        kwargs
            All parameters relevant to decide upon the correct processing step.

            A list of key--value pairs, either as :class:`dict` or
            separate, *i.e.* the Python ``**kwargs`` argument.

        Returns
        -------
        processing_step : :class:`ProcessingStep`
            Processing step fitting to the criteria provided by the parameters.

        """
        return ProcessingStep()


class ProcessingStep(material.AbstractProcessingStep):
    """
    Base class for all concrete processing steps of the ocdb package.

    A concrete processing step depends strongly on what shall actually be
    processed, be it interpolating values for *n* or *k*, be it converting
    units. Nevertheless, all these types of processing steps share a common
    base, and this is implemented in this class.

    Real processing steps will always be performed by a descendant of this class.
    Which processing step to actually use is in the realm of the
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
