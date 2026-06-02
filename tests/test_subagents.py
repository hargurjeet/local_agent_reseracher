import os
import sys

# Ensure the project root is in the Python search path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.state import Subtask
from agents.subagents import SubAgentRunner

def main():
    # Define a surgical subtask to analyze our state file
    task = Subtask(
        task_id="task_1",
        description="Inspect state.py file, list the names of all Pydantic classes defined, and summarize their fields.",
        target_path="src/"
    )
    
    print(f"Initializing SubAgentRunner using local Ollama model (llama3.2:latest)...")
    runner = SubAgentRunner()
    
    print(f"Executing subtask '{task.task_id}' on path '{task.target_path}'...")
    print(f"Objective: '{task.description}'\n")
    
    try:
        # Run execution
        result = runner.execute_task(task)
        print("\n🟢 Subagent Execution finished!")
        print(f"Output Raw Response:\n{result}")
        
        # Verify if findings were saved to local cache
        findings_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "workspace", "raw_findings", f"{task.task_id}.txt"
        )
        
        print(f"\n[Validation] Checking local cache path: '{findings_file}'...")
        if os.path.exists(findings_file):
            print("🟢 Validation Passed! Finding file was successfully saved.")
            with open(findings_file, "r", encoding="utf-8") as f:
                content = f.read()
            print("\n--- CACHED FINDINGS CONTENT ---")
            print(content)
            print("--------------------------------")
        else:
            print("🔴 Validation Failed! Finding file was NOT saved to the local cache.")
            
    except Exception as e:
        print(f"🔴 Error executing subagent: {e}")

if __name__ == "__main__":
    main()
