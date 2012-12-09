# -*- coding: utf-8 -*-

import its
try:
    from mox3 import mox
except ImportError:
    if its.py3:
        raise
    import mox

try:
    import unittest2 as unittest
except ImportError:
    if its.py2 and not its.py27:
        raise
    import unittest
