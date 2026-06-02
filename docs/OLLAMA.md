# Ollama Developer & Agent Guidelines

This document outlines the coding workflow and execution guidelines adapted for Ollama local model execution, inspired by Karpathy's guidelines for agent workflows.

---

## Coding Workflow Principles

### 1. Plan Mode First
- Use plan mode for any non-trivial task.
- Write detailed specs up front.
- Reduce ambiguity before writing code.
- Lightweight inline plan for smaller tasks.

### 2. Verify Relentlessly
- Watch execution closely in your terminal or IDE.
- Check assumptions, edge cases, and architectural tradeoffs.
- Run tests, review diffs, and verify correctness.
- Don't blindly accept agent suggestions—stay in the loop.

### 3. Keep It Simple
- Avoid overengineering and bloated abstractions.
- Prefer 100 lines of clear, readable code over 1000 lines of complex structures.
- Clean up dead code and cruft.
- Always ask: "Is there a simpler way?"

### 4. Surgical Edits Only
- Change only what's necessary to solve the problem.
- Don't touch unrelated code, comments, or formatting.
- Don't "improve" things that are working fine.
- Minimize side effects and churn.

### 5. Goal-Driven Execution
- Define clear success criteria before starting.
- Write tests first (where applicable), then make them pass.
- Leverage local model APIs (Ollama endpoints) and tools.
- Let the agent iterate until the goal is fully achieved.

### 6. Parallelize with Subagents
- Offload research, exploration, and heavy analysis to focused subagents.
- Use subagents to keep the parent context clean.
- Ensure one distinct task per subagent.
- Merge results back with human/parent judgment.

---

## Core Principles

- **Simplicity First**: Minimal, elegant code that directly solves the problem. Nothing speculative.
- **No Laziness**: Find the root cause of bugs/issues. Avoid temporary patches. Keep senior developer standards.
- **Minimal Impact**: Touch only the relevant code paths. No side effects. Prevent new bugs.

---

## Local Execution Mindset (Ollama)

* **Tenacity**: Local models don't have rate limits, but they can be slower on CPU/GPU. relently optimize prompt contexts to prevent execution lag.
* **Leverage**: Focus on structured output format parameters to ensure parsing reliability (e.g. JSON schema formats).
* **Fun**: Automate the drudgery to focus on creativity.
* **Atrophy**: Reading and writing code are different skills; stay sharp on both.
* **Speedups &ne; Just Faster**: Use the local nature of Ollama to run experiments freely without cost.
* **Slopocalypse**: Reverify all output. Small local models can hallucinate or fail formatting more often. Signal requires verification.
