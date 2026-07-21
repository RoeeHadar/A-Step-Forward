from crewai import Agent, Crew, Process, Task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import FileReadTool, DirectoryReadTool


@CrewBase
class UiTesterCrew:
    """UI / E2E testing crew — scout → execute → report."""

    agents: list[BaseAgent]
    tasks: list[Task]

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def ui_scout(self) -> Agent:
        return Agent(
            config=self.agents_config["ui_scout"],  # type: ignore[index]
            tools=[FileReadTool(), DirectoryReadTool()],
        )

    @agent
    def ui_executor(self) -> Agent:
        return Agent(
            config=self.agents_config["ui_executor"],  # type: ignore[index]
            tools=[FileReadTool(), DirectoryReadTool()],
        )

    @agent
    def ui_reporter(self) -> Agent:
        return Agent(
            config=self.agents_config["ui_reporter"],  # type: ignore[index]
        )

    @task
    def scout_ui_flows(self) -> Task:
        return Task(config=self.tasks_config["scout_ui_flows"])  # type: ignore[index]

    @task
    def execute_ui_plan(self) -> Task:
        return Task(config=self.tasks_config["execute_ui_plan"])  # type: ignore[index]

    @task
    def report_ui_findings(self) -> Task:
        return Task(config=self.tasks_config["report_ui_findings"])  # type: ignore[index]

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
