import contextlib
import io
import os
import unittest

import jinja2

from ocdb import report


class TestReporter(unittest.TestCase):
    def setUp(self):
        self.reporter = report.Reporter()
        self.template = "test_template.j2"
        self.filename = "test_report.txt"

    def tearDown(self):
        if os.path.exists(self.template):
            os.remove(self.template)
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
            report = file.read()
        self.assertEqual("bla foobar", report)


class TestGenericEnvironment(unittest.TestCase):
    def setUp(self):
        self.environment = report.GenericEnvironment()

    def test_instantiate_class(self):
        pass

    def test_has_filesystem_and_package_loader(self):
        self.assertIsInstance(
            self.environment.loader.loaders[0],
            jinja2.FileSystemLoader,
        )
        self.assertIsInstance(
            self.environment.loader.loaders[1],
            jinja2.PackageLoader,
        )

    def test_has_correct_loader_path(self):
        path = "templates/report"
        self.assertEqual(
            path, self.environment.loader.loaders[-1].package_path
        )


class TestLaTeXEnvironment(unittest.TestCase):
    def setUp(self):
        self.environment = report.LaTeXEnvironment()

    def test_instantiate_class(self):
        pass

    def test_has_filesystem_and_package_loader(self):
        self.assertIsInstance(
            self.environment.loader.loaders[0],
            jinja2.FileSystemLoader,
        )
        self.assertIsInstance(
            self.environment.loader.loaders[1],
            jinja2.PackageLoader,
        )

    def test_has_correct_loader_path(self):
        path = "templates/report/latex"
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

    def tearDown(self):
        if os.path.exists(self.template):
            os.remove(self.template)
        if os.path.exists(self.filename):
            os.remove(self.filename)
        if os.path.exists(self.result):
            os.remove(self.result)
        if os.path.exists(self.include):
            os.remove(self.include)

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
