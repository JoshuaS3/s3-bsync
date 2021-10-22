# s3-bsync Copyright (c) 2021 Joshua Stockin
# <https://joshstock.in>
# <https://git.joshstock.in/s3-bsync>
#
# This software is licensed and distributed under the terms of the MIT License.
# See the MIT License in the LICENSE file of this project's root folder.
#
# This comment block and its contents, including this disclaimer, MUST be
# preserved in all copies or distributions of this software's source.

import os
import re
import argparse

import logging

from .meta import package_info

logger = logging.getLogger(__name__)

__all__ = ["command_parse", "sanitize_arguments"]


def command_parse(args: list[str]):
    parser = argparse.ArgumentParser(
        prog=package_info["name"],
        description=package_info["description"],
        formatter_class=lambda prog: argparse.HelpFormatter(prog, width=88),
        allow_abbrev=False,
        add_help=False,
    )

    parser.add_argument(
        "-h", "-?", "--help", action="help", help="Display this help message and exit."
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        help="Display program and version information and exit.",
        version=f"s3-bsync version {package_info['version_string']}\n"
        "<https://joshstock.in> <josh@joshstock.in>\n"
        "<https://git.joshstock.in/s3-bsync>",
    )

    group1 = parser.add_argument_group(
        "program behavior", "The program runs in sync mode by default."
    )

    group1.add_argument(
        "-i",
        "--init",
        action="store_true",
        default=False,
        help="Run in initialize mode. This allows tracking file management and directory options to be used. (default: False)",
    )
    group1.add_argument(
        "--debug",
        action="store_true",
        default=False,
        help="Enables debug mode, which prints program information to stdout. (default: False)",
    )
    group1.add_argument(
        "--file",
        nargs=1,
        metavar=("SYNCFILE"),
        default=None,
        help='The s3sync format file used to store tracking and state information. (default: "~/.state.s3sync")',
    )
    group1.add_argument(
        "--dryrun",
        action="store_true",
        default=False,
        help="Run program logic without actually making changes. Useful when paired with debug mode to see what changes would be made. (default: False)",
    )

    group2 = parser.add_argument_group(
        "tracking file management", "Requires initialize mode to be enabled."
    )

    group2.add_argument(
        "--purge",
        action="store_true",
        default=False,
        help="Deletes the default (if not otherwise specified) tracking configuration file if it exists. (default: False)",
    )
    group2.add_argument(
        "--overwrite",
        action="store_true",
        default=False,
        help="Overwrite tracking file with new directory maps instead of appending. (default: False)",
    )

    group3 = parser.add_argument_group(
        "directory mapping", "Requires initialize mode to be enabled."
    )

    group3.add_argument(
        "--dir",
        action="append",
        nargs=2,
        metavar=("PATH", "S3_DEST"),
        help="Directory map to detail which local directory corresponds to S3 bucket "
        "and key prefix. Can be used multiple times to set multiple directories. "
        "Local directories must be fully expanded. S3 destination in `s3://bucket-name/prefix` "
        "format. Example: `--dir /home/josh/Documents s3://joshstockin/Documents`",
    )

    return parser.parse_args(args)


def sanitize_arguments(args: argparse.Namespace):
    if args.debug:
        logger.debug("DEBUG mode set")

    if args.init:
        logger.debug("INIT mode set")
    else:
        logger.debug("SYNC mode set implicitly (INIT not set)")

    if args.dryrun:
        logger.debug("DRYRUN mode set")

    if not args.file:
        logger.debug("No tracking file set. Determining default...")
        args.file = os.path.expanduser(os.path.join("~", ".state.s3sync"))
    else:
        logger.debug(f'User supplied tracking file "{args.file[0]}". Sanitizing...')
        whitespace_pattern = re.compile(r"\s+")
        args.file = re.sub(whitespace_pattern, "", args.file[0])
        if not args.file:
            logger.error("Inputted tracking file path string is empty")
            exit(1)
        if not os.path.isabs(args.file):
            logger.error("Inputted tracking file path is not an absolute path")
            exit(1)
    logger.debug(f'Tracking file set to "{args.file}"')

    if args.purge:
        if args.init:
            logger.debug("PURGE mode set")
        else:
            logger.debug("PURGE mode set, but INIT mode isn't. Ignoring")

    if args.overwrite:
        if args.init:
            logger.debug("OVERWRITE mode set")
        else:
            logger.debug("OVERWRITE mode set, but INIT mode isn't. Ignoring")

    return args
