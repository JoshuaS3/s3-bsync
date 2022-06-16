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
import logging

from .classes import *

logger = logging.getLogger(__name__)

__all__ = ["syncfile"]


CONTROL_BYTES = {
    "SIGNATURE": b"\x9D\x9F\x53\x33",
    "BUCKET_BEGIN": b"\x90",
    "BUCKET_END": b"\x91",
    "DIRECTORY_BEGIN": b"\x92",
    "DIRECTORY_END": b"\x93",
    "OBJECT_BEGIN": b"\x94",
    "OBJECT_END": b"\x95",
    "ETAG_MD5": b"\x96",
    "ETAG_OTHER": b"\x97",
    "METADATA_BEGIN": b"\x9A",
    "METADATA_END": b"\x9B",
}

CURRENT_VERSION = 1
ENDIANNESS = "little"


class CorruptSyncfileException(Exception):
    """Exception passed by syncfile class when experiencing errors deserializing a supplied s3sync file."""


class syncfile:
    file_path = None
    file = None
    file_version = 0
    last_synced_time = 0
    tracked_buckets = {}

    def __init__(self, state_file: str):
        self.file_path = state_file
        self.file = open(state_file, "wb+")
        logger.debug(f"Opened s3sync state file at {state_file}")

    def file_exists(self):
        if os.path.exists(self.file_path) and not os.path.isdir(self.file_path):
            return True
        return False

    def deserialize(self):
        f = self.file
        logger.debug(f"Deserializing file {f}")
        f.seek(0)

        def get_string():
            return "".join(iter(lambda: f.read(1), "\x00"))

        b = f.read(4)
        if b is not CONTROL_BYTES["SIGNATURE"]:
            logger.error(
                "File signature does not match expected s3state file signature (not an s3sync file format or file corrupted)"
            )
            exit(1)

        self.file_version = int(f.read(1))
        if self.file_version is 0 or self.file_version >= 1:
            logger.error(
                f"File version outside expected range (1..{CURRENT_VERSION}) (corrupt file)"
            )
            exit(1)

        b = f.read(1)
        if b is not CONTROL_BYTES["METADATA_BEGIN"]:
            logger.error("Expected metadata block begin byte not found (corrupt file)")
            exit(1)
        if self.file_version <= 1:
            self.last_synced_time = int.from_bytes(b.read(8), byteorder=ENDIANNESS)
            logger.debug(f"Last synced time reported as {self.last_synced_time}")

        b = f.read(1)
        if b is not CONTROL_BYTES["METADATA_END"]:
            logger.error("Expected metadata block end byte not found (corrupt file)")
            exit(1)

        while b := f.read(1):
            if b is not CONTROL_BYTES["BUCKET_BEGIN"]:
                logger.error(b"Unexpected control byte {b} detected (corrupt file)")
                exit(1)
            bucket_name = get_string()
            bucket = classes.bucket(bucket_name)
