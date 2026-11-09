"""Question bank for VoicePrep practice sessions.

Questions are grouped by category. They are generic interview prompts —
no company-specific or proprietary material — so the bank stays useful
for any software engineering interview.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Question:
    id: str
    category: str
    text: str
    hint: str = ""


QUESTIONS: tuple[Question, ...] = (
    Question(
        id="b1",
        category="behavioral",
        text="Tell me about a time you had to learn a new technology quickly to finish a project.",
        hint="Use STAR: set the scene, your task, what you did, and the result.",
    ),
    Question(
        id="b2",
        category="behavioral",
        text="Describe a disagreement you had with a teammate and how you resolved it.",
        hint="Focus on what you did, not on who was wrong.",
    ),
    Question(
        id="b3",
        category="behavioral",
        text="Tell me about a time you made a mistake at work. What happened and what did you change afterwards?",
        hint="Own the mistake, then show the concrete fix.",
    ),
    Question(
        id="b4",
        category="behavioral",
        text="Describe a project you are most proud of and why.",
        hint="Pick one project and go deep instead of listing several.",
    ),
    Question(
        id="b5",
        category="behavioral",
        text="Tell me about a time you had to prioritize when everything felt urgent.",
        hint="Show the criteria you used to decide what went first.",
    ),
    Question(
        id="b6",
        category="behavioral",
        text="Describe a time you helped a teammate who was struggling.",
        hint="Concrete actions beat general claims about being helpful.",
    ),
    Question(
        id="t1",
        category="technical",
        text="Explain how a hash map works to someone who has never used one.",
        hint="Cover the idea first, then collisions and trade-offs.",
    ),
    Question(
        id="t2",
        category="technical",
        text="How would you find a bug in a program that only fails some of the time?",
        hint="Walk through reproducing, narrowing, and verifying the fix.",
    ),
    Question(
        id="t3",
        category="technical",
        text="What is the difference between a process and a thread, and when would you pick one over the other?",
        hint="Give a definition, then a concrete example for each.",
    ),
    Question(
        id="t4",
        category="technical",
        text="Explain what an API is and how you would design one for a simple to-do app.",
        hint="Start with the resources and the operations on them.",
    ),
    Question(
        id="s1",
        category="situational",
        text="You are halfway through a sprint and a critical dependency breaks. What do you do?",
        hint="Show how you communicate the problem while you work on it.",
    ),
    Question(
        id="s2",
        category="situational",
        text="A user reports a bug you cannot reproduce on your machine. How do you proceed?",
        hint="Logs, environment differences, and a minimal reproduction.",
    ),
)


def list_questions(category: str | None = None) -> list[Question]:
    """Return all questions, optionally filtered by category."""
    if category is None:
        return list(QUESTIONS)
    return [q for q in QUESTIONS if q.category == category]


def categories() -> list[str]:
    """Return the categories in the order they first appear."""
    seen: list[str] = []
    for question in QUESTIONS:
        if question.category not in seen:
            seen.append(question.category)
    return seen


def get_question(question_id: str) -> Question:
    """Return one question by id, raising KeyError for an unknown id."""
    for question in QUESTIONS:
        if question.id == question_id:
            return question
    raise KeyError(f"unknown question id: {question_id!r}")
