from pathlib import Path
from shutil import copy2
from dataclasses import dataclass
import os

import process_options as po
import tailscale as ts

from experiment import Experiment
import notify

def run_analysis(exp: Experiment):
    """Runs the analysis on specified machines with given parameters.
    """
    split_folder_list = exp.split_folder()
    mapped = exp.map_folders_to_machines(split_folder_list)
    print(mapped.keys)
    exp.send_split_folders_to_machines(mapped)
    for machine, split_folder in mapped.items():
        exp.run_on_machine(machine, split_folder)







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
    run_analysis(exp)
    if exp.notify:
        notify.send_notification(
            url="""https://ntfy.sh/""",
            topic="csit_30_1u",
            message=f"Experiment \n{str(exp)} completed successfully."
        )
    


if __name__ == "__main__":
    args = main()