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
import datetime

from . import syncfile
from .classes import sync_managed_bucket

logger = logging.getLogger(__name__)

__all__ = ["run"]


def purge(state):
    logger.debug("Purging syncfile")
    state.purge()
    logger.debug("Success. Exiting...")
    exit(0)


def dump(state):
    logger.debug("Running in DUMP mode. Echoing deserialized information to stdout:")
    print(f"DUMP mode")
    print(
        f'Inputted valid s3sync File "{state.file_path}" (version {state.file_version})'
    )
    print(f"Metadata")
    print(
        f"  Last synced time: {state.last_synced_time} (resolves to {datetime.datetime.fromtimestamp(state.last_synced_time / 1000.0)})"
    )
    print(f"  Number of tracked buckets:      {len(state.managed_buckets)}")
    print(
        f"  Total # of mapped directores:   {sum([len(bucket.directory_maps) for bucket in state.managed_buckets])}"
    )
    print(
        f"  Total # of tracked fileobjects: {sum([len(bucket.fileobjects) for bucket in state.managed_buckets])}"
    )
    print(f"  Filesize: {state.file_size}")

    for bucket in state.managed_buckets:
        print(f'Bucket "{bucket.bucket_name}"')
        print(f"  # of mapped directores:   {len(bucket.directory_maps)}")
        print(f"  # of tracked fileobjects: {len(bucket.fileobjects)}")
        if len(bucket.directory_maps) > 0:
            print(f"  Mapped directories:")
            for dirmap in bucket.directory_maps:
                print(
                    f'  > "{dirmap.local_path}" to "s3://{bucket.bucket_name}/{dirmap.s3_prefix}"'
                )
                print(f"    gz_compress {dirmap.gz_compress}")
                print(f"    recursive   {dirmap.recursive}")
                print(f"    gpg_enabled {dirmap.gpg_enabled}")
                print(f'    gpg_email   "{dirmap.gpg_email}"')

    logger.debug("Finished dump. Exiting...")
    exit(0)


def run(settings):
    logger.debug("Entering run sequence")
    state = syncfile.syncfile(settings.syncfile)

    if "PURGE" in settings.mode:
        purge(state)

    if (
        state.file_exists() and not "OVERWRITE" in settings.mode
    ):  # data will be used, not overwritten
        logger.debug("Syncfile exists. Deserializing...")
        state.deserialize()

    if not state.file_exists() and "INIT" not in settings.mode:
        logger.error("Syncfile is nonexistent; run in INIT mode to create")
        exit(1)

    if "DUMP" in settings.mode:
        dump(state)

    if "INIT" in settings.mode:
        if hasattr(settings, "dirmaps"):
            for local_path in settings.dirmaps:
                state.map_directory(local_path, settings.dirmaps[local_path])
        state.serialize()
