import os
import argparse
import concurrent.futures
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from src.state import ResearchState, Subtask
from agents.lead_researcher import LeadResearcher
from agents.subagents import SubAgentRunner

console = Console()

class LocalAgentResearcher:
    def __init__(self, workspace_path: str, model_name: str = "llama3.2:latest"):
        self.workspace_path = workspace_path
        self.model_name = model_name
        self.lead_agent = LeadResearcher(model_name=self.model_name)
        self.subagent_runner = SubAgentRunner(model_name=self.model_name)

    def run(self, query: str):
        # Initialize state
        state = ResearchState(query=query)
        
        # --- Step 1: Lead Researcher Planning ---
        console.print(Panel(f"[bold blue]Step 1: Lead Researcher Planning[/bold blue]\nQuery: '{query}'", border_style="blue"))
        
        try:
            plan = self.lead_agent.generate_plan(query)
            state.objective = plan.objective
            state.success_criteria = plan.success_criteria
            state.tasks = plan.tasks
        except Exception as e:
            console.print(f"[bold red]Planning phase failed:[/bold red] {e}")
            return
            
        # Display the calculated plan
        console.print(f"[bold green]calculated Primary Objective:[/bold green] {state.objective}")
        
        sc_table = Table(title="Success Criteria Checklist", show_header=True, header_style="bold green")
        sc_table.add_column("No.", style="dim", width=4)
        sc_table.add_column("Criteria Description")
        for idx, sc in enumerate(state.success_criteria, 1):
            sc_table.add_row(str(idx), sc)
        console.print(sc_table)

        # --- Step 2: Parallel Subagent Execution ---
        console.print(Panel(f"[bold blue]Step 2: Spawning Subagents in Parallel (Concurrency)[/bold blue]", border_style="blue"))
        
        # We run the subagents in parallel threads using ThreadPoolExecutor
        findings_map = {}
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Map the execution of each task to the thread pool
            futures = {
                executor.submit(self.subagent_runner.execute_task, task): task 
                for task in state.tasks
            }
            
            console.print(f"[yellow]Triggered {len(state.tasks)} subagents in parallel...[/yellow]\n")
            
            for future in concurrent.futures.as_completed(futures):
                task = futures[future]
                try:
                    result_summary = future.result()
                    findings_map[task.task_id] = result_summary
                    console.print(f"🟢 [bold green]Subagent Completed:[/bold green] {task.task_id} on path '{task.target_path}'")
                except Exception as e:
                    console.print(f"🔴 [bold red]Subagent Failed:[/bold red] {task.task_id} with error: {e}")
        
        # Consolidate findings into the state
        for task in state.tasks:
            if task.task_id in findings_map:
                state.raw_findings.append(findings_map[task.task_id])
                
        console.print(Panel(f"[bold green]Step 2 Validation Complete![/bold green]\nAll subagent findings are saved in 'workspace/raw_findings/'.", border_style="green"))


def main():
    parser = argparse.ArgumentParser(description="Local Agent Researcher Orchestrator")
    parser.add_argument("query", type=str, help="Research query or objective")
    parser.add_argument("--workspace", type=str, default="./workspace", help="Path to workspace directory")
    parser.add_argument("--model", type=str, default="llama3.2:latest", help="Ollama local model name")
    args = parser.parse_args()

    researcher = LocalAgentResearcher(workspace_path=args.workspace, model_name=args.model)
    researcher.run(args.query)

if __name__ == "__main__":
    main()
