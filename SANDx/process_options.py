#!/usr/bin/env python3
"""
CLI options parser for SANDx analysis tool.
This script provides a command-line interface for configuring the SANDx tool,
allowing users to specify input folders, machines, CPU architectures, experiments,
and output folders. It includes validation for paths and machine lists, ensuring
that the provided configurations are correct before proceeding with the analysis.

# Basic usage
python app.py -i /data/input -m server1,server2 -c x86 -e dynamic_opcodes -o /data/output

# Multiple experiments
python app.py --input-folder /path --machines vm1,vm2,vm3 --cpu arm --experiments dynamic_opcodes,syscalls --output-folder /results

# With custom folder count
python app.py -n 5 -i /input -m machine1 -c mips -e static_opcodes,syscalls -o /output
"""

import argparse
import sys
import os
from pathlib import Path


def parse_machine_list(value):
    """Parse comma-separated list of machines and validate it's not empty"""
    machines = [machine.strip() for machine in value.split(',')]
    machines = [m for m in machines if m]  # Remove empty strings
    
    if not machines:
        raise argparse.ArgumentTypeError("Machine list cannot be empty")
    
    return machines


def validate_existing_path(path):
    """Validate that the input path exists"""
    if not os.path.exists(path):
        raise argparse.ArgumentTypeError(f"Path does not exist: {path}")
    if not os.path.isdir(path):
        raise argparse.ArgumentTypeError(f"Path is not a directory: {path}")
    return Path(path).resolve()


def validate_output_path(path):
    """Validate output path (create if doesn't exist)"""
    output_path = Path(path)
    
    # Create directory if it doesn't exist
    try:
        output_path.mkdir(parents=True, exist_ok=True)
    except (OSError, PermissionError) as e:
        raise argparse.ArgumentTypeError(f"Cannot create output directory {path}: {e}")
    
    return output_path.resolve()


def create_parser():
    """Creates and configures the argument parser"""
    parser = argparse.ArgumentParser(
        description="SANDx Analysis tool for distributing experiments on binary files across architectures",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  runner.py -i /path/to/input -m machine1,machine2 -c x86 -e dynamic_opcodes -o /path/to/output -N yes
  runner.py --input-folder /data --machines vm1,vm2,vm3 --cpu arm --experiments dynamic_opcodes,syscalls --output-folder /results --num-folders 5
        """
    )
    
    # Number of folders (optional, default 1)
    parser.add_argument(
        '-n', '--num-folders',
        type=int,
        default=1,
        help='Number of folders to process (default: 1)'
    )
    
    # Input folder path (mandatory)
    parser.add_argument(
        '-i', '--input-folder',
        type=validate_existing_path,
        required=True,
        help='Input folder path (mandatory)'
    )
    
    # List of machines (mandatory, comma-separated)
    parser.add_argument(
        '-m', '--machines',
        type=parse_machine_list,
        required=True,
        help='Comma-separated list of machines (mandatory)'
    )
    
    # CPU target (mandatory choice)
    parser.add_argument(
        '-c', '--cpu',
        choices=['arm', 'sparc', 'x86', 'm68k', 'mips', 'mipsel', 'powerpc'],
        type=str.lower, # Normalize to lowercase
        required=True,
        help='Target CPU architecture (mandatory)'
    )
    
    # Experiment choices (mandatory, can choose multiple)
    parser.add_argument(
        '-e', '--experiments',
        choices=['dynamic_opcodes', 'static_opcodes', 'syscalls'],
        nargs='+',
        required=True,
        help='Experiment type(s) to run (mandatory, can specify multiple)'
    )
    
    # Output folder (mandatory)
    parser.add_argument(
        '-o', '--output-folder',
        type=validate_output_path,
        required=True,
        help='Output folder path to store results (mandatory)'
    )

    # Output folder (mandatory)
    parser.add_argument(
        '-N', '--notify',
        choices=['yes', 'no'],
        default='no',
        help='Enable or disable notifications (default: no)',
        required=False,
        help='Use ntfy to notify when the analysis is complete (default: no)'
    )
    
    return parser

def display_config(args):
    """Display the parsed configuration"""
    print("Configuration:")
    print(f"Input Folder: {args.input_folder}")
    print(f"Machines: {', '.join(args.machines)}")
    print(f"CPU Architecture: {args.cpu}")
    print(f"Experiments: {', '.join(args.experiments)}")
    print(f"Output Folder: {args.output_folder}")
    print(f"Number of Folders: {args.num_folders}")
    print(f"Notifications: {args.notify}")

def get_options():
    """Main function to parse arguments and validate configuration"""
    parser = create_parser()
    
    try:
        args = parser.parse_args()
    except argparse.ArgumentTypeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    
    return args

