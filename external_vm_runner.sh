#!/bin/bash


usage() {
    echo "Usage: $0 -i INPUT_FOLDER -c CPU -e EXPERIMENTS -o OUTPUT_FOLDER"
    echo "Required arguments:"
    echo "  -i, --input-folder    Input folder path (mandatory)"
    echo "  -c, --cpu            Target CPU architecture: arm, sparc, 386, m68k, mips, mipsel, powerpc (mandatory)"
    echo "  -e, --experiments    Experiment type: dynamic_opcodes, static_opcodes, syscalls (single choice)"
    echo "  -o, --output-folder  Output folder path to store results (mandatory)"
    echo ""
    echo "  -h, --help           Display this help message"
    echo ""
    echo "Examples:"
    echo "  $0 -i /data/input -c 386 -e dynamic_opcodes -o /data/output"
    echo "  $0 -i /data/input -c arm -e static_opcodes -o /data/output"
    exit 1
}

# Function to validate path exists
validate_existing_path() {
    if [[ ! -d "$1" ]]; then
        echo "Error: Input folder '$1' does not exist"
        exit 1
    fi
}

# Validate CPU choice
validate_cpu() {
    local cpu="$1"
    local valid_cpus=("arm" "sparc" "386" "m68k" "mips" "mipsel" "powerpc")
    
    # Convert to lowercase
    cpu=$(echo "$cpu" | tr '[:upper:]' '[:lower:]')
    
    for valid_cpu in "${valid_cpus[@]}"; do
        if [[ "$cpu" == "$valid_cpu" ]]; then
            echo "$cpu"
            return 0
        fi
    done
    
    echo "Error: Invalid CPU '$1'. Valid options: ${valid_cpus[*]}"
    exit 1
}

# Function to validate experiment choice
validate_experiment() {
    local experiment="$1"
    local valid_experiments=("dynamic_opcodes" "static_opcodes" "syscalls")
    
    for valid_exp in "${valid_experiments[@]}"; do
        if [[ "$experiment" == "$valid_exp" ]]; then
            return 0
        fi
    done
    
    echo "Error: Invalid experiment '$experiment'. Valid options: ${valid_experiments[*]}"
    exit 1
}

# Initialise variables
INPUT_FOLDER=""
CPU=""
EXPERIMENT=""
OUTPUT_FOLDER=""
TEST_MODE=false
echo "CL args"
# Process command line arguments
process_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -i|--input-folder)
                echo "i"
                if [[ -z "$2" || "$2" =~ ^-.*$ ]]; then
                    echo "Error: --input-folder requires a path"
                    usage
                    exit 1
                fi
                INPUT_FOLDER="$2"
                shift 2
                ;;
            -c|--cpu)
                if [[ -z "$2" || "$2" =~ ^-.*$ ]]; then
                    echo "Error: --cpu requires a value"
                    usage
                    exit 1
                    return 1
                fi
                CPU=$(validate_cpu "$2")
                shift 2
                ;;
            -e|--experiments)
                if [[ -z "$2" || "$2" =~ ^-.*$ ]]; then
                    echo "Error: --experiments requires a value"
                    usage
                    exit 1
                fi
                validate_experiment "$2"
                EXPERIMENT="$2"
                shift 2
                ;;
            -o|--output-folder)
                if [[ -z "$2" || "$2" =~ ^-.*$ ]]; then
                    echo "Error: --output-folder requires a path"
                    usage
                    exit 1
                fi
                OUTPUT_FOLDER="$2"
                shift 2
                ;;
            -t|--test-mode)
                TEST_MODE=true
                shift 1
                ;;
            -h|--help)
                usage
                exit 0
                ;;
            *)
                echo "Unknown option: $1"
                usage
                exit 1
                ;;
        esac
    done
}

run() {
    local input_dir="$1"
    echo "run"
    echo "Scanning input folder: $input_dir"
    
    # Find all files in the input directory (not subdirectories)
    local file_count=0
    
    for file in "$input_dir"/*; do
        # Check if it's a regular file (not a directory)
        if [[ -f "$file" ]]; then
            ((file_count++))
            # now you can test the flag
            if [ "$TEST_MODE" = true ]; then
            echo "Running in test mode!"
            test_run_vm "$cpu" "$file"
            else
            run_vm "$cpu" "$file"
            fi

        fi
    done
    
    if [[ $file_count -eq 0 ]]; then
        echo "No files found in input directory: $input_dir"
        return 1
    fi
    
    echo "Processed $file_count file(s) total"
}

test_run_vm(){

	local VM_NAME='charIoT'
	local USER='test'
	local PW='test'
	local TO_EXEC=$1
	local SLEEP=20
	local SNAPSHOT='all_modes'

    if [[ $EXPERIMENT == "dynamic_opcodes" ]]; then
        command_to_run="internal_runner_dynamic_opcode.sh"
    elif [[ $EXPERIMENT == "static_opcodes" ]]; then
        command_to_run="internal_runner_static_opcode.sh"
    elif [[ $EXPERIMENT == "syscalls" ]]; then
        command_to_run="internal_runner_syscalls.sh"
    fi

	#begin session
	echo "vboxmanage snapshot $VM_NAME restore $SNAPSHOT"
	echo "vboxmanage startvm $VM_NAME --type headless"
	
	echo "sleep $SLEEP"
	
	#run file
	echo "echo "Processing  "$TO_EXEC"
	#vboxmanage guestcontrol $VM_NAME --username $USER --password $PW start --exe=/home/admin2/runner_ppc.sh -- "$TO_EXEC"
	echo "vboxmanage guestcontrol $VM_NAME --username admin2 --password admin23 run --timeout 60000 $command_to_run $cpu $TO_EXEC"


	echo "sleep $SLEEP"
	
	#close session
	echo "vboxmanage guestcontrol $VM_NAME closesession --all"
	echo "VBoxManage controlvm $VM_NAME poweroff"
	#rm $TO_EXEC
	echo "sleep 10"
	
}

run_vm(){
    local cpu="$1"
    local input_file="$2"

	local VM_NAME='charIoT'
	local USER='user'
	local PW='password'
	local TO_EXEC=$1
	local SLEEP=20
	local SNAPSHOT='all_modes'

    local command_to_run
	
	#begin session
	vboxmanage snapshot $VM_NAME restore $SNAPSHOT
	vboxmanage startvm $VM_NAME --type gui
	
	sleep $SLEEP
	
	#run file
	echo "Processing  "$TO_EXEC
	#vboxmanage guestcontrol $VM_NAME --username $USER --password $PW start --exe=/home/admin2/runner_ppc.sh -- "$TO_EXEC"
	vboxmanage guestcontrol $VM_NAME --username admin2 --password admin23 run --timeout 60000 $command_to_run $cpu $TO_EXEC

	sleep $SLEEP
	
	#close session
	vboxmanage guestcontrol $VM_NAME closesession --all
	VBoxManage controlvm $VM_NAME poweroff
	#rm $TO_EXEC
	sleep 10
}

print_ascii(){

	echo	 
	echo  ▄▖▄▖▖ ▖▄ ▖▖
	echo  ▚ ▌▌▛▖▌▌▌▚▘
	echo  ▄▌▛▌▌▝▌▙▘▌▌
	echo
		   

}


echo "start"
##############################
#         START              #
##############################
echo "param check"
# Validate required parameters
if [[ -z "$INPUT_FOLDER" || -z "$CPU" || -z "$EXPERIMENT" || -z "$OUTPUT_FOLDER" ]]; then
    echo "Error: Missing required parameters"
    echo "Required:
    -i INPUT_FOLDER 
    -c CPU [arm,sparc,386,m68k,mips,mipsel,powerpc]
    -e EXPERIMENT [dynamic_opcodes,static_opcodes,syscalls]
    -o OUTPUT_FOLDER
    
    Optional:
    -t --test-mode - echo output to run vm, rather than executing."
    usage
fi

echo "validate folder"
# Validate input folder exists
validate_existing_path "$INPUT_FOLDER"

# Create output folder if it doesn't exist
mkdir -p "$OUTPUT_FOLDER"

print_ascii

# Display parsed parameters
echo "================================================"
echo "Experiment Configuration"
echo "================================================"
echo "Input folder:      $INPUT_FOLDER"
echo "CPU architecture:  $CPU"
echo "Experiment:        $EXPERIMENT"
echo "Output folder:     $OUTPUT_FOLDER"
echo
echo "================================================"
echo


    # Processing
echo "Starting."
echo "Running experiment"


run $INPUT_FOLDER

echo "Processing complete!"


