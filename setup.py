config = {
  "name": "biblicity_net",
  "version": "0.3.1",
  "description": "Python web application for biblicity.net",
  "url": "",
  "author": "Sean Harrison",
  "author_email": "sah@bookgenesis.com",
  "license": "LGPL 3.0",
  "classifiers": [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: Mozilla Public License verson 2.0 (MPL2)",
    "Programming Language :: Python :: 3"
  ],
  "entry_points": {},
  "install_requires": ['bl', 'bxml', 'bsql', 'bweb', 'tornado', 'bcrypt', 'passlib', 'psycopg2', 'Markdown'],
  "extras_require": {
    "dev": [],
    "test": []
  },
  "package_data": {
    "": []
    },
  "data_files": [],
  "scripts": []
}

import os, json
from setuptools import setup, find_packages
from codecs import open

path = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(path, 'README.md'), encoding='utf-8') as f:
    read_me = f.read()

setup(
    long_description=read_me,
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    **config
)
