import json
from typing import List
from pydantic import BaseModel, Field
from crewai import Agent, Task, Crew, LLM

from src.state import Subtask

class FileMoveProposal(BaseModel):
    filename: str = Field(description="Name of the file including extension")
    proposed_path: str = Field(description="Semantic relative target path within the category folder (e.g. Financial/tax_receipt.pdf)")

class ProposedMovesList(BaseModel):
    category: str = Field(description="The category of files processed")
    proposals: List[FileMoveProposal] = Field(description="List of proposed file moves")

class SubAgentRunner:
    def __init__(self, model_name: str = "llama3.2:latest"):
        self.model_name = model_name
        self.llm = LLM(
            model=f"ollama/{model_name}",
            base_url="http://localhost:11434"
        )

    def execute_category_task(self, subtask: Subtask) -> ProposedMovesList:
        """
        Spawns a specialized subagent to semantically plan target paths for a category of files.
        """
        # Define the specialized agent for this category
        agent = Agent(
            role=f"{subtask.category} Specialist",
            goal=f"Determine semantic subfolder destinations for all files in the '{subtask.category}' category.",
            backstory=(
                f"You are a file organization analyst specializing in the '{subtask.category}' file group. "
                "You inspect filenames, understand their semantic context, and group them into logical subfolders. "
                "For example, a receipt should go to a 'Finance' or 'Receipts' subfolder."
            ),
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )

        files_list_str = "\n".join([f"- {f}" for f in subtask.files])

        # Define the task
        task = Task(
            description=(
                f"Review this list of files categorized under '{subtask.category}':\n\n"
                f"{files_list_str}\n\n"
                f"Your goal is to suggest a neat, organized subfolder path for each file. "
                "Create logical subfolders within the category. For example:\n"
                "- Documents: receipts to 'Finance/Receipts/', books to 'Books/', logs to 'Logs/'\n"
                "- Media: family photos to 'Photos/', videos to 'Videos/'\n"
                "- Code: python files to 'Python/', configurations to 'Configs/'\n\n"
                "Ensure every file in the input list is assigned a proposed path."
            ),
            expected_output="Structured JSON matching the ProposedMovesList schema.",
            agent=agent,
            output_json=ProposedMovesList
        )

        # Run the crew
        crew = Crew(
            agents=[agent],
            tasks=[task],
            verbose=False
        )

        result = crew.kickoff()

        if hasattr(result, 'pydantic') and result.pydantic:
            return result.pydantic

        # Fallback parsing
        data = json.loads(result.raw)
        return ProposedMovesList(**data)
