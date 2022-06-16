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
    class Formatter(
        argparse.RawDescriptionHelpFormatter,
        argparse.ArgumentDefaultsHelpFormatter,
        argparse.HelpFormatter,
    ):
        pass

    parser = argparse.ArgumentParser(
        prog=package_info["name"],
        description=package_info["description"],
        formatter_class=lambda prog: Formatter(prog, width=88),
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
        help="Run in initialize mode. This allows tracking file management and directory options to be used.",
    )
    group1.add_argument(
        "--debug",
        action="store_true",
        default=False,
        help="Enables debug mode, which prints program information to stdout.",
    )
    group1.add_argument(
        "--file",
        nargs=1,
        metavar=("SYNCFILE"),
        default=["~/.state.s3sync"],
        help="The s3sync state file used to store tracking and state information. It should resolve to an absolute path.",
    )
    group1.add_argument(
        "--dump",
        action="store_true",
        default=False,
        help="Dump s3sync state file configuration. --dryrun implicitly enabled.",
    )
    group1.add_argument(
        "--dryrun",
        action="store_true",
        default=False,
        help="Run program logic without making changes. Useful when paired with debug mode to see what changes would be made.",
    )

    group2 = parser.add_argument_group(
        "tracking file management", "Requires initialize mode to be enabled."
    )

    group2.add_argument(
        "--purge",
        action="store_true",
        default=False,
        help="Deletes the default (if not otherwise specified with --file) tracking configuration file if it exists.",
    )
    group2.add_argument(
        "--overwrite",
        action="store_true",
        default=False,
        help="Overwrite tracking file with new directory maps instead of appending.",
    )

    group3 = parser.add_argument_group(
        "directory mapping", "Requires initialize mode to be enabled."
    )

    group3.add_argument(
        "--dir",
        action="append",
        nargs=2,
        metavar=("PATH", "S3_DEST"),
        default=argparse.SUPPRESS,
        help="Directory map to detail which local directory corresponds to S3 bucket "
        "and key prefix. Can be used multiple times to set multiple directories. "
        "Local directories must be absolute. S3 destination in `s3://bucket-name/prefix` "
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

    logger.debug(f'User supplied tracking file "{args.file[0]}". Sanitizing...')
    whitespace_pattern = re.compile(r"\s+")
    args.file = os.path.expanduser(args.file[0])
    args.file = re.sub(whitespace_pattern, "", args.file)
    if not args.file:
        logger.error("Inputted tracking file path string is empty")
        exit(1)
    if not os.path.isabs(args.file):
        logger.error("Inputted tracking file path is not an absolute path")
        exit(1)
    if os.path.isdir(args.file):
        logger.error("Inputted tracking file path resolves to an existing directory")
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
