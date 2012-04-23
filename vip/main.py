# -*- coding: utf-8 -*-

import argparse
import contextlib
import sys

import vip
from vip import core


@contextlib.contextmanager
def protect_from_VipError():
    try:
        yield
    except core.VipError as e:
        core.logger.exception("fatal: " + str(e))


def create_argument_parser():
    usage = """
  %(prog)s command ...
  %(prog)s --init [directory]
  %(prog)s --locate [directory]
"""

    parser = argparse.ArgumentParser(description=vip.__doc__, usage=usage)

    # Command execution
    parser.add_argument('command', metavar='command', type=str, nargs='?',
        help='an executable in .vip/bin directory')

    parser.add_argument('arguments', type=str, nargs=argparse.REMAINDER,
        help='arguments passed to a given command')

    parser.add_argument('-i', '--init', dest="init", metavar="directory",
        nargs="?", const=".", help='initializes a brand new virtualenv in '
        'given directory, using "." by default')

    parser.add_argument('-l', '--locate', metavar="directory",
        nargs="?", const=".", help='shows where the .vip directory is')

    parser.add_argument('-v', '--verbose', action='store_true',
            help='verbose error messages')

    parser.add_argument('-V', '--version', action='store_true',
            help='prints version and exits')

    return parser, parser.parse_args()


def main():
    parser, args = create_argument_parser()

    commands = ['init', 'locate', 'command']

    # Configure logger using --verbose option
    core.logger.verbose = bool(args.verbose)

    with protect_from_VipError():

        if args.version:
            print vip.VERSION
            sys.exit(0)

        # Check for only one command
        used_commands = [int(bool(getattr(args, cmd))) for cmd in commands]
        if sum(used_commands) > 1:
            parser.print_help()

        elif args.init:
            directory = core.create_virtualenv(args.init)
            core.logger.info("Initialized virtualenv in %s" % directory)

        elif args.locate:
            print core.find_vip_directory(args.locate)

        elif args.command:
            directory = core.find_vip_directory()
            core.execute_virtualenv_command(directory, args.command,
                                            args.arguments)

        else:
            parser.print_help()


if __name__ == "__main__":
    main()
