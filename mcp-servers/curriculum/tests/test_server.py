"""Unit tests for the curriculum MCP server."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest
from mcp.server.fastmcp.exceptions import ToolError
from schemas.curriculum import (
    CourseSummary,
    CurriculumFindForConceptInput,
    CurriculumGetCourseInput,
    CurriculumGetLessonInput,
    CurriculumListCoursesInput,
    CurriculumSuggestPathInput,
    LearningPathSuggestion,
    Level,
)
from schemas.errors import NotFoundError

from curriculum_mcp.errors import invoke, raise_tool_error
from curriculum_mcp.server import create_server


@pytest.fixture
def mock_svc() -> MagicMock:
    summary = CourseSummary(
        id="course-1",
        title="Algebra I",
        level=Level.BEGINNER,
        summary="Intro algebra",
        unit_count=1,
        lesson_count=3,
    )
    svc = MagicMock()
    svc.list_courses = AsyncMock(return_value=[summary])
    svc.get_course = AsyncMock(return_value=None)
    svc.get_lesson = AsyncMock(return_value=None)
    svc.find_for_concept = AsyncMock(return_value=[])
    svc.suggest_path = AsyncMock(
        return_value=LearningPathSuggestion(learner_id="learner-1", goal_id="goal-1", steps=[])
    )
    return svc


@pytest.fixture
def mcp_server(mock_svc: MagicMock):
    return create_server(svc=mock_svc)


@pytest.mark.asyncio
async def test_list_tools_registers_curriculum_tools(mcp_server) -> None:
    tools = await mcp_server.list_tools()
    names = {tool.name for tool in tools}
    expected = {
        "curriculum.list_courses",
        "curriculum.get_course",
        "curriculum.get_lesson",
        "curriculum.find_for_concept",
        "curriculum.suggest_path",
    }
    assert expected <= names


@pytest.mark.asyncio
async def test_curriculum_list_courses(mcp_server, mock_svc: MagicMock) -> None:
    inp = CurriculumListCoursesInput()
    await mcp_server.call_tool("curriculum.list_courses", {"inp": inp.model_dump(mode="json")})
    mock_svc.list_courses.assert_awaited_once()


@pytest.mark.asyncio
async def test_curriculum_get_course(mcp_server, mock_svc: MagicMock) -> None:
    inp = CurriculumGetCourseInput(course_id="course-1")
    await mcp_server.call_tool("curriculum.get_course", {"inp": inp.model_dump(mode="json")})
    mock_svc.get_course.assert_awaited_once_with("course-1")


@pytest.mark.asyncio
async def test_curriculum_get_lesson(mcp_server, mock_svc: MagicMock) -> None:
    inp = CurriculumGetLessonInput(lesson_id="lesson-1")
    await mcp_server.call_tool("curriculum.get_lesson", {"inp": inp.model_dump(mode="json")})
    mock_svc.get_lesson.assert_awaited_once_with("lesson-1")


@pytest.mark.asyncio
async def test_curriculum_find_for_concept(mcp_server, mock_svc: MagicMock) -> None:
    inp = CurriculumFindForConceptInput(concept_id="concept-1")
    await mcp_server.call_tool("curriculum.find_for_concept", {"inp": inp.model_dump(mode="json")})
    mock_svc.find_for_concept.assert_awaited_once()


@pytest.mark.asyncio
async def test_curriculum_suggest_path(mcp_server, mock_svc: MagicMock) -> None:
    inp = CurriculumSuggestPathInput(learner_id="learner-1", goal_id="goal-1")
    await mcp_server.call_tool("curriculum.suggest_path", {"inp": inp.model_dump(mode="json")})
    mock_svc.suggest_path.assert_awaited_once()


def test_create_server_boots(mock_svc: MagicMock) -> None:
    server = create_server(svc=mock_svc)
    assert server.name == "curriculum"


@pytest.mark.asyncio
async def test_curriculum_get_course_maps_app_error(mcp_server, mock_svc: MagicMock) -> None:
    mock_svc.get_course.side_effect = NotFoundError("course missing")
    with pytest.raises(ToolError, match="not_found"):
        await mcp_server.call_tool(
            "curriculum.get_course", {"inp": CurriculumGetCourseInput(course_id="missing").model_dump(mode="json")}
        )


@pytest.mark.asyncio
async def test_invoke_maps_service_error() -> None:
    async def _fail() -> None:
        raise NotFoundError("missing")

    with pytest.raises(ToolError, match="not_found"):
        await invoke(_fail())


def test_main_invokes_run(monkeypatch: pytest.MonkeyPatch) -> None:
    mock_server = MagicMock()
    monkeypatch.setattr("curriculum_mcp.server.create_server", lambda **_: mock_server)
    from curriculum_mcp.server import main

    main()
    mock_server.run.assert_called_once()
