# -*- coding: utf-8 -*-

import os
import logging
import path
import signal
import StringIO
import subprocess
import sys
import virtualenv


VIP_DIRECTORY = ".vip"
DEFAULT_VIRTUALENV_DIRS = [VIP_DIRECTORY, '.venv']
REQUIREMENTS_FILENAME = 'requirements.txt'


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


def is_exe(p):
    return p.isfile() and p.access(os.X_OK)


def find_vip_directory(start="."):
    """ Finds the `.vip` directory up in the directory tree.

    Args:
        start: str directory name from where the search is started

    Returns:
        An absolute path to `.vip` directory.

    Raises:
        VipError: when no `.vip` directory has been found to the root.
    """
    look_for = set(DEFAULT_VIRTUALENV_DIRS)

    directory = path.path(start).abspath()

    while directory.parent != directory:
        items = os.listdir(directory)
        if any(i in look_for and (directory / i).isdir() for i in items):
            return directory / VIP_DIRECTORY

        directory = directory.parent

    raise VipError(
        "not a virtualenv (or any of the parent directories): %s" % start)


def create_virtualenv(directory=".", install_requirements=True):
    """ Creates an virtualenv in given directory

    Returns:
        A path to directory containing virtualenv

    Raises:
        VipError: when installation cannot be finished
    """

    directory = path.path(directory)

    try:
        vip_directory = find_vip_directory(directory)
    except VipError:
        vip_directory = (path.path(directory) / VIP_DIRECTORY).abspath()

    # TODO: allow to pass additional flags to virtualenv tool
    if not vip_directory.exists():
        virtualenv.create_environment(vip_directory)

    else:
        logger.warning("Found %s directory, assuming it is "
                       "a virtualenv" % vip_directory)

    # Let's assume that if .vip is directory it is also our virtualenv
    if vip_directory.exists() and not vip_directory.isdir():
        raise VipError("%s is not a directory" % vip_directory)

    # if requirements.txt exists try to install all packages
    if install_requirements:
        # TODO(dejw): allow installing all *requirements.txt files
        requirements_file = directory / REQUIREMENTS_FILENAME

        if requirements_file.exists() and requirements_file.isfile():
            logger.info("Installing requirements from %s" % requirements_file)
            execute_virtualenv_command(vip_directory, "pip", ["install", "-r",
                                       requirements_file])

    return vip_directory


def execute_virtualenv_command(vip_directory, command, args):
    """ Executes a vip_directory/bin/command executable with given arguments

    Raises:
        VipError: when command is not found or cannot be executed
    """
    vip_directory = path.path(vip_directory)

    executable_path = vip_directory / "bin" / command
    if not executable_path.exists() or not is_exe(executable_path):
        raise VipError("%s not found or is not executable" % executable_path)

    arguments = [executable_path] + args
    p = subprocess.Popen(arguments, stdout=sys.stdout, stderr=sys.stderr,
                         stdin=subprocess.PIPE)

    try:
        p.stdin.close()
        p.communicate()
        return p.returncode
    except subprocess.CalledProcessError as e:
        raise VipError(str(e))
    except KeyboardInterrupt:
        pass
    finally:
        if p.poll() is None:
            p.terminate()
