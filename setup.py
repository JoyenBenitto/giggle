"""Setup script for Giggle - A modern static site generator."""

import os
from setuptools import setup, find_packages

# Base directory of package
here = os.path.abspath(os.path.dirname(__file__))

def read_requires():
    """Read requirements from requirements.txt."""
    requirements = [
        'click>=8.0.0',
        'Jinja2>=3.0.0',
        'PyYAML>=6.0.0',
        'markdown>=3.4.0',
        'ruamel.yaml>=0.17.0',
        'python-frontmatter>=1.0.0'
    ]
    return requirements

with open("README.md", "r", encoding='utf-8') as fh:
    readme = fh.read()

setup(
    name='giggle',
    version='0.1.0',
    description="A modern static site generator with enhanced configuration management",
    long_description=readme,
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Topic :: Internet :: WWW/HTTP :: Site Management",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="static-site-generator, blog, website, markdown, jinja2",
    url='https://github.com/JoyenBenitto/giggle',
    author="Joyen Benitto",
    author_email='joyen.benitto@gmail.com',
    license="MIT",
    packages=find_packages(include=['giggle', 'giggle.*']),
    package_data={
        'giggle': [
            'constants/jinja_templates/*.jinja',
            'constants/css/*.css',
            'constants/js/*.js'
        ]
    },
    install_requires=read_requires(),
    python_requires=">=3.10",
    entry_points={
        'console_scripts': ['giggle=giggle.main:cli'],
    },
    include_package_data=True,
    zip_safe=False)
