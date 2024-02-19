==================
Essential Concepts
==================

Why another Python package for accessing optical constants? What makes the ocdb package different from `periodictable <https://periodictable.readthedocs.io/en/latest/index.html>`_ providing convenient access primarily to the data from the `CXRO database (Henke) <https://henke.lbl.gov/optical_constants/>`_? Three essential concepts make it stand out: providing **uncertainties**, **transparency and reproducibility** regarding the origin of the data, and a **history of records**.


Uncertainties
=============

One essential goal of the `Optical Constants Database (OCDB) <https://www.ocdb.ptb.de/>`_ maintained by the German National Metrology Institute, the `Physikalisch-Technische Bundesanstalt, PTB <https://www.ptb.de/>`_ is to provide **uncertainties** together with the optical constants.


Transparency and reproducibility
================================

Can I trust the data? The essence of science is to be as transparent as possible regarding the origin of the data and results. This allows the individual using the data to judge for themselves. To this end, the ocdb package provides crucial **metadata** and **citable references** for each individual dataset describing all relevant aspects in the necessary detail.


History of records
==================

Science never provides definite and final answers, and similarly, the data provided by the OCDB and the ocdb Python package in turn will change over time. Reasons for change are manifold: extending the available wavelength range (from the EUV to the VUV and eventually all the way to the IR), improved setup to measure the primary data, an enhanced understanding of the factors influencing the measurements and in turn an improved sample preparation and measurement strategies, and more advanced algorithms and strategies to obtain optical constants from the measured data, to name but the most important aspects.

The ocdb Python package aims at creating a **full transparency how the datasets for a given substance have been evolved**, besides providing access to previous versions of the data for the same substance if there are any. This leads to an essential distinction: dataset vs. measurement.


Dataset vs. measurement
-----------------------

The **primary dataset** for a given substance provided by the ocdb Python package will always be the consolidated latest data, potentially stitched together from different (partly overlapping) measurements. Hence, the primary data used to obtain the optical constants contained as the data in a dataset can originate from different samples and measurements.

A **measurement** in contrast is understood here as the entire workflow from a single recording of primary data for a given sample and a particular wavelength/energy range all the way through data processing and analysis to the optical constants extracted from these primary data.

What does that mean in practice? For a measurement, we can directly provide metadata for measurement (facility, beamline, measurement mode, ...) and sample (thickness, layer stack, morphology) and usually give an individual reference. For a dataset consisting potentially of the consolidated merge of different measurements, there is not necessarily a direct relation to a single sample or measurement.

For the time being, the ocdb package will only provide datasets, *i.e.* one set of (consolidated) optical constants for a given material, potentially spanning multiple wavelength ranges and resulting from a series of individual measurements. For each and every version of a dataset, there will be a citable reference, be it via Zenodo or as a text publication. Detailed information on how the data (read: optical constants) have been extracted from the primary data (read: measurements) can be found there.
