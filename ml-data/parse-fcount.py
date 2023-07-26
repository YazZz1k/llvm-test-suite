#!/usr/bin/python3

import sys

def is_fname(line):
    # if indent is 2 spaces this line is func name
    return (line[0:2] == '  ' and line[2] != ' ')

def is_fcount(line):
    return ('Function count' in line)

for line in sys.stdin:
    if not is_fname(line):
        continue
    fname = line[2:-2]
        
    # we find the fname, lets find the function count
    for line in sys.stdin:
        if not is_fcount(line):
            continue
        
        fcount = line.split(' ')[-1][:-1]
        
        print(f'{fname} {fcount}')
        break
