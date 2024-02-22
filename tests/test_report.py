import contextlib
import datetime
import io
import os
import unittest

import jinja2
import numpy as np

import ocdb.material
import ocdb.management
from ocdb import report


class TestReporter(unittest.TestCase):
    def setUp(self):
        self.reporter = report.Reporter()
        self.template = "test_template.j2"
        self.template2 = os.path.abspath(self.template)
        self.filename = "test_report.txt"

    def tearDown(self):
        if os.path.exists(self.template):
            os.remove(self.template)
        if os.path.exists(self.template2):
            os.remove(self.template2)
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def test_instantiate_class(self):
        pass

    def test_render_without_template_raises(self):
        self.reporter.template = ""
        with self.assertRaisesRegex(ValueError, "No template provided"):
            self.reporter.render()

    def test_render_with_nonexistent_template_raises(self):
        self.reporter.template = "foo.bar"
        with self.assertRaises(jinja2.exceptions.TemplateNotFound):
            self.reporter.render()

    def test_render_with_template(self):
        with open(self.template, "w+", encoding="utf8") as file:
            file.write("Lorem ipsum")
        self.reporter.template = self.template
        self.reporter.render()
        self.assertTrue(self.reporter.report)

    def test_render_replaces_variable(self):
        content = "bla {{ blub }}"
        with open(self.template, "w+", encoding="utf8") as file:
            file.write(content)
        self.reporter.template = self.template
        self.reporter.context = {"blub": "foobar"}
        self.reporter.render()
        self.assertEqual("bla foobar", self.reporter.report)

    def test_save_without_filename_raises(self):
        with self.assertRaisesRegex(
            ValueError, "No output filename provided"
        ):
            self.reporter.save()

    def test_save_with_filename_writes_file(self):
        self.reporter.filename = self.filename
        self.reporter.save()
        self.assertTrue(os.path.exists(self.filename))

    def test_report_replaces_variable_and_saves_report(self):
        content = "bla {{ blub }}"
        with open(self.template, "w+", encoding="utf8") as file:
            file.write(content)
        self.reporter.template = self.template
        self.reporter.filename = self.filename
        self.reporter.context = {"blub": "foobar"}
        self.reporter.create()
        self.assertTrue(os.path.exists(self.filename))
        with open(self.filename, "r", encoding="utf8") as file:
            report_content = file.read()
        self.assertEqual("bla foobar", report_content)

    def test_render_sets_template_dir_in_context(self):
        with open(self.template2, "w+") as f:
            f.write("")
        self.reporter.template = self.template2
        self.reporter.render()
        self.assertEqual(
            os.path.split(self.reporter.template)[0] + os.path.sep,
            self.reporter.context["template_dir"],
        )

    def test_render_sets_timestamp_in_context(self):
        with open(self.template, "w+") as f:
            f.write("")
        self.reporter.template = self.template
        self.reporter.render()
        self.assertEqual(
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            self.reporter.context["timestamp"],
        )


class TestGenericEnvironment(unittest.TestCase):
    def setUp(self):
        self.environment = report.GenericEnvironment()

    def test_instantiate_class(self):
        pass

    def test_has_filesystem_and_package_loader(self):
        # noinspection PyUnresolvedReferences
        self.assertIsInstance(
            self.environment.loader.loaders[0],
            jinja2.FileSystemLoader,
        )
        # noinspection PyUnresolvedReferences
        self.assertIsInstance(
            self.environment.loader.loaders[1],
            jinja2.PackageLoader,
        )

    def test_has_correct_loader_path(self):
        path = "templates/report"
        # noinspection PyUnresolvedReferences
        self.assertEqual(
            path, self.environment.loader.loaders[-1].package_path
        )


class TestLaTeXEnvironment(unittest.TestCase):
    def setUp(self):
        self.environment = report.LaTeXEnvironment()

    def test_instantiate_class(self):
        pass

    def test_has_filesystem_and_package_loader(self):
        # noinspection PyUnresolvedReferences
        self.assertIsInstance(
            self.environment.loader.loaders[0],
            jinja2.FileSystemLoader,
        )
        # noinspection PyUnresolvedReferences
        self.assertIsInstance(
            self.environment.loader.loaders[1],
            jinja2.PackageLoader,
        )

    def test_has_correct_loader_path(self):
        path = "templates/report/latex"
        # noinspection PyUnresolvedReferences
        self.assertEqual(
            path, self.environment.loader.loaders[-1].package_path
        )


class TestLaTeXReporter(unittest.TestCase):
    def setUp(self):
        self.reporter = report.LaTeXReporter()
        self.template = "test_template.tex"
        self.filename = "test_report.tex"
        self.result = "test_report.pdf"
        self.include = "include.tex"
        self.bibtex_file = "literature.bib"

    def tearDown(self):
        if os.path.exists(self.template):
            os.remove(self.template)
        if os.path.exists(self.filename):
            os.remove(self.filename)
        if os.path.exists(self.result):
            os.remove(self.result)
        if os.path.exists(self.include):
            os.remove(self.include)
        if os.path.exists(self.bibtex_file):
            os.remove(self.bibtex_file)

    def test_instantiate_class(self):
        pass

    def test_environment_is_latex_environment(self):
        self.assertTrue(
            isinstance(self.reporter._environment, report.LaTeXEnvironment)
        )

    def test_compile_with_not_existing_latex_executable_raises(self):
        self.reporter.latex_executable = "foo"
        message = r"LaTeX executable \w* not found"
        with self.assertRaisesRegex(FileNotFoundError, message):
            self.reporter.compile()

    def test_compile_with_not_existing_bibtex_executable_raises(self):
        self.reporter.bibtex_executable = "foo"
        message = r"BibTeX executable \w* not found"
        with self.assertRaisesRegex(FileNotFoundError, message):
            self.reporter.compile()

    def test_compile_creates_output(self):
        template_content = (
            "\\documentclass{article}"
            "\\begin{document}"
            "test"
            "\\end{document}"
        )
        with open(self.template, "w+") as f:
            f.write(template_content)
        self.reporter.template = self.template
        self.reporter.filename = self.filename
        self.reporter.render()
        self.reporter.save()
        with contextlib.redirect_stdout(io.StringIO()):
            self.reporter.compile()
        self.assertTrue(os.path.exists(self.result))

    def test_compile_with_includes_creates_output(self):
        include_name, _ = os.path.splitext(self.include)
        template_content = (
            "\\documentclass{article}"
            "\\begin{document}"
            "\\include{" + include_name + "}"
            "\\end{document}"
        )
        with open(self.template, "w+") as f:
            f.write(template_content)
        include_content = "foobar"
        with open(self.include, "w+") as f:
            f.write(include_content)
        self.reporter.includes.append(self.include)
        self.reporter.template = self.template
        self.reporter.filename = self.filename
        self.reporter.render()
        self.reporter.save()
        with contextlib.redirect_stdout(io.StringIO()):
            self.reporter.compile()
        self.assertTrue(os.path.exists(self.result))

    def test_compile_does_not_leave_temp_files(self):
        template_content = (
            "\\documentclass{article}"
            "\\begin{document}"
            "test"
            "\\end{document}"
        )
        with open(self.template, "w+") as f:
            f.write(template_content)
        self.reporter.template = self.template
        self.reporter.filename = self.filename
        self.reporter.render()
        self.reporter.save()
        with contextlib.redirect_stdout(io.StringIO()):
            self.reporter.compile()
        basename, _ = os.path.splitext(self.result)
        logfile = ".".join([basename, "log"])
        self.assertFalse(os.path.exists(logfile))

    def test_render_with_template_from_package(self):
        self.reporter.template = "base.tex"
        self.reporter.context = {}
        self.reporter.filename = self.filename
        self.reporter.create()

    @unittest.skip("LaTeX runs take too long...")
    def test_compile_with_bibtex_creates_bibliography(self):
        include_name, _ = os.path.splitext(self.include)
        template_content = (
            "\\documentclass{article}"
            "\\usepackage{biblatex}"
            "\\addbibresource{literature.bib}"
            "\\begin{document}"
            "\\cite{ocdb}"
            "\\printbibliography"
            "\\end{document}"
        )
        with open(self.template, "w+") as f:
            f.write(template_content)
        bibtex_content = (
            "@software{ocdb,"
            "   author = {Till Biskup},"
            "   title = {ocdb Python package},"
            "   url = {https://pypi.org/project/ocdb/},"
            "   doi = {10.5281/zenodo.1233456789}"
            "}"
        )
        with open(self.bibtex_file, "w+") as f:
            f.write(bibtex_content)
        self.reporter.bibtex_executable = "biber"
        self.reporter.includes.append(self.bibtex_file)
        self.reporter.template = self.template
        self.reporter.filename = self.filename
        self.reporter.render()
        self.reporter.save()
        with contextlib.redirect_stdout(io.StringIO()):
            self.reporter.compile()
        self.assertTrue(os.path.exists(self.result))


@unittest.skip("LaTeX runs take too long...")
class TestMaterialReporter(unittest.TestCase):
    def setUp(self):
        self.reporter = report.MaterialReporter()
        collection = ocdb.management.CollectionCreator().create(
            name="elements"
        )
        self.material = collection.Ta
        self.figure_filename = f"{self.material.symbol}.pdf"
        self.bibliography_filename = f"{self.material.symbol}.bib"
        self.report_filename = f"{self.material.symbol}-report.tex"
        self.report_pdf = f"{self.material.symbol}-report.pdf"

    def tearDown(self):
        if os.path.exists(self.figure_filename):
            os.remove(self.figure_filename)
        if os.path.exists(self.bibliography_filename):
            os.remove(self.bibliography_filename)
        if os.path.exists(self.report_filename):
            os.remove(self.report_filename)
        if os.path.exists(self.report_pdf):
            os.remove(self.report_pdf)

    def test_instantiate_class(self):
        pass

    def test_create_sets_reporter(self):
        self.reporter.material = self.material
        with contextlib.redirect_stdout(io.StringIO()):
            self.reporter.create()
        self.assertTrue(self.reporter.reporter)

    def test_create_with_unknown_output_format_raises(self):
        self.reporter.material = self.material
        self.reporter.output_format = "unknown"
        with self.assertRaisesRegex(ValueError, r"Output format \w+ unknown"):
            self.reporter.create()

    def test_create_without_material_raises(self):
        with self.assertRaisesRegex(ValueError, "No material to report on"):
            self.reporter.create()

    def test_create_creates_plot(self):
        self.reporter.material = self.material
        with contextlib.redirect_stdout(io.StringIO()):
            self.reporter.create()
        self.assertTrue(os.path.exists(self.figure_filename))

    def test_create_creates_bibliography(self):
        self.reporter.material = self.material
        with contextlib.redirect_stdout(io.StringIO()):
            self.reporter.create()
        self.assertTrue(os.path.exists(self.bibliography_filename))

    def test_create_fills_bibliography(self):
        self.reporter.material = self.material
        with contextlib.redirect_stdout(io.StringIO()):
            self.reporter.create()
        with open(self.bibliography_filename) as file:
            bibliography = file.read()
        self.assertIn(self.material.references[0].key, bibliography)

    def test_create_creates_report(self):
        self.reporter.material = self.material
        with contextlib.redirect_stdout(io.StringIO()):
            self.reporter.create()
        self.assertTrue(os.path.exists(self.report_filename))

    def test_create_compiles_report(self):
        self.reporter.material = self.material
        with contextlib.redirect_stdout(io.StringIO()):
            self.reporter.create()
        self.assertTrue(os.path.exists(self.report_pdf))
