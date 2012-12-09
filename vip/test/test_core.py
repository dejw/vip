# -*- coding: utf-8 -*-

from __future__ import absolute_import

import os
import signal
import subprocess

from os import path

from .test_helper import mox
from .test_helper import unittest

from vip import core


class EndsWith(mox.Comparator):

    def __init__(self, pattern):
        self._pattern = pattern

    def equals(self, rhs):
        return hasattr(rhs, 'endswith') and rhs.endswith(self._pattern)

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
        root = '/tmp'

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
        case_dir = "test4" if core.is_win else "test1"
        bin_dir = "Scripts" if core.is_win else "bin"

        # See TestVipDirectoryFinder for the reason behind the normpath call.
        dirname = path.normpath(path.dirname(__file__))
        vip_dir_parts = [case_dir, ".vip"]
        self.vip_dir = path.join(dirname, "fixtures", *vip_dir_parts)

        command = path.sep.join(vip_dir_parts + [bin_dir, "command"])
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
        self.popen_mock.poll().AndReturn(0)
        self.mox.ReplayAll()

        core.execute_virtualenv_command(self.vip_dir, "command",
                                        ["-arg", "123"])

        self.mox.VerifyAll()

    def test_should_raise_VipError_when_CalledProcessError_is_found(self):
        (self.popen_mock.communicate()
            .AndRaise(subprocess.CalledProcessError(1, "error")))
        self.popen_mock.poll().AndReturn(127)
        self.mox.ReplayAll()

        with self.assertRaises(core.VipError):
            core.execute_virtualenv_command(self.vip_dir, "command",
                                            ["-arg", "123"])

        self.mox.VerifyAll()

    def test_should_propagate_status_code(self):
        self.popen_mock.communicate()
        self.popen_mock.poll().AndReturn(123)
        self.popen_mock.returncode = 123
        self.mox.ReplayAll()

        code = core.execute_virtualenv_command(self.vip_dir, 'command',
                                               ["-arg", "123"])

        self.mox.VerifyAll()
        self.assertEqual(123, code)

    def test_should_propagate_SIGINT(self):
        self.popen_mock.communicate().AndRaise(KeyboardInterrupt())
        self.popen_mock.poll().AndReturn(None)
        self.popen_mock.terminate()
        self.mox.ReplayAll()

        code = core.execute_virtualenv_command(self.vip_dir, 'command',
                                               ["-arg", "123"])

        self.mox.VerifyAll()


@unittest.skipUnless(core.is_win, "Windows-specific test")
class TestWindowsFindExecutable(unittest.TestCase):

    def setUp(self):
        dirname = path.normpath(path.dirname(__file__))
        self.bin_dir = path.join(dirname, "fixtures", "test5", ".vip",
                                 "Scripts")
        self.exec_ext = '.bat'

    def test_should_return_best_valid_executable(self, exe=None,
                                                 expected=None):
        if exe is None:
            base_exe = path.join(self.bin_dir,
                                 "command_with_better_executable")
        else:
            base_exe = path.join(self.bin_dir, exe)

        if expected is None:
            expected = base_exe + self.exec_ext
        else:
            expected = path.join(self.bin_dir, expected)

        exe_path = core.find_windows_executable(base_exe)

        self.assertEqual(expected, exe_path)
        self.assertTrue(path.exists(expected) and path.isfile(expected))

    def test_should_return_valid_path_with_executable_extension(self):
        cmd = "command_with_executable_ext" + self.exec_ext
        self.test_should_return_best_valid_executable(cmd, cmd)

    def test_should_return_valid_path_to_executable_with_extension(self):
        self.test_should_return_best_valid_executable("command_with_ext")

    def test_should_return_valid_path_to_executable_without_extension(self):
        self.test_should_return_best_valid_executable("command_without_ext",
                                                      "command_without_ext")

    def test_should_raise_VipError_when_no_executable_is_found(self):
        base_exe = path.join(self.bin_dir, "missing")

        with self.assertRaisesRegexp(core.VipError, "not found"):
            core.find_windows_executable(base_exe)
