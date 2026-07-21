from crewai import Agent, Crew, Process, Task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import FileReadTool, DirectoryReadTool


@CrewBase
class QaTesterCrew:
    """Product QA crew — scenarios → scripts → report."""

    agents: list[BaseAgent]
    tasks: list[Task]

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def qa_scenario_designer(self) -> Agent:
        return Agent(
            config=self.agents_config["qa_scenario_designer"],  # type: ignore[index]
            tools=[FileReadTool(), DirectoryReadTool()],
        )

    @agent
    def qa_executor(self) -> Agent:
        return Agent(
            config=self.agents_config["qa_executor"],  # type: ignore[index]
            tools=[FileReadTool(), DirectoryReadTool()],
        )

    @agent
    def qa_reporter(self) -> Agent:
        return Agent(
            config=self.agents_config["qa_reporter"],  # type: ignore[index]
        )

    @task
    def design_qa_scenarios(self) -> Task:
        return Task(config=self.tasks_config["design_qa_scenarios"])  # type: ignore[index]

    @task
    def execute_qa_scripts(self) -> Task:
        return Task(config=self.tasks_config["execute_qa_scripts"])  # type: ignore[index]

    @task
    def report_qa_findings(self) -> Task:
        return Task(config=self.tasks_config["report_qa_findings"])  # type: ignore[index]

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
