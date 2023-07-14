#!/usr/bin/python3

import sys
import re
import json
import os
import subprocess

from collections import defaultdict

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('input_dir', type=str)
parser.add_argument('aliases', type=str)
parser.add_argument('output_dir', type=str)
args = parser.parse_args()

# handle arguments
with open(args.aliases) as aliases_json:
    aliases = json.load(aliases_json)
in_dir = args.input_dir
o_dir = args.output_dir

# TODO: add an option
WARMUP = 10000000
warmup_count = [0]

# funcname to duration list
result = defaultdict(list)

call_stack = []


def appendResult(fname : str, start_time : float, end_time : float):
    if aliases:
        result[aliases[fname]].append((end_time - start_time))
    else:
        result[fname].append((end_time - start_time))

def isReturnEvent(event : str) -> bool:
    return bool(re.match('.*__return', event))

def handleEntry(fname : str, start_time : float):
    call_stack.append([fname, start_time])

def handleReturn(fname : str, end_time: float):
    if len(call_stack) == 0:
        print("Warning! Unexpected perf event")
        return
    
    (sfname, start_time) = call_stack.pop(-1)
    if sfname != fname:
        print("Warning! Unexpected perf event")
    else:
        appendResult(fname, start_time, end_time)

def dump():
    ofname = o_dir + '/' + 'outdata.warmup' + str(warmup_count[0]) + '.json'
    with open(ofname, 'w') as outfile:
       print(f'store result to {ofname}')
       json.dump(result, outfile, indent=4)
       result.clear()

def main():
    input_files = filter(lambda fname: re.match(r'[\S]+.perf.data.[\S]', fname),
                         os.listdir(in_dir))
    count = 0
    for perf_file in input_files:
        cmd = ['perf', 'script', '-F', 'pid,cpu,event,time', f'--input={in_dir}/{perf_file}']
        perf_input = subprocess.run(cmd, stdout=subprocess.PIPE)
        perf_input = subprocess.run(['uniq'], input=perf_input.stdout, stdout=subprocess.PIPE)
        for perf_line in perf_input.stdout.splitlines():
            # decode string
            perf_line = str(perf_line, encoding='utf-8')
            pattern = re.compile("(?P<pid>.*?)\s\
                                 \[(?P<cpu>.*?)\]\s\
                                 (?P<event_time>.*?):\
                                 \s*probe_(?P<exec_bin>.*?):\
                                 (?P<event>.*?):", re.VERBOSE)
            match = pattern.match(perf_line)
  
            # {pid, cpu exec_bin} are currently unused stuff
            pid = match.group('pid')
            cpu = match.group('cpu')
            exec_bin = match.group('exec_bin')
        
            event_time = float(match.group('event_time'))
            event = match.group('event')

            if not isReturnEvent(event):
                fname = event
                handleEntry(fname, event_time)
            else:
                fname = re.match('(?P<fname>.*?)__return', event).group('fname')
                handleReturn(fname, event_time)

            count+=1
            if count == WARMUP:
                dump()
                warmup_count[0] += 1
                count=0

    dump()

    
if __name__ == '__main__':
    main()
