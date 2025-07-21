import subprocess

def get_tailscale_members():
    base_cmd = "tailscale status"
    filter = "grep -v offline"

    cmd = f"{base_cmd} | {filter}"
    try:
        output = subprocess.check_output(cmd, shell=True, text=True)
        members = []
        for line in output.strip().split('\n'):
            parts = line.split()
            if len(parts) > 1:
                members.append(parts[1])  # Assuming the second part is the member name
        return members


