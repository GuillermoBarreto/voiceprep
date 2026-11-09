"""Tests for the question bank."""

import pytest

from voiceprep import questions


def test_bank_is_not_empty():
    assert len(questions.list_questions()) >= 10


def test_every_question_has_text_and_category():
    for question in questions.list_questions():
        assert question.id
        assert question.category
        assert question.text.endswith((".", "?"))


def test_ids_are_unique():
    ids = [q.id for q in questions.list_questions()]
    assert len(ids) == len(set(ids))


def test_category_filter():
    behavioral = questions.list_questions("behavioral")
    assert behavioral
    assert all(q.category == "behavioral" for q in behavioral)
    assert questions.list_questions("no-such-category") == []


def test_categories_listed():
    cats = questions.categories()
    assert "behavioral" in cats
    assert "technical" in cats


def test_get_question_by_id():
    question = questions.get_question("b1")
    assert question.category == "behavioral"
    with pytest.raises(KeyError):
        questions.get_question("zzz")
