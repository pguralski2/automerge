from setuptools import setup, find_packages


# read the contents of README file
from os import path

# get current file directory
this_directory = path.abspath(path.dirname(__file__))
# open README with UTF-8 encoding
with open(path.join(this_directory, "README.md"), encoding="utf-8") as f:
    # read README
    long_description = f.read()

with open("requirements/prod.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="automerge",
    version="0.0.1",
    description="automerge GitHub PRs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="http://github.com/abmamo/automerge",
    author="Abenezer Mamo",
    author_email="contact@abmamo.com",
    license="MIT",
    packages=find_packages(exclude=("tests", "venv", "env")),
    install_requires=requirements,
    zip_safe=False,
    py_modules=['automerge'],
    entry_points={
        'console_scripts': [
            'automerge = automerge:cli',
        ],
    },
)
