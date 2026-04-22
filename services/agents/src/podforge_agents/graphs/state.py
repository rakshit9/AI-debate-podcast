from typing import Any, Literal, TypedDict


class ScriptLine(TypedDict):
    speaker: str
    text: str


class PipelineState(TypedDict):
    # ── Inputs ────────────────────────────────────────────────────────────────
    topic: str
    show_id: str
    episode_id: str
    format: Literal["debate", "interview", "panel"]

    # ── Intermediate ──────────────────────────────────────────────────────────
    research_data: dict[str, Any]
    outline: dict[str, Any]
    script: list[ScriptLine]
    fact_check_results: dict[str, Any]
    audio_segments: list[dict[str, Any]]

    # ── Outputs ───────────────────────────────────────────────────────────────
    final_audio_url: str | None
    transcript: str | None
    published_urls: dict[str, str]

    # ── Control ───────────────────────────────────────────────────────────────
    retry_count: int
    errors: list[str]
    outline_approved: bool
    script_clean: bool
    requires_human_approval: bool


def initial_state(
    topic: str,
    show_id: str,
    episode_id: str,
    fmt: Literal["debate", "interview", "panel"] = "debate",
    requires_human_approval: bool = False,
) -> PipelineState:
    return PipelineState(
        topic=topic,
        show_id=show_id,
        episode_id=episode_id,
        format=fmt,
        research_data={},
        outline={},
        script=[],
        fact_check_results={},
        audio_segments=[],
        final_audio_url=None,
        transcript=None,
        published_urls={},
        retry_count=0,
        errors=[],
        outline_approved=False,
        script_clean=False,
        requires_human_approval=requires_human_approval,
    )
