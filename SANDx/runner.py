from pathlib import Path
from shutil import copy2
from dataclasses import dataclass
import os

import process_options as po
import tailscale as ts

import config as cfg

# Define the experiment class to hold the parameters for running the analysis
@dataclass
class Experiment:
    
    def __init__(self, input_folder: Path, selected_machines: list[str], 
                 cpu: str, experiments: list[str], output_folder: str, 
                 num_folders: int = 1, notify: bool = False):
        self.input_folder = input_folder
        self.selected_machines = selected_machines
        self.cpu = cpu
        self.experiments = experiments
        self.output_folder = output_folder
        self.num_folders = num_folders
        self.notify = notify
    
    def __str__(self):
        return (f"Experiment(input_folder:{self.input_folder}, "
                f"selected_machines:{self.selected_machines}, "
                f"cpu:{self.cpu}, "
                f"experiments:{self.experiments}, "
                f"output_folder:{self.output_folder}, "
                f"num_folders:{self.num_folders}, "
                f"notify:{self.notify})")
    
    def map_folders_to_machines(self) -> dict[Path, str]:
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
        print(f"Mapping {self.num_folders} folders to machines: {self.selected_machines}")
        folder_machine_map = {}
        for idx, folder in enumerate(self.input_split_folders):
            machine = self.selected_machines[idx % len(self.selected_machines)]
            folder_machine_map[folder] = machine
        print(f"Folder to machine mapping: {folder_machine_map}")
        return folder_machine_map

    def split_input_folder(self) -> list[Path]:
        """
        Splits the input folder into the specified number of folders.
        
        Args:
            input_folder (str): The path to the input folder.
            num_folders (int): The number of folders to split into.
        """
        print(f"Splitting {self.input_folder} into {self.num_folders} folders...")
        split_folder_list = []
        all_files = sorted([f for f in self.input_folder.iterdir() if f.is_file()])
        files_per_folder = (len(all_files) + self.num_folders - 1) // self.num_folders  # ceil division
        # loop to split files into folders
        for i in range(self.num_folders):
            split_subfolder = self.input_folder.parent / f"{self.input_folder.name}_{i+1:02d}"
            split_subfolder.mkdir(exist_ok=True)
            split_folder_list.append(split_subfolder)
            start = i * files_per_folder
            end = start + files_per_folder
            for file in all_files[start:end]:   
                copy2(file, split_subfolder)    
        print(f"Created split folders: {split_folder_list}")
        return split_folder_list
    
    def send_split_folders_to_machines(self):
        """
        Sends the split folders to the specified machines.
        
        Args:
            machines (list): List of machine names or addresses.
            input_folder (str): The path to the input folder.
            num_folders (int): The number of folders to send.
        """
        remote_path = cfg.remote_path

        for machine in self.selected_machines:
            for i in range(self.num_folders):
                local_folder = f"{self.input_split_folders[i]}"
                
                print(f"Copying {local_folder} to {machine}:{remote_path}")
                try:
                    ts.scp_folder_to_tailscale_machine(machine, local_folder, remote_path)
                except Exception as e:
                    print(f"Error copying to {machine}:{remote_path} - {e}")
                print(f"Copied {local_folder} to {machine}:{remote_path}")
    def run_on_machine(self):
        
        """        Runs the analysis on the specified machine with given parameters.
        """
        print(f"Running analysis on {machine} with CPU {cpu} for experiments {experiments}...")
        # Placeholder for running logic
        # Implement the actual running logic here

def run_analysis(exp: Experiment):
    """Runs the analysis on specified machines with given parameters.
    """
    input_split_folders = exp.split_input_folder(exp.input_folder, exp.num_folders)
    map_folders_to_machines(exp.num_folders, input_split_folders, exp.selected_machines)
    send_split_folders_to_machines(exp.num_folders, exp.selected_machines, input_split_folders)

    for machine in exp.selected_machines:
        run_on_machine(machine, exp.cpu, exp.experiments, exp.output_folder)








def main():
    """Main entry point for the script"""
    args = po.get_options()
    po.display_config(args)
    exp = Experiment(   
        input_folder=Path(args.input_folder),
        selected_machines=args.machines,
        cpu=args.cpu,
        experiments=args.experiments,
        output_folder=args.output_folder,
        num_folders=args.num_folders,
        notify=args.notify
    )
    run_analysis(exp))
    
    return args  # Return args for further processing if needed


if __name__ == "__main__":
    args = main()