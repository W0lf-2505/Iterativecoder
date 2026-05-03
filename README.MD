# 🚀 Project: **IterativeCoder Agent**

## Autonomous Coding Agent (Level 2 Iterative System)

---

## 📌 Overview

**IterativeCoder Agent** is a working autonomous coding system that can:

* Take a high-level goal
* Break it into executable steps
* Generate tool actions via LLM
* Execute those actions safely
* Capture outputs (stdout/stderr)
* Replan on failure
* Iterate until completion

This is a **Level 2 autonomous agent** with a functional closed-loop system.

---

## ✅ Current Capabilities

The system can already:

* ✔ Plan multi-step tasks
* ✔ Execute file + terminal operations
* ✔ Run Python code
* ✔ Capture execution output
* ✔ Pass data between steps (stdout → next action)
* ✔ Retry on LLM errors
* ✔ Replan on failure
* ✔ Maintain execution state
* ✔ Expose agent via FastAPI REST + WebSocket routes

---

## 🧠 Core Architecture

```
User Goal
   ↓
Planner (LLM)
   ↓
Step Executor (LLM → single action)
   ↓
Validator → Executor (Tools)
   ↓
State Update (stdout, stderr, history)
   ↓
Replanner (on failure)
   ↓
Loop until success
```

---

## 🔧 Components

### 1. Planner

* Converts goal → structured steps
* Outputs JSON plan
* Enforced to generate **execution-ready steps only**

---

### 2. Step Executor (LLM)

* Converts ONE step → ONE action
* Strict JSON output enforced
* No multi-step execution allowed

Example:

```json
{
  "action": "write_to_file",
  "input": {
    "file_path": "main.py",
    "data": "print('hello')"
  }
}
```

---

### 3. Executor (Tool Layer)

Handles real-world operations:

* `write_to_file(path, data)`
* `read_from_file(path)`
* `run_command(command)`
* `install_package(package_name)`
* `create_directory(directory_path)`
* `run_tests()`

---

### 4. Validator

* Ensures tool exists in registry
* Filters invalid arguments
* Prevents unsafe execution

---

### 5. State (Critical)

Tracks:

```python
goal
project
last_output
last_error
execution_history
```

Enables:

* stdout chaining
* error-based replanning
* contextual reasoning

---

### 6. Controller Loop (WORKING)

```python
while True:
    for step in plan:
        action = llm_generate(step)
        action = validate(action)
        action = inject_context(action)

        result = execute(action)
        state.update(result)

        if failure:
            plan = replan(...)
            break
    else:
        break
```

---

## 🌐 API Routes

The agent is exposed via **FastAPI** with REST and WebSocket endpoints.

### REST

| Method | Route | Description |
|--------|-------|-------------|
| `POST` | `/run` | Submit a goal and start the agent. Returns a `task_id`. |

### WebSocket

| Route | Description |
|-------|-------------|
| `/ws/{task_id}` | Stream real-time agent output for a running task. |

#### WebSocket message format

Messages are prefixed by type:

```
PLAN: {"plan": [{"step": 1, "description": "..."}]}
STEP: Create a project directory
RESULT: {"status": "success", "tool": "write_to_file", ...}
STATUS: complete
```

---

## 🚀 Getting Started

### 1. Clone & install

```bash
git clone <repo>
cd iterativecoder
pip install -r requirements.txt
```

### 2. Run the backend

```bash
uvicorn app.api.server:app --reload
```

The API will be available at `http://localhost:8000`.
Interactive docs at `http://localhost:8000/docs`.

---

## 🖥️ Agent UI (Frontend)

The `AgentUI/` folder contains a **Vite + React** frontend that connects to the backend.

### Setup

```bash
cd AgentUI
npm install
```

### Generate typed API client

The frontend uses an auto-generated typed client from the FastAPI OpenAPI schema.
Make sure the backend is running first, then:

```bash
npm run generate-api
```

This reads `http://localhost:8000/openapi.json` and outputs a fully typed client to `src/lib/api/`.

> The generate script is defined in `package.json` as:
> ```json
> "generate-api": "openapi-ts --input http://localhost:8000/openapi.json --output src/lib/api --client @hey-api/client-fetch"
> ```

### Run the frontend

```bash
npm run dev
```

The UI will be available at `http://localhost:5173`.

---

## 🔥 Key Features Implemented

### ✅ 1. Deterministic Execution Context

* Project folder is system-controlled
* LLM cannot override execution paths
* All steps run inside:

```text
workspace/projects/<project_id>/
```

---

### ✅ 2. Safe Command Execution

* No `cd`, `&&`, or shell chaining
* Uses `subprocess.run(..., cwd=...)`
* Prevents command injection risks

---

### ✅ 3. Robust JSON Handling

* Extracts first valid JSON from LLM output
* Ignores explanations / markdown / noise
* Handles malformed responses with retries

---

### ✅ 4. Single-Action Enforcement

* Each step → exactly ONE tool call
* Prevents planner/executor confusion

---

### ✅ 5. Output Chaining (Critical)

System injects runtime data:

```text
stdout → next step
stderr → next step
```

No LLM guessing.

---

### ✅ 6. Retry + Recovery

* Retries invalid LLM outputs
* Replans on execution failure
* Continues loop correctly (no premature exit)

---

## ⚙️ Tech Stack

### Core

* Python
* FastAPI

### LLM

* Ollama (local inference)

  * Mistral
  * DeepSeek Coder

### Execution

* subprocess (safe execution)
* python-dotenv (config)

### Frontend

* Vite + React + TypeScript
* `@hey-api/openapi-ts` — typed API client generation
* `@hey-api/client-fetch` — fetch-based HTTP client

---

## 🧠 Design Principles (Now Enforced)

### 1. LLM ≠ Execution Engine

LLM decides:

```text
WHAT to do
```

System controls:

```text
HOW it runs
```

---

### 2. No Runtime Data in LLM

❌ LLM guessing:

```json
"data": "<use previous stdout>"
```

✅ System injection:

```json
"source": "stdout"
```

---

### 3. Single Source of Truth

* Tool registry = validation source
* State = execution memory
* Controller = orchestration

---

### 4. Defensive Execution

* Invalid args filtered
* Missing context injected
* Unsafe commands blocked

---

## ⚠️ Current Limitations

### ❌ FastAPI / Framework Knowledge

LLM still:

* uses `app.run()` ❌
* forgets `uvicorn` ❌

---

### ❌ Weak Planning Quality

Planner sometimes generates:

* non-executable steps
* redundant steps

---

### ❌ Long-running Processes

* `uvicorn --reload` blocks execution
* no background execution yet

---

### ❌ No Multi-file Awareness

* Works best on small tasks
* struggles with larger systems

---

## 🧪 What It Can Build (Today)

* CLI tools
* simple APIs
* Python scripts
* file processors
* small automation tasks

---

## 🚧 Roadmap (Updated)

### Phase 1 — Stabilization (Current)

* ✔ Execution loop
* ✔ Context injection
* ✔ Tool safety
* ✔ JSON robustness
* ✔ FastAPI routes + WebSocket streaming

---

### Phase 2 — Intelligence Upgrade

* Better planner constraints
* Improved replanner logic
* Schema-based outputs

---

### Phase 3 — Execution Power

* Background process handling
* Docker sandbox
* async execution

---

### Phase 4 — Multi-Agent System

* Planner agent
* Coder agent
* Debug agent

---

## 🔒 Safety

* Workspace sandboxing
* Command restrictions
* No arbitrary shell execution
* Controlled file access

---

## 💡 Vision

IterativeCoder is evolving into:

> A system that doesn't just generate code
> but **executes, validates, and improves it autonomously**

---

## 📊 Current Status

```text
Level: 2 (Iterative Agent)
State: Functional MVP
Focus: Stability → Intelligence → Scale
```

---

## 🤝 Contributions

Open for experimentation. Expect rapid iteration and breaking changes.

---

## 📄 License

MIT License — see LICENSE file for details.
