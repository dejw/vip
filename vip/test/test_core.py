# -*- coding: utf-8 -*-

import mox
import subprocess
import unittest

from os import path

from vip import core


class EndsWith(mox.Comparator):

  def __init__(self, pattern):
    self._pattern = pattern

  def equals(self, rhs):
    return isinstance(rhs, basestring) and rhs.endswith(self._pattern)

  def __repr__(self):
    return "<endswith %r>" % (self._pattern)


class TestVipDirectoryFinder(unittest.TestCase):

    def test_should_return_absolute_path_to_vip_directory(self):
        start = path.join(path.dirname(__file__), "fixtures", "test1", "..", "test1")

        directory = core.find_vip_directory(start=start)

        self.assertEqual(path.abspath(path.join(start, ".vip")), directory)

    def test_should_skip_vip_which_is_no_directory(self):
        root = path.join(path.dirname(__file__), "fixtures", "test2")

        directory = core.find_vip_directory(start=path.join(root, "with_plain_file"))

        self.assertEqual(path.join(root, ".vip"), directory)

    def test_should_raise_VipError_when_no_vip_is_found(self):
        root = path.join(path.dirname(__file__), "fixtures", "test3")

        with self.assertRaisesRegexp(core.VipError, "not a virtualenv"):
            core.find_vip_directory(start=root)


class TestCommandExecution(unittest.TestCase):

    def setUp(self):
        self.mox = mox.Mox()

        self.mox.StubOutWithMock(subprocess, "check_call")
        self.subprocess_mock = subprocess

    def tearDown(self):
        self.mox.ResetAll()
        self.mox.UnsetStubs()

    def test_should_raise_VipError_when_command_is_not_found(self):

        with self.assertRaisesRegexp(core.VipError, "not found"):
            core.execute_virtualenv_command("missing/.vip", "command", [])

    def test_should_call_command(self):
        vip_dir = path.join(path.dirname(__file__), "fixtures", "test1", ".vip")
        self.subprocess_mock.check_call(
            [EndsWith("test1/.vip/bin/command"), "-arg", "123"],
            stdout=mox.IgnoreArg(), stderr=mox.IgnoreArg())
        self.mox.ReplayAll()

        core.execute_virtualenv_command(vip_dir, "command", ["-arg", "123"])

        self.mox.VerifyAll()

    def test_should_raise_VipError_when_CalledProcessError_is_encountered(self):
        vip_dir = path.join(path.dirname(__file__), "fixtures", "test1", ".vip")
        (self.subprocess_mock
            .check_call([EndsWith("test1/.vip/bin/command")],
                stdout=mox.IgnoreArg(), stderr=mox.IgnoreArg())
            .AndRaise(subprocess.CalledProcessError(1, "error")))

        self.mox.ReplayAll()

        with self.assertRaises(core.VipError):
            core.execute_virtualenv_command(vip_dir, "command", [])

        self.mox.VerifyAll()


if __name__ == "__main__":
    unittest.main()