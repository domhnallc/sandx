#!/bin/bash

# $1 is the cpu architecture
# $2 is the input file

if [[ $# -lt 2 ]]; then
    echo -e "ERROR!\nUsage: $0 <cpu> <input_file>"
    exit 1
fi

cpu="$1"
input_file="$2"

experiment="dynamic_opcodes"

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

# qemu commands for different CPU architectures
m68k_command="$qemu_path/qemu-m68k"
powerpc_command="$qemu_path/ppc-linux-user/qemu-ppc"
mips_command="$qemu_path/qemu-mips"
mipsel_command="$qemu_path/qemu-mipsel"



build_experiment() {

    case "$cpu" in
        "m68k")
            command_to_run="$m68k_command"
            subfolder="m68k/$experiment"
            ;;
        "powerpc")
            command_to_run="$powerpc_command"
            subfolder="powerpc/$experiment"
            ;;
        "mips")
            command_to_run="$mips_command"
            subfolder="mips/$experiment"
            ;;
        "mipsel")
            command_to_run="$mipsel_command"
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

base_dynamic_opcode_command="timeout 180 $command_to_run -plugin $plugin_path -d plugin $input_file 2> $shared_folder_path/$subfolder/$(basename "$input_file").trace"

eval $base_dynamic_opcode_command 


