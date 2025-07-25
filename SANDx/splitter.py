
import os
import shutil
import math
from pathlib import Path
from typing import List, Optional


def split_folder(source_folder: str, n_parts: int, output_base: Optional[str] = None) -> List[str]:
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
    if n_parts <= 0:
        raise ValueError("Number of parts must be greater than 0")
    
    source_path = Path(source_folder)
    if not source_path.exists():
        raise ValueError(f"Source folder '{source_folder}' does not exist")
    
    if not source_path.is_dir():
        raise ValueError(f"'{source_folder}' is not a directory")
    
    # Get all files in the source folder (recursively)
    all_files = []
    for root, dirs, files in os.walk(source_folder):
        for file in files:
            file_path = os.path.join(root, file)
            # Store both absolute path and relative path from source
            rel_path = os.path.relpath(file_path, source_folder)
            all_files.append((file_path, rel_path))
    
    if not all_files:
        raise ValueError("Source folder is empty")
    
    # Determine output base directory
    if output_base is None:
        output_base = source_path.parent
    else:
        output_base = Path(output_base)
    
    # Create split folder names
    source_name = source_path.name
    split_folders = []
    for i in range(n_parts):
        folder_name = f"{source_name}_part_{i+1}"
        split_path = output_base / folder_name
        split_folders.append(str(split_path))
    
    # Calculate files per part
    files_per_part = math.ceil(len(all_files) / n_parts)
    
    # Create directories and distribute files
    created_folders = []
    
    try:
        for i, split_folder in enumerate(split_folders):
            # Create the split folder
            os.makedirs(split_folder, exist_ok=True)
            created_folders.append(split_folder)
            
            # Calculate file range for this part
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
        # Clean up created folders on error
        for folder in created_folders:
            if os.path.exists(folder):
                shutil.rmtree(folder, ignore_errors=True)
        raise OSError(f"Error creating split folders: {e}")
    
    return split_folders
    
split_folder('/home/domhnall/test',2)