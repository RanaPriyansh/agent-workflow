FROM python:3.9-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -e .

CMD ["python", "-c", "from agent_workflow import Workflow; print('Agent Workflow ready')"]