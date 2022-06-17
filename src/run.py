# s3-bsync Copyright (c) 2022 Joshua Stockin
# <https://joshstock.in>
# <https://git.joshstock.in/s3-bsync>
#
# This software is licensed and distributed under the terms of the MIT License.
# See the MIT License in the LICENSE file of this project's root folder.
#
# This comment block and its contents, including this disclaimer, MUST be
# preserved in all copies or distributions of this software's source.

import logging

from . import *

logger = logging.getLogger(__name__)

__all__ = ["run"]


def run(settings):
    logger.debug("Entering run sequence")
    state = syncfile.syncfile(settings.syncfile)
    if "PURGE" in settings.mode:
        logger.debug("Purging syncfile")
        state.purge()
        logger.debug("Success. Exiting...")
        exit(0)
    if state.file_exists() and not "OVERWRITE" in settings.mode:
        logger.debug("Syncfile exists. Deserializing...")
        state.deserialize()
    if not state.file_exists() and not "INIT" in settings.mode:
        logger.error("Not in INIT mode and state file is nonexistent.")
        exit(1)
    state.serialize()
