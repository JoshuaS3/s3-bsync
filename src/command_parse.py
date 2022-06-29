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
        "--help", "-h", "-?", action="help", help="Display this help message and exit."
    )
    parser.add_argument(
        "--version",
        "-v",
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
        "--init",
        "-i",
        action="store_true",
        default=False,
        help="Run in initialize (edit) mode. This allows tracking file management and directory options to be used.",
    )
    group1.add_argument(
        "--debug",
        action="store_true",
        default=False,
        help="Enables debug flag, which prints program information to stdout.",
    )
    group1.add_argument(
        "--dryrun",
        action="store_true",
        default=False,
        help="Run program logic without making changes. Useful when paired with debug mode to see what changes would be made.",
    )

    group2 = parser.add_argument_group(
        "tracking file management", "Configuring the tracking file."
    )

    group2.add_argument(
        "--file",
        metavar=("SYNCFILE"),
        default="~/.state.s3sync",
        help="The s3sync state file used to store tracking and state information. It should resolve to an absolute path.",
    )
    group2.add_argument(
        "--dump",
        action="store_true",
        default=False,
        help="Dump s3sync state file configuration and exit.",
    )
    group2.add_argument(
        "--purge",
        action="store_true",
        default=False,
        help="Deletes the tracking configuration file if it exists and exits. Requires init mode.",
    )
    group2.add_argument(
        "--overwrite",
        action="store_true",
        default=False,
        help="Overwrite tracking file with new directory maps instead of appending. Requires init mode.",
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
    group3.add_argument(
        "--rmdir",
        action="append",
        nargs=2,
        metavar=("RMPATH", "S3_DEST"),
        default=argparse.SUPPRESS,
        help="Remove tracked directory map by local directory identifier. Running "
        "`--rmdir /home/josh/Documents s3://joshstockin/Documents` would remove the"
        "directory map from the s3sync file and stop tracking/syncing that directory.",
    )
    return parser.parse_args(args)


class sync_settings:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


def sanitize_arguments(args: argparse.Namespace):
    settings = sync_settings()

    if args.debug:
        logger.debug("DEBUG flag set")
        settings.debug = True

    logger.debug(f'User supplied tracking file "{args.file}". Sanitizing...')
    whitespace_pattern = re.compile(r"\s+")
    args.file = os.path.expanduser(args.file)
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
    settings.syncfile = args.file

    if args.init:
        logger.debug("INIT mode set")
        settings.mode = ["INIT"]
    if args.overwrite:
        if args.init:
            logger.debug("OVERWRITE mode set")
            settings.mode.append("OVERWRITE")
        else:
            logger.error("OVERWRITE mode requires INIT mode")
            exit(1)
    if args.purge:
        if args.init:
            logger.debug("PURGE mode set")
            settings.mode.append("PURGE")
        else:
            logger.error("PURGE mode requires INIT mode")
            exit(1)
    if args.dump:
        logger.debug("DUMP mode set")
        settings.mode = ["DUMP"]

    if not hasattr(settings, "mode"):
        logger.debug("No mode set. Enabling SYNC mode implicitly")
        settings.mode = ["SYNC"]
        if args.dryrun:
            logger.debug("DRYRUN flag enabled")
            settings.mode.append("DRYRUN")

    if hasattr(args, "dir"):
        if not args.init:
            logger.error("--dir requires INIT mode")
            exit(1)
        settings.dirmaps = {}
        for dirmap in args.dir:
            if not os.path.isabs(dirmap[0]):
                logger.error(f'Local path "{dirmap[0]}" is not absolute')
                exit(1)
            if not os.path.isdir(dirmap[0]):
                logger.error(
                    f'Local path "{dirmap[0]}" does not resolve to an existing directory'
                )
                exit(1)
            settings.dirmaps[os.path.realpath(dirmap[0])] = dirmap[1]

    if hasattr(args, "rmdir"):
        if not args.init:
            logger.error("--rmdir requires INIT mode")
            exit(1)
        settings.rmdirs = {}
        for rmdir in args.rmdir:
            if not os.path.isabs(rmdir[0]):
                logger.error(f'Local path "{rmdir[0]}" is not absolute')
                exit(1)
            if not os.path.isdir(rmdir[0]):
                logger.error(
                    f'Local path "{rmdir[0]}" does not resolve to an existing directory'
                )
                exit(1)
            settings.rmdirs[os.path.realpath(rmdir[0])] = rmdir[1]

    return settings
