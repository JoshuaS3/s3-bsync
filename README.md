## s3-bsync

Bidirectional syncing tool to sync local filesystem directories with S3
buckets.  Developed by [Josh Stockin](https://joshstock.in) and licensed under
the MIT License.

**Work in progress (v0.1.0).  Not in a functional or usable state.  Do NOT use
this unless you know what you are doing.**

### Behavior

After an initial sync (manually handling conflicts and uncommon files), the S3
bucket maintains precedence.  Files with the same size and modify time on both
hosts are ignored.  A newer copy of a file always overwrites the corresponding
old, regardless of changes in the old.  (In other words, **there is no manual
conflict resolution after the first sync.  Conflicting files are handled
automatically as described here.**  This script is meant to run without input
or output by default, in a cron job for example.)  Untracked files, in either
S3 or on the local machine, are copied to the opposite host and tracked.
Tracked files that are moved or removed on either host are moved or removed on
the corresponding host, with the tracking adjusted accordingly.  Ultimately,
after a sync, the `.state.s3sync` state tracking file should match the contents
of the S3 bucket's and local synced directories.

### Installation

Depends on `python3` and `aws-cli`.  Both can be installed with your package
manager.  Requires Python modules `pip` and `setuptools` if you want to install
on your system path using one of the methods listed below. Python module
`python-gnupg` optionally required if you wish to use GPG encryption options.

Install with one of the following:

* `./install.sh [<python interpreter>?]` (Preferred)
* `python3 -m pip install .`
* `python3 ./setup.py install` (Not recommended)

Uninstall with one of the following:

* `./install.sh uninstall [<python interpreter>?]` (Preferred)
* `python3 -m pip uninstall s3-bsync`

`install.sh` is a frontend for `pip (un)install`, configured by setuptools in
`setup.py`. The script automatically performs compatibility checks on Python
interpreter and other required dependencies.

Root permissions are not required.  *This program does not manage S3
authentication or `aws-cli` credentials. You must do this yourself with the
`aws configure` command, or through some other means of IAM/S3 policy.*

### Usage

```
usage: s3-bsync [--help] [--version] [--init] [--debug] [--dryrun] [--file SYNCFILE]
                [--dump] [--purge] [--overwrite] [--dir PATH S3_DEST] [--rmdir RMPATH]

Bidirectional syncing tool to sync local filesystem directories with S3 buckets.

optional arguments:
  --help, -h, -?      Display this help message and exit.
  --version, -v       Display program and version information and exit.

program behavior:
  The program runs in sync mode by default.

  --init, -i          Run in initialize (edit) mode. This allows tracking file
                      management and directory options to be used. (default: False)
  --debug             Enables debug mode, which prints program information to stdout.
                      (default: False)
  --dryrun            Run program logic without making changes. Useful when paired with
                      debug mode to see what changes would be made. (default: False)

tracking file management:
  Configuring the tracking file.

  --file SYNCFILE     The s3sync state file used to store tracking and state
                      information. It should resolve to an absolute path. (default:
                      ['~/.state.s3sync'])
  --dump              Dump s3sync state file configuration and exit. (default: False)
  --purge             Deletes the tracking configuration file if it exists and exits.
                      Requires init mode. (default: False)
  --overwrite         Overwrite tracking file with new directory maps instead of
                      appending. Requires init mode. (default: False)

directory mapping:
  Requires initialize mode to be enabled.

  --dir PATH S3_DEST  Directory map to detail which local directory corresponds to S3
                      bucket and key prefix. Can be used multiple times to set multiple
                      directories. Local directories must be absolute. S3 destination in
                      `s3://bucket-name/prefix` format. Example: `--dir
                      /home/josh/Documents s3://joshstockin/Documents`
  --rmdir RMPATH      Remove tracked directory map by local directory identifier.
                      Running `--rmdir /home/josh/Documents` would remove the directory
                      map from the s3syncfile and stop tracking/syncing that directory.
```

#### Source files

`setup.py` manages installation metadata.
`install.sh` handles installation and uninstallation using pip.

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

Version 1 of the s3sync file format.

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
        S3 key prefix (no `/` termination)     - null-terminated string
        Compress (gzip level)                  - 0-11 (1 byte)
        Recursive sync                         - 1 byte boolean
        GPG encryption enabled                 - 1 byte boolean
        GPG encryption email                   - null-terminated string
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
s3-bsync Copyright (c) 2022 Joshua Stockin
<https://joshstock.in>
<https://git.joshstock.in/s3-bsync>

This software is licensed and distributed under the terms of the MIT License.
See the MIT License in the LICENSE file of this project's root folder.

This comment block and its contents, including this disclaimer, MUST be
preserved in all copies or distributions of this software's source.
```

&lt;<https://joshstock.in>&gt; | [josh@joshstock.in](mailto:josh@joshstock.in) | joshuas3#9641
