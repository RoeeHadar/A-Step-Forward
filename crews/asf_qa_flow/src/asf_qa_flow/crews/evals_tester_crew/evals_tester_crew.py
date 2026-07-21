from crewai import Agent, Crew, Process, Task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import FileReadTool, DirectoryReadTool


@CrewBase
class EvalsTesterCrew:
    """Evals / agent-quality testing crew — scout → execute → report."""

    agents: list[BaseAgent]
    tasks: list[Task]

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def evals_scout(self) -> Agent:
        return Agent(
            config=self.agents_config["evals_scout"],  # type: ignore[index]
            tools=[FileReadTool(), DirectoryReadTool()],
        )

    @agent
    def evals_executor(self) -> Agent:
        return Agent(
            config=self.agents_config["evals_executor"],  # type: ignore[index]
            tools=[FileReadTool(), DirectoryReadTool()],
        )

    @agent
    def evals_reporter(self) -> Agent:
        return Agent(
            config=self.agents_config["evals_reporter"],  # type: ignore[index]
        )

    @task
    def scout_evals_coverage(self) -> Task:
        return Task(config=self.tasks_config["scout_evals_coverage"])  # type: ignore[index]

    @task
    def execute_evals_plan(self) -> Task:
        return Task(config=self.tasks_config["execute_evals_plan"])  # type: ignore[index]

    @task
    def report_evals_findings(self) -> Task:
        return Task(config=self.tasks_config["report_evals_findings"])  # type: ignore[index]

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
