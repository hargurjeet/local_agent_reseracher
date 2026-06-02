import json
from typing import List
from pydantic import BaseModel, Field
from crewai import Agent, Task, Crew, LLM

from src.state import Subtask

class LeadResearcherOutput(BaseModel):
    objective: str = Field(description="Primary research objective derived from the query")
    success_criteria: List[str] = Field(description="List of specific, actionable validation criteria checklist items")
    tasks: List[Subtask] = Field(description="Surgical subagent tasks partitioned to satisfy the objective")

class LeadResearcher:
    def __init__(self, model_name: str = "llama3.2:latest"):
        # Setup Ollama LLM configuration for CrewAI
        self.llm = LLM(
            model=f"ollama/{model_name}",
            base_url="http://localhost:11434"
        )
        # Define the CrewAI Agent
        self.agent = Agent(
            role="Lead Researcher",
            goal="Analyze research queries and define surgical, specific plans containing subtasks and success criteria.",
            backstory=(
                "You are the lead planner of the agentic research team. You analyze user queries, "
                "formulate clear objectives and validation criteria, and partition the workload into target subtasks "
                "for specialized subagents to execute."
            ),
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )

    def generate_plan(self, query: str) -> LeadResearcherOutput:
        """
        Takes a research query and plans the target folders, subtasks, and success criteria using a CrewAI Crew.
        """
        # Define a CrewAI Task that enforces structured output using output_json
        task = Task(
            description=(
                f"Analyze the user query: '{query}'\n\n"
                "Plan the implementation and split the query into targeted subtasks.\n"
                "Each subtask must contain:\n"
                "- A task ID (e.g., task_1, task_2)\n"
                "- A target path to inspect (e.g., src/, tests/)\n"
                "- A goal description of what the subagent needs to find.\n\n"
                "Define explicit, measurable success criteria to check if the research is complete."
            ),
            expected_output="Structured JSON matching the LeadResearcherOutput schema.",
            agent=self.agent,
            output_json=LeadResearcherOutput
        )

        # Run the single-agent Crew
        crew = Crew(
            agents=[self.agent],
            tasks=[task],
            verbose=False
        )
        
        result = crew.kickoff()
        
        # Access the parsed Pydantic object if available
        if hasattr(result, 'pydantic') and result.pydantic:
            return result.pydantic
            
        # Fallback raw parsing
        data = json.loads(result.raw)
        return LeadResearcherOutput(**data)
