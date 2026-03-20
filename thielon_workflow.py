class AgentTask:
    def __init__(self, agent_id, depends_on=None, human_approval=False):
        self.agent_id = agent_id
        self.depends_on = depends_on or []
        self.human_approval = human_approval
class Workflow:
    def __init__(self, name):
        self.name = name
        self.tasks = []
    def add_task(self, task):
        self.tasks.append(task)
    def run(self):
        return {"status": "running", "tasks": len(self.tasks)}
