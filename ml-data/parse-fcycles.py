#!/usr/bin/python3

import sys
from collections import defaultdict

def dump():
    for fname, ecycles in sorted(result.items(), key=lambda x:-x[1]):
        #print(f'{fname} {round(ecycles/total_ecycles, 5)}')
        print(f'{fname} {ecycles}')

result = defaultdict(int)

total_ecycles = 0

for line in sys.stdin:
    (strace, ecycles) = line.split(' ')
    
    ecycles = int(ecycles)
    strace = strace.split(';')
    
    total_ecycles += ecycles
    
    # ignore perf-exec process
    if strace[0] == 'perf-exec':
        continue
    # also ignore stuff that doen't inside the main
    if not strace[1] == '__libc_start_main':
        continue

    strace = strace[2:]

    for fname in strace:
        # TODO:
        # perf can't handle functions with a long names
        # in such cases it store fnames as an address
        assert fname != '[unknown]'
        result[fname] += ecycles

dump()

