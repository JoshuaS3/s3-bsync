# s3-bsync Copyright (c) 2021 Joshua Stockin
# <https://joshstock.in>
# <https://git.joshstock.in/s3-bsync>
#
# This software is licensed and distributed under the terms of the MIT License.
# See the MIT License in the LICENSE file of this project's root folder.
#
# This comment block and its contents, including this disclaimer, MUST be
# preserved in all copies or distributions of this software's source.


from .sync_directory_map import sync_directory_map
from .sync_fileobject import sync_fileobject

__all__ = ["sync_managed_bucket"]


class sync_managed_bucket:
    bucket_name = ""
    directory_maps = []
    fileobjects = []

    def __init__(self, bucket_name):
        self.bucket_name = bucket_name

    def create_dirmap(
        self,
        local_path,
        s3_prefix,
        gz_compress=0,
        recursive=True,
        gpg_enabled=False,
        gpg_email="",
    ):
        dirmap = sync_directory_map()
        dirmap.local_path = local_path
        dirmap.s3_prefix = s3_prefix
        dirmap.gz_compress = gz_compress
        dirmap.recursive = recursive
        dirmap.gpg_enabled = gpg_enabled
        dirmap.gpg_email = gpg_email
        self.directory_maps.append(dirmap)

    def create_fileobject(self, key, modified, etag, size):
        fileobject = sync_fileobject()
        fileobject.key = None
        fileobject.modified = 0
        fileobject.etag = None
        fileobject.size = 0
        self.fileobjects.append(fileobject)
