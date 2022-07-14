# s3-bsync Copyright (c) 2022 Joshua Stockin
# <https://joshstock.in>
# <https://git.joshstock.in/s3-bsync>
#
# This software is licensed and distributed under the terms of the MIT License.
# See the MIT License in the LICENSE file of this project's root folder.
#
# This comment block and its contents, including this disclaimer, MUST be
# preserved in all copies or distributions of this software's source.

import os
import time
import logging
import glob

from .classes import *
from . import syncfile

logger = logging.getLogger(__name__)

__all__ = ["bucket_scan"]


COMPARE_RESULTS = {
    "LOCAL_NOT_FOUND": 0b00000001,
    "S3OBJ_NOT_FOUND": 0b00000010,
    "LOCAL_OLDER":     0b00000100,
    "LOCAL_LARGER":    0b00001000,
    "S3OBJ_OLDER":     0b00010000,
    "S3OBJ_LARGER":    0b00100000,
}

def by_bucket(bucket: sync_managed_bucket):
    for dirmap in bucket.directory_maps:
        for root, dirs, files in os.walk(dirmap.local_path):
            for file in files:
                logger.debug(f"{os.path.join(root, file)}")
