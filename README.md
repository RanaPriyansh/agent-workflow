# Thielon Agent Workflow

[![GitHub](https://img.shields.io/badge/GitHub-000000?logo=github)](https://github.com/thielon-apps/thielon-agent-workflow)
[![License](https://img.shields.io/github/license/thielon-apps/thielon-agent-workflow)](https://github.com/thielon-apps/thielon-agent-workflow/blob/main/LICENSE)
[![Last commit](https://img.shields.io/github/last-commit/thielon-apps/thielon-agent-workflow)](https://github.com/thielon-apps/thielon-agent-workflow/commits/main)

Orchestrate multiple AI agents in complex workflows. Define DAGs, queues, state machines, and human-in-the-loop approvals.

## Features

- **DAG Workflows**: Define agent execution order with dependencies
- **State Management**: Persistent workflow state (Redis/DB)
- **Queue System**: Async task queue for agent coordination
- **Human-in-the-Loop**: Pause for approval, inject human input
- **Retry & Error Handling**: Automatic retries, dead letter queues
- **Observability**: Track workflow execution, visualize DAGs

## Quick Start

```python
from thielon_workflow import Workflow, AgentTask

# Define workflow
wf = Workflow(name="content-generation")

# Define tasks
research = AgentTask("research-agent", input="topic")
write = AgentTask("writer-agent", depends_on=[research])
review = AgentTask("reviewer-agent", depends_on=[write], human_approval=True)

# Add tasks
wf.add_task(research)
wf.add_task(write)
wf.add_task(review)

# Execute
wf.run()
```

## Install

```bash
pip install thielon-agent-workflow
```

## Why

Single agents are limited. Complex tasks need multiple agents:
- Researcher → Writer → Editor → Publisher
- Data collector → Analyzer → Visualizer → Reporter
- Planner → Executor → Reviewer

This workflow engine provides:
- Reliable coordination
- Error recovery
- Human oversight points
- Debugging/tracing

## License

MIT
