#!/usr/bin/env python
import distribute_setup
distribute_setup.use_setuptools()

import os
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

from janrain.capture import get_version

setup(
    name = "janrain-python-api",
    version = get_version(),
    description = "Python interface to the Janrain Capture API.",
    long_description = read("README.rst"),
    author = "Micah Carrick",
    author_email = "micah@janrain.com",
    url = "http://developers.janrain.com/",
    packages = find_packages(),
    namespace_packages = ["janrain"],
    scripts=[os.path.join("bin", script) for script in os.listdir("./bin")],
    package_data={
        'janrain.capture.test': ["janrain-config"]
    },
    #license = "",
    classifiers = [
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP",
        "License :: OSI Approved :: MIT License"
    ],
    test_suite = "janrain.capture.test",
    use_2to3 = True,
    install_requires = [
        'requests',
        'pyyaml',
    ],
    setup_requires=[
        'Nose',
    ],
)
