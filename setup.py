# -*- coding: utf-8 -*-

from __future__ import with_statement

import sys
import os

from setuptools import setup, find_packages

import vip

try:
    from deps import find_requirements
except ImportError:
    import urllib
    urllib.urlretrieve('https://raw.github.com/dejw/deps/master/deps.py', 'deps.py')
    from deps import find_requirements


def get_info():
    return vip.VERSION, vip.__doc__.strip()


version, long_description = get_info()


setup(
    name='vip',
    version=version,
    url='https://github.com/dejw/vip/',
    license='BSD',
    author='Dawid Fatyga',
    author_email='dawid.fatyga@gmail.com',
    description='vip is a simple library that makes your python aware of existing virtualenv underneath.',
    long_description=long_description,
    packages=find_packages(),
    zip_safe=False,
    platforms='any',
    install_requires=find_requirements(),
    entry_points={
        'console_scripts': [
            'vip = vip.main:main',
        ]
    },
    use_2to3=True,
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
