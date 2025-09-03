#!/bin/bash

# Resides in the shared folder
# Runs inside the VM

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
shared_folder_path="/home/domhnall/shared"
subfolder=""
command_to_run=""
experiment="static_opcodes"

build_experiment() {

    case "$cpu" in
        "sparc")
            subfolder="sparc/$experiment"
            ;;
        "x86_64")
            subfolder="x86_64/$experiment"
            ;;
        "386")
            subfolder="386/$experiment"
            ;;
        "arm")
            subfolder="arm/$experiment"
            ;;
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

#vboxmanage guestcontrol alpine --username USERNAME --password PASSWORD run -- /bin/sh -- /home/admin2/statoptest.sh /bin/ls -- > testbinls.statop
