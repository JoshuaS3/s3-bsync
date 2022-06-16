# s3-bsync Copyright (c) 2021 Joshua Stockin
# <https://joshstock.in>
# <https://git.joshstock.in/s3-bsync>
#
# This software is licensed and distributed under the terms of the MIT License.
# See the MIT License in the LICENSE file of this project's root folder.
#
# This comment block and its contents, including this disclaimer, MUST be
# preserved in all copies or distributions of this software's source.


from . import sync_directory_map, sync_fileobject

__all__ = ["sync_managed_bucket"]


class sync_managed_bucket:
    bucket_name = ""
    directory_maps = []
    fileobjects = []

    def __init__(self, bucket_name):
        self.bucket_name = bucket_name

    def create_dirmap(
        local_path,
        s3_prefix,
        gz_compress=0,
        recursive=True,
        gpg_enabled=False,
        gpg_email="",
    ):
        dirmap = classes.sync_dirmap()
        dirmap.local_path = ""
        dirmap.s3_prefix = ""
        dirmap.gz_compress = 0
        dirmap.recursive = True
        dirmap.gpg_enabled = False
        dirmap.gpg_email = ""
        self.directory_maps.append(dirmap)

    def create_fileobject(key, modified, etag, size):
        fileobject = classes.sync_fileobject()
        fileobject.key = None
        fileobject.modified = 0
        fileobject.etag = None
        fileobject.size = 0
        self.fileobjects.append(fileobject)
