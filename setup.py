# -*- coding: utf-8 -*-

"""
vip (Virtual Python) is a simple library that makes your python and pip aware
of existing virtualenv underneath. In its design, it is inspired by Git and its
way of handling its repositories.
"""

import sys
import os

from setuptools import setup, find_packages

def get_version():
    basedir = os.path.dirname(__file__)
    with open(os.path.join(basedir, 'vip/__init__.py')) as f:
        VERSION = None
        exec(f.read())
        return VERSION
    raise RuntimeError('No version info found.')

setup(
    name='vip',
    version=get_version(),
    url='https://github.com/dejw/vip/',
    license='BSD',
    author='Dawid Fatyga',
    author_email='dawid.fatyga@gmail.com',
    description='vip is a simple library that makes your python aware of existing virtualenv underneath.',
    long_description=__doc__,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=["virtualenv==1.7"],
    scripts=['bin/vip'],
    classifiers=[
        # http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 1 - Planning',
        #'Development Status :: 2 - Pre-Alpha',
        #'Development Status :: 3 - Alpha',
        #'Development Status :: 4 - Beta',
        #'Development Status :: 5 - Production/Stable',
        #'Development Status :: 6 - Mature',
        #'Development Status :: 7 - Inactive',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX',
        'Operating System :: MacOS',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities'
    ]
)