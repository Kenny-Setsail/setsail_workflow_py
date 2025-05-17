## My Dear Colleagues
This repository is for QA tools(workflows), you can use this on your python projects.

# SS-PyWorkflow

This project is designed to simplify and standardize workflow execution using decorators to automate task execution and result tracking. It is primarily used for `llm-graph`, but it can be extended to other projects as well.

---

## 🚀 Installation

```bash
pip install ss-pyworkflow
```

## Environment Variables

To configure the Workflow Monitoring Service, please add the following environment variables to your `.env` file or your environment settings:

| Variable Name                 | Description                          | Example Value                    |
|-------------------------------|--------------------------------------|----------------------------------|
| `WORKFLOW_MONITORING_URL`    | The endpoint URL for sending data.   | `https://example.com/api/v1/log` |
| `WORKFLOW_MONITORING_API_KEY`| The API key for authentication.      | `your-secret-api-key`            |

### Example:
```env
WORKFLOW_MONITORING_URL=https://example.com/api/v1/log
WORKFLOW_MONITORING_API_KEY=your-secret-api-key
```

## 📖 Usage
`SS-PyWorkflow` provides two main modes for managing workflows:

### 1️⃣ Single Function Mode
When you only need to track a single function, you can use the `@workflow_entry` decorator:

```python
from ss_pyworkflow import workflow_entry

@workflow_entry(name="llm-graph")
async def _run_multigraph(**kwargs):
    # Your logic here...
    ...
```

After the function execution is completed, the result of this node will automatically be sent to the specified workflow backend and trigger the workflow end signal.

### 2️⃣ Chained Function Mode
If your workflow consists of multiple functions that execute sequentially, and each function's output is the next function's input, use the `@workflow_lifecycle` decorator:

```python
from ss_pyworkflow import workflow_lifecycle

@workflow_lifecycle()
async def aexecute(self, state: AgentStateT) -> AgentStateT:
    # Each function's output will be passed to the next function
    ...
```

In this mode, after each function execution, data is automatically sent to the workflow and visualized as step-by-step nodes in the backend.

## ⚙️ Kwargs Explanation
Both `@workflow_entry` and `@workflow_lifecycle` require workflow_trace_data to be passed in kwargs for proper tracking and data transmission:

```json
"workflow_trace_data": {
    "enable": true,
    "traceId": "592225192fb1ac17022e80c85fb8a749",
    "prevSpanId": "3f7decc34dc8d03a",
    "userId": "202505125600020250512145500563QSLVDGS96F",
    "projectId": "mtr-kiosk-pquzibd",
    "componentName": "llm-graph",
    "post_url": "https://dev.setsailapi.com/workflow/v1/event",
    "log_enabled": true
}
```
## Parameter Description:
| Parameter Name  | Type   | Description                                                                              |
| --------------- | ------ | ---------------------------------------------------------------------------------------- |
| `enable`        | `bool` | Whether to enable the workflow. If `False`, no operations will be performed.             |
| `traceId`       | `str`  | A unique identifier for the entire workflow execution (32-character hexadecimal format). |
| `prevSpanId`    | `str`  | The parent span ID (16-character hexadecimal format). Can be `null` for root spans.      |
| `userId`        | `str`  | The user ID that triggers this workflow.                                                 |
| `projectId`     | `str`  | The project ID associated with this workflow.                                            |
| `componentName` | `str`  | Specifies the name of the workflow (e.g., `llm-graph`).                                  |
| `post_url`      | `str`  | The backend API URL to send workflow data.                                               |
| `log_enabled`   | `bool` | Whether to enable logging.                                                               |

## 📌 Examples
### Single Function Mode
```python
from ss_pyworkflow import workflow_entry

@workflow_entry(name="llm-graph")
async def run_task(**kwargs):
    print("Executing task...")
```

### Chained Function Mode
```python
from ss_pyworkflow import workflow_lifecycle

@workflow_lifecycle()
async def task_one(state):
    print("Task One")
    return state

@workflow_lifecycle()
async def task_two(state):
    print("Task Two")
    return state
```

## 🌐 Extension Support
Currently, it is mainly focused on `llm-graph`, but it can be extended to other workflow scenarios by modifying the decorators or adding new ones.

## License

This project is licensed under the [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0).  
Copyright © 2025 Set Sail Venture Limited
