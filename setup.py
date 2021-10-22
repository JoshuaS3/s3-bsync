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

from src.meta import package_info

setup(
    name=package_info["name"],
    version=package_info["version_string"],
    description=package_info["description"],
    license=package_info["license"],
    author=package_info["author"],
    author_email=package_info["author_email"],
    url=package_info["url"],
    download_url=package_info["download_url"],
    package_dir={"s3_bsync": "src"},
    packages=["s3_bsync", "s3_bsync.classes"],
    entry_points={"console_scripts": ["s3-bsync = s3_bsync.__main__:main"]},
)
