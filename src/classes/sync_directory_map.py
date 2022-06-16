# s3-bsync Copyright (c) 2021 Joshua Stockin
# <https://joshstock.in>
# <https://git.joshstock.in/s3-bsync>
#
# This software is licensed and distributed under the terms of the MIT License.
# See the MIT License in the LICENSE file of this project's root folder.
#
# This comment block and its contents, including this disclaimer, MUST be
# preserved in all copies or distributions of this software's source.

__all__ = ["sync_directory_map"]


class sync_directory_map:
    local_path = ""
    s3_prefix = ""
    gz_compress = 0
    recursive = True
    gpg_enabled = False
    gpg_email = ""
