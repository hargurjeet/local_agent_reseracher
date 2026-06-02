# Local Agent Researcher - Implementation Plan (CrewAI Flow)

This document tracks the implementation roadmap and progress for the Local Agent Researcher. The architecture organizes our agents into a unified event-driven **CrewAI Flow State Machine**, utilizing Ollama local models for inference.

---

## Step 1: Build & Verify Lead Researcher (Planning & Parsing) — [COMPLETED & VERIFIED]
*   **Objective**: Parse the user query and establish the structured research plan.
*   **Implementation Details**:
    *   Shared State: Defined in [src/state.py](file:///Users/hargurjeetsinghganger/programming_local/local_agent_reseracher/src/state.py) as `ResearchState` and `Subtask` models.
    *   Planner Agent: Implemented in [agents/lead_researcher.py](file:///Users/hargurjeetsinghganger/programming_local/local_agent_reseracher/agents/lead_researcher.py) using the CrewAI `Agent` and `Task` frameworks.
    *   Model Integration: Tied to local Ollama inference using `llama3.2:latest`.
    *   Output Format: Enforces Pydantic structured output mapping to `LeadResearcherOutput`.
*   **Validation**:
    *   Verified via [tests/test_lead_researcher.py](file:///Users/hargurjeetsinghganger/programming_local/local_agent_reseracher/tests/test_lead_researcher.py), which successfully queries the local model and asserts correct JSON schema parameters.

---

## Step 2: Build & Verify Sub-Agents (Scraping & Local Storage) — [COMPLETED & VERIFIED]
*   **Objective**: Execute the planned subtasks surgically on the codebase and local directory files.
*   **Implementation Details**:
    *   File Tools: Implemented in [src/tools.py](file:///Users/hargurjeetsinghganger/programming_local/local_agent_reseracher/src/tools.py). Custom tools handle listing files, reading text (capped to 50KB to preserve context), and saving results to `workspace/raw_findings/`.
    *   Ollama Argument Fix: Added input validation inside the tools to normalize dictionary wrappers passed by smaller models (such as `llama3.2`).
    *   Parallel execution loop: Integrates `concurrent.futures.ThreadPoolExecutor` in [src/main.py](file:///Users/hargurjeetsinghganger/programming_local/local_agent_reseracher/src/main.py) to trigger subagent model executions in parallel threads.
*   **Validation**:
    *   Verified via [tests/test_subagents.py](file:///Users/hargurjeetsinghganger/programming_local/local_agent_reseracher/tests/test_subagents.py), which runs a subagent to parse `state.py` and logs the cache output to `workspace/raw_findings/task_1.txt`.

---

## Step 3: Build & Verify Citation Agent (Post-Processing & Document Mapping) — [PENDING]
*   **Objective**: Ensure that all research findings are linked to their source files and lines (Zero Slop / Relentless Verification).
*   **Architecture**:
    *   Read the aggregated summaries from the sub-agent output cache.
    *   Implement the **Citation Agent** whose sole role is to verify statements and map them back to the exact files/lines.
    *   Format findings into a clean Markdown document with numbered citation footnotes linking to the source files in the local codebase.
*   **Tasks**:
    *   Create `agents/citation_agent.py` (inheriting CrewAI specifications).
*   **Verification**:
    *   Write a simplified validation script `tests/test_citation_agent.py`.

---

## Step 4: Connect Everything into a Single CrewAI Flow State Machine — [PENDING]
*   **Objective**: Integrate the Lead Researcher, Sub-Agents, and Citation Agent into a single orchestrator state machine.
*   **Architecture**:
    *   Utilize **CrewAI Flows** to manage the execution lifecycle.
    *   Define event handlers using `@start` (Lead Researcher planning) and `@listen` (triggering sub-agent execution, followed by the citation post-processing step).
    *   Enable state persistence and recovery.
*   **Tasks**:
    *   Integrate handlers inside `src/main.py` using CrewAI's `Flow` class.
*   **Verification**:
    *   Perform end-to-end integration tests by executing a full research query.
    *   Verify that `workspace/research_report.md` is compiled successfully with correct citations.
