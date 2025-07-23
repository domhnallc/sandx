import process_options as po
import tailscale as ts
from pathlib import Path

def run_analysis(input_folder, machines, cpu, experiments, output_folder, num_folders, notify='no'):
    """Runs the analysis on specified machines with given parameters.
    """
    split_input_folder(input_folder, num_folders)
    map_folders_to_machines(input_folder, machines, num_folders, cpu, experiments, output_folder)
    

    
    send_split_folders_to_machines(machines, input_folder, num_folders)

    for machine in machines:
        run_on_machine(machine, cpu, experiments, output_folder)    

def map_folders_to_machines(num_folders: int, input_folders: list[Path], machines: list[str]) -> dict[Path, str]:
    """
    Maps the input folders to the specified machines.
    
    Args:
        input_folder (str): The path to the input folder.
        machines (list): List of machine names or addresses.
        num_folders (int): The number of folders to map.
        cpu (str): The CPU architecture to target.
        experiments (list): List of experiments to run.
        output_folder (str): The folder to store results.
    """
    print(f"Mapping {num_folders} folders from {input_folder} to machines: {machines}")
    folder_machine_map = {}
    split_folders = [f"split_folder_{i}" for i in range(num_folders)]
    for idx, folder in enumerate(split_folders):
        machine = machines[idx % len(machines)]
        folder_machine_map[folder] = machine
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
    for i in range(num_folders):
        split_folder_list.append(f"{input_folder}/split_folder_{i}")
    return split_folder_list

def send_split_folders_to_machines(machines, input_folder, num_folders):
    """
    Sends the split folders to the specified machines.
    
    Args:
        machines (list): List of machine names or addresses.
        input_folder (str): The path to the input folder.
        num_folders (int): The number of folders to send.
    """
    for machine in machines:
        for i in range(num_folders):
            local_folder = f"{input_folder}/split_folder_{i}"
            remote_folder = f"/remote/path/split_folder_{i}"
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