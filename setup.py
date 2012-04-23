# -*- coding: utf-8 -*-

import sys
import os


from setuptools import setup, find_packages


with open('requirements.txt') as f:
    requirements = f.read().splitlines()


def get_info():
    import vip
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
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'vip = vip.main:main',
        ]
    },
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
