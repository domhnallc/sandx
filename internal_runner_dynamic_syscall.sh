#!/bin/bash

# $1 is the cpu architecture
# $2 is the input file

if [[ $# -lt 2 ]]; then
    echo -e "ERROR!\nUsage: $0 <cpu> <input_file>"
    exit 1
fi

cpu="$1"
input_file="$2"
plugin_path="/home/admin2/qemu5/qemu/build/contrib/plugins/libexeclog.so"
shared_folder_path="/home/admin2/shared/"
subfolder=""


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

base_system_call_command="timeout 10 strace -c -o $shared_folder_path/$subfolder/$(basename "$input_file").strace $input_file"
eval $base_system_call_command

exit 0