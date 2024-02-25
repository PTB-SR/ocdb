import os
import setuptools


def read(filename):
    with open(os.path.join(os.path.dirname(__file__), filename)) as file:
        content = file.read()
    return content


setuptools.setup(
    name="ocdb",
    version=read("VERSION").strip(),
    description="Optical constants for elements and various materials in "
    "the EUV and VUV wavelengths",
    long_description=read("README.rst"),
    long_description_content_type="text/x-rst",
    author="Till Biskup",
    author_email="till.biskup@ptb.de",
    url="https://www.ocdb.ptb.de/",
    project_urls={
        "Documentation": "https://ocdb-data.readthedocs.io/",
        "Source": "https://github.com/PTB-SR/ocdb",
    },
    packages=setuptools.find_packages(exclude=("tests", "docs")),
    license="GPLv3",
    keywords=[
        "optical constants",
        "EUV",
        "VUV",
        "reflectometry",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Development Status :: 4 - Beta",
    ],
    install_requires=[
        "bibrecord>=0.2.2",
        "numpy",
        "oyaml",
    ],
    extras_require={
        "presentation": [
            "matplotlib",
            "jinja2",
        ],
        "dev": [
            "prospector",
            "pyroma",
            "bandit",
            "black",
            "pymetacode",
        ],
        "docs": [
            "sphinx",
            "sphinx-rtd-theme",
            "sphinx_multiversion",
        ],
        "deployment": [
            "build",
            "twine",
        ],
    },
    python_requires=">=3.9",
    include_package_data=True,
)
