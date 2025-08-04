#!/bin/bash
# This script is used to run experiments on a specific CPU architecture using QEMU within a VM environment.

m68k_command="/home/admin2/qemu5/qemu/build/qemu-m68k"
powerpc_command="/home/admin2/qemu3/qemu/build/ppc-linux-user/qemu-ppc"
plugin_path="/home/admin2/qemu5/qemu/build/contrib/plugins/libexeclog.so"
shared_folder_path="/home/admin2/shared/"
subfolder=""

base_dynamic_opcode_command="timeout 180  $command_to_run -plugin  $plugin_path\ -d plugin $1 2> $shared_folder_path/$subfolder/$(basename "$1").trace"
base_system_call_command="timeout 10 strace -c -o $shared_folder_path/$subfolder/$(basename "$1").strace $1"
base_static_opcode_command="timeout 10 objdump -D -j .text $1 > $shared_folder_path/$subfolder/$(basename "$1").stat_opcode"

run_experiment() {
    local cpu="$1"
    local experiment="$2"
    local input_file="$3"

    case "$cpu" in
        "m68k")
            command_to_run="$m68k_command"
            subfolder="m68k/$experiment"
            ;;
        "powerpc")
            command_to_run="$powerpc_command"
            subfolder="powerpc/$experiment"
            ;;
        *)
            echo "Unsupported CPU architecture: $cpu"
            exit 1
            ;;
    esac

    case "$experiment" in
        "dynamic_opcodes")
            eval "$base_dynamic_opcode_command"
            ;;
        "static_opcodes")
            eval "$base_static_opcode_command"
            ;;
        "syscalls")
            eval "$base_system_call_command"
            ;;
        *)
            echo "Unsupported experiment type: $experiment"
            exit 1
            ;;
    esac
}