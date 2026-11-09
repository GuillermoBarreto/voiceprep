"""Answer analysis: filler words, pacing, length, and STAR structure.

All analysis is heuristic and runs locally on the transcript text. It is
meant to surface patterns for the speaker to work on, not to grade an
answer. Nothing here calls a network service.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

# Words and phrases that usually add nothing to a spoken answer.
FILLERS: tuple[str, ...] = (
    "um",
    "uh",
    "like",
    "you know",
    "basically",
    "actually",
    "literally",
    "sort of",
    "kind of",
    "i mean",
    "right",
    "so yeah",
)

# Keyword cues for each STAR section. A section counts as present when at
# least one cue appears in the transcript.
STAR_CUES: dict[str, tuple[str, ...]] = {
    "situation": (
        "when",
        "at the time",
        "the situation was",
        "we were",
        "the context",
        "back then",
    ),
    "task": (
        "i needed to",
        "my job was",
        "my role",
        "i was responsible",
        "the task",
        "i had to",
    ),
    "action": (
        "i decided",
        "i built",
        "i implemented",
        "i reached out",
        "i organized",
        "i led",
        "i wrote",
        "i set up",
        "i talked to",
        "i suggested",
    ),
    "result": (
        "the result",
        "the outcome",
        "improved",
        "reduced",
        "saved",
        "shipped",
        "as a result",
        "i learned",
        "in the end",
    ),
}

# Guidance for spoken answers, in words per minute and seconds.
TARGET_WPM_LOW = 110
TARGET_WPM_HIGH = 180
TARGET_SECONDS_LOW = 45
TARGET_SECONDS_HIGH = 150


@dataclass(frozen=True)
class Analysis:
    word_count: int
    filler_count: int
    filler_rate_per_100_words: float
    fillers_found: dict[str, int]
    wpm: float | None
    estimated_seconds: float | None
    star_sections: dict[str, bool]
    star_score: float
    feedback: tuple[str, ...]


def _word_list(text: str) -> list[str]:
    return re.findall(r"[A-Za-z']+", text.lower())


def count_fillers(text: str) -> dict[str, int]:
    """Count each filler phrase in the transcript (case-insensitive)."""
    lowered = " " + re.sub(r"[^a-z' ]", " ", text.lower()) + " "
    found: dict[str, int] = {}
    for filler in FILLERS:
        matches = len(re.findall(r"\b" + re.escape(filler) + r"\b", lowered))
        if matches:
            found[filler] = matches
    return found


def star_sections_present(text: str) -> dict[str, bool]:
    """Check which STAR sections have at least one keyword cue."""
    lowered = " " + re.sub(r"[^a-z' ]", " ", text.lower()) + " "
    present: dict[str, bool] = {}
    for section, cues in STAR_CUES.items():
        present[section] = any(
            re.search(r"\b" + re.escape(cue) + r"\b", lowered) for cue in cues
        )
    return present


def estimate_seconds(word_count: int, wpm: float = 150.0) -> float:
    """Estimate speaking time from a word count at a typical pace."""
    return word_count / wpm * 60.0


def analyze(text: str, seconds: float | None = None) -> Analysis:
    """Analyze one answer transcript.

    ``seconds`` is the measured speaking time when known. Without it, the
    speaking time is estimated at 150 words per minute and no WPM is
    reported.
    """
    words = _word_list(text)
    word_count = len(words)
    fillers_found = count_fillers(text)
    filler_count = sum(fillers_found.values())
    filler_rate = (filler_count / word_count * 100) if word_count else 0.0
    sections = star_sections_present(text)
    star_score = sum(sections.values()) / len(sections)

    if seconds is not None and seconds > 0:
        wpm = word_count / seconds * 60.0
        estimated = seconds
    else:
        wpm = None
        estimated = estimate_seconds(word_count) if word_count else None

    feedback: list[str] = []
    if word_count == 0:
        feedback.append("No answer recorded — try speaking the answer out loud first.")
    if filler_rate > 5:
        feedback.append(
            f"Fillers are high ({filler_rate:.1f} per 100 words). "
            "Slow down slightly and pause instead of filling the gap."
        )
    elif filler_rate > 2:
        feedback.append(
            f"A few fillers ({filler_rate:.1f} per 100 words). "
            "A short pause reads better than 'um'."
        )
    if wpm is not None:
        if wpm > TARGET_WPM_HIGH:
            feedback.append(
                f"Pace is fast ({wpm:.0f} wpm). Slow down so each point lands."
            )
        elif wpm < TARGET_WPM_LOW:
            feedback.append(
                f"Pace is slow ({wpm:.0f} wpm). Pick up the tempo a little."
            )
    if estimated is not None:
        if estimated < TARGET_SECONDS_LOW:
            feedback.append(
                f"Answer is short (about {estimated:.0f}s). "
                "Add one concrete detail or example."
            )
        elif estimated > TARGET_SECONDS_HIGH:
            feedback.append(
                f"Answer runs long (about {estimated:.0f}s). "
                "Trim it to the strongest example."
            )
    missing = [section for section, present in sections.items() if not present]
    if word_count > 0 and missing:
        feedback.append(
            "STAR structure is missing: " + ", ".join(missing) + ". "
            "Add a sentence for each missing part."
        )
    if not feedback:
        feedback.append(
            "Solid answer: reasonable length, low fillers, and full STAR structure."
        )

    return Analysis(
        word_count=word_count,
        filler_count=filler_count,
        filler_rate_per_100_words=round(filler_rate, 1),
        fillers_found=fillers_found,
        wpm=round(wpm, 1) if wpm is not None else None,
        estimated_seconds=round(estimated, 1) if estimated is not None else None,
        star_sections=sections,
        star_score=round(star_score, 2),
        feedback=tuple(feedback),
    )
