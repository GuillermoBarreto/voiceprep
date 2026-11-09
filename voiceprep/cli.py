"""Command-line interface for VoicePrep.

Usage:
    python -m voiceprep.cli questions [--category behavioral]
    python -m voiceprep.cli practice [--question b1] [--transcript FILE] [--seconds N]
    python -m voiceprep.cli report [--limit N]

The practice flow shows a question, then reads the spoken answer as a
transcript. Type or paste the transcript and finish with an empty line
(or Ctrl-D). Pass ``--transcript FILE`` to read it from a file instead —
that is the hook for a speech-to-text tool to drop a transcript in.
"""

from __future__ import annotations

import argparse
import random
import sys
import time

from . import __version__, analysis, questions, store


def _read_transcript_from_stdin() -> str:
    print("Speak your answer, then type or paste the transcript.")
    print("Finish with an empty line (Ctrl-D also works).")
    lines: list[str] = []
    try:
        while True:
            line = input()
            if line == "":
                break
            lines.append(line)
    except EOFError:
        pass
    return "\n".join(lines)


def cmd_questions(args: argparse.Namespace) -> int:
    found = questions.list_questions(args.category)
    if not found:
        print(f"No questions in category {args.category!r}.")
        print("Categories:", ", ".join(questions.categories()))
        return 1
    for question in found:
        print(f"[{question.id}] ({question.category}) {question.text}")
        if question.hint:
            print(f"    Hint: {question.hint}")
    return 0


def cmd_practice(args: argparse.Namespace) -> int:
    if args.question:
        try:
            question = questions.get_question(args.question)
        except KeyError as exc:
            print(exc)
            return 1
    else:
        pool = questions.list_questions(args.category)
        if not pool:
            print(f"No questions in category {args.category!r}.")
            return 1
        question = random.choice(pool)

    print(f"Question [{question.id}] ({question.category}):")
    print(f"  {question.text}")
    if question.hint:
        print(f"  Hint: {question.hint}")
    print()

    seconds: float | None = args.seconds
    if args.transcript:
        transcript = args.transcript.read()
    else:
        start = time.monotonic()
        transcript = _read_transcript_from_stdin()
        if seconds is None:
            seconds = time.monotonic() - start

    result = analysis.analyze(transcript, seconds=seconds)

    print()
    print(f"Words: {result.word_count}  |  Fillers: {result.filler_count} "
          f"({result.filler_rate_per_100_words} per 100 words)")
    if result.wpm is not None:
        print(f"Pace: {result.wpm} wpm")
    if result.estimated_seconds is not None:
        print(f"Length: about {result.estimated_seconds:.0f}s")
    star = ", ".join(
        f"{name}: {'yes' if present else 'no'}"
        for name, present in result.star_sections.items()
    )
    print(f"STAR ({result.star_score:.0%}): {star}")
    if result.fillers_found:
        fillers = ", ".join(
            f"{word} x{count}" for word, count in result.fillers_found.items()
        )
        print(f"Fillers found: {fillers}")
    print()
    for note in result.feedback:
        print(f"- {note}")

    conn = store.connect(args.db)
    session_id = store.save_session(
        conn,
        question_id=question.id,
        category=question.category,
        transcript=transcript,
        seconds=seconds,
        word_count=result.word_count,
        filler_count=result.filler_count,
        filler_rate=result.filler_rate_per_100_words,
        wpm=result.wpm,
        star_score=result.star_score,
    )
    conn.close()
    print(f"\nSaved as session #{session_id}. Run `voiceprep report` to track progress.")
    return 0


def cmd_report(args: argparse.Namespace) -> int:
    conn = store.connect(args.db)
    totals = store.summary(conn)
    recent = store.list_sessions(conn, limit=args.limit)
    conn.close()

    if totals["sessions"] == 0:
        print("No practice sessions yet. Run `voiceprep practice` first.")
        return 0

    print(f"Sessions: {totals['sessions']}")
    print(f"Avg fillers: {totals['avg_filler_rate']} per 100 words")
    print(f"Avg pace: {totals['avg_wpm']} wpm")
    print(f"Avg STAR score: {totals['avg_star_score']:.0%}")
    print(f"Avg length: {totals['avg_word_count']} words")
    print()
    print("Recent sessions:")
    for session in recent:
        print(
            f"  #{session.id} [{session.question_id}] {session.created_at} — "
            f"{session.word_count} words, {session.filler_rate} fillers/100w, "
            f"STAR {session.star_score:.0%}"
        )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="voiceprep",
        description="Voice-first mock interview coach.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument(
        "--db",
        default=store.DEFAULT_DB_PATH,
        help="SQLite database path (default: %(default)s)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_questions = sub.add_parser("questions", help="List practice questions.")
    p_questions.add_argument("--category", default=None, help="Filter by category.")
    p_questions.set_defaults(func=cmd_questions)

    p_practice = sub.add_parser("practice", help="Practice one question.")
    p_practice.add_argument("--question", default=None, help="Question id, e.g. b1.")
    p_practice.add_argument("--category", default=None, help="Pick a random question from this category.")
    p_practice.add_argument(
        "--transcript",
        type=argparse.FileType("r", encoding="utf-8"),
        default=None,
        help="Read the transcript from a file instead of stdin.",
    )
    p_practice.add_argument(
        "--seconds",
        type=float,
        default=None,
        help="Speaking time in seconds (measured automatically otherwise).",
    )
    p_practice.set_defaults(func=cmd_practice)

    p_report = sub.add_parser("report", help="Show progress across sessions.")
    p_report.add_argument("--limit", type=int, default=10, help="Recent sessions to show.")
    p_report.set_defaults(func=cmd_report)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
