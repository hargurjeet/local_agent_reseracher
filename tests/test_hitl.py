import os
import sys
import shutil
import json
from unittest.mock import patch

# Add project root to python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.main import LocalAgentOrganizer

MOCK_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tests", "mock_hitl_downloads")
WORKSPACE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tests", "mock_hitl_workspace")

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

    sample_files = [
        "hitl_receipt_2026.pdf",
        "hitl_photo_vacation.png",
        "hitl_script.py"
    ]
    for fname in sample_files:
        with open(os.path.join(MOCK_DIR, fname), "w") as f:
            f.write(f"hitl data for {fname}")
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

def test_hitl_dry_run():
    print("\n" + "="*40 + "\nTesting HITL - Dry Run Mode\n" + "="*40)
    create_mock_sandbox()
    
    organizer = LocalAgentOrganizer(workspace_path=WORKSPACE_DIR, model_name="llama3.2:latest")
    
    try:
        # Run with dry_run = True
        state = organizer.run(MOCK_DIR, dry_run=True)
        
        print(f"\nDry Run Result Status: {state.status}")
        assert state.status == "awaiting_approval", f"Expected awaiting_approval, got {state.status}"
        
        # Files should still exist in MOCK_DIR
        for fname in ["hitl_receipt_2026.pdf", "hitl_photo_vacation.png", "hitl_script.py"]:
            assert os.path.exists(os.path.join(MOCK_DIR, fname)), f"File {fname} was moved in dry-run!"
            
        print("🟢 Dry Run verification passed!")
    finally:
        cleanup_mock_sandbox()

def test_hitl_aborted():
    print("\n" + "="*40 + "\nTesting HITL - Aborted by User\n" + "="*40)
    create_mock_sandbox()
    
    organizer = LocalAgentOrganizer(workspace_path=WORKSPACE_DIR, model_name="llama3.2:latest")
    
    try:
        # Run with dry_run = False and mock user input to say "no"
        with patch("builtins.input", return_value="n"):
            state = organizer.run(MOCK_DIR, dry_run=False)
            
        print(f"\nAborted Result Status: {state.status}")
        assert state.status == "aborted", f"Expected aborted, got {state.status}"
        
        # Files should still exist in MOCK_DIR
        for fname in ["hitl_receipt_2026.pdf", "hitl_photo_vacation.png", "hitl_script.py"]:
            assert os.path.exists(os.path.join(MOCK_DIR, fname)), f"File {fname} was moved after cancellation!"
            
        print("🟢 Abort verification passed!")
    finally:
        cleanup_mock_sandbox()

def test_hitl_approved():
    print("\n" + "="*40 + "\nTesting HITL - Approved by User\n" + "="*40)
    create_mock_sandbox()
    
    organizer = LocalAgentOrganizer(workspace_path=WORKSPACE_DIR, model_name="llama3.2:latest")
    
    try:
        # Run with dry_run = False and mock user input to say "yes"
        with patch("builtins.input", return_value="yes"):
            state = organizer.run(MOCK_DIR, dry_run=False)
            
        print(f"\nApproved / Executed Result Status: {state.status}")
        assert state.status == "executed", f"Expected executed, got {state.status}"
        
        # Files should be moved out of the root mock downloads folder
        for fname in ["hitl_receipt_2026.pdf", "hitl_photo_vacation.png", "hitl_script.py"]:
            assert not os.path.exists(os.path.join(MOCK_DIR, fname)), f"File {fname} was NOT moved after approval!"
            
        # history.json log file should exist
        history_path = os.path.join(WORKSPACE_DIR, "history.json")
        assert os.path.exists(history_path), "history.json transaction log was not created"
        with open(history_path, "r") as f:
            history_data = json.load(f)
        print(f"Created history transaction log: {history_data}")
        assert len(history_data) > 0, "history.json log is empty"
        
        print("🟢 Approval & Execution verification passed!")
    finally:
        cleanup_mock_sandbox()

if __name__ == "__main__":
    test_hitl_dry_run()
    test_hitl_aborted()
    test_hitl_approved()
