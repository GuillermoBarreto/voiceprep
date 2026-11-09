"""Tests for the CLI commands (questions, practice, report)."""

from voiceprep.cli import main


def test_questions_command(capsys):
    assert main(["questions"]) == 0
    out = capsys.readouterr().out
    assert "[b1]" in out
    assert "behavioral" in out


def test_questions_unknown_category(capsys):
    assert main(["questions", "--category", "nope"]) == 1
    assert "No questions" in capsys.readouterr().out


def test_practice_with_transcript_file(tmp_path, capsys):
    db = tmp_path / "sessions.db"
    transcript = tmp_path / "answer.txt"
    transcript.write_text(
        "When the deploy broke, my role was to fix it. "
        "I decided to roll back and I wrote a runbook. "
        "The result was a faster recovery.",
        encoding="utf-8",
    )
    assert (
        main(
            [
                "--db",
                str(db),
                "practice",
                "--question",
                "b1",
                "--transcript",
                str(transcript),
                "--seconds",
                "60",
            ]
        )
        == 0
    )
    out = capsys.readouterr().out
    assert "Words:" in out
    assert "STAR" in out
    assert "Saved as session #1" in out


def test_practice_unknown_question():
    assert main(["practice", "--question", "zzz"]) == 1


def test_report_empty_db(tmp_path, capsys):
    assert main(["--db", str(tmp_path / "sessions.db"), "report"]) == 0
    assert "No practice sessions yet" in capsys.readouterr().out


def test_report_after_practice(tmp_path, capsys):
    db = tmp_path / "sessions.db"
    transcript = tmp_path / "answer.txt"
    transcript.write_text("I built a dashboard and shipped it.", encoding="utf-8")
    main(
        [
            "--db",
            str(db),
            "practice",
            "--question",
            "b4",
            "--transcript",
            str(transcript),
            "--seconds",
            "30",
        ]
    )
    capsys.readouterr()
    assert main(["--db", str(db), "report"]) == 0
    out = capsys.readouterr().out
    assert "Sessions: 1" in out
    assert "#1 [b4]" in out
