# -*- coding: utf-8 -*-

from os import path


class VipError(StandardError):
    pass


def find_vip_directory(start="."):
    """ Finds the `.vip` directory up in the directory tree.

    Args:
      start: str directory name from where the search is started

    Returns:
        An absolute path to `.vip` directory.

    Raises:
        VipError when no `.vip` directory has been found to the root.
    """
    directory = path.abspath(start)

    while directory != "/":
        vip_directory = path.join(directory, ".vip")
        if path.exists(vip_directory) and path.isdir(vip_directory):
            return vip_directory

        directory, _ = path.split(directory)

    raise VipError("not a virtualenv (or any of the parent directories)")
