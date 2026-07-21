from crewai import Agent, Crew, Process, Task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import FileReadTool, DirectoryReadTool


@CrewBase
class IntegrationTesterCrew:
    """Integration testing crew — scout → execute → report."""

    agents: list[BaseAgent]
    tasks: list[Task]

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def test_scout(self) -> Agent:
        return Agent(
            config=self.agents_config["test_scout"],  # type: ignore[index]
            tools=[FileReadTool(), DirectoryReadTool()],
        )

    @agent
    def test_executor(self) -> Agent:
        return Agent(
            config=self.agents_config["test_executor"],  # type: ignore[index]
            tools=[FileReadTool(), DirectoryReadTool()],
        )

    @agent
    def findings_reporter(self) -> Agent:
        return Agent(
            config=self.agents_config["findings_reporter"],  # type: ignore[index]
        )

    @task
    def scout_integration_surface(self) -> Task:
        return Task(config=self.tasks_config["scout_integration_surface"])  # type: ignore[index]

    @task
    def execute_integration_plan(self) -> Task:
        return Task(config=self.tasks_config["execute_integration_plan"])  # type: ignore[index]

    @task
    def report_integration_findings(self) -> Task:
        return Task(config=self.tasks_config["report_integration_findings"])  # type: ignore[index]

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
