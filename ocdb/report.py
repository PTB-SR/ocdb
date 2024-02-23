r"""
Textual description of the data and metadata contained in the ocdb package.

Although not the primary concern of the ocdb package, getting an overview
of the data contained in the database together with their respective metadata
is always a good idea. Hence, well-formatted reports containing both, a
graphical representation of the data and a summary of all the relevant
metadata including the references come in quite handy.


.. important::

    In order to access the reporting capabilities, you do need to have
    Jinja installed, although it is not a hard requirement of the ocdb
    package, to keep things clean and simple. The convenient way to install
    the necessary requirements would be to use pip with the optional
    requirements, such as:

     .. code-block:: bash

         pip install ocdb[presentation]

    This will install all necessary dependencies for you. Note that
    this step is only necessary if you ever want to access the
    reporting capabilities. Using the ocdb package without Jinja
    is entirely possible.


Output formats
==============

Template engines provide means of a "separation of concerns" (a term coined
by Edsger W. Dijkstra and highly important not only in software development):
The data source is entirely independent of the formatting of the report, and
one and the same template engine can be used to create reports in a multitude
of output formats.

Currently, the ocdb package supports one output format (more may be added in
the future): LaTeX. The respective reporter classes are:

  * :class:`LaTeXReporter`

The bundled templates used with the respective reporters are stored within
the ``templates/report/`` directory of the ocdb package, and here within
subdirectories (``latex``) for each of the formats. This makes it easy to add
additional formats and to shorten the template paths when using the reporters.


Dedicated reporters
===================

Besides the general reporters as described above that can be used in general
for any template, there are dedicated reporters for special tasks. The
difference between these reporters and the general reporters described above:
The dedicated reporters usually perform additional and specific tasks,
such as creating a graphical representation of data to be included into the
report. Furthermore, these dedicated reporters create a specific context that
is accessed from within the accompanying template.

Currently, the ocdb package contains the following dedicated reporters:

  * :class:`MaterialReporter`

    Report generator for materials.




Organisation of templates
=========================

As mentioned above, the bundled templates used with the respective reporters
are stored within the ``templates/report/`` directory of the ocdb package.
Each output format has its own subdirectory, currently existing directories
are ``latex``.

Currently, the ocdb template organisation looks similar to the following:

.. code-block::

    templates/
        report/
            latex/
                base.tex
                material.tex
                ...

The templates are supposed to be in English language.


A note on LaTeX templates
-------------------------

The LaTeX templates make extensive use of the Jinja machinery supporting to
define blocks in templates as well as a template to extend another template.
In other words, there is one base template ``base.tex`` containing the
overall LaTeX scaffold with ``documentclass`` declaration, header, and body:

.. literalinclude:: ../../ocdb/templates/report/latex/base.tex
    :language: latex


A typical template used for generating reports may hence look similar to what
is shown below. For further details, have a look at the available templates
in the respective folder in the source code:

.. code-block:: latex

    %{ extends template_dir + 'base.tex' }%

    %{ block preamble }%
    \usepackage[sorting=none]{biblatex}
    \addbibresource{{@ material.symbol }.bib}
    \DeclareBibliographyCategory{software}
    \BiblatexSplitbibDefernumbersWarningOff
    %{ endblock }%

    %{ block title }%
    %{ endblock }%

    %{ block body }%
    \thispagestyle{empty}
    ...
    %{ endblock }%


Here, you can see a few crucial aspects:

* The first line ``%{ extends template_dir + 'base.tex' }%`` states which
  template will be used to extend. The reporter will always provide the
  ``template_dir`` key in the context. Hence, nothing to do here.

* The only necessary block is the ``body`` block, as otherwise, your document
  will not have any content.

* You can extend the LaTeX header providing details in the block ``preamble``.

* Use the block ``title`` if you intend to set the usual title commands known
  from LaTeX.


Sometimes, it is quite helpful to include other templates as well. This can
be done with a line similar to the following:

.. code-block:: text

    %{ include template_dir + "colophon.tex" }%

Again, it is crucial to provide the ``template_dir`` variable here, in order
to get templates residing in the package data included.


Background: Jinja
=================

The report functionality relies heavily on the `Jinja template engine
<https://jinja.palletsprojects.com/>`_ . Therefore, it is very useful to be
generally familiar with the concepts of Jinja. Basically, this template engine
allows users to specify rather complicated replacements and logic within
the template. However, logic within templates should be used sparingly,
and the template should always be rendered correctly even without
processing it by the template engine. Only then templates are easy to
develop and adapt.

Two concepts used by Jinja the user of the report facilities of the ocdb
package should be familiar with are "environment" and "context".


Environment
-----------

An environment is a list of settings determining the type of delimiters used
within a certain template for the control structures that are understood by
Jinja. As Jinja is developed with web applications (and hence HTML) in
mind, those delimiters may not be feasible for other types of languages a
template may be written in, such as LaTeX.

Currently, the :mod:`ocdb.report` module provides a generic environment as
well as a dedicated LaTeX environment, implemented as respective classes:

  * :class:`GenericEnvironment`
  * :class:`LaTeXEnvironment`

These environments get automatically loaded by the respective reporter
classes:

  * :class:`Reporter`
  * :class:`LaTeXReporter`

The :class:`LaTeXEnvironment` and :class:`LaTeXReporter` provide some heavy
adaptations to rendering and even compiling LaTeX templates.


Context
-------

The second important concept of Jinja is that of the "context": Think of
it as a dictionary containing all the key--value pairs you can use to
replace placeholders within a template with their actual values. In the
simplest of all cases within the context of the ocdb package,
this could be the metadata of an :obj:`ocdb.material.Material` object.


Notes for developers
====================

As mentioned above, the templates are stored as package data and organised
according to the output format. Hence, adding another output format usually
requires three steps:

* Add templates to the respective subdirectory in the templates package
  directory.

* Create an environment inheriting from :class:`GenericEnvironment` that at
  least sets the path to the templates in the package data.

* Create a reporter class inheriting from :class:`Reporter` and set its
  :attr:`Reporter._environment` attribute to the environment just created.


Module documentation
====================

"""

import contextlib
import datetime
import importlib.metadata
import os
import shutil
import subprocess  # nosec
import tempfile

try:
    # noinspection PyUnresolvedReferences
    import jinja2
except ImportError:
    pass


class Reporter:
    """
    Base class for reports.

    To generate a report from a template, you will need a template in the
    first place. The path to the template (including its filename) is set in
    the :attr:`template` attribute. Similarly, you should specify an
    output filename, stored in the :attr:`filename` attribute. The variables
    known to the template that should be replaced by appropriate content,
    termed "context" in Jinja language, are stored in the :attr:`context`
    attribute.

    Next, you want to render the template, and most often, save it to a file
    afterwards. If you would like to separate those steps, you can call the
    :meth:`render` and :meth:`save` methods separately. For convenience,
    simply call :meth:`create` to render the report and save it to the file
    whose name you have provided.


    Attributes
    ----------
    template : :class:`str`
        Template file used to generate report.

    filename : :class:`str`
        Name of the resulting template file.

    context : :class:`collections.OrderedDict`
        Variables of a template that are replaced with the given content.

    report : :class:`str`
        Actual report, i.e. rendered template.

    Raises
    ------
    ValueError
        Raised if the template file provided does not exist.


    Examples
    --------
    Given a template name and a filename for the rendered report, using a
    reporter is fairly straight-forward:

    .. code-block::

        reporter = Reporter()
        reporter.template = "<template>.j2.tex"
        reporter.filename = "<report>.tex"
        reporter.create()

    Templates are looked up at two different places: Either in the file system
    using the name as relative path, or in the package data. In both cases, if
    you provide a name for a template that cannot be found, a respective
    exception will be raised.

    """

    def __init__(self):
        self.template = ""
        self.filename = ""
        self.context = {}
        self.report = ""

        self._environment = GenericEnvironment()
        self._jinja_template = None

    def render(self):
        """
        Render the template.

        Make sure to provide a (valid) template name in the :attr:`template`
        attribute. Furthermore, you will need a dictionary in attribute
        :attr:`context` to have the engine actually replacing values in the
        template.

        The actual rendering of the template takes place in the non-public
        method :meth:`_render`. Before calling :meth:`_render`, the renderer
        checks the existence of the file provided as attribute
        :attr:`template`. If this is not the case, a corresponding exception
        will be raised.

        To actually save the rendered template, call the method :meth:`save`.
        As usually, rendering a template without saving the results is less
        useful, you may call :meth:`create` instead to get both at once, your
        template rendered and saved.

        Raises
        ------
        ValueError
            Raised if the template file provided does not exist.

        """
        if not self.template:
            raise ValueError("No template provided")
        self._jinja_template = self._environment.get_template(self.template)
        self._add_to_context()
        self._render()

    def _add_to_context(self):
        self.context["template_dir"] = os.path.split(self.template)[0]
        if self.context["template_dir"]:
            self.context["template_dir"] += os.path.sep
        # noinspection PyTypeChecker
        self.context["timestamp"] = datetime.datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    def _render(self):
        self.report = self._jinja_template.render(self.context)

    def save(self):
        """
        Save the (rendered) report to a file.

        The filename is set in the :attr:`filename` attribute.

        Raises
        ------
        ValueError
            Raised if no output file for the report is provided.

        """
        if not self.filename:
            raise ValueError("No output filename provided")
        with open(self.filename, mode="w+", encoding="utf8") as output_file:
            output_file.write(self.report)

    def create(self):
        """
        Render the template and save the result to a file.

        Convenience method to render the template and save the generated
        report to a file, thus simply calling :meth:`render` and
        :meth:`save` subsequently.

        """
        self.render()
        self.save()


class GenericEnvironment(jinja2.Environment):
    """
    Jinja environment for rendering generic templates.

    The environment does not change any of the Jinja settings except of the
    loaders. Here, a list of loaders using :class:`jinja2.ChoiceLoader` is
    implemented. Using this loader makes it possible to search subsequently
    in different places for a template. Here, the first hit is used,
    therefore, the sequence of loaders is *crucial*.

    Currently, there are two loaders implemented, in exactly this sequence:

    #. :class:`jinja2.FileSystemLoader`

        Looking for templates in the current directory and using an absolute
        path.

    #. :class:`jinja2.PackageLoader`

        Looking for templates in the ocdb package in the package path
        "templates/report/", *i.e.* the base directory for all report
        templates of the ocdb package.

    Parameters
    ----------
    env : :class:`dict`
        Dictionary used for creating the :class:`jinja2.Environment`.

        Can be used by derived classes to override the environment.

        Note that in any case, the ``loader`` will be replaced in the
        resulting :class:`jinja.Environment`. Hence, to set the path, use the
        ``path`` parameter (see below for details).

    path : :class:`str`
        Path to the templates within the package.

        This is the relative path, *i.e.* the last, format-specific part, for
        the templates.

    """

    def __init__(self, env=None, path=""):
        if not env:
            env = {}
        package_path = os.path.join("templates/report", path)
        env["loader"] = jinja2.ChoiceLoader(
            [
                jinja2.FileSystemLoader(
                    [os.path.abspath("."), os.path.abspath("/")]
                ),
                jinja2.PackageLoader(__package__, package_path=package_path),
            ]
        )
        super().__init__(**env)


class LaTeXEnvironment(GenericEnvironment):
    """
    Jinja2 environment for rendering LaTeX-based templates.

    This environment is designed for using templates written in LaTeX that
    can be rendered by LaTeX without having their control code replaced by
    Jinja2. While variables are usually output in LaTeX, control structures
    are prefixed by a LaTeX comment character (``%``). For convenience,
    the following table lists all the variables currently set within this
    environment.

    ===================== =====
    Variable              Value
    ===================== =====
    block_start_string    %{
    block_end_string      }%
    variable_start_string {@
    variable_end_string   }
    comment_start_string  %#{
    comment_end_string    }
    line_statement_prefix %%
    line_comment_prefix   %#
    trim_blocks           True
    autoescape            False
    ===================== =====

    While every measure is taken to keep the above information as accurate
    as possible, for authoritative information the reader is referred to
    the actual source code.

    The idea behind all these modifications is to have templates work with
    LaTeX, even if the template is not rendered.

    Besides extensively modifying the control codes used within the
    template, the environment implements a list of loaders using
    :class:`jinja2.ChoiceLoader`. Using this loader makes it possible to
    search subsequently in different places for a template. Here, the first
    hit is used, therefore, the sequence of loaders is *crucial*.

    Currently, there are two loaders implemented, in exactly this sequence:

    #. :class:`jinja2.FileSystemLoader`

        Looking for templates in the current directory and using an absolute
        path

    #. :class:`jinja2.PackageLoader`

        Looking for templates in the ocdb package in the package path
        "templates/report/latex/", *i.e.* the directory for all LaTeX report
        templates of the ocdb package.

    """

    def __init__(self):
        env = {
            "block_start_string": "%{",
            "block_end_string": "}%",
            "variable_start_string": "{@",
            "variable_end_string": "}",
            "comment_start_string": "%#{",
            "comment_end_string": "}",
            "line_statement_prefix": "%%",
            "line_comment_prefix": "%#",
            "trim_blocks": True,
            "autoescape": False,
        }
        super().__init__(env=env, path="latex")


class LaTeXReporter(Reporter):
    """
    LaTeX Reporter.

    Often, templates for reports are written in LaTeX, and the results
    typeset as PDF file upon a (pdf)LaTeX run. For convenience, this class
    offers the necessary facilities to compile the template once written.

    Note that for compiling a temporary directory is used, such as not to
    clutter the current working directory with all the auxiliary files
    usually created during a (pdf)LaTeX run. Furthermore, currently, only a
    single (pdf)LaTeX run is performed with option
    ``-interaction=nonstopmode`` passed in order to not block further
    execution.

    .. important::
        For enhanced security, the temporary directory used for compiling
        the template will be removed after successful compilation.
        Therefore, no traces of your report should remain outside the
        current directory controlled by the user.

    Attributes
    ----------
    includes : :class:`list`
        List of files that need to be present for compiling the template.

        These files will be copied into the temporary directory used for
        compiling the template.

    latex_executable : :class:`str`
        Name of/path to the LaTeX executable.

        Defaults to "pdflatex"

    bibtex_executable : :class:`str`
        Name of/path to the BibTeX executable.

        Defaults to ""

        Only in case this attribute is set to a non-empty value will the
        bibliography be built.

    Raises
    ------
    FileNotFoundError
        Raised if the LaTeX executable could not be found

    FileNotFoundError
        Raised if the BibTeX executable could not be found


    Examples
    --------
    The whole procedure may look as follows:

    .. code-block::

        report = LaTeXReporter()
        report.template = "template.tex"
        report.filename = "report.tex"
        report.create()
        report.compile()

    This will result with a file "report.pdf" in the current directory. If
    you specify a relative or absolute path for the filename of the report,
    the resulting PDF file will be copied to that path accordingly.

    """

    def __init__(self):
        super().__init__()
        self.includes = []
        self.latex_executable = "pdflatex"
        self.bibtex_executable = ""

        self._environment = LaTeXEnvironment()
        self._temp_dir = tempfile.mkdtemp()
        self._pwd = os.getcwd()

    def compile(self):
        """
        Compile LaTeX template.

        The template is copied to a temporary directory and the LaTeX
        executable specified in :attr:`latex_executable` called on the
        report. Afterwards, the result is copied back to the original
        directory.

        Additionally, all files necessary to compile the report are copied
        to the temporary directory as well.

        Raises
        ------
        FileNotFoundError
            Raised if the LaTeX executable could not be found

        FileNotFoundError
            Raised if the BibTeX executable could not be found

        """
        self._check_for_prerequisites()
        self._copy_files_to_temp_dir()
        self._compile_latex()
        if self.bibtex_executable:
            self._compile_bibtex()
            self._compile_latex()
        # Note: In order to resolve references in LaTeX, compile twice.
        #       There might be a better option, automatically detecting
        #       whether compiling twice is necessary, but for now...
        self._compile_latex()
        self._copy_files_from_temp_dir()
        self._remove_temp_dir()

    def _check_for_prerequisites(self):
        if not shutil.which(self.latex_executable):
            raise FileNotFoundError(
                f"LaTeX executable {self.latex_executable} not found"
            )
        if self.bibtex_executable and not shutil.which(
            self.bibtex_executable
        ):
            raise FileNotFoundError(
                f"BibTeX executable {self.bibtex_executable} not found"
            )

    def _copy_files_to_temp_dir(self):
        """Copy all necessary files to compile the LaTeX report to temp_dir

        Takes care of relative or absolute paths of both, report and includes.
        """
        _, filename_wo_path = os.path.split(self.filename)
        shutil.copy2(
            self.filename, os.path.join(self._temp_dir, filename_wo_path)
        )
        for filename in self.includes:
            _, filename_wo_path = os.path.split(filename)
            shutil.copy2(
                filename, os.path.join(self._temp_dir, filename_wo_path)
            )

    def _compile_latex(self):
        """Actual compiling of the report.

        The compiling takes place in a temporary directory that gets
        removed after the (successful) compile step using the
        :meth:`_remove_temp_dir` method.

        (pdf)LaTeX is currently called with the "-interaction=nonstopmode"
        option in order to not block further execution.
        """
        with change_working_dir(self._temp_dir):
            _, filename_wo_path = os.path.split(self.filename)
            # Path stripped, there should be no security implications.
            process = subprocess.run(
                [
                    self.latex_executable,  # nosec
                    "-output-directory",
                    self._temp_dir,
                    "-interaction=nonstopmode",
                    filename_wo_path,
                ],
                check=False,
                capture_output=True,
            )
            print(process.stdout.decode())
            print(process.stderr.decode())

    def _compile_bibtex(self):
        """Creating bibliography of the report.

        The compiling takes place in a temporary directory that gets
        removed after the (successful) compile step using the
        :meth:`_remove_temp_dir` method.
        """
        with change_working_dir(self._temp_dir):
            _, filename_wo_path = os.path.split(self.filename)
            # Path stripped, there should be no security implications.
            process = subprocess.run(
                [
                    self.bibtex_executable,  # nosec
                    os.path.splitext(filename_wo_path)[0],
                ],
                check=False,
                capture_output=True,
            )
            print(process.stdout.decode())
            print(process.stderr.decode())

    def _copy_files_from_temp_dir(self):
        """Copy result of compile step from temporary to target directory

        Takes care of any relative or absolute paths provided for the
        report output file provided in :attr:`filename`.
        """
        basename, _ = os.path.splitext(self.filename)
        path, basename = os.path.split(basename)
        pdf_filename = ".".join([basename, "pdf"])
        if os.path.isabs(path):
            shutil.copy2(
                os.path.join(self._temp_dir, pdf_filename),
                os.path.join(path, pdf_filename),
            )
        else:
            shutil.copy2(
                os.path.join(self._temp_dir, pdf_filename),
                os.path.join(self._pwd, path, pdf_filename),
            )

    def _remove_temp_dir(self):
        """Remove temporary directory used for compile step.

        The (pdf)LaTeX step is performed in a temporary directory such as
        not to clutter the current working directory with all the auxiliary
        files usually created during a (pdf)LaTeX run.

        This temporary directory is removed after the (successful) compile
        step. Note that therefore, all sometimes useful information stored,
        e.g., in the log file, is lost. However, manually compiling the
        report is probably the easiest way of figuring out if something
        gets wrong with the (pdf)LaTeX compile step
        """
        shutil.rmtree(self._temp_dir)


@contextlib.contextmanager
def change_working_dir(path=""):
    """
    Context manager for temporarily changing the working directory.

    Sometimes it is necessary to temporarily change the working directory,
    but one would like to ensure that the directory is reverted even in case
    an exception is raised.

    Due to its nature as a context manager, this function can be used with a
    ``with`` statement. See below for an example.


    Parameters
    ----------
    path : :class:`str`
        Path the current working directory should be changed to.


    Examples
    --------
    To temporarily change the working directory:

    .. code-block::

        with change_working_dir(os.path.join('some', 'path')):
            # Do something that may raise an exception

    This can come in quite handy in case of tests.

    """
    old_pwd = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(old_pwd)


class MaterialReporter:
    """
    Report generator for materials.

    The idea behind this reporter is to create an overview of the data and
    metadata available for each individual material.

    By default, the reporter uses LaTeX, hence instances of the
    :class:`LaTeXReporter` class, and it compiles the rendered LaTeX report
    automatically. Furthermore, the reporter generates a graphical
    representation of the data.

    The reporter does a few things:

    * Create a figure with a graphical representation of the data,
      and save this figure to a file.

    * Create the actual report from a template.

    * Create the bibliography with the references.

    * Compile the created report.


    Attributes
    ----------
    material : :class:`ocdb.material.Material`
        Material the report should be generated for.

    reporter : :class:`Reporter`
        Reporter used for generating the report.

    output_format : :class:`str`
        Identifier of the output format.

        Currently, only "latex" is supported.

        Note that output formats are case-insensitive.

    Examples
    --------
    Creating a report for a given material is fairly straight-forward. All it
    requires is the :mod:`ocdb` package and the :mod:`ocdb.report` module
    loaded:

    .. code-block::

        import ocdb
        import ocdb.report

        reporter = MaterialReporter()
        reporter.material = ocdb.elements.Co
        reporter.create()

    This would create the report for Cobalt. To this end, four files will be
    created: ``Co.pdf`` containing the figure with the data, ``Co.bib``
    containing the references as BibTeX bibliography, and ``Co-report.tex``
    and ``Co-report.pdf`` as LaTeX source and compiled PDF of the report.

    .. important::

        As the :meth:`create` method does do the (pdf)LaTeX compiling for
        you, and due to the fact that a bibliography is included, generating
        the final PDF file of the report will take some time (at least a few
        seconds). The steps are basically: pdflatex, biber, pdflatex, pdflatex.

    .. note::

        For developers: Currently, despite the generic name, this reporter is
        rather tied to LaTeX as output format, partly due to handling the
        bibliography in this way. Hence, if other formats should be supported
        in the future, a bit of code reorganisation will necessarily need to
        take place, perhaps subclassing the reporter.

    """

    def __init__(self):
        self.material = None
        self.reporter = None
        self.output_format = "latex"

        # Note: the values are the corresponding classes
        self._output_formats = {
            "latex": LaTeXReporter,
        }
        self._includes = []

    def create(self):
        """
        Render the template and save the result to a file.

        As currently, only LaTeX is supported, these are the steps performed:

        * Create a figure with a graphical representation of the data,
          and save this figure to the file ``<material-symbol>.pdf``.

        * Create the actual report from a template.

          The template file used is ``material.tex``. The resulting report is
          named ``<material-symbol>-report.tex``.

        * Create the bibliography with the references.

          The template file used is ``literature.bib``. The resulting
          bibliography is named ``<material-symbol>.bib``.

        * Compile the created report.

          The resulting file is named ``<material-symbol>-report.pdf``.

        Raises
        ------
        ValueError
            Raised if no material is provided to report on.

        ValueError
            Raised if the output format is not supported/known.

        """
        self._check_prerequisits()
        self.reporter = self._output_formats[self.output_format]()
        self._create_figure()
        self._create_bibliography()
        self._create_report()

    def _check_prerequisits(self):
        if not self.material:
            raise ValueError("No material to report on")
        if self.output_format.lower() not in self._output_formats:
            raise ValueError(f"Output format {self.output_format} unknown")

    def _create_figure(self):
        plotter = self.material.plot(uncertainties=True, values="both")
        figure_filename = ".".join([self.material.symbol, "pdf"])
        plotter.figure.savefig(figure_filename)
        self._includes.append(figure_filename)

    def _create_bibliography(self):
        reporter = LaTeXReporter()
        reporter.template = "literature.bib"
        reporter.filename = f"{self.material.symbol}.bib"
        references = [
            reference.to_bib() for reference in self.material.references
        ]
        reporter.context["references"] = "\n\n".join(references)
        reporter.create()
        self._includes.append(reporter.filename)

    def _create_report(self):
        reporter = LaTeXReporter()
        reporter.bibtex_executable = "biber"
        reporter.template = "material.tex"
        reporter.filename = f"{self.material.symbol}-report.tex"
        reporter.includes = self._includes
        references = ",".join(
            [reference.key for reference in self.material.references]
        )
        versions = [
            {
                "date": version.material.metadata.date,
                "description": version.description,
            }
            for version in self.material.versions
        ]
        reporter.context["material"] = {
            "symbol": self.material.symbol,
            "name": self.material.name,
            "date": self.material.metadata.date,
            "uncertainties": self.material.metadata.uncertainties.confidence_interval,
            "comment": self.material.metadata.comment,
            "references": references,
            "versions": versions,
        }
        reporter.context["ocdb"] = {
            "version": importlib.metadata.version(__package__)
        }
        reporter.create()
        reporter.compile()
