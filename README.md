# s3-bsync

Bidirectional syncing tool to sync local filesystem directories with S3
buckets.  Written by [Josh Stockin](https://joshstock.in).

**Work in progress.  Not in a functional state.  Do NOT use this.**

### Behavior

After an initial sync (manually handling conflicts and uncommon files), the S3
bucket maintains precedence.  Files with the same size and modify time on both
hosts are ignored.  A newer copy of a file always overwrites the corresponding
old, regardless of changes in the old.  (In other words, **there is no manual
conflict resolution after first sync.  Conflicting files are handled
automatically as described here.**  This script is meant to run without input
or output by default, in a cron job for example.)  Untracked files, in either
S3 or on the local machine, are copied to the opposite host and tracked.
Tracked files that are moved or removed on either host are moved or removed on
the corresponding host, with the tracking adjusted accordingly.  Ultimately,
after a sync, the `.state.s3sync` state tracking file should match the contents
of the S3 bucket's synced directories.

### Installation

Depends on `python3` and `aws-cli`.  Both can be installed with your package
manager.

Install with `python3 setup.py install`.  Root permissions not required.
*This program does not manage S3 authentication or `aws-cli` credentials. You
must do this yourself with the `aws configure` command, or other means of
IAM/S3 policy.*

#### Source files

`setup.py` manages installation metadata.

#### Created files and .s3syncignore

The default file used to store sync information is `~/.state.s3sync`, but this
location can be reconfigured.  The file uses the binary s3sync file format
specified later in this document.  If you want to intentionally ignore
untracked files, use a `.s3syncignore` file, in the same manner as
[`.gitignore`](https://git-scm.com/docs/gitignore).

## s3sync file format

The `.state.s3sync` file saved in home directory defines the state of tracked
objects from the specified S3 buckets and key prefixes used in the last sync.

### Control bytes

    90 - Begin bucket block
    91 - End bucket block
    92 - Begin directory map
    93 - End directory map
    94 - Begin object block
    95 - End object block
    96 - ETag type MD5
    97 - ETag type null-terminated string (non-MD5)
    98
    99
    9A - Begin metadata block
    9B - End metadata block
    9C
    9D - File signature byte
    9E
    9F - File signature byte

### File structure

```
Header {
    File signature - 4 bytes - 9D 9F 53 33
    File version   - 1 byte  - 01
}

Metadata block {
    Begin metadata block control byte - 9A
    Last synced time                  - 8 bytes uint
    End metadata block control byte   - 9B
}

Bucket block {
    Begin bucket block control byte - 90
    Bucket name                     - null-terminated string
    Directory map {
        Begin directory map block control byte - 92
        Path to local directory                - null-terminated string
        S3 key prefix                          - null-terminated string
        Recursive sync                         - 1 byte boolean
        End directory map block control byte   - 93
    }...
    Recorded object {
        Begin object block control byte - 94
        Key                             - null-terminated string
        Last modified time              - 8 bytes uint
        ETag type                       - 96 or 97
        ETag                            - 16 bytes or null-terminated string
        File size                       - 8 bytes uint
        End object block control byte   - 95
    }...
    End bucket block control byte - 91
}...
```

## Copyright

This program is copyrighted by [Joshua Stockin](https://joshstock.in/) and
licensed under the [MIT License](LICENSE).

A form of the following should be present in each source file.

```txt
s3-bsync Copyright (c) 2021 Joshua Stockin
<https://joshstock.in>
<https://git.joshstock.in/s3-bsync>

This software is licensed and distributed under the terms of the MIT License.
See the MIT License in the LICENSE file of this project's root folder.

This comment block and its contents, including this disclaimer, MUST be
preserved in all copies or distributions of this software's source.
```

&lt;<https://joshstock.in>&gt; | [josh@joshstock.in](mailto:josh@joshstock.in) | joshuas3#9641
