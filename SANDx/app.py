import streamlit as st
from tailscale import get_online_tailscale_members

machines = get_online_tailscale_members()
machines.append("test-machine-1")
machines.append("test-machine-2")

def choose_executable_folder():
    """
    Displays a file uploader widget for selecting a folder to execute commands in.

    Returns:
        str: The path to the selected folder.
    """
    folder_path = st.file_uploader("Choose a folder", type=["zip", "tar", "gz","txt"], accept_multiple_files=True, key="folder_uploader")
    return folder_path

def display_select_tailscale_nodes(machines):
    """
    Displays a multiselect widget for selecting Tailscale nodes.

    Returns:
        list: A list of selected Tailscale nodes.
    """
    selected_nodes = st.multiselect("Select Tailscale Nodes to Run", options=machines)
    return selected_nodes

def enumerate_selected_files():
    """
    Enumerates the selected files from the file uploader.

    Returns:
        list: A list of paths to the selected files.
    """
    no_files = len(st.session_state.folder_uploader)
    if no_files == 0:
        st.warning("No files selected.")
        return []
    
    return st.write(f"Selected {no_files} files:")

def enumerate_selected_nodes(selected_nodes):
    """
    Displays the selected Tailscale nodes.

    Args:
        selected_nodes (list): List of selected Tailscale nodes.
    """
    if not selected_nodes:
        st.warning("No Tailscale nodes selected.")
    else:
        no_nodes = len(selected_nodes)
        st.write(f"Selected {no_nodes} Tailscale nodes:")
        for node in selected_nodes:
            st.write(f"- {node}")


choose_executable_folder()
enumerate_selected_files()
#display_select_tailscale_nodes(machines)
enumerate_selected_nodes(display_select_tailscale_nodes(machines))