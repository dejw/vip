# -*- coding: utf-8 -*-

import itertools
import logging
import os
import path
import signal
try:
    import StringIO
except ImportError:
    import io as StringIO

import subprocess
import sys
import virtualenv


VIP_DIRECTORY = ".vip"
DEFAULT_VIRTUALENV_DIRS = [VIP_DIRECTORY, '.venv']
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


class VipError(Exception):
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
            execute_virtualenv_command(vip_directory, "pip",
                                       ["install", "-r", requirements_file])

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
    exe_base = path.path(exe_base)

    ext_val = os.environ["PATHEXT"].lower()\
        if "PATHEXT" in os.environ\
        else ".exe;.cmd;.bat;.py;.pyw"
    path_exts = filter(lambda v: len(v) > 0, [v.strip() for v in ext_val
                                              .split(';')])
    exe_exists = False
    if exe_base.exists() and exe_base.isfile():
        exe_ext = exe_base.splitext()[-1].lower()
        if exe_ext in path_exts:
            return exe_base
        else:
            exe_exists = True

    for ext in path_exts:
        exe_path = path.path(exe_base + ext)
        if exe_path.exists() and exe_path.isfile():
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
    vip_directory = path.path(vip_directory)

    if is_win:
        executable_base = vip_directory / "Scripts" / command
        executable_path = find_windows_executable(executable_base)
    else:
        executable_path = vip_directory / "bin" / command
        if not executable_path.exists() or not is_exe(executable_path):
            raise VipError(
                "%s not found or is not executable" % executable_path)

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


def get_requirements_filenames(prefix=None, version=None, extension='txt'):
    """Produces requirements filenames based on prefix and interpreter version.

    Filenames are following pattern:

        [prefix-]?requirements[-version+]?.txt

    For instance, for prefix `devel` and `version` (2, 7, 3) it will produce:

              requirements.txt
              requirements-2.txt
              requirements-27.txt
              requirements-273.txt
        devel-requirements.txt
        devel-requirements-2.txt
        devel-requirements-27.txt
        devel-requirements-273.txt

    Args:
        prefix: str, a prefix for requirements, like 'dev', 'devel', 'prod'
        version: an iterable, with version segments to use, using
            os.version_info by default
        extension: str, what extension to use, 'txt' by default

    Returns:
        a sequence of filenames
    """
    prefixes = ['']

    if prefix:
        prefixes.append('%s-' % prefix)

    version = os.version_info if version is None else version
    version = [str(v) for v in version]
    version = [''] + ['-%s' % ''.join(version[:i + 1])
                      for i, v in enumerate(version) if v]

    for p, v in itertools.product(prefixes, version):
        yield '%srequirements%s.%s' % (p, v, extension)
