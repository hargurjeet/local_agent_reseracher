from crewai import Agent, Task, Crew, LLM

from src.state import Subtask
from src.tools import list_workspace_files, read_file_content, save_subagent_findings

class SubAgentRunner:
    def __init__(self, model_name: str = "llama3.2:latest"):
        self.model_name = model_name
        self.llm = LLM(
            model=f"ollama/{model_name}",
            base_url="http://localhost:11434"
        )

    def execute_task(self, subtask: Subtask) -> str:
        """
        Spawns a specialized subagent to execute a specific target task surgically.
        """
        # Define the specialized agent
        agent = Agent(
            role="Research Specialist",
            goal=f"Examine the target path '{subtask.target_path}' and extract findings related to the objective.",
            backstory=(
                f"You are a focused research analyst. Your task is to investigate target path '{subtask.target_path}' "
                f"and find information satisfying the description: '{subtask.description}'. "
                "Use the provided tools surgically. Focus ONLY on this objective and avoid speculative analysis."
            ),
            verbose=True,
            allow_delegation=False,
            tools=[list_workspace_files, read_file_content, save_subagent_findings],
            llm=self.llm
        )

        # Define the task. Instruct the agent to execute findings, then save it using the Save Subagent Findings tool.
        task_prompt = (
            f"Analyze files under the target path: '{subtask.target_path}'\n"
            f"Surgical Task Description: {subtask.description}\n\n"
            "Steps:\n"
            "1. List files in the target path using the 'List Workspace Files' tool if you need to discover files.\n"
            "2. Read the contents of the relevant files using the 'Read File Content' tool.\n"
            f"3. Consolidate your findings and save them to the local cache using the 'Save Subagent Findings' tool. "
            f"Pass the argument 'task_id' as '{subtask.task_id}' and 'content' as the text summary of your findings.\n"
            "4. Return the summary as your final response text."
        )

        task = Task(
            description=task_prompt,
            expected_output=f"A summary of findings for {subtask.task_id} saved to the local cache.",
            agent=agent
        )

        crew = Crew(
            agents=[agent],
            tasks=[task],
            verbose=False
        )

        result = crew.kickoff()
        return result.raw
