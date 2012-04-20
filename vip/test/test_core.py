# -*- coding: utf-8 -*-

import unittest

from os import path

from vip import core


class TestVipDirectoryFinder(unittest.TestCase):

    def test_should_return_absolute_path_to_vip_directory(self):
        start = path.join(path.dirname(__file__), "fixtures", "test1", "..", "test1")

        directory = core.find_vip_directory(start=start)

        self.assertEqual(path.abspath(path.join(start, ".vip")), directory)

    def test_should_skip_vip_which_is_no_directory(self):
        start = path.join(path.abspath(__file__), "fixtures", "test_fail")

        with self.assertRaisesRegexp(core.VipError, "not a virtualenv"):
            core.find_vip_directory(start=start)


if __name__ == "__main__":
    unittest.main()