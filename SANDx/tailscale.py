import subprocess

def get_online_tailscale_members():
    """
    Retrieves a list of online Tailscale members by executing the 'tailscale status' command
    and filtering out offline entries.

    Returns:
        list: A list of member names (as strings) that are currently online.

    Notes:
        - Assumes the second column in the 'tailscale status' output is the member name.
        - Returns an empty list if the command fails or no online members are found.
    """
    base_cmd = "tailscale status"
    filter = "grep -v offline"

    cmd = f"{base_cmd} | {filter}"
    try:
        output = subprocess.check_output(cmd, shell=True, text=True)
        members = []
        for line in output.strip().split('\n'):
            if len(line) == 0 or line.startswith('#'):
                pass
            else:
                parts = line.split()
                if len(parts) > 1:
                    members.append(parts[1])  # Assuming the second part is the member name
        return members
    except subprocess.CalledProcessError as e:
        print("error" + e.output)
        return []
    

def select_tailscale_machines(online_machines, user_selected_machines):
    """
    Filters the list of online Tailscale machines based on user selection.

    Args:
        online_machines (list): List of online Tailscale machine names.
        user_selected_machines (list): List of machine names selected by the user.

    Returns:
        list: A list of machines that are both online and selected by the user.
    """
    return [machine for machine in online_machines if machine in user_selected_machines]

def scp_folder_to_tailscale_machine(machine, local_folder, remote_folder, user="admin2"):
    """
    Copies a local folder to a remote folder on a Tailscale machine using SCP.

    Args:
        machine (str): The Tailscale machine's address (hostname or IP).
        local_folder (str): The path to the local folder to copy.
        remote_folder (str): The destination path on the remote machine.

    Raises:
        subprocess.CalledProcessError: If the SCP command fails.

    Prints:
        Success or failure message indicating the result of the copy operation.
    """
    cmd = f"scp -r {local_folder} {user}@{machine}:{remote_folder}"
    try:
        subprocess.check_call(cmd, shell=True)
        print(f"Successfully copied {local_folder} to {machine}:{remote_folder}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to copy folder to {machine}: {e}")

def run_command_on_tailscale_machine(machine, command, user="admin2"):
    """
    Executes a command on a Tailscale machine via SSH.

    Args:
        machine (str): The Tailscale machine's address (hostname or IP).
        command (str): The command to execute on the remote machine.
        user (str): The username to use for SSH (default is "admin2").

    Raises:
        subprocess.CalledProcessError: If the SSH command fails.

    Prints:
        The output of the executed command or an error message if it fails.
    """
    cmd = f"ssh {user}@{machine} '{command}'"
    try:
        output = subprocess.check_output(cmd, shell=True, text=True)
        print(f"Command output from {machine}:\n{output}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to run command on {machine}: {e.output}")


    
def main():
    online_machines = get_online_tailscale_members()


    # Example of adding test machines

    print(online_machines)

if __name__ == "__main__":
    args = main()
