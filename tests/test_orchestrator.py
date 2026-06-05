import os
import sys
import shutil

# Add the project root to Python search path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.tools import list_directory_metadata
from agents.orchestrator import OrchestratorPlanner

# Target path for sandbox downloads
MOCK_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tests", "mock_downloads")

def create_mock_sandbox():
    """
    Creates a temporary directory with dummy files for testing.
    """
    if os.path.exists(MOCK_DIR):
        shutil.rmtree(MOCK_DIR)
    os.makedirs(MOCK_DIR)
    
    # Create sample files
    sample_files = [
        "uber_receipt_may2026.pdf",
        "tax_return_form.pdf",
        "family_photo.png",
        "vacation_video.mp4",
        "chrome_installer.dmg",
        "script.py"
    ]
    
    print(f"Creating sandbox folder at: {MOCK_DIR}")
    for fname in sample_files:
        filepath = os.path.join(MOCK_DIR, fname)
        with open(filepath, "w") as f:
            f.write(f"dummy data for {fname}")
        print(f" - Created file: {fname}")

def cleanup_mock_sandbox():
    """
    Wipes the temporary sandbox directory.
    """
    if os.path.exists(MOCK_DIR):
        shutil.rmtree(MOCK_DIR)
        print(f"Cleaned up sandbox folder.")

def test_orchestrator():
    # 1. Setup mock folder
    create_mock_sandbox()
    
    # 2. Scan folder using Python tool
    print("\nScanning mock folder...")
    files = list_directory_metadata(MOCK_DIR)
    print(f"Found {len(files)} files.")
    for f in files:
        print(f" - {f.filename} ({f.extension}), size: {f.size_bytes} bytes")
        
    # 3. Instantiate Orchestrator Agent
    print("\nInitializing Orchestrator Agent (Ollama + CrewAI)...")
    planner = OrchestratorPlanner()
    
    # 4. Generate structured subtasks
    print("Generating categorization plan...")
    try:
        tasks = planner.generate_tasks(files)
        print("\n🟢 Orchestrator Output Success!\n")
        
        for task in tasks:
            print(f"Category: [bold]{task.category}[/bold] (ID: {task.task_id})")
            print("Files in this category:")
            for filename in task.files:
                print(f"  - {filename}")
            print()
            
    except Exception as e:
        print(f"\n🔴 Orchestrator Run Failed: {e}")
        
    # 5. Clean up sandbox
    cleanup_mock_sandbox()

if __name__ == "__main__":
    test_orchestrator()
