import os
import shutil
import json
from typing import List
from crewai.tools import tool
from src.state import FileMetadata

def list_directory_metadata(directory_path: str) -> List[FileMetadata]:
    """
    Scans a directory and returns metadata (filename, extension, size) for all files.
    This is a simple Python helper function.
    """
    if not os.path.exists(directory_path):
        return []
        
    metadata_list = []
    
    # List files in the directory (non-recursive to keep it simple for Downloads)
    for entry in os.scandir(directory_path):
        if entry.is_file():
            # Skip hidden files
            if entry.name.startswith("."):
                continue
                
            name_parts = entry.name.rsplit(".", 1)
            ext = name_parts[1] if len(name_parts) > 1 else ""
            
            metadata = FileMetadata(
                filename=entry.name,
                extension=ext.lower(),
                size_bytes=entry.stat().st_size
            )
            metadata_list.append(metadata)
            
    return metadata_list

@tool("Create Directory")
def create_directory(directory_path: str) -> str:
    """
    Safely creates a directory if it does not exist.
    Input must be a valid directory path string.
    """
    try:
        os.makedirs(directory_path, exist_ok=True)
        return f"Successfully created or verified directory: {directory_path}"
    except Exception as e:
        return f"Failed to create directory {directory_path}: {e}"

@tool("Move File")
def move_file(source_path: str, destination_path: str) -> str:
    """
    Safely moves a file from source_path to destination_path.
    If the destination directory does not exist, it creates it first.
    Input must be the source_path and destination_path strings.
    """
    try:
        dest_dir = os.path.dirname(destination_path)
        if dest_dir:
            os.makedirs(dest_dir, exist_ok=True)
        # Using shutil.move which safely handles cross-device movements as well
        shutil.move(source_path, destination_path)
        return f"Successfully moved file from '{source_path}' to '{destination_path}'"
    except Exception as e:
        return f"Failed to move file from '{source_path}' to '{destination_path}': {e}"

# Module level variable to simplify tool parameter requirements for local LLMs
HISTORY_LOG_PATH = "workspace/history.json"

@tool("Write Transaction Log")
def write_transaction_log(transactions_json: str) -> str:
    """
    Writes the transaction rollback log to history.json.
    Input must be a JSON string mapping source filenames to their target relative paths.
    """
    log_path = HISTORY_LOG_PATH
    try:
        import ast
        # Attempt to parse python-style single-quoted dictionaries or JSON
        try:
            data = ast.literal_eval(transactions_json)
        except Exception:
            data = json.loads(transactions_json)
            
        if not isinstance(data, dict):
            raise ValueError("Parsed data is not a dictionary mapping.")
            
        # Ensure parent directories for the log file exist
        log_dir = os.path.dirname(log_path)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        with open(log_path, "w") as f:
            json.dump(data, f, indent=4)
        return f"Successfully wrote transaction log to {log_path}"
    except Exception as e:
        return f"Failed to write transaction log to {log_path}: {e}"



