"""Tests for SQLite session storage."""

from voiceprep import store


def _sample_session(**overrides):
    data = {
        "question_id": "b1",
        "category": "behavioral",
        "transcript": "When the system went down, I fixed it.",
        "seconds": 60.0,
        "word_count": 9,
        "filler_count": 0,
        "filler_rate": 0.0,
        "wpm": 9.0,
        "star_score": 0.5,
    }
    data.update(overrides)
    return data


def test_save_and_list_roundtrip(tmp_path):
    conn = store.connect(tmp_path / "sessions.db")
    session_id = store.save_session(conn, **_sample_session())
    sessions = store.list_sessions(conn)
    assert len(sessions) == 1
    assert sessions[0].id == session_id
    assert sessions[0].question_id == "b1"
    assert sessions[0].word_count == 9
    conn.close()


def test_list_returns_newest_first(tmp_path):
    conn = store.connect(tmp_path / "sessions.db")
    store.save_session(conn, **_sample_session(question_id="b1"))
    store.save_session(conn, **_sample_session(question_id="b2"))
    sessions = store.list_sessions(conn)
    assert [s.question_id for s in sessions] == ["b2", "b1"]
    conn.close()


def test_summary_empty_db(tmp_path):
    conn = store.connect(tmp_path / "sessions.db")
    totals = store.summary(conn)
    assert totals["sessions"] == 0
    assert totals["avg_filler_rate"] == 0
    conn.close()


def test_summary_averages(tmp_path):
    conn = store.connect(tmp_path / "sessions.db")
    store.save_session(conn, **_sample_session(filler_rate=4.0, wpm=120.0, star_score=0.5))
    store.save_session(conn, **_sample_session(filler_rate=2.0, wpm=140.0, star_score=1.0))
    totals = store.summary(conn)
    assert totals["sessions"] == 2
    assert totals["avg_filler_rate"] == 3.0
    assert totals["avg_wpm"] == 130.0
    assert totals["avg_star_score"] == 0.75
    conn.close()
