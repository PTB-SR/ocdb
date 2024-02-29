.. _GITHUB_REPO: https://github.com/PTB-SR/ocdb

.. _PYPI: https://pypi.org/project/ocdb/

.. _ZENODO: https://doi.org/10.5281/zenodo.10697496

=========
Deploying
=========

This section documents the relevant details regarding the deployment of the ocdb package. Focus is on automating all tasks as much as possible, to ease maintenance of the package.


Versioning
==========

The ocdb package follows `Semantic Versioning (SemVer) <https://semver.org/>`_. The version number is contained in the file ``VERSION`` in the repository root directory and automatically imported into the ``setup.py`` file. Furthermore, a bash script ``./bin/incrementVersion.sh`` is provided to be added as git hook for developers. This increments the ``.dev#`` suffix of the version number of development versions residing in the ``master`` branch of the repository.


Versioning and git branches
===========================

The ocdb package is maintained in a `GitHub repository <GITHUB_REPO_>`_. Development takes place in the ``master`` branch, releases are set as tags with the version number (and additionally, for each minor version an additional tag in the form ``MAJOR.MINOR``) in the ``stable`` branch. Upon creating a release within GitHub (by the package maintainers), the package will be automatically be built and uploaded to the `Python Package Index (PyPI) <PYPI_>`_. For details, see below.


When to increment which version number part
===========================================

Different to other software packages, the ocdb package has at least *two* reasons to change, hence for incrementing version numbers: changes in the code, and changes to the data it provides. Given that it follows Semantic Versioning (SemVer, see above), below are criteria when to increment which part of the version number.


PATCH: Bug fixes
----------------

Bug fixes can be either fixes in the code that do *not* introduce qualitatively new functionality (in the public API), or it could be fixes to metadata of datasets. Every bug fix release increments the PATCH part of the version number.


MINOR: New functionality or data
--------------------------------

As soon as there is new functionality in the public API of the code that is backwards-compatible, the MINOR part of the version number gets incremented. The same is true for new data, be it a new material or a new version of an existing dataset. Releasing a new MINOR version means to reset the PATCH part of the version number to zero.


MAJOR: Breaking changes
-----------------------

Backwards-incompatible changes in the public API of the code require a release incrementing the MAJOR part of the version number. These changes should be usually rare. In terms of data, it is not straight-forward to see what would trigger a MAJOR release.


.. note::

    Technically speaking, as long as the MAJOR part of the version number is still zero, everything would be allowed. Furthermore, the criteria when to start with version 1.0.0 are not strict. In any case, the public API should be reasonably stable for this step.


Creating a release
==================

.. important::

    Creating a release should (and can) only be done by the package maintainers. This requires a series of additional Python packages. Hence, if not done already as a maintainer/developer of the package, install the prerequisites for both, documentation and package development:

    .. code-block:: bash

        pip install ocdb[dev,docs,deployment]

    This will install a series of additional packages. For details, have a look at the ``setup.py`` file.


Before creating a release, make sure that the tests pass and that static code analysis running prospector does not issue any warnings. For convenience, a ``Makefile`` with the relevant targets is part of the source code. Running tests and static code analysis is as simple as:

.. code-block:: bash

    make tests
    make check

Developers should have setup automatic code formatting using Black as ``pre-commit`` git hook. To this end, a helper script ``./bin/formatPythonCode.sh`` is provided. See the :doc:`contributing` guide for further details. Just in case you would want to manually trigger the code formatting, run:

.. code-block:: bash

    make black

Eventually, after all the above tests pass, create the documentation and check for errors there:

.. code-block:: bash

    make docs

Now it is time to check whether the package can be successfully built:

.. code-block:: bash

    python -m build
    twine check dist/*

Don't forget to afterwards remove the packages built having the ``-dev#`` suffix and located in the ``dist`` directory.

If everything is well, creating the release can proceed. First, commit your latest changes, then checkout the ``stable`` branch and get all changes from the ``master`` branch:

.. code-block:: bash

    git checkout stable
    git merge --no-commit -X theirs master

Next, change the version number in the ``VERSION`` file (remove the „.dev#“ suffix, add „-rc.#“ if necessary), add the release date to the changelog in the docs, and update the roadmap. Now you are ready to do the final commit:

.. code-block:: bash

    git commit -m "release `cat VERSION`" -a

Next is to tag the release appropriately:

.. code-block:: bash

    git tag v`cat VERSION`
    git tag -f v`cat VERSION | cut -d. -f1-2`

This will create two tags and update the second one if necessary: The first tag is the full version number, *i.e.* ``MAJOR.MINOR.PATCH``, the second is the abbreviated two-part version number, *i.e.* ``MAJOR.MINOR``.

.. important::

    If you are about to release a "release candidate", do *not* create the second tag.

Now, you can push the new commit and the tags:

.. code-block:: bash

    git push --tags -f origin stable

After the commit and tags have been pushed to the `GitHub repository <GITHUB_REPO_>`_, create a new release in GitHub. The name is identical to the last commit message, *i.e.* ``Version #.#.#``, the description should be identical with the corresponding section in the changelog.

Upon creating the release, a few things will happen automatically:

* Thanks to the included GitHub workflow, the package will automatically be built and uploaded to `PyPI <PYPI_>`_.
* As Zenodo is connected to the GitHub repository, the `Zenodo record <ZENODO_>`_ will be updated as well.

The last thing left to be done: Go back to the master branch,

.. code-block:: bash

    git checkout master

bump the version number (typically resetting ``PATCH`` and setting ``dev#`` to ``dev0``), cherry-pick ``docs/changelog.rst``:

.. code-block:: bash

    git checkout stable docs/changelog.rst

and commit the changes. Typically, a generic commit message such as "Post-release" will be used.
