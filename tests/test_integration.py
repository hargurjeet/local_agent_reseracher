import os
import sys
import shutil
import json

# Add project root to python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.main import LocalAgentOrganizer

MOCK_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tests", "mock_integration_downloads")
WORKSPACE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tests", "mock_integration_workspace")

def create_mock_sandbox():
    """
    Creates a temporary sandbox folder with mock files.
    """
    if os.path.exists(MOCK_DIR):
        shutil.rmtree(MOCK_DIR)
    os.makedirs(MOCK_DIR)

    if os.path.exists(WORKSPACE_DIR):
        shutil.rmtree(WORKSPACE_DIR)
    os.makedirs(WORKSPACE_DIR)

    sample_files = [
        "tax_return_2025.pdf",
        "quarterly_financial_report.pdf",
        "family_photo_hawaii.png",
        "vacation_vlog.mp4",
        "web_server_script.py",
        "package_installer.dmg"
    ]

    print(f"Creating sandbox folder at: {MOCK_DIR}")
    for fname in sample_files:
        filepath = os.path.join(MOCK_DIR, fname)
        with open(filepath, "w") as f:
            f.write(f"mock contents for {fname}")
        print(f" - Created file: {fname}")

def cleanup_mock_sandbox():
    """
    Cleans up mock directories.
    """
    if os.path.exists(MOCK_DIR):
        shutil.rmtree(MOCK_DIR)
    if os.path.exists(WORKSPACE_DIR):
        shutil.rmtree(WORKSPACE_DIR)
    print("Cleaned up sandbox folder and workspace.")

def test_integration():
    # 1. Setup mock sandbox
    create_mock_sandbox()

    # 2. Run LocalAgentOrganizer
    print("\nInitializing LocalAgentOrganizer...")
    organizer = LocalAgentOrganizer(workspace_path=WORKSPACE_DIR, model_name="llama3.2:latest")

    print("Running integration pipeline...")
    try:
        state = organizer.run(MOCK_DIR)
        
        print("\n🟢 Integration Test Executed Successfully!")
        print(f"Status: {state.status}")
        print(f"Total scanned files: {len(state.all_files)}")
        print(f"Total categorization tasks: {len(state.tasks)}")
        print(f"Proposed Moves Map: {state.proposed_moves}")

        # Assertions
        assert len(state.all_files) == 6, f"Expected 6 files, found {len(state.all_files)}"
        assert len(state.tasks) > 0, "Orchestrator did not generate any categorization tasks"
        assert len(state.proposed_moves) > 0, "Subagents did not generate any proposed moves"

        # Check raw findings cache
        raw_findings_path = os.path.join(WORKSPACE_DIR, "raw_findings")
        assert os.path.exists(raw_findings_path), "Raw findings cache directory does not exist"
        
        cached_files = os.listdir(raw_findings_path)
        print(f"Cached plans found: {cached_files}")
        assert len(cached_files) > 0, "No cached category plans found in raw findings"

        print("🟢 All assertions passed successfully!")

    except Exception as e:
        print(f"\n🔴 Integration Test Failed: {e}")
        raise e
    finally:
        # 3. Cleanup sandbox
        cleanup_mock_sandbox()

if __name__ == "__main__":
    test_integration()
