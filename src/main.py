import os
import sys
import json
import argparse
import concurrent.futures
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Add project root to python search path to resolve relative module imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.state import FolderOrganizeState, Subtask, FileMetadata
from src.tools import list_directory_metadata
from agents.orchestrator import OrchestratorPlanner
from agents.subagents import SubAgentRunner
from agents.executor import ExecutorRunner

console = Console()

class LocalAgentOrganizer:
    def __init__(self, workspace_path: str, model_name: str = "llama3.2:latest"):
        self.workspace_path = workspace_path
        self.model_name = model_name
        self.orchestrator = OrchestratorPlanner(model_name=self.model_name)
        self.subagent_runner = SubAgentRunner(model_name=self.model_name)

    def run(self, directory_path: str, dry_run: bool = False):
        # Resolve absolute path of directory to organize, expanding user home directory symbols like ~
        abs_directory_path = os.path.abspath(os.path.expanduser(directory_path))
        console.print(Panel(f"[bold blue]Step 0: Scanning Directory[/bold blue]\nTarget: '{abs_directory_path}'", border_style="blue"))
        
        if not os.path.exists(abs_directory_path):
            console.print(f"[bold red]Error:[/bold red] Target directory '{abs_directory_path}' does not exist.")
            return

        # 1. Scan directory files
        files = list_directory_metadata(abs_directory_path)
        if not files:
            console.print("[bold yellow]Warning:[/bold yellow] No files found in the directory to organize.")
            return

        # Initialize State
        state = FolderOrganizeState(
            downloads_path=abs_directory_path,
            all_files=files,
            status="planning"
        )
        
        console.print(f"Found {len(state.all_files)} files to organize.")

        # --- Step 1: Orchestrator Planning ---
        console.print(Panel(f"[bold blue]Step 1: Orchestrator Categorization & Planning[/bold blue]", border_style="blue"))
        
        try:
            tasks = self.orchestrator.generate_tasks(state.all_files)
            state.tasks = tasks
        except Exception as e:
            console.print(f"[bold red]Planning phase failed:[/bold red] {e}")
            return
            
        # Display the categorization plan
        console.print(f"[bold green]Categorization Complete. Created {len(state.tasks)} subagent tasks:[/bold green]")
        for task in state.tasks:
            console.print(f" - [bold cyan]{task.category}[/bold cyan] ({task.task_id}): {len(task.files)} files")

        # --- Step 2: Parallel Subagent Execution ---
        console.print(Panel(f"[bold blue]Step 2: Spawning Specialist Subagents in Parallel[/bold blue]", border_style="blue"))
        
        findings_map = {}
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Map the execution of each task to the thread pool
            futures = {
                executor.submit(self.subagent_runner.execute_category_task, task): task 
                for task in state.tasks
            }
            
            console.print(f"[yellow]Triggered {len(state.tasks)} subagents in parallel...[/yellow]\n")
            
            for future in concurrent.futures.as_completed(futures):
                task = futures[future]
                try:
                    result_summary = future.result()  # This returns ProposedMovesList
                    findings_map[task.task_id] = result_summary
                    console.print(f"🟢 [bold green]Subagent Completed:[/bold green] {task.task_id} for category '{task.category}'")
                    
                    # Cache raw findings to disk under workspace/raw_findings/
                    raw_findings_dir = os.path.join(self.workspace_path, "raw_findings")
                    os.makedirs(raw_findings_dir, exist_ok=True)
                    category_plan_path = os.path.join(raw_findings_dir, f"{task.category.lower()}_plan.json")
                    
                    # Convert to dictionary safely supporting multiple Pydantic versions
                    dumped_data = result_summary.model_dump() if hasattr(result_summary, 'model_dump') else result_summary.dict()
                    with open(category_plan_path, "w") as f:
                        json.dump(dumped_data, f, indent=4)
                        
                except Exception as e:
                    console.print(f"🔴 [bold red]Subagent Failed:[/bold red] {task.task_id} for category '{task.category}' with error: {e}")
        
        # Consolidate findings into the state
        for task in state.tasks:
            if task.task_id in findings_map:
                proposal_list = findings_map[task.task_id]
                for prop in proposal_list.proposals:
                    # Formulate target path: ensure category folder is prefixed
                    # Strip leading slashes to prevent os.path.join from treating it as an absolute path
                    proposed_path = prop.proposed_path.lstrip("/")
                    if not proposed_path.startswith(task.category):
                        final_rel_path = os.path.join(task.category, proposed_path)
                    else:
                        final_rel_path = proposed_path
                    state.proposed_moves[prop.filename] = final_rel_path


        console.print(Panel(f"[bold green]Step 2 Completed![/bold green]\nAll subagent plans have been saved in '{self.workspace_path}/raw_findings/'.", border_style="green"))

        # Display proposed reorganization table
        proposed_table = Table(title="Proposed File Organization Plan", show_header=True, header_style="bold magenta")
        proposed_table.add_column("Original Filename", style="dim")
        proposed_table.add_column("Proposed Relative Path", style="cyan")
        
        for filename, proposed_path in sorted(state.proposed_moves.items()):
            proposed_table.add_row(filename, proposed_path)
            
        console.print(proposed_table)

        # --- Step 3: Human-in-the-Loop (HITL) Gate ---
        if dry_run:
            console.print(Panel("[bold yellow]Dry Run Mode Enabled[/bold yellow]\nNo files will be modified.", border_style="yellow"))
            state.status = "awaiting_approval"
            return state
            
        console.print("\n[bold yellow]Awaiting user confirmation...[/bold yellow]")
        try:
            confirm = input("Do you want to proceed with the proposed file organization? (y/N): ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[bold red]Operation cancelled. No files were moved.[/bold red]")
            state.status = "aborted"
            return state
        
        if confirm not in ("y", "yes"):
            console.print("[bold red]Operation cancelled by user. No files were moved.[/bold red]")
            state.status = "aborted"
            return state
            
        state.status = "approved"
        
        # --- Step 4: Executor Execution ---
        console.print(Panel("[bold blue]Step 4: Executing File Relocations[/bold blue]", border_style="blue"))
        executor_runner = ExecutorRunner(model_name=self.model_name)
        
        try:
            execution_result = executor_runner.execute_plan(
                downloads_path=abs_directory_path,
                workspace_path=self.workspace_path,
                proposed_moves=state.proposed_moves
            )
            
            if execution_result.status == "success":
                state.status = "executed"
                console.print(Panel(f"[bold green]Success![/bold green]\nSuccessfully moved {len(execution_result.executed_moves)} files.\nTransaction log written to '{self.workspace_path}/history.json'.", border_style="green"))
            else:
                state.status = "failed"
                console.print(f"[bold red]Execution failed or partially failed:[/bold red] {execution_result.status}")
                
        except Exception as e:
            console.print(f"[bold red]Execution phase encountered an error:[/bold red] {e}")
            state.status = "failed"
            
        return state



def main():
    parser = argparse.ArgumentParser(description="Local Agent Organizer Orchestrator")
    parser.add_argument("directory", type=str, help="Path to the directory to organize")
    parser.add_argument("--workspace", type=str, default="./workspace", help="Path to workspace directory")
    parser.add_argument("--model", type=str, default="llama3.2:latest", help="Ollama local model name")
    parser.add_argument("--dry-run", action="store_true", help="Preview the organization plan without moving files")
    args = parser.parse_args()

    organizer = LocalAgentOrganizer(workspace_path=args.workspace, model_name=args.model)
    organizer.run(args.directory, dry_run=args.dry_run)

if __name__ == "__main__":
    main()

