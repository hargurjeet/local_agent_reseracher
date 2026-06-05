# Local Agent Organizer - Implementation Plan (Step-by-Step Agent Build)

This document tracks the incremental, stage-by-stage implementation plan for the **Downloads Folder Organizer**. Each stage focuses on building one specific agent and writing a dedicated validation test to verify it before moving forward.

---

## Design Constraints
* **Framework**: All agents MUST be developed using **CrewAI**.
* **LLM Engine**: All model inference and LLM calls MUST go through **Ollama** local models.
* **Coding Style**: Maintain simplicity first. Avoid complex, over-engineered abstractions. Write clean, readable, and simple Python functions that are easy to follow.

---

## Stage 1: Build & Verify Orchestrator Agent — [COMPLETED & VERIFIED]
* **Objective**: Build the `Orchestrator Agent` that scans the target directory, categorizes the files, and creates subtasks.
* **Tasks**:
  * Implement `FileMetadata` and `FolderOrganizeState` schemas in [src/state.py](file:///Users/hargurjeetsinghganger/programming_local/local_agent_reseracher/src/state.py).
  * Write the directory scanner tool `list_directory_metadata` in [src/tools.py](file:///Users/hargurjeetsinghganger/programming_local/local_agent_reseracher/src/tools.py).
  * Create `agents/orchestrator.py` containing the Orchestrator agent using local Ollama parsing.
* **Testing & Verification**:
  * Verified via [tests/test_orchestrator.py](file:///Users/hargurjeetsinghganger/programming_local/local_agent_reseracher/tests/test_orchestrator.py), which successfully scans directory files, triggers the Ollama planner, and categorizes them into structured Pydantic `Subtask` objects.

---

## Stage 2: Build & Verify Categorical Class Specialists — [COMPLETED & VERIFIED]
* **Objective**: Build the specialized subagents that take file groups and formulate semantic target paths.
* **Tasks**:
  * Create `agents/subagents.py` defining the specialized subagents (Documents, Media, Installers/Archives).
  * Define the input/output schemas for the subagent outputs.
  * Integrate parallel execution of subagents using `ThreadPoolExecutor` inside [src/main.py](file:///Users/hargurjeetsinghganger/programming_local/local_agent_reseracher/src/main.py).
* **Testing & Verification**:
  * Verified via [tests/test_subagents.py](file:///Users/hargurjeetsinghganger/programming_local/local_agent_reseracher/tests/test_subagents.py), which feeds Document and Media file lists to categorical specialists and successfully outputs structured target directory proposals.

---

## Stage 3: Build & Verify Executor Agent — [COMPLETED & VERIFIED]
* **Objective**: Build the `Executor Agent` that aggregates mappings, creates directories, and safely executes file movements.
* **Tasks**:
  * Create `agents/executor.py` containing the Executor agent definition.
  * Implement safe file-operation tools (`create_directory`, `move_file`) in [src/tools.py](file:///Users/hargurjeetsinghganger/programming_local/local_agent_reseracher/src/tools.py).
  * Implement the writing of a transaction rollback log (`workspace/history.json`).
* **Testing & Verification**:
  * Verified via [tests/test_executor.py](file:///Users/hargurjeetsinghganger/programming_local/local_agent_reseracher/tests/test_executor.py), which feeds a mock organization map, executes the physical moves in the sandbox, creates required subfolders, and outputs the completed log.


---

## Stage 4: Build & Verify Human-in-the-Loop Gateway — [COMPLETED & VERIFIED]
* **Objective**: Integrate the interactive console gate and dry-run preview capabilities.
* **Tasks**:
  * Build the plan-aggregation module that formats proposed moves into a clean table using `Rich`.
  * Implement the terminal validation prompt asking for user approval `(y/n)` before execution.
  * Implement a `--dry-run` flag to display the plan table without modifying files.
* **Testing & Verification**:
  * Verified via [tests/test_hitl.py](file:///Users/hargurjeetsinghganger/programming_local/local_agent_reseracher/tests/test_hitl.py), which checks:
    1. Dry-run mode exits safely with `"awaiting_approval"` and moves no files.
    2. Interactive rejection exits safely with `"aborted"` and moves no files.
    3. Interactive approval triggers Stage 3 executor, moves files, writes log, and exits with `"executed"`.


---

## Stage 5: Sandbox Testing & End-to-End Rollback — [PENDING]
* **Objective**: Create the testing sandbox environment and verify rollback/undo functionality.
* **Tasks**:
  * Write the sandbox utility `seed_mock_downloads()` in `tests/conftest.py` to easily spawn mock files of various types.
  * Implement the `--undo` command line flag to reverse all operations recorded in `history.json`.
* **Testing & Verification**:
  * Run a complete end-to-end integration test:
    1. Seed the mock folder.
    2. Run the organizer in dry-run mode (verify output table).
    3. Run in live mode, approve via HITL prompt (verify files are correctly organized).
    4. Run the `--undo` command (verify all files are restored to their original state).
