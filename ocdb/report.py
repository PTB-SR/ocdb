"""
Textual description of the data and metadata contained in the ocdb package.

Although not the primary concern of the ocdb package, getting an overview
of the data contained in the database together with their respective metadata
is always a good idea. Hence, well-formatted reports containing both, a
graphical representation of the data and a summary of all the relevant
metadata including the references come in quite handy.


.. important::

    In order to access the reporting capabilities, you do need to have
    Jinja installed, although it is not a hard requirement of the ocdb package,
    to keep things clean and simple. The convenient way to install the
    necessary requirements would be to use pip with the optional requirements,
    such as:

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

Currently, the :mod:`ocdb.report` module provides a generic environment as well
as a dedicated LaTeX environment, implemented as respective classes:

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
        self._render()

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

    Raises
    ------
    FileNotFoundError
        Raised if the LaTeX executable could not be found


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

        """
        if not shutil.which(self.latex_executable):
            raise FileNotFoundError(
                f"LaTeX executable {self.latex_executable} not found"
            )
        self._copy_files_to_temp_dir()
        self._compile()
        # Note: In order to resolve references in LaTeX, compile twice.
        #       There might be a better option, automatically detecting
        #       whether compiling twice is necessary, but for now...
        self._compile()
        self._copy_files_from_temp_dir()
        self._remove_temp_dir()

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

    def _compile(self):
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
