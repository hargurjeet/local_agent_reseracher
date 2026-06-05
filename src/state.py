from typing import List, Dict
from pydantic import BaseModel, Field

class FileMetadata(BaseModel):
    filename: str = Field(description="Name of the file including extension")
    extension: str = Field(description="Extension of the file (e.g., pdf, png)")
    size_bytes: int = Field(description="Size of the file in bytes")

class Subtask(BaseModel):
    task_id: str = Field(description="Unique task identifier (e.g., task_1)")
    category: str = Field(description="General category of the files (e.g., Documents, Media, Installers)")
    files: List[str] = Field(description="List of filenames belonging to this category")

class FolderOrganizeState(BaseModel):
    downloads_path: str = Field(default="", description="Path of the downloads folder to organize")
    all_files: List[FileMetadata] = Field(default_factory=list, description="List of all files detected in the folder")
    tasks: List[Subtask] = Field(default_factory=list, description="Targeted subagent tasks grouped by category")
    proposed_moves: Dict[str, str] = Field(default_factory=dict, description="Consolidated mapping of original file names to target paths")
    status: str = Field(default="planning", description="Workflow state (planning, awaiting_approval, approved, executed, aborted)")
