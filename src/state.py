from typing import List
from pydantic import BaseModel, Field

class Subtask(BaseModel):
    task_id: str = Field(description="Unique task identifier (e.g., task_1)")
    description: str = Field(description="Surgical target description for the subagent")
    target_path: str = Field(description="Specific file or directory path to inspect")

class ResearchState(BaseModel):
    query: str = Field(default="", description="The original user query")
    objective: str = Field(default="", description="Calculated primary research objective")
    success_criteria: List[str] = Field(default_factory=list, description="Measurable validation criteria checklist")
    tasks: List[Subtask] = Field(default_factory=list, description="Targeted subagent tasks partitioned by the planner")
    raw_findings: List[str] = Field(default_factory=list, description="Aggregated findings from subagents")
    final_report: str = Field(default="", description="The final verified citation report")
