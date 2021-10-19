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
from setuptools import setup

setup(
    name="s3-bsync",
    version="0.1.0",
    description="Bidirectional syncing tool to sync local filesystem directories with S3 buckets.",
    license="MIT License",
    author="Joshua Stockin",
    author_email="josh@joshstock.in",
    url="https://git.joshstock.in/s3-bsync",
    download_url="https://git.joshstock.in/s3-bsync.git",
    package_dir={"s3_bsync": "src"},
    packages=["s3_bsync", "s3_bsync.classes"],
    entry_points={
        "console_scripts": [
            "s3-bsync = s3_bsync.__main__:main"
        ]
    }
)
