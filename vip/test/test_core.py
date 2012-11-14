# -*- coding: utf-8 -*-

import mox
import subprocess

try:
    import unittest2 as unittest
except ImportError:
    import unittest


from os import path, name as osname

from vip import core


class EndsWith(mox.Comparator):

    def __init__(self, pattern):
        self._pattern = pattern

    def equals(self, rhs):
        return isinstance(rhs, basestring) and rhs.endswith(self._pattern)

    def __repr__(self):
        return "<EndsWith %r>" % (self._pattern)


class TestVipDirectoryFinder(unittest.TestCase):

    def test_should_return_absolute_path_to_vip_directory(self):
        start = path.join(path.dirname(__file__), "fixtures", "test1", "..",
                          "test1")

        directory = core.find_vip_directory(start=start)

        self.assertEqual(path.abspath(path.join(start, ".vip")), directory)

    def test_should_skip_vip_which_is_no_directory(self):
        root = path.join(path.dirname(__file__), "fixtures", "test2")

        directory = core.find_vip_directory(start=path.join(root,
                                                            "with_plain_file"))
        expected = path.abspath(path.join(root, ".vip"))
        self.assertEqual(expected, directory)

    def test_should_raise_VipError_when_no_vip_is_found(self):
        root = path.join(path.dirname(__file__), "fixtures", "test3")

        with self.assertRaisesRegexp(core.VipError, "not a virtualenv"):
            core.find_vip_directory(start=root)


if osname == 'nt':
    class TestWindowsVipDirectoryFinder(unittest.TestCase):

        def setUp(self):
            drive, folderpath = path.splitdrive(
                path.abspath(path.dirname(__file__)))

            # The test root folder with a backslash following the drive letter.
            # In normal circumstances, C:\
            self.rootbs = path.join(drive, '\\' + folderpath[1:])
            # The test root folder with a slash following the drive letter.
            # In normal circumstances, C:/
            self.rootfs = path.join(drive, '/' + folderpath[1:])

        def test_should_return_absolute_path_to_vip_directory_backslash(self):
            start = path.join(self.rootbs, "fixtures", "test1", "..", "test1")

            directory = core.find_vip_directory(start=start)

            self.assertEqual(path.abspath(path.join(start, ".vip")), directory)

        def test_should_return_absolute_path_to_vip_directory_slash(self):
            start = path.join(self.rootfs, "fixtures", "test1", "..", "test1")

            directory = core.find_vip_directory(start=start)

            self.assertEqual(path.abspath(path.join(start, ".vip")), directory)

        def test_should_skip_vip_which_is_no_directory_backslash(self):
            root = path.join(self.rootbs, "fixtures", "test2")
            start = path.join(root, "with_plain_file")
            directory = core.find_vip_directory(start=start)
            vip_folder = path.abspath(path.join(root, ".vip"))
            self.assertEqual(vip_folder, directory)

        def test_should_skip_vip_which_is_no_directory_slash(self):
            root = path.join(self.rootfs, "fixtures", "test2")
            start = path.join(root, "with_plain_file")
            directory = core.find_vip_directory(start=start)
            vip_folder = path.abspath(path.join(root, ".vip"))
            self.assertEqual(vip_folder, directory)

        def test_should_raise_VipError_when_no_vip_is_found_backslash(self):
            root = path.join(self.rootbs, "fixtures", "test3")

            with self.assertRaisesRegexp(core.VipError, "not a virtualenv"):
                core.find_vip_directory(start=root)

        def test_should_raise_VipError_when_no_vip_is_found_slash(self):
            root = path.join(self.rootfs, "fixtures", "test3")

            with self.assertRaisesRegexp(core.VipError, "not a virtualenv"):
                core.find_vip_directory(start=root)

    class TestWindowsCommandExecution(unittest.TestCase):

        def setUp(self):
            self.mox = mox.Mox()

            self.mox.StubOutWithMock(subprocess, "Popen")

            self.popen_mock = self.mox.CreateMockAnything("popen")
            self.popen_mock.stdin = self.mox.CreateMockAnything("stdin")

            # Assert that stdin is closed
            self.popen_mock.stdin.close()

            dirname = path.dirname(__file__)
            self.vip_dir = path.join(dirname, "fixtures", "test4", ".vip")
            command = "test4\\.vip\\Scripts\\command"
            (subprocess
                .Popen([EndsWith(command), "-arg", "123"],
                       stdout=mox.IgnoreArg(), stderr=mox.IgnoreArg(),
                       stdin=subprocess.PIPE)
                .AndReturn(self.popen_mock))

        def tearDown(self):
            self.mox.ResetAll()
            self.mox.UnsetStubs()

        def test_should_raise_VipError_when_command_is_not_found(self):

            with self.assertRaisesRegexp(core.VipError, "not found"):
                core.execute_virtualenv_command("missing\\.vip", "command", [])

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
else:
    class TestCommandExecution(unittest.TestCase):

        def setUp(self):
            self.mox = mox.Mox()

            self.mox.StubOutWithMock(subprocess, "Popen")

            self.popen_mock = self.mox.CreateMockAnything("popen")
            self.popen_mock.stdin = self.mox.CreateMockAnything("stdin")

            # Assert that stdin is closed
            self.popen_mock.stdin.close()

            dirname = path.dirname(__file__)
            self.vip_dir = path.join(dirname, "fixtures", "test1", ".vip")

            (subprocess
                .Popen([EndsWith("test1/.vip/bin/command"), "-arg", "123"],
                       stdout=mox.IgnoreArg(), stderr=mox.IgnoreArg(),
                       stdin=subprocess.PIPE)
                .AndReturn(self.popen_mock))

        def tearDown(self):
            self.mox.ResetAll()
            self.mox.UnsetStubs()

        def test_should_raise_VipError_when_command_is_not_found(self):

            with self.assertRaisesRegexp(core.VipError, "not found"):
                core.execute_virtualenv_command("missing/.vip", "command", [])

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
