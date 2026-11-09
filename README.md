# VoicePrep

A voice-first mock interview coach. Practice behavioral and technical
interview answers out loud, then get structured feedback on filler words,
pacing, answer length, and STAR structure — all locally, with no account
and no network calls.

## Why

Talking through an answer is different from writing one. Fillers creep
in, pacing drifts, and a good story can lose its structure halfway
through. VoicePrep gives you a question, records your spoken answer as a
transcript, and shows you the patterns to work on. Sessions are stored in
a local SQLite database so you can see progress over time.

## Install

Requires Python 3.11+.

```bash
git clone https://github.com/GuillermoBarreto/voiceprep.git
cd voiceprep
pip install -e .
```

No third-party dependencies. Tests use pytest:

```bash
pip install pytest
pytest
```

## Usage

List the question bank:

```bash
voiceprep questions
voiceprep questions --category behavioral
```

Practice one question. Speak your answer, then type or paste the
transcript and finish with an empty line:

```bash
voiceprep practice
voiceprep practice --question b1
voiceprep practice --category technical
```

If you use a speech-to-text tool, pass its transcript file instead:

```bash
voiceprep practice --question b1 --transcript answer.txt --seconds 75
```

After each session you get a breakdown: word count, filler count and
rate, speaking pace, estimated length, and which STAR sections were
present, plus concrete feedback. Sessions are saved to
`~/.voiceprep/sessions.db` (override with `--db`).

Track progress across sessions:

```bash
voiceprep report
```

## How the feedback works

- **Fillers** — counts words and phrases like "um", "uh", "like",
  "you know", "basically". More than 5 per 100 words is flagged.
- **Pacing** — words per minute from the measured speaking time.
  Conversational pace is roughly 110–180 wpm.
- **Length** — spoken answers land best around 45–150 seconds.
- **STAR structure** — checks for keyword cues in each section
  (Situation, Task, Action, Result).

These are heuristics to surface patterns, not a grade. A short answer
with a clear story beats a long one that ticks every box.

## Roadmap

- Record audio directly and transcribe on-device (Whisper) instead of
  pasting transcripts.
- Per-question follow-ups: ask a clarifying question based on the answer.
- Spaced repetition: resurface questions you scored lowest on.
- Export a session summary as Markdown for review before an interview.
- Web UI for practicing from a phone.

## License

MIT — see [LICENSE](LICENSE).
