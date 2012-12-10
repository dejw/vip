# -*- coding: utf-8 -*-

import itertools
import os
import sys

from pip import req


def get_requirements_filenames(source_dir=None, prefix=None, version=None,
                               extension='txt'):
    """Produces requirements filenames based on prefix and interpreter version.

    Filenames are following pattern:

        [prefix-]?requirements[-version+]?.txt

    For instance, for prefix `devel` and `version` (2, 7, 3) it will produce:

              requirements.txt
              requirements-2.txt
              requirements-27.txt
              requirements-273.txt
        devel-requirements.txt
        devel-requirements-2.txt
        devel-requirements-27.txt
        devel-requirements-273.txt

    Args:
        prefix: str, a prefix for requirements, like 'dev', 'devel', 'prod'
        version: an iterable, with version segments to use, using
            os.version_info by default
        extension: str, what extension to use, 'txt' by default

    Returns:
        a sequence of filenames
    """
    prefixes = ['']

    if prefix:
        prefixes.append('%s-' % prefix)

    version = sys.version_info if version is None else version
    version = [str(v) for v in version if v and v != '.']
    version = [''] + ['-%s' % ''.join(version[:i + 1])
                      for i, v in enumerate(version)]

    for p, v in itertools.product(prefixes, version):
        filename = '%srequirements%s.%s' % (p, v, extension)

        if source_dir:
            filename = os.path.join(source_dir, filename)

        yield filename


def find_requirements(source_dir=None, prefix=None, version=None):
    """Generates requirements based on given prefix and version.

    It works similar to find_packages function. It accepts source_dir argument
    and yields install requiremnets.

    Note that this function will not search for requirement files recursively -
    it expects that all files are in the same directory.

    Args:
        source_dir: a directory where requirement files resides
        prefix: a configuration prefix, like 'devel', 'prod'
        version: what version of python to use, current by default

    Returns:
        a list of requiremnets
    """

    reqs = []

    for filename in get_requirements_filenames(source_dir, prefix, version):
        if os.path.exists(filename):
            for install_req in req.parse_requirements(filename):
                reqs.append(str(install_req.req))

    return reqs
