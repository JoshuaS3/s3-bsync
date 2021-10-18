#!/usr/bin/env bash
# use md2html with basic styling to test README.md
cat <(echo "<style>body{max-width:650px;margin:20px auto;color:#252525}</style>") <(md2html README.md) > README.html
