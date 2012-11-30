# -*- coding: utf-8 -*-

import os
import subprocess
import logging
import sys
import StringIO
import virtualenv

from os import path

VIP_DIRECTORY = ".vip"
REQUIREMENTS_FILENAME = 'requirements.txt'

is_win = sys.platform.startswith("win")


class _Logger(object):
    def __init__(self):
        self._logger = logging.getLogger(__name__)
        self._logger.addHandler(logging.StreamHandler())
        self._logger.setLevel(logging.INFO)

    def exception(self, *args, **kwargs):
        if self.verbose:
            self._logger.exception(*args, **kwargs)
        else:
            self.error(*args, **kwargs)

    def __getattr__(self, name):
        return getattr(self._logger, name)


logger = _Logger()


class VipError(StandardError):
    pass


def is_exe(fpath):
    return path.isfile(fpath) and os.access(fpath, os.X_OK)


def find_vip_directory(start="."):
    """ Finds the `.vip` directory up in the directory tree.

    Args:
        start: str directory name from where the search is started

    Returns:
        An absolute path to `.vip` directory.

    Raises:
        VipError: when no `.vip` directory has been found to the root.
    """
    directory, head = path.abspath(start), None

    while (directory != "/" and directory[1:] != ':\\'
           and directory[1:] != ':/') or head:
        vip_directory = path.join(directory, VIP_DIRECTORY)

        if path.exists(vip_directory) and path.isdir(vip_directory):
            return vip_directory

        directory, head = path.split(directory)

    raise VipError(
        "not a virtualenv (or any of the parent directories): %s" % start)


def create_virtualenv(directory=".", install_requirements=True):
    """ Creates an virtualenv in given directory

    Returns:
        A path to directory containing virtualenv

    Raises:
        VipError: when installation cannot be finished
    """

    try:
        vip_directory = find_vip_directory(directory)
    except VipError:
        vip_directory = path.abspath(path.join(directory, ".vip"))

    # TODO: allow to pass additional flags to virtualenv tool
    if not path.exists(vip_directory):
        virtualenv.create_environment(vip_directory)

    else:
        logger.warning("Found %s directory, assuming it is "
                       "a virtualenv" % vip_directory)

    # Let's assume that if .vip is directory it is also our virtualenv
    if path.exists(vip_directory) and not path.isdir(vip_directory):
        raise VipError("%s is not a directory" % vip_directory)

    # if requirements.txt exists try to install all packages
    if install_requirements:
        requirements = path.join(directory, REQUIREMENTS_FILENAME)
        if path.exists(requirements) and path.isfile(requirements):
            logger.info("Installing requirements from %s" % requirements)
            execute_virtualenv_command(vip_directory, "pip", ["install", "-r",
                                                              requirements])

    return vip_directory


def find_windows_executable(exe_base):
    """ Given a base filepath, try to resolve the file path to an executable
    on Windows. If the base filepath exists and is a file, we'll return that
    file path only if it has an executable extension, or if no other file
    could be found.

    Args:
        exe_base: str A base filepath. Will return without searching if this
        filepath exists and has an executable file extension.

    Returns:
        The filepath that a Window's shell would resolve, given the base.

    Raises:
        VipError: when no executable can be found.
    """
    ext_val = os.environ["PATHEXT"].lower()\
        if "PATHEXT" in os.environ\
        else ".exe;.cmd;.bat;.py;.pyw"
    path_exts = filter(lambda v: len(v) > 0, [v.strip() for v in ext_val
                                              .split(';')])
    exe_exists = False
    if path.exists(exe_base) and path.isfile(exe_base):
        exe_ext = path.splitext(exe_base)[1].lower()
        if exe_ext in path_exts:
            return exe_base
        else:
            exe_exists = True

    for ext in path_exts:
        exe_path = exe_base + ext
        if path.exists(exe_path) and path.isfile(exe_path):
            return exe_path

    if exe_exists:
        return exe_base
    else:
        raise VipError("%s not found or is not executable" % exe_base)


def execute_virtualenv_command(vip_directory, command, args):
    """ Executes a vip_directory/bin/command executable with given arguments

    Raises:
        VipError: when command is not found or cannot be executed
    """

    if is_win:
        executable_base = path.join(vip_directory, "Scripts", command)
        executable_path = find_windows_executable(executable_base)
    else:
        executable_path = path.join(vip_directory, "bin", command)
        if not path.exists(executable_path) or not is_exe(executable_path):
            raise VipError(
                "%s not found or is not executable" % executable_path)

    try:
        arguments = [executable_path] + args

        p = subprocess.Popen(arguments, stdout=sys.stdout, stderr=sys.stderr,
                             stdin=subprocess.PIPE)
        p.stdin.close()
        p.communicate()
    except subprocess.CalledProcessError as e:
        raise VipError(str(e))
    except KeyboardInterrupt:
        # Ignore keyboard interrupt here
        pass
