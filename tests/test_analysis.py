"""Tests for answer analysis (fillers, pacing, STAR, length)."""

from voiceprep import analysis


def test_clean_answer_has_no_fillers():
    result = analysis.analyze(
        "When I joined the team, my role was to fix the on-call rotation. "
        "I decided to rebuild the schedule, and the result was fewer pages.",
        seconds=60,
    )
    assert result.word_count > 0
    assert result.filler_count == 0
    assert result.filler_rate_per_100_words == 0.0


def test_filler_counting_is_case_insensitive():
    result = analysis.analyze("Um, uh, basically I like, you know, did the work.")
    assert result.filler_count >= 4
    assert result.fillers_found["um"] == 1
    assert result.fillers_found["uh"] == 1
    assert result.fillers_found["you know"] == 1


def test_filler_rate_scales_with_words():
    short = analysis.analyze("Um um um um.")
    long_text = "Um " + "word " * 96 + "um um um."
    long_result = analysis.analyze(long_text)
    assert short.filler_rate_per_100_words > long_result.filler_rate_per_100_words


def test_wpm_uses_measured_seconds():
    result = analysis.analyze("one two three four five six", seconds=3)
    assert result.wpm == 120.0
    assert result.estimated_seconds == 3


def test_wpm_is_none_without_seconds():
    result = analysis.analyze("one two three")
    assert result.wpm is None
    assert result.estimated_seconds is not None


def test_star_sections_detected():
    text = (
        "When the system went down, my role was to restore it. "
        "I decided to roll back the deploy and I wrote a runbook. "
        "The result was a faster recovery and I learned to test rollbacks."
    )
    sections = analysis.star_sections_present(text)
    assert sections == {
        "situation": True,
        "task": True,
        "action": True,
        "result": True,
    }


def test_star_score_partial():
    result = analysis.analyze("I built a dashboard.")
    assert result.star_score < 1.0
    assert result.star_sections["action"] is True
    assert result.star_sections["result"] is False


def test_short_answer_gets_length_feedback():
    result = analysis.analyze("Yes.", seconds=5)
    assert any("short" in note for note in result.feedback)


def test_fast_pace_gets_feedback():
    words = "word " * 300
    result = analysis.analyze(words, seconds=60)
    assert result.wpm == 300.0
    assert any("fast" in note for note in result.feedback)


def test_empty_transcript_is_handled():
    result = analysis.analyze("")
    assert result.word_count == 0
    assert result.star_score == 0.0
    assert result.feedback


def test_estimate_seconds():
    assert analysis.estimate_seconds(150) == 60.0
    assert analysis.estimate_seconds(75) == 30.0
