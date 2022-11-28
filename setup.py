j   """
automerge
-------------

auto merge GitHub PRs
"""
import versioneer

from os import path
from setuptools import setup, find_packages

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

with open("requirements/production.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="automerge",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description="automerge GitHub PRs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="http://github.com/abmamo/automerge",
    author="Abenezer Mamo",
    author_email="hi@abenezer.sh",
    license="MIT",
    packages=find_packages(exclude=("tests", "venv", "env")),
    install_requires=requirements,
    zip_safe=False,
    py_modules=["automerge"],
    entry_points={
        "console_scripts": [
            "automerge = automerge:cli",
        ],
    },
)
