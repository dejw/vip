# -*- coding: utf-8 -*-

import sys

from .test.test_helper import mox
from .test.test_helper import unittest

from . import req


class TestGetRequirementsFilenames(unittest.TestCase):

    def test_empty(self):
        names = list(req.get_requirements_filenames(prefix='', version=''))

        self.assertEqual(['requirements.txt'], names)

    def test_prefix_and_version(self):
        names = list(req.get_requirements_filenames(prefix='devel',
                     version=(2, 7, 3)))

        self.assertEqual([
            'requirements.txt',
            'requirements-2.txt',
            'requirements-27.txt',
            'requirements-273.txt',
            'devel-requirements.txt',
            'devel-requirements-2.txt',
            'devel-requirements-27.txt',
            'devel-requirements-273.txt',
        ], names)

    def test_no_prefix(self):
        names = list(req.get_requirements_filenames(version=(2, 7, 3)))

        self.assertEqual([
            'requirements.txt',
            'requirements-2.txt',
            'requirements-27.txt',
            'requirements-273.txt',
        ], names)

    def test_version_info(self):
        names = list(req.get_requirements_filenames(prefix='prod',
                     version=sys.version_info))

        self.assertIn('requirements.txt', names)
        self.assertIn('requirements-%s.txt' % sys.version_info.major, names)

        self.assertIn('prod-requirements.txt', names)
        self.assertIn('prod-requirements-%s.txt' % sys.version_info.major,
                      names)

    def test_version_as_str(self):
        names = list(req.get_requirements_filenames(version="2.1"))

        self.assertEqual([
            'requirements.txt',
            'requirements-2.txt',
            'requirements-21.txt',
        ], names)

    def test_source_dir(self):
        names = list(req.get_requirements_filenames(source_dir="/tmp",
                     version="2"))

        self.assertEqual([
            '/tmp/requirements.txt',
            '/tmp/requirements-2.txt',
        ], names)


if __name__ == '__main__':
    unittest.main()
