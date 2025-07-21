import subprocess

def get_online_tailscale_members():
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

def scp_folder_to_tailscale_machine(machine, local_folder, remote_folder):
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
    cmd = f"scp -r {local_folder} {machine}:{remote_folder}"
    try:
        subprocess.check_call(cmd, shell=True)
        print(f"Successfully copied {local_folder} to {machine}:{remote_folder}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to copy folder to {machine}: {e}")
    
def main():
    online_machines = get_online_tailscale_members()
    print(online_machines)

main()
