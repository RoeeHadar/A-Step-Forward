from crewai import Agent, Crew, Process, Task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import FileReadTool, DirectoryReadTool


@CrewBase
class DeliberationCrew:
    """Five suite advocates + facilitator. No binding decisions."""

    agents: list[BaseAgent]
    tasks: list[Task]

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def integration_advocate(self) -> Agent:
        return Agent(
            config=self.agents_config["integration_advocate"],  # type: ignore[index]
            tools=[FileReadTool(), DirectoryReadTool()],
        )

    @agent
    def ui_advocate(self) -> Agent:
        return Agent(
            config=self.agents_config["ui_advocate"],  # type: ignore[index]
            tools=[FileReadTool(), DirectoryReadTool()],
        )

    @agent
    def qa_advocate(self) -> Agent:
        return Agent(
            config=self.agents_config["qa_advocate"],  # type: ignore[index]
            tools=[FileReadTool(), DirectoryReadTool()],
        )

    @agent
    def security_advocate(self) -> Agent:
        return Agent(
            config=self.agents_config["security_advocate"],  # type: ignore[index]
            tools=[FileReadTool(), DirectoryReadTool()],
        )

    @agent
    def evals_advocate(self) -> Agent:
        return Agent(
            config=self.agents_config["evals_advocate"],  # type: ignore[index]
            tools=[FileReadTool(), DirectoryReadTool()],
        )

    @agent
    def facilitator(self) -> Agent:
        return Agent(
            config=self.agents_config["facilitator"],  # type: ignore[index]
            tools=[FileReadTool(), DirectoryReadTool()],
        )

    @task
    def advocate_integration(self) -> Task:
        return Task(config=self.tasks_config["advocate_integration"])  # type: ignore[index]

    @task
    def advocate_ui(self) -> Task:
        return Task(config=self.tasks_config["advocate_ui"])  # type: ignore[index]

    @task
    def advocate_qa(self) -> Task:
        return Task(config=self.tasks_config["advocate_qa"])  # type: ignore[index]

    @task
    def advocate_security(self) -> Task:
        return Task(config=self.tasks_config["advocate_security"])  # type: ignore[index]

    @task
    def advocate_evals(self) -> Task:
        return Task(config=self.tasks_config["advocate_evals"])  # type: ignore[index]

    @task
    def facilitate_deliberation(self) -> Task:
        return Task(config=self.tasks_config["facilitate_deliberation"])  # type: ignore[index]

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
