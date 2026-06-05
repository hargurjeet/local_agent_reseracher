# Local Agent Directory Organizer

A local multi-agent system built using **CrewAI** and **Ollama** that semantically restructures and cleans up cluttered directories (e.g., your `Downloads` folder). 

Instead of basic extension-based sorting (e.g., moving all `.pdf` files into a single generic `Documents/` folder), this system uses LLMs to understand the semantic meaning of filenames and group them into logical, context-aware subfolders (e.g., placing `uber_invoice_2026.pdf` into `Documents/Finance/Receipts/`).

---

## 🏗️ Architecture & Workflow

The system utilizes a hierarchical coordinator-specialist agent architecture to handle large directories without running into LLM context window limits:

```mermaid
graph TD
    User([Downloads Folder]) --> Coordinator[Coordinator src/main.py]
    Coordinator --> Orchestrator[Orchestrator Agent]
    Orchestrator -->|Partitions into Subtasks| Coordinator
    Coordinator -->|Parallel Execution| Subagents[Category Specialists]
    
    subgraph Parallel Subagent Execution
        Subagents -->|Media Specialist| MediaPlan[Media Subfolder Mappings]
        Subagents -->|Documents Specialist| DocPlan[Documents Subfolder Mappings]
        Subagents -->|Code/Installers Specialist| CodePlan[Code Subfolder Mappings]
    end
    
    MediaPlan & DocPlan & CodePlan --> Coordinator
    Coordinator -->|Renders Rich Console Table| HITL{Human Approval Gate}
    HITL -->|Approved y| Executor[Executor Agent]
    Executor -->|Safely moves files| FS[(File System)]
    Executor -->|Writes rollback history| Log[(history.json)]
    HITL -->|Rejected n| Abort([Abort / Exit safely])
```

---

## ✨ Features

*   **Semantic Classification**: Analyzes filenames contextually to place files in domain-specific folders (e.g., `learning/`, `finance/receipts/`, `packages/`).
*   **100% Local Inference**: Runs entirely on your local machine using **Ollama** and lightweight models (configured for `llama3.2:latest`). No API keys or cloud costs required.
*   **Concurreny & Speed**: Spawns specialist subagents in parallel using a Python `ThreadPoolExecutor` to speed up local execution.
*   **Human-in-the-Loop (HITL) Gate**: Preview proposed relocations in a beautiful CLI table (built with `Rich`) before approving or cancelling the operations.
*   **Dry-Run Support**: Run the entire pipeline in preview mode (`--dry-run`) to check proposed movements without touching your filesystem.
*   **Safe Execution & Logging**: File operations are logged to a rollback transaction file (`workspace/history.json`) for safety and future rollback options.

---

## 🚀 Getting Started

### **1. Prerequisites**
*   Python 3.10+
*   [Ollama](https://ollama.com/) running locally.
*   Pull the default local model:
    ```bash
    ollama pull llama3.2:latest
    ```

### **2. Installation**
Clone this repository, navigate to the folder, set up a virtual environment, and install dependencies:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r docs/requirements.txt
```

---

## 💻 Usage

Run the program by passing the target directory (e.g. your `Downloads` folder) to the main script:

### **Preview proposed moves (Dry Run):**
```bash
.venv/bin/python3 src/main.py ~/Downloads --dry-run
```

### **Execute organization (requires interactive approval):**
```bash
.venv/bin/python3 src/main.py ~/Downloads
```

---

## 🧪 Running Verification Tests

Each stage of the implementation plan includes standalone validation tests:

*   **Test Stage 1 (Orchestrator)**:
    ```bash
    .venv/bin/python3 tests/test_orchestrator.py
    ```
*   **Test Stage 2 (Subagent Specialists)**:
    ```bash
    .venv/bin/python3 tests/test_subagents.py
    ```
*   **Test Stage 3 (Executor)**:
    ```bash
    .venv/bin/python3 tests/test_executor.py
    ```
*   **Test Stage 4 (Human-in-the-Loop Gateway)**:
    ```bash
    .venv/bin/python3 tests/test_hitl.py
    ```
