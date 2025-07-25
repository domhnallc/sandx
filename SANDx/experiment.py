import config as cfg

from pathlib import Path
from shutil import copy2
from dataclasses import dataclass
import os
import process_options as po
import tailscale as ts
import subprocess

@dataclass
class Experiment:
    '''Represents an experiment workflow that manages input data, splits it into folders, maps folders to machines,
    transfers data to remote machines, and runs analyses.
    Attributes:
        input_folder (Path): Path to the folder containing input data.
        selected_machines (list[str]): List of machine names or addresses to use for the experiment.
        cpu (str): Target CPU architecture for running the experiment.
        experiments (list[str]): List of experiment identifiers or names to run.
        output_folder (str): Path to the folder where results will be stored.
        num_folders (int, optional): Number of folders to split the input data into. Defaults to 1.
        notify (bool, optional): Whether to send notifications upon completion. Defaults to False.
    Methods:
        __str__():
            Returns a string representation of the Experiment instance.
        map_folders_to_machines() -> dict[Path, str]:
            Maps split input folders to the specified machines in a round-robin fashion.
        split_input_folder() -> list[Path]:
            Splits the input folder into the specified number of subfolders, distributing files evenly.
        send_split_folders_to_machines():
            Transfers each split folder to its assigned machine using SCP.
        run_on_machine():
            SSHs a command that runs the analysis on the specified machine(s) with the given parameters.'''

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
    
    def map_folders_to_machines(self, split_folder_list: list) -> dict[Path, str]:
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
        for idx, folder in enumerate(split_folder_list):
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


    #def run_on_machine(self, split_folder: Path):
    #    """
    #    Runs the analysis on the specified machine with given parameters.
    #    """
    #    print(f"Running analysis on {machine} with CPU {cpu} for experiments {experiments}...")
    #
#
 #       cmd = f"./vm_runner.sh {split_folder}"
  #      
   #     ts.run_command_on_tailscale_machine(machine, cmd, user='admin2')