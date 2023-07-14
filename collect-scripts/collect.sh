#!/usr/bin/bash

# Usage : sudo ./collect.sh -cmd 'exec <args>'

set -e
# set -x

usage() { echo "Usage: "; exit 1; }

#TODO: add an options
#while getopts ":e" o; do
#    case "${o}" in
#        e)
#	    exec_line=${OPTARG}
#            ;;
#        o)
#            odir=${OPTARG}
#            ;;
#        *)
#            usage
#            ;;
#    esac
#done

# parse functions from binary
parse_funcs() {
  nm --no-demangle --defined-only "$exec_bin"\
            | grep " T "\
	    | awk '{ print $3 }'
}

# $1 -- func_name
# $2 - func alias
perf_set_probe() {
  # try to set entry func event
  if ! perf probe --no-demangle -x "$exec_bin"\
	  --add "$2"="$1" &> /dev/null; then
    echo "Warning! can not set the entry func probe event "$1""
    return 1
  fi

  # try to set func__ return event
  if ! perf probe --no-demangle -x "$exec_bin"\
	  --add "$2"="$1"%return &> /dev/null; then
    # in case of error firstly delete the entry event
    perf probe --no-demangle -x "$exec_bin"\
	  --del probe_"$exec_name":"$2" &> /dev/null
    echo "Warning! can not set the return func probe event "$1""
    return 1
  fi

  # add func to alias table
  FUN_ALIASES["$alias"]="$func"

  return 0
}

perf_record() {
  # TODO: add an option for switch-output
  perf record $1 \
	--switch-output=500M --no-no-buildid  --no-no-buildid-cache \
	--output="$tmp_dir"/"$exec_name".perf.data -- $exec_line \
	|| finish 255

}

process_data() {
  /home/huawei/ml-in-comp/llvm-test-suite/collect-scripts/parse-time.py \
        "$tmp_dir" "$aliases" "$odir" \
	|| finish 255

}

dump_alias_table() {
  for key in "${!FUN_ALIASES[@]}"; do
    echo "$key"
    echo "${FUN_ALIASES[$key]}"
  done |
  jq -n -R 'reduce inputs as $i ({}; . + { ($i): input })' > "$aliases" \
  || finish 255
}

# clean the temporary files and delete perf probes
finish() {
    echo "Warning! temp files were not removed"
    #rm -rf "$tmp_dir" || echo
    perf probe --del probe_"$exec_name_stripped":* > /dev/null
    exit $1
}

declare -A FUN_ALIASES

exec_line="$@"
exec_bin=$(echo $exec_line | cut -d' ' -f1)
exec_name=$(basename "$exec_bin")
tmp_dir=RMME
aliases="$tmp_dir"/"$exec_name".aliases.json

# TODO: add an option for odir
odir="$exec_name"_odir

# strip name of exec due to perf can't correctly handle '-' symbol
exec_name_stripped=$(echo $exec_name | cut -d'-' -f1)

# clear the output dir
rm -rf "$odir" || echo
rm -rf "$tmp_dir" || echo

mkdir $odir
mkdir "$tmp_dir"

funcs=$(parse_funcs)

# collect events and add probes
events_cmd=""
declare -i n=0
for func in $funcs; do
  n=n+1
  alias=func"$n"
  
  if ! perf_set_probe $func $alias; then
    continue
  fi
  
  # add events to record table
  events_cmd+="-e probe_"$exec_name_stripped":"$alias" \
	       -e probe_"$exec_name_stripped":"$alias"__return "
done

dump_alias_table

perf_record "$events_cmd"
process_data "$odir"

finish 0
