"""Curriculum MCP tool handlers."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP
from schemas.curriculum import (
    Course,
    CourseSummary,
    CurriculumFindForConceptInput,
    CurriculumGetCourseInput,
    CurriculumGetLessonInput,
    CurriculumListCoursesInput,
    CurriculumSuggestPathInput,
    LearningPathSuggestion,
    Lesson,
    LessonMatch,
)

from curriculum_mcp.errors import invoke
from curriculum_service.api import CurriculumService, get_curriculum_service


def register_curriculum_tools(
    mcp: FastMCP,
    *,
    svc: CurriculumService | None = None,
) -> CurriculumService:
    service = svc or get_curriculum_service()

    @mcp.tool(name="curriculum.list_courses", description="List published courses.")
    async def curriculum_list_courses(inp: CurriculumListCoursesInput) -> list[CourseSummary]:
        return await invoke(service.list_courses(level=inp.level, limit=inp.limit))

    @mcp.tool(name="curriculum.get_course", description="Fetch a course by id.")
    async def curriculum_get_course(inp: CurriculumGetCourseInput) -> Course | None:
        return await invoke(service.get_course(inp.course_id))

    @mcp.tool(name="curriculum.get_lesson", description="Fetch a lesson by id.")
    async def curriculum_get_lesson(inp: CurriculumGetLessonInput) -> Lesson | None:
        return await invoke(service.get_lesson(inp.lesson_id))

    @mcp.tool(name="curriculum.find_for_concept", description="Find lessons that cover a concept.")
    async def curriculum_find_for_concept(inp: CurriculumFindForConceptInput) -> list[LessonMatch]:
        return await invoke(service.find_for_concept(inp.concept_id, limit=inp.limit))

    @mcp.tool(
        name="curriculum.suggest_path",
        description="Suggest a personalized learning path for a learner and goal.",
    )
    async def curriculum_suggest_path(inp: CurriculumSuggestPathInput) -> LearningPathSuggestion:
        return await invoke(
            service.suggest_path(learner_id=inp.learner_id, goal_id=inp.goal_id, max_steps=inp.max_steps)
        )

    return service
