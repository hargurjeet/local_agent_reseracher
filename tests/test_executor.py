import os
import sys
import shutil
import json

# Add the project root to Python search path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.executor import ExecutorRunner

MOCK_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tests", "mock_executor_downloads")
WORKSPACE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tests", "mock_executor_workspace")

def create_mock_sandbox():
    """
    Creates temporary mock directories and files.
    """
    if os.path.exists(MOCK_DIR):
        shutil.rmtree(MOCK_DIR)
    os.makedirs(MOCK_DIR)

    if os.path.exists(WORKSPACE_DIR):
        shutil.rmtree(WORKSPACE_DIR)
    os.makedirs(WORKSPACE_DIR)

    sample_files = ["file1.txt", "file2.txt"]
    for fname in sample_files:
        with open(os.path.join(MOCK_DIR, fname), "w") as f:
            f.write(f"sample content for {fname}")
        print(f" - Seeded file: {fname}")

def cleanup_mock_sandbox():
    """
    Wipes temporary mock directories.
    """
    if os.path.exists(MOCK_DIR):
        shutil.rmtree(MOCK_DIR)
    if os.path.exists(WORKSPACE_DIR):
        shutil.rmtree(WORKSPACE_DIR)
    print("Cleaned up sandbox and workspace folders.")

def test_executor():
    create_mock_sandbox()
    
    proposed_moves = {
        "file1.txt": "Documents/file1.txt",
        "file2.txt": "Media/file2.txt"
    }

    print("\nInitializing Executor Runner...")
    runner = ExecutorRunner()

    print("Executing file moves plan...")
    try:
        output = runner.execute_plan(
            downloads_path=MOCK_DIR,
            workspace_path=WORKSPACE_DIR,
            proposed_moves=proposed_moves
        )

        print("\n🟢 Executor Agent Execution Success!")
        print(f"Status: {output.status}")
        print(f"Executed Moves: {output.executed_moves}")

        # Assertions
        assert output.status == "success", f"Expected status 'success', got '{output.status}'"
        assert len(output.executed_moves) == 2, "Expected 2 executed moves"

        # Check physical file relocation
        dest1 = os.path.join(MOCK_DIR, "Documents", "file1.txt")
        dest2 = os.path.join(MOCK_DIR, "Media", "file2.txt")
        assert os.path.exists(dest1), f"File was not moved to {dest1}"
        assert os.path.exists(dest2), f"File was not moved to {dest2}"

        # Verify transaction log
        history_path = os.path.join(WORKSPACE_DIR, "history.json")
        assert os.path.exists(history_path), "history.json transaction log was not created"
        with open(history_path, "r") as f:
            history_data = json.load(f)
        
        print(f"Written transaction log: {history_data}")
        assert history_data.get("file1.txt") == "Documents/file1.txt"
        assert history_data.get("file2.txt") == "Media/file2.txt"

        print("🟢 All executor assertions passed successfully!")

    except Exception as e:
        print(f"\n🔴 Executor Test Failed: {e}")
        raise e
    finally:
        cleanup_mock_sandbox()

if __name__ == "__main__":
    test_executor()
