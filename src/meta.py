# s3-bsync Copyright (c) 2021 Joshua Stockin
# <https://joshstock.in>
# <https://git.joshstock.in/s3-bsync>
#
# This software is licensed and distributed under the terms of the MIT License.
# See the MIT License in the LICENSE file of this project's root folder.
#
# This comment block and its contents, including this disclaimer, MUST be
# preserved in all copies or distributions of this software's source.

__all__ = ["package_info"]

major = 0
minor = 1
patch = 0

# Consolidated information for setup.py and other scripts
package_info = {
    "version_major": major,
    "version_minor": minor,
    "version_patch": patch,
    "version_string": f"{major}.{minor}.{patch}",
    "name": "s3-bsync",
    "description": "Bidirectional syncing tool to sync local filesystem directories with S3 buckets.",
    "license": "MIT License",
    "author": "Joshua Stockin",
    "author_email": "josh@joshstock.in",
    "url": "https://git.joshstock.in/s3-bsync",
    "download_url": "https://git.joshstock.in/s3-bsync.git",
}
