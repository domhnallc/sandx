from pathlib import Path
from shutil import copy2
from dataclasses import dataclass
import os

import process_options as po
import tailscale as ts

from experiment import Experiment

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