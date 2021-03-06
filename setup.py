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
import warnings
# from distutils.core import setup, Extension

__version__ = '0.5.0'

__required__ = [
    'numpy>=1.12.1',
    'qimage2ndarray>=1.6',
    'six',
    'lxml',
    'pyyaml',
    'BeautifulTable',
]
required = __required__
try:
    import cv2
    print('Searching for cv2==%s' % cv2.__version__)
    assert LooseVersion(cv2.__version__) >= LooseVersion('2.4.10')
    print('Best match: cv2 %s' % cv2.__version__)
except(ImportError, AssertionError):
    required.append('opencv-python>=2.4.10')

try:
    import PyQt5
    print('Searching for PyQt5')
except(ImportError, AssertionError):
    import sys
    if sys.version_info.major == 3:
        required.append('PyQt5')
    else:
        warnings.warn(
            'Cannot find optional module PyQt5 or python-qt5, you need to install it before you use IMGallery module', ImportWarning)

setup(
    name='senseToolkit',
    version=__version__,
    description='Python functions for convenience',
    author='Toka',
    author_email='fengweitao@sensetime.com',
    url='https://github.com/Helicopt/senseToolkit',
    license='MIT',
    install_requires=required,
    packages=find_packages(),
    ext_modules=[
        Extension('senseTk.extension.functional', sources=[
                  './senseTk/extension/functional/functional.cpp']),
        Extension('senseTk.extension.flow', sources=[
                  './senseTk/extension/flow/flow.cpp']),
    ]
)

if __name__ == '__main__':
    # __author__ == '__toka__'
    pass
