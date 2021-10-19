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
import s3_bsync

def main():
    args = sys.argv[1:]
    print("Hello, World!")

if __name__ == "__main__":
    sys.exit(main() or 0)
