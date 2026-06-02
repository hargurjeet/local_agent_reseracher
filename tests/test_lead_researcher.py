import os
import sys

# Ensure the project root is in the Python search path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.lead_researcher import LeadResearcher

def main():
    # Allow overriding the query via command-line arguments
    query = "Find all python files in the src directory and list all defined classes and functions."
    if len(sys.argv) > 1:
        query = sys.argv[1]
        
    print(f"Initializing LeadResearcher agent using local Ollama model (llama3.2:latest)...")
    researcher = LeadResearcher()
    
    print(f"Executing plan-first parsing for query: '{query}'\n")
    try:
        result = researcher.generate_plan(query)
        
        print("🟢 Success! Calculated Plan Output:\n")
        print(f"Primary Objective: {result.objective}")
        print("\nSuccess Criteria:")
        for idx, sc in enumerate(result.success_criteria, 1):
            print(f"  {idx}. {sc}")
            
        print("\nSubagent Tasks:")
        for task in result.tasks:
            print(f"  - [{task.task_id}] Target Path: {task.target_path}")
            print(f"    Goal: {task.description}")
            
    except Exception as e:
        print(f"🔴 Error executing Lead Researcher: {e}")

if __name__ == "__main__":
    main()
