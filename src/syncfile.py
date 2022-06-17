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


class syncfile:
    file_path = None
    file_version = 0
    last_synced_time = 0
    managed_buckets = {}

    def __init__(self, state_file: str):
        self.file_path = state_file

    def file_exists(self):
        if os.path.exists(self.file_path) and not os.path.isdir(self.file_path):
            return True
        return False

    def purge(self):
        if self.file_exists():
            if self.verify_file():
                os.remove(self.file_path)
            else:
                logger.error("Attempt to purge (delete) a non-s3sync file")
                exit(1)
        else:
            logger.debug("File already nonexistent")

    def verify_file(self):
        if not self.file_exists():
            return False
        f = open(self.file_path, "rb")
        f.seek(0)
        b = f.read(4)
        f.close()
        if b != CONTROL_BYTES["SIGNATURE"]:
            return False
        return True

    def serialize(self):
        logger.debug("Compiling bytearray")

        b = bytearray()

        b += CONTROL_BYTES["SIGNATURE"]
        b += CURRENT_VERSION.to_bytes(1, byteorder=ENDIANNESS)

        b += CONTROL_BYTES["METADATA_BEGIN"]
        current_time = time.time_ns() // 1000000
        b += current_time.to_bytes(8, byteorder=ENDIANNESS)
        b += CONTROL_BYTES["METADATA_END"]

        for bucket in self.managed_buckets:
            b += CONTROL_BYTES["BUCKET_BEGIN"]
            b += bucket.bucket_name.encode()

            for dirmap in bucket.directory_maps:
                b += CONTROL_BYTES["DIRECTORY_BEGIN"]
                b += dirmap.local_path.encode() + b"\x00"
                b += dirmap.s3_prefix.encode() + b"\x00"
                b += dirmap.gz_compress.to_bytes(1, byteorder=ENDIANNESS)
                b += dirmap.recursive.to_bytes(1, byteorder=ENDIANNESS)
                b += dirmap.gpg_enabled.to_bytes(1, byteorder=ENDIANNESS)
                if dirmap.gpg_enabled:
                    b += dirmap.gpg_email.encode() + b"\x00"
                b += CONTROL_BYTES["DIRECTORY_END"]

            for fileobject in bucket.fileobjects:
                b += CONTROL_BYTES["OBJECT_BEGIN"]
                b += fileobject.key.encode() + b"\x00"
                b += fileobject.modified.to_bytes(8, byteorder=ENDIANNESS)
                if fileobject and len(fileobject.etag) == 16:
                    b += CONTROL_BYTES["ETAG_MD5"]
                    b += bytes.fromhex(fileobject.etag)
                else:
                    b += CONTROL_BYTES["ETAG_OTHER"]
                    b += fileobject.etag.encode() + b"\x00"
                b += fileobject.size.to_bytes(8, byteorder=ENDIANNESS)
                b += CONTROL_BYTES["OBJECT_END"]

            b += CONTROL_BYTES["BUCKET_END"]

        logger.debug("Writing serialized state information to syncfile")
        f = open(self.file_path, "wb")
        f.seek(0)
        f.write(b)
        f.truncate()
        f.close()

    def deserialize(self):
        if not self.file_exists():
            logger.error("Attempt to deserialize file that doesn't exist")
            exit(1)

        f = open(self.file_path, "rb")
        logger.debug(f"Deserializing file {f}")
        f.seek(0)

        def get_string():
            return "".join(iter(lambda: f.read(1), "\x00"))

        b = f.read(4)
        if b != CONTROL_BYTES["SIGNATURE"]:
            logger.error(
                "File signature does not match expected s3state file signature (not an s3sync file format or file corrupted)"
            )
            exit(1)

        self.file_version = int.from_bytes(f.read(1), byteorder=ENDIANNESS)
        if self.file_version == 0 or self.file_version > CURRENT_VERSION:
            logger.error(
                f"File version outside expected range (1..{CURRENT_VERSION}) (corrupt file)"
            )
            exit(1)
        logger.debug(f"File is version {self.file_version}")

        b = f.read(1)
        if b != CONTROL_BYTES["METADATA_BEGIN"]:
            logger.error("Expected metadata block begin byte not found (corrupt file)")
            exit(1)
        self.last_synced_time = int.from_bytes(f.read(8), byteorder=ENDIANNESS)
        logger.debug(f"Last synced time reported as {self.last_synced_time}")

        b = f.read(1)
        if b != CONTROL_BYTES["METADATA_END"]:
            logger.error("Expected metadata block end byte not found (corrupt file)")
            exit(1)

        while b := f.read(1):
            if b != CONTROL_BYTES["BUCKET_BEGIN"]:
                logger.error(b"Unexpected control byte detected (corrupt file)")
                exit(1)
            bucket_name = get_string()
            bucket = classes.sync_managed_bucket(bucket_name)

        f.close()
