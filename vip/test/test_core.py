# -*- coding: utf-8 -*-

import mox
import subprocess

try:
    import unittest2 as unittest
except ImportError:
    import unittest


from os import path

from vip import core


class EndsWith(mox.Comparator):

    def __init__(self, pattern):
        self._pattern = pattern

    def equals(self, rhs):
        return isinstance(rhs, basestring) and rhs.endswith(self._pattern)

    def __repr__(self):
        return "<EndsWith %r>" % (self._pattern)


class TestVipDirectoryFinder(unittest.TestCase):

    def setUp(self):
        # On Windows, dirname(__file__) would return a path to the folder
        # that uses the alternative seperators. (C:/path/to/dir) For the
        # purpose of this test, though, we want to use the OS's native file
        # paths.
        self.root = path.normpath(path.dirname(__file__))

    def test_should_return_absolute_path_to_vip_directory(self):
        start = path.join(self.root, "fixtures", "test1", "..",
                          "test1")

        directory = core.find_vip_directory(start=start)

        self.assertEqual(path.abspath(path.join(start, ".vip")), directory)

    def test_should_skip_vip_which_is_no_directory(self):
        root = path.join(self.root, "fixtures", "test2")

        directory = core.find_vip_directory(start=path.join(root,
                                                            "with_plain_file"))
        expected = path.abspath(path.join(root, ".vip"))
        self.assertEqual(expected, directory)

    def test_should_raise_VipError_when_no_vip_is_found(self):
        root = path.join(self.root, "fixtures", "test3")

        with self.assertRaisesRegexp(core.VipError, "not a virtualenv"):
            core.find_vip_directory(start=root)


@unittest.skipUnless(core.is_win, "Windows-specific test")
class TestWindowsVipDirectoryFinder(TestVipDirectoryFinder):

    def setUp(self):
        # Because no Windows path can contain the \ character,
        # replacing all \'s characters with / will only change
        # the separator
        super(TestWindowsVipDirectoryFinder, self).setUp()
        self.root = self.root.replace(path.sep, path.altsep)


class TestCommandExecution(unittest.TestCase):

    def setUp(self):
        self.mox = mox.Mox()

        self.mox.StubOutWithMock(subprocess, "Popen")

        self.popen_mock = self.mox.CreateMockAnything("popen")
        self.popen_mock.stdin = self.mox.CreateMockAnything("stdin")

        # Assert that stdin is closed
        self.popen_mock.stdin.close()

        # OS-specific stuff.
        casedir = "test4" if core.is_win else "test1"
        bindir = "Scripts" if core.is_win else "bin"

        # See TestVipDirectoryFinder for the reason behind the normpath call.
        dirname = path.normpath(path.dirname(__file__))
        vip_dir_parts = [casedir, ".vip"]
        self.vip_dir = path.join(dirname, "fixtures", *vip_dir_parts)

        command = path.sep.join(vip_dir_parts + [bindir, "command"])
        (subprocess
            .Popen([EndsWith(command), "-arg", "123"],
                   stdout=mox.IgnoreArg(), stderr=mox.IgnoreArg(),
                   stdin=subprocess.PIPE)
            .AndReturn(self.popen_mock))

    def tearDown(self):
        self.mox.ResetAll()
        self.mox.UnsetStubs()

    def test_should_raise_VipError_when_command_is_not_found(self):
        missing = path.sep.join(["missing", ".vip"])
        with self.assertRaisesRegexp(core.VipError, "not found"):
            core.execute_virtualenv_command(missing, "command", [])

    def test_should_call_command(self):
        self.popen_mock.communicate()
        self.mox.ReplayAll()

        core.execute_virtualenv_command(self.vip_dir, "command",
                                        ["-arg", "123"])

        self.mox.VerifyAll()

    def test_should_raise_VipError_when_CalledProcessError_is_found(self):
        (self.popen_mock.communicate()
            .AndRaise(subprocess.CalledProcessError(1, "error")))
        self.mox.ReplayAll()

        with self.assertRaises(core.VipError):
            core.execute_virtualenv_command(self.vip_dir, "command",
                                            ["-arg", "123"])

        self.mox.VerifyAll()
