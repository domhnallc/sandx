import config as cfg

from pathlib import Path
from shutil import copy2
from dataclasses import dataclass
import os
import process_options as po
import tailscale as ts
import subprocess
import os
import shutil
import math
from pathlib import Path
from typing import List, Optional


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
      
        print(f"Mapping {self.num_folders} folders to machines: {self.selected_machines}")
        folder_machine_map = {}
        for idx, folder in enumerate(split_folder_list):
            machine = self.selected_machines[idx % len(self.selected_machines)]
            folder_machine_map[folder] = machine
        print(f"Folder to machine mapping: {folder_machine_map}")
        return folder_machine_map


    def split_folder(self) -> List[str]:
        """
        Split a folder into n parts by distributing files across multiple subdirectories.
        
        Args:
            source_folder (str): Path to the source folder to split
            n_parts (int): Number of parts to split the folder into
            output_base (str, optional): Base path for output folders. If None, creates
                                    subfolders in the same directory as source_folder
        
        Returns:
            List[str]: List of paths to the created split folders
        
        Raises:
            ValueError: If n_parts <= 0 or source_folder doesn't exist
            OSError: If there are permission issues creating directories or copying files
        """
        if self.num_folders <= 0:
            raise ValueError("Number of parts must be greater than 0")
        
        source_path = Path(self.input_folder)
        if not source_path.exists():
            raise ValueError(f"Source folder '{self.input_folder}' does not exist")
        
        if not source_path.is_dir():
            raise ValueError(f"'{self.input_folder}' is not a directory")
        
        # Get all files in the source folder (recursively)
        all_files = []
        for root, dirs, files in os.walk(self.input_folder):
            for file in files:
                file_path = os.path.join(root, file)
                # Store both absolute path and relative path from source
                rel_path = os.path.relpath(file_path, self.input_folder)
                all_files.append((file_path, rel_path))
        
        if not all_files:
            raise ValueError("Source folder is empty")
        
        # Determine output base directory
        if self.output_folder is None:
            output_base = source_path.parent
        else:
            output_base = Path(self.output_folder)
        
        # Create split folder names
        source_name = source_path.name
        split_folders = []
        for i in range(self.num_folders):
            folder_name = f"{source_name}_part_{i+1}"
            split_path = output_base / folder_name
            split_folders.append(str(split_path))
        
        # Calculate files per part
        files_per_part = math.ceil(len(all_files) / self.num_folders)
        
        # Create directories and distribute files
        created_folders = []
        
        try:
            for i, split_folder in enumerate(split_folders):
                # Create split folder
                os.makedirs(split_folder, exist_ok=True)
                created_folders.append(split_folder)
                
                # file range for this part
                start_idx = i * files_per_part
                end_idx = min(start_idx + files_per_part, len(all_files))
                
                if start_idx >= len(all_files):
                    # No more files to distribute
                    continue
                
                # Copy files to this part
                for j in range(start_idx, end_idx):
                    src_file, rel_path = all_files[j]
                    dst_file = os.path.join(split_folder, rel_path)
                    
                    # Create subdirectories if needed
                    dst_dir = os.path.dirname(dst_file)
                    if dst_dir:
                        os.makedirs(dst_dir, exist_ok=True)
                    
                    # Copy the file
                    shutil.copy2(src_file, dst_file)
        
        except Exception as e:
            for folder in created_folders:
                if os.path.exists(folder):
                    shutil.rmtree(folder, ignore_errors=True)
            raise OSError(f"Error creating split folders: {e}")
        
        return split_folders

    
    def send_split_folders_to_machines(machine_split_map: dict[Path, str]):
        """        Sends split folders to the specified machines using SCP.
        Args:
            machine_split_map (dict[Path, str]): Mapping of split folders to machines.
        """

        remote_path = cfg.remote_path

        for machine in machine_split_map.values():
            local_folder = f"{machine.key}"
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