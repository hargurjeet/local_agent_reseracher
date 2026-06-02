import os
from typing import Any
from crewai.tools import tool

# Base path for the local agent workspace
WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FINDINGS_DIR = os.path.join(WORKSPACE_ROOT, "workspace", "raw_findings")

# Ensure findings directory exists
os.makedirs(FINDINGS_DIR, exist_ok=True)

def _resolve_safe_path(target_path: str) -> str:
    """
    Resolves target_path relative to WORKSPACE_ROOT and ensures it cannot escape.
    """
    # Clean up target path
    target_path = target_path.strip().lstrip("/")
    # Handle wildcard paths from agent outputs
    if target_path.endswith("*"):
        target_path = target_path[:-1].rstrip("/")
        
    resolved = os.path.abspath(os.path.join(WORKSPACE_ROOT, target_path))
    if not resolved.startswith(WORKSPACE_ROOT):
        raise ValueError(f"Security Alert: Target path '{target_path}' is outside the workspace root!")
    return resolved

def _extract_string_arg(arg: Any, key_fallback: str) -> str:
    """
    Safely extracts a string argument, handling cases where the model
    passes a dictionary instead of a raw string.
    """
    if isinstance(arg, dict):
        # Look for typical parameter keys
        for key in [key_fallback, "target_path", "file_path", "content", "task_id"]:
            if key in arg and isinstance(arg[key], str):
                return arg[key]
        # Ignore schema definition leaks
        if "description" in arg:
            return ""
        # Return first string value found
        for val in arg.values():
            if isinstance(val, str):
                return val
    return str(arg) if arg is not None else ""


# --- Tools ---

@tool("List Workspace Files")
def list_workspace_files(target_path: Any = None) -> str:
    """
    Recursively lists all files in the target directory relative to the workspace.
    Parameter 'target_path' should be a string path (e.g., 'src/').
    """
    try:
        path_str = _extract_string_arg(target_path, "target_path")
        safe_path = _resolve_safe_path(path_str)
        if not os.path.exists(safe_path):
            return f"Error: Path '{path_str}' does not exist."
            
        if os.path.isfile(safe_path):
            return f"File found: {path_str} (size: {os.path.getsize(safe_path)} bytes)"
            
        files_list = []
        for root, _, files in os.walk(safe_path):
            # Ignore hidden files, virtual environments, node_modules, and cache
            if any(p in root for p in [".git", ".venv", "node_modules", "__pycache__", "docs", "workspace"]):
                continue
            for f in files:
                full_p = os.path.join(root, f)
                rel_p = os.path.relpath(full_p, WORKSPACE_ROOT)
                files_list.append(rel_p)
                
        if not files_list:
            return f"No files found under directory '{path_str}'."
        return "\n".join(files_list)
    except Exception as e:
        return f"Error listing files: {e}"


@tool("Read File Content")
def read_file_content(file_path: Any = None) -> str:
    """
    Reads the content of a specific code or text file in the workspace.
    Parameter 'file_path' should be the path of the file relative to the workspace root (e.g., 'src/state.py').
    """
    try:
        path_str = _extract_string_arg(file_path, "file_path")
        safe_path = _resolve_safe_path(path_str)
        if not os.path.exists(safe_path) or not os.path.isfile(safe_path):
            return f"Error: File '{path_str}' does not exist or is a directory."
            
        # Read max 1000 lines or 50KB to preserve model context limits
        max_bytes = 50 * 1024
        with open(safe_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read(max_bytes)
            
        suffix = "\n[Content truncated due to size limits]" if os.path.getsize(safe_path) > max_bytes else ""
        return f"--- FILE CONTENT: {path_str} ---\n{content}{suffix}"
    except Exception as e:
        return f"Error reading file: {e}"


@tool("Save Subagent Findings")
def save_subagent_findings(task_id: Any = None, content: Any = None) -> str:
    """
    Saves the subagent's raw findings to local workspace storage.
    Parameters should be: 'task_id' (e.g., 'task_1') and 'content' (findings summary text).
    """
    try:
        # Extract task_id and content safely from dictionary or direct arguments
        t_id = ""
        cont = ""
        
        if isinstance(task_id, dict):
            t_id = _extract_string_arg(task_id, "task_id")
            cont = _extract_string_arg(task_id, "content")
        else:
            t_id = _extract_string_arg(task_id, "task_id")
            cont = _extract_string_arg(content, "content")
            
        t_id = t_id.strip()
        cont = cont.strip()
        
        # Validate task_id format
        if not t_id.startswith("task_"):
            return "Error: task_id must follow the format 'task_x'"
            
        safe_name = f"{t_id}.txt"
        file_path = os.path.join(FINDINGS_DIR, safe_name)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(cont)
            
        return f"Success: Findings for {t_id} successfully saved to local cache."
    except Exception as e:
        return f"Error saving findings: {e}"
