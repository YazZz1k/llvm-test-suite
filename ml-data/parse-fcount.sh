#!/usr/bin/bash
set -e
#set -x

gprof $1 $2 --no-demangle --flat-profile --no-graph --brief | awk 'NR > 7 {print $7" "$4}'

