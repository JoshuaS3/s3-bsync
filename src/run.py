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
    state.deserialize()
