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
    
def main():
    online_machines = get_online_tailscale_members()
    print(online_machines)

main()
