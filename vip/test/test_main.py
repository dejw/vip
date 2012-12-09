# -*- coding: utf-8 -*-

import os
import signal
import subprocess

from os import path

from .test_helper import mox
from .test_helper import unittest


class TestMain(unittest.TestCase):

    def test_import(self):
        from vip import main

if __name__ == '__main__':
    unittest.main()
