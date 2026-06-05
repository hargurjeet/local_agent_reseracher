import os
import json
import shutil
from typing import Dict
from pydantic import BaseModel, Field
from crewai import Agent, Task, Crew, LLM

import src.tools as tools
from src.tools import move_file, write_transaction_log

class ExecutorOutput(BaseModel):
    executed_moves: Dict[str, str] = Field(description="Map of successfully executed source filenames to relative target paths")
    status: str = Field(description="Execution status, e.g., success, partial_success, or failure")

class ExecutorRunner:
    def __init__(self, model_name: str = "llama3.2:latest"):
        self.model_name = model_name
        self.llm = LLM(
            model=f"ollama/{model_name}",
            base_url="http://localhost:11434"
        )
        
        self.agent = Agent(
            role="File Execution Specialist",
            goal="Aggregate proposed file paths, resolve organizational conflicts, and safely perform file movements.",
            backstory=(
                "You are a meticulous systems administrator. You review compiled file movement plans, "
                "move files to their target directories, and record all transactions to a rollback history log."
            ),
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=[move_file, write_transaction_log]
        )

    def execute_plan(self, downloads_path: str, workspace_path: str, proposed_moves: Dict[str, str]) -> ExecutorOutput:
        """
        Executes the file moves plan using Python for absolute reliability,
        while utilizing the agent to audit and summarize the final execution.
        """
        if not proposed_moves:
            return ExecutorOutput(executed_moves={}, status="success")

        # 1. Execute moves in Python to guarantee absolute reliability
        executed_moves = {}
        for filename, proposed_rel_path in proposed_moves.items():
            src_abs = os.path.join(downloads_path, filename)
            
            # Clean leading slashes
            cleaned_rel = proposed_rel_path.lstrip("/")
            if cleaned_rel.lower().startswith("files/"):
                cleaned_rel = cleaned_rel[6:]
                
            # If the path is a directory (ends with / or matches category directory), append the filename
            if cleaned_rel.endswith("/") or cleaned_rel in ("Documents", "Media", "Installers", "Code"):
                dest_rel = os.path.join(cleaned_rel, filename)
            else:
                dest_rel = cleaned_rel
                
            dest_abs = os.path.join(downloads_path, dest_rel)
            
            try:
                dest_dir = os.path.dirname(dest_abs)
                if dest_dir:
                    os.makedirs(dest_dir, exist_ok=True)
                shutil.move(src_abs, dest_abs)
                executed_moves[filename] = dest_rel
            except Exception as e:
                print(f"Error moving {filename} to {dest_abs}: {e}")

        # 2. Write transaction log
        log_path = os.path.abspath(os.path.join(workspace_path, "history.json"))
        try:
            log_dir = os.path.dirname(log_path)
            if log_dir:
                os.makedirs(log_dir, exist_ok=True)
            with open(log_path, "w") as f:
                json.dump(executed_moves, f, indent=4)
        except Exception as e:
            print(f"Warning: Failed to write transaction log: {e}")

        # 3. Use the agent to audit the final moves list and print a summary report
        moves_str = json.dumps(executed_moves, indent=2)
        task = Task(
            description=(
                f"The following file moves have been successfully executed on the system:\n\n{moves_str}\n\n"
                f"Verify the execution log and summarize the organization results for the user."
            ),
            expected_output="A concise text summary listing the successfully moved files.",
            agent=self.agent
        )

        crew = Crew(
            agents=[self.agent],
            tasks=[task],
            verbose=False
        )

        # Run audit task
        crew.kickoff()

        status = "success" if len(executed_moves) == len(proposed_moves) else "partial_success"
        if not executed_moves:
            status = "failure"

        return ExecutorOutput(
            executed_moves=executed_moves,
            status=status
        )



