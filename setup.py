#!/usr/bin/env python
from setuptools import setup, find_packages
import os
import time


if os.path.exists("VERSION.txt"):
    # this file can be written by CI tools (e.g. Travis)
    with open("VERSION.txt") as version_file:
        version = version_file.read().strip().strip("v")
else:
    version = str(time.time())

setup(
    name='knesset-datapackage',
    version=version,
    description='tools to create downloadable Knesset (Israeli parliament) data packages',
    author='Ori Hoch',
    author_email='ori@uumpa.com',
    license='GPLv3',
    url='https://github.com/hasadna/knesset-data-datapackage',
    packages=find_packages(exclude=["tests", "test.*"]),
    install_requires=['knesset-data', 'datapackage'],
    entry_points={'console_scripts': ['make_knesset_datapackage = knesset_datapackage.cli:make_datapackage']}
)
