# Harness vs Loop

**Two strategies for AI agents that actually work.** The material of a meetup talk (in French):
the slides, and a live demo where we build our own AI agent.

The talk's main idea: it's not the model, it's what you want and how it's specified and built that
makes the difference.

- **Agent = model + harness.** Everything that isn't the model is the harness.
- **Harness:** everything around the model. That is its tools, the systems and data it can reach,
  the rules it must follow, and its way of working: the loop.
- **Loop:** the cycle the agent repeats until a stop condition is met. Each time round, it acts,
  checks the result, corrects itself if it's wrong, and decides whether to stop.

## What's here

```
harness-vs-loop/
├── slides/
│   ├── slides.fr.md     the slide content, one section per slide (French, used on stage)
│   ├── slides.en.md     the same content in English
│   └── slides.fr.pdf    the deck
├── demo/
│   ├── README.md        the demo: setup, run order, how to read the screen
│   ├── 00-…05-*.md      one file per step: what to type, what appears, what to say
│   ├── reset            puts the agent in a step: ./demo/reset 2 before
│   └── states/          the files each step changes
└── app/server/          Python: the quote agent, its tools, and a fake engine
```

## Try the demo

You need [uv](https://docs.astral.sh/uv/) and internet access.

```bash
cd app/server
uv sync
cp .env.example .env              # BACKEND=fake works without any key
uv run uvicorn fake_engine.main:app --port 8089     # in a second terminal
cd ../.. && ./demo/reset 0
cd app/server && uv run python -m quote_agent
```

Then follow [demo/README.md](demo/README.md), step by step.

The fake engine replays the real engine's answers, recorded during our rehearsals. To run a real
model, use a local one with Ollama (`BACKEND=ollama`), or ask lamalo.ai for an engine key
(`BACKEND=engine`).

## Tests

```bash
cd app/server && uv run pytest
```

The tests check our harness with a scripted model: each step of the demo, built by `./demo/reset`
in a temporary copy.
