import json
from typing import List
from pydantic import BaseModel, Field
from crewai import Agent, Task, Crew, LLM

from src.state import FileMetadata, Subtask

class OrchestratorOutput(BaseModel):
    tasks: List[Subtask] = Field(description="List of tasks grouped by general category")

class OrchestratorPlanner:
    def __init__(self, model_name: str = "llama3.2:latest"):
        # Configure Ollama LLM for CrewAI
        self.llm = LLM(
            model=f"ollama/{model_name}",
            base_url="http://localhost:11434"
        )
        
        # Define the Orchestrator Agent
        self.agent = Agent(
            role="Folder Cataloger & Planner",
            goal="Scan the list of files, catalog them, and group them into general category tasks.",
            backstory=(
                "You are an expert file organizer. You take a list of files with sizes and extensions, "
                "and categorize them into logical groups (like Documents, Media, Installers, Code, etc.) "
                "so that specialty subagents can organize each group individually."
            ),
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )

    def generate_tasks(self, files: List[FileMetadata]) -> List[Subtask]:
        """
        Takes a list of file metadata and groups them into category subtasks.
        """
        if not files:
            return []
            
        # Format the file list for the prompt
        files_info = []
        for f in files:
            files_info.append(f"Name: {f.filename}, Extension: {f.extension}, Size: {f.size_bytes} bytes")
        files_str = "\n".join(files_info)

        # Define the CrewAI Task
        task = Task(
            description=(
                f"Analyze the following list of files:\n\n{files_str}\n\n"
                "Group ALL of these files into general categories (e.g. Documents, Media, Installers, Code, Other).\n"
                "For each category, generate a subtask. Each subtask MUST include:\n"
                "- task_id (e.g. task_1, task_2, etc.)\n"
                "- category (the category name, e.g. Documents, Media, Installers, Code)\n"
                "- files (a list of names of files belonging to that category)\n\n"
                "CRITICAL: You must process every single file in the list. Do not leave any file out. "
                "For example, ensure video files (e.g. .mp4) and images (e.g. .png) are categorized, e.g. under 'Media'. "
                "Every file name in the input must appear in exactly one task's file list."
            ),
            expected_output="Structured JSON matching the OrchestratorOutput schema.",
            agent=self.agent,
            output_json=OrchestratorOutput
        )

        # Execute using a Crew
        crew = Crew(
            agents=[self.agent],
            tasks=[task],
            verbose=False
        )
        
        result = crew.kickoff()
        
        # Return parsed output
        if hasattr(result, 'pydantic') and result.pydantic:
            return result.pydantic.tasks
            
        # Fallback raw parsing
        data = json.loads(result.raw)
        output = OrchestratorOutput(**data)
        return output.tasks
