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
import re
import logging

from .classes import *

logger = logging.getLogger(__name__)

__all__ = ["syncfile", "dirmap_stringify"]


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


def dirmap_stringify(local_path, bucket_name, s3_prefix):
    return f'"{local_path}" <=> "s3://{bucket_name}/{s3_prefix}"'


class syncfile:
    file_path = None
    file_version = 0
    file_size = 0
    last_synced_time = 0
    managed_buckets = []

    def __init__(self, state_file: str):
        self.file_path = state_file

    def map_directory(self, local_path, s3_path):
        # Verify local path validity
        if not os.path.isdir(local_path):
            logger.error(
                f'User supplied local directory ("{local_path}") is not a directory'
            )
            exit(1)

        # Check S3 path supplied is valid
        s3match = re.match("^s3:\/\/([a-z0-9][a-z0-9-]{1,61}[a-z0-9])\/(.*)$", s3_path)
        if not s3match or len(s3match.groups()) != 2:
            logger.error(f'User supplied invalid S3 path ("{s3_path}")')
            exit(1)
        bucket_name = s3match.group(1)
        s3_prefix = s3match.group(2)
        if s3_prefix.endswith("/") or len(s3_prefix) == 0:
            logger.error(f'User supplied invalid S3 path prefix ("{s3_prefix}")')
            exit(1)

        logger.debug(
            f'Local directory "{local_path}" mapped to bucket "{bucket_name}" at path prefix "{s3_prefix}"'
        )

        bucket = next(
            (b for b in self.managed_buckets if b.bucket_name == bucket_name), False
        )

        if not bucket:
            bucket = sync_managed_bucket(bucket_name)
            self.managed_buckets.append(bucket)

        dirmap_exists = next(
            (
                True
                for d in bucket.directory_maps
                if d.local_path == local_path and d.s3_prefix == s3_prefix
            ),
            False,
        )

        if dirmap_exists:
            logger.error(
                f"Directory map {dirmap_stringify(local_path, bucket.bucket_name, s3_prefix)} already exists"
            )
            exit(1)

        logger.debug(
            f"Creating directory map {dirmap_stringify(local_path, bucket.bucket_name, s3_prefix)}"
        )
        bucket.create_dirmap(local_path, s3_prefix)

    def remove_dirmap(self, local_path, s3_path):
        # Check S3 path supplied is valid
        s3match = re.match("^s3:\/\/([a-z0-9][a-z0-9-]{1,61}[a-z0-9])\/(.*)$", s3_path)
        if not s3match or len(s3match.groups()) != 2:
            logger.error(f'User supplied invalid S3 path ("{s3_path}")')
            exit(1)
        bucket_name = s3match.group(1)
        s3_prefix = s3match.group(2)
        if s3_prefix.endswith("/") or len(s3_prefix) == 0:
            logger.error(f'User supplied invalid S3 path prefix ("{s3_prefix}")')
            exit(1)

        bucket = next(
            (
                bucket
                for bucket in self.managed_buckets
                if bucket.bucket_name == bucket_name
            ),
            None,
        )
        if not bucket:
            logger.error(f"Bucket s3://{bucket_name} is not tracked by the sync file")
            exit(1)

        dirmaps = [
            x
            for x in bucket.directory_maps
            if x.local_path == local_path and x.s3_prefix == s3_prefix
        ]
        if len(dirmaps) > 0:
            for dirmap in dirmaps:
                logger.debug(
                    f"Deleting directory map {dirmap_stringify(local_path, bucket.bucket_name, s3_prefix)}"
                )
                bucket.directory_maps.remove(dirmap)
                del dirmap
        else:
            logger.error(
                f"Directory map {dirmap_stringify(local_path, bucket.bucket_name, s3_prefix)} does not exist"
            )
            exit(1)

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
            logger.error("State file nonexistent")
            exit(1)

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
            if (
                len(bucket.directory_maps) == 0
            ):  # Don't serialize any buckets with no dirmaps
                continue

            b += CONTROL_BYTES["BUCKET_BEGIN"]
            b += bucket.bucket_name.encode() + b"\x00"

            logger.debug(f"Bucket {bucket.bucket_name}")

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
                logger.debug(
                    f"Serialized directory map {dirmap_stringify(dirmap.local_path, bucket.bucket_name, dirmap.s3_prefix)}"
                )

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
                logger.debug(
                    f"Serialized fileobject s3://{bucket.name}/{fileobject.key} ({fileobject.etag})"
                )

            b += CONTROL_BYTES["BUCKET_END"]

        logger.debug("Writing serialized state information to syncfile")
        f = open(self.file_path, "wb")
        f.seek(0)
        f.write(b)
        f.truncate()
        f.close()
        logger.debug(f"Finished writing to file (length {len(b)})")

    def deserialize(self):
        if not self.file_exists():
            logger.error("Attempt to deserialize file that doesn't exist")
            exit(1)

        self.file_size = os.path.getsize(self.file_path)
        f = open(self.file_path, "rb")
        logger.debug(f"Deserializing file {f}")
        f.seek(0)

        def get_string():
            return b"".join(iter(lambda: f.read(1), b"\x00")).decode()

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
            bucket = sync_managed_bucket(bucket_name)
            self.managed_buckets.append(bucket)

            logger.debug(f"Bucket {bucket_name}")

            while b2 := f.read(1):
                if b2 == CONTROL_BYTES["DIRECTORY_BEGIN"]:
                    local_path = get_string()
                    s3_prefix = get_string()
                    gz_compress = int.from_bytes(f.read(1), byteorder=ENDIANNESS)
                    recursive = bool.from_bytes(f.read(1), byteorder=ENDIANNESS)
                    gpg_enabled = bool.from_bytes(f.read(1), byteorder=ENDIANNESS)
                    gpg_email = ""
                    if gpg_enabled:
                        gpg_email = get_string()
                    if f.read(1) != CONTROL_BYTES["DIRECTORY_END"]:
                        logger.error(
                            "Expected directory block end byte not found (corrupt file)"
                        )
                        exit(1)
                    bucket.create_dirmap(
                        local_path,
                        s3_prefix,
                        gz_compress,
                        recursive,
                        gpg_enabled,
                        gpg_email,
                    )
                    logger.debug(
                        f"Deserialized directory map {dirmap_stringify(local_path, bucket.bucket_name, s3_prefix)}"
                    )

                elif b2 == CONTROL_BYTES["OBJECT_BEGIN"]:
                    key = get_string()
                    modified = int.from_bytes(f.read(8), byteorder=ENDIANNESS)
                    etag_type = f.read(1)
                    etag = ""
                    if etag_type == CONTROL_BYTES["ETAG_MD5"]:
                        etag = f.read(16)
                    elif etag_type == CONTROL_BYTES["ETAG_OTHER"]:
                        etag = get_string()
                    file_size = int.form_bytes(f.read(8), byteorder=ENDIANNESS)
                    if f.read(1) != CONTROL_BYTES["OBJECT_END"]:
                        logger.error(
                            "Expected fileobject block end byte not found (corrupt file)"
                        )
                        exit(1)
                    bucket.create_fileobject(key, modified, etag, file_size)
                    logger.debug(
                        f"Deserialized fileobject s3://{bucket.name}/{key} ({etag})"
                    )

                elif b2 == CONTROL_BYTES["BUCKET_END"]:
                    break

                else:
                    logger.error("Unexpected control byte detected (corrupt file)")

        f.close()
