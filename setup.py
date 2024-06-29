"""The setup script."""

import os
from setuptools import setup, find_packages

# Base directory of package
here = os.path.abspath(os.path.dirname(__file__))

def read_requires():
    with open(os.path.join(here, "giggle/requirements.txt"),"r") as reqfile:
        return reqfile.read().splitlines()

with open("README.md", "r") as fh:
    readme = fh.read()


setup_requirements = []

test_requirements = []

requirements= read_requires()

setup(
    name='giggle',
    version='0.0.1',
    description="giggle",
    long_description= readme + '\n\n',
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "License :: UNLICENSED",
        "Development Status :: 4 - Beta"
    ],
    keywords = "device_manger",
    url = 'https://github.com/JoyenBenitto/giggle',
    author = "Joyen Benitto",
    author_email = 'joyen.benitto@gmail.com',
    license = "MIT License",
    packages = find_packages(),
    package_dir={'giggle': 'giggle/'},
    package_data={'giggle': ['requirements.txt']},
    install_requires = requirements,
    python_requires = ">=3.10",
    entry_points={
        'console_scripts': ['giggle=giggle.main:cli'],
    },
    include_package_data=True,
    tests_require=[],
    zip_safe=False
)

