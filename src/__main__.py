#!/usr/bin/env python3
# s3-bsync Copyright (c) 2021 Joshua Stockin
# <https://joshstock.in>
# <https://git.joshstock.in/s3-bsync>
#
# This software is licensed and distributed under the terms of the MIT License.
# See the MIT License in the LICENSE file of this project's root folder.
#
# This comment block and its contents, including this disclaimer, MUST be
# preserved in all copies or distributions of this software's source.

import sys
import logging
import pprint

from . import *

logger = logging.getLogger(__name__)


def main():
    args = command_parse.command_parse(sys.argv[1:])

    logLevel = logging.INFO
    if args.debug:
        logLevel = logging.DEBUG

    logging.basicConfig(
        format="\x1b[0;37m[ \x1b[0;35m%(relativeCreated)04d\x1b[0;37m / \x1b[0;33m%(name)s\x1b[0;37m:\x1b[1;36m%(funcName)s\x1b[0;37m / \x1b[0;34m%(levelname)s\x1b[0;37m ] \x1b[0m%(message)s",
        datefmt="%H:%M:%S",
        level=logLevel,
    )

    if args.debug:
        logger.debug("Debug mode enabled")

    logger.debug(f"Parsed input arguments:\n{pprint.pformat(vars(args))}")
    logger.debug("Sanitizing input arguments")
    settings = command_parse.sanitize_arguments(args)

    logger.debug(f"Interpreted settings:\n{pprint.pformat(vars(settings))}")

    run(settings)

    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
