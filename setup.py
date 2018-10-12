#!/usr/bin/python
# -*- coding: utf8 -*-
#########################################################################
# File Name: setup.py
# Author: Toka
# mail: fengweitao@sensetime.com
# Created Time: 2018年07月27日 星期五 11时58分11秒
#########################################################################

from setuptools import setup, find_packages, Extension
from distutils.version import LooseVersion, StrictVersion
# from distutils.core import setup, Extension

__version__ = '0.4.3'

__required__ = [
            'numpy>=1.12.1',
            'qimage2ndarray>=1.6'
        ]
required = __required__
try:
    import cv2
    print 'Searching for cv2==%s'%cv2.__version__
    assert LooseVersion(cv2.__version__)>=LooseVersion('2.4.10')
    print 'Best match: cv2 %s'%cv2.__version__
except ImportError, AssertionError:
    required.append('cv2>=2.4.10')

setup(
    name = 'senseToolkit',
    version = __version__,
    description = 'Python functions for CV process',
    author = 'Toka',
    url = 'https://github.com/Helicopt/senseToolkit',
    license = 'MIT',
    install_requires = required,
    packages = find_packages(),
    ext_modules=[Extension('senseTk.extension.functional', sources=['./senseTk/extension/functional/functional.cpp'])]
)

if __name__=='__main__':
    # __author__ == '__toka__'
    pass
