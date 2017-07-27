import sys

from setuptools import find_packages, setup

from pymmonit import __version__, __author__

setup(name='PyMMonit',
      version=__version__,
      description='MMonit API wrapper written in Python',
      author=__author__,
      author_email='javier.palomo.almena@gmail.com',
      url='https://github.com/jthacker/PyMMonit',
      license='GPLv3',
      packages=find_packages(),
      install_requires=['requests >= 2.18.0'])
