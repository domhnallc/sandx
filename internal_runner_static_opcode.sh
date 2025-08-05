#!/bin/bash

# $1 is the cpu architecture
# $2 is the input file

if [[ $# -lt 2 ]]; then
    echo -e "ERROR!\nUsage: $0 <cpu> <input_file>"
    exit 1
fi

cpu="$1"
input_file="$2"

experiment="static_opcodes"

# filepaths
qemu_path="/home/admin2/qemu5/qemu/build"
#if [[ ! -d "$qemu_path" ]]; then
#    echo "QEMU path does not exist: $qemu_path"
#    exit 1
#fi
plugin_path="/home/admin2/qemu5/qemu/build/contrib/plugins/libexeclog.so"
shared_folder_path="/home/admin2/shared"
subfolder=""
command_to_run=""


build_experiment() {

    case "$cpu" in
        "m68k")
            subfolder="m68k/$experiment"
            ;;
        "powerpc")
            subfolder="powerpc/$experiment"
            ;;
        "mips")
            subfolder="mips/$experiment"
            ;;
        "mipsel")
            subfolder="mipsel/$experiment"
            ;;

        *)
            echo "Unsupported CPU architecture: $cpu"
            exit 1
            ;;
    esac

    if [[ ! -d "$shared_folder_path/$subfolder" ]]; then
        mkdir -p "$shared_folder_path/$subfolder"
    fi
}

build_experiment

base_static_opcode_command="timeout 10 objdump -D -j .text $input_file > $shared_folder_path/$subfolder/$(basename "$input_file").stat_opcode"

eval $base_static_opcode_command

exit 0
