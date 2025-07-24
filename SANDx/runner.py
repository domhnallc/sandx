from pathlib import Path
from shutil import copy2

import process_options as po
import tailscale as ts

import os

def run_analysis(input_folder, selected_machines, cpu, experiments, output_folder, num_folders, notify='no'):
    """Runs the analysis on specified machines with given parameters.
    """
    input_split_folders = split_input_folder(input_folder, num_folders)
    map_folders_to_machines(num_folders, input_split_folders, selected_machines)
    send_split_folders_to_machines(num_folders, selected_machines, input_split_folders) 

    for machine in selected_machines:
        run_on_machine(machine, cpu, experiments, output_folder)    

def map_folders_to_machines(num_folders: int, input_split_folders: list[Path], selected_machines: list[str]) -> dict[Path, str]:
    """
    Maps the input folders to the specified machines.
    
    Args:
        input_split_folders (list[Path]): The list of input split folders.
        machines (list): List of machine names or addresses.
        num_folders (int): The number of folders to map.
        cpu (str): The CPU architecture to target.
        experiments (list): List of experiments to run.
        output_folder (str): The folder to store results.
    """
    print(f"Mapping {num_folders} folders to machines: {selected_machines}")
    folder_machine_map = {}
    for idx, folder in enumerate(input_split_folders):
        machine = selected_machines[idx % len(selected_machines)]
        folder_machine_map[folder] = machine
    print(f"Folder to machine mapping: {folder_machine_map}")
    return folder_machine_map

def split_input_folder(input_folder: Path, num_folders: int) -> list[Path]:
    """
    Splits the input folder into the specified number of folders.
    
    Args:
        input_folder (str): The path to the input folder.
        num_folders (int): The number of folders to split into.
    """
    # Placeholder for splitting logic
    print(f"Splitting {input_folder} into {num_folders} folders...")
    split_folder_list = []
    input_folder = Path(input_folder)
    all_files = sorted([f for f in input_folder.iterdir() if f.is_file()])
    files_per_folder = (len(all_files) + num_folders - 1) // num_folders  # ceil division

    for i in range(num_folders):
        split_subfolder = input_folder.parent / f"{input_folder.name}_{i+1:02d}"
        split_subfolder.mkdir(exist_ok=True)
        split_folder_list.append(split_subfolder)
        start = i * files_per_folder
        end = start + files_per_folder
        for file in all_files[start:end]:   
            copy2(file, split_subfolder)    
    for i in range(num_folders):
        split_folder_list.append(f"{input_folder}/split_folder_{i}")
    return split_folder_list

def send_split_folders_to_machines(num_folders, selected_machines, input_split_folders):
    """
    Sends the split folders to the specified machines.
    
    Args:
        machines (list): List of machine names or addresses.
        input_folder (str): The path to the input folder.
        num_folders (int): The number of folders to send.
    """
    for machine in selected_machines:
        for i in range(num_folders):
            local_folder = f"{input_split_folders[i]}"
            remote_folder = f"/remote/path/split_folder_{i}"
            print(f"Copying {local_folder} to {machine}:{remote_folder}")
            ts.scp_folder_to_tailscale_machine(machine, local_folder, remote_folder)

def run_on_machine(machine, cpu, experiments, output_folder):
    """
    Runs the analysis on the specified machine with the given parameters.
    
    Args:
        machine (str): The machine to run the analysis on.
        cpu (str): The CPU architecture to target.
        experiments (list): List of experiments to run.
        output_folder (str): The folder to store results.
    """
    print(f"Running analysis on {machine} with CPU {cpu} for experiments {experiments}...")
    # Placeholder for running logic
    # Implement the actual running logic here

def main():
    """Main entry point for the script"""
    args = po.get_options()
    po.display_config(args)
    run_analysis(args.input_folder, args.machines, args.cpu, args.experiments, args.output_folder, args.num_folders)
    
    return args  # Return args for further processing if needed


if __name__ == "__main__":
    args = main()