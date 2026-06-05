import os
import sys

# Add the project root to Python search path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.state import Subtask
from agents.subagents import SubAgentRunner

def test_document_subagent():
    print("Testing Documents Subagent...")
    subtask = Subtask(
        task_id="task_1",
        category="Documents",
        files=[
            "tax_return_form.pdf",
            "uber_receipt_may2026.pdf",
            "attention_paper.pdf"
        ]
    )
    runner = SubAgentRunner()
    try:
        result = runner.execute_category_task(subtask)
        print("\n🟢 Documents Subagent Output Success!\n")
        print(f"Category: {result.category}")
        for prop in result.proposals:
            print(f" - {prop.filename} ──► {prop.proposed_path}")
        print()
    except Exception as e:
        print(f"🔴 Documents Subagent failed: {e}")

def test_media_subagent():
    print("Testing Media Subagent...")
    subtask = Subtask(
        task_id="task_2",
        category="Media",
        files=[
            "family_photo.png",
            "vacation_video.mp4"
        ]
    )
    runner = SubAgentRunner()
    try:
        result = runner.execute_category_task(subtask)
        print("\n🟢 Media Subagent Output Success!\n")
        print(f"Category: {result.category}")
        for prop in result.proposals:
            print(f" - {prop.filename} ──► {prop.proposed_path}")
        print()
    except Exception as e:
        print(f"🔴 Media Subagent failed: {e}")

def test_installer_subagent():
    print("Testing Installers Subagent...")
    subtask = Subtask(
        task_id="task_3",
        category="Installers",
        files=[
            "chrome_installer.dmg",
            "python_setup.pkg"
        ]
    )
    runner = SubAgentRunner()
    try:
        result = runner.execute_category_task(subtask)
        print("\n🟢 Installers Subagent Output Success!\n")
        print(f"Category: {result.category}")
        for prop in result.proposals:
            print(f" - {prop.filename} ──► {prop.proposed_path}")
        print()
    except Exception as e:
        print(f"🔴 Installers Subagent failed: {e}")

def test_code_subagent():
    print("Testing Code Subagent...")
    subtask = Subtask(
        task_id="task_4",
        category="Code",
        files=[
            "script.py",
            "utils.js",
            "styles.css"
        ]
    )
    runner = SubAgentRunner()
    try:
        result = runner.execute_category_task(subtask)
        print("\n🟢 Code Subagent Output Success!\n")
        print(f"Category: {result.category}")
        for prop in result.proposals:
            print(f" - {prop.filename} ──► {prop.proposed_path}")
        print()
    except Exception as e:
        print(f"🔴 Code Subagent failed: {e}")

if __name__ == "__main__":
    test_document_subagent()
    print("="*40)
    test_media_subagent()
    print("="*40)
    test_installer_subagent()
    print("="*40)
    test_code_subagent()
