# Contributing

Thanks for taking the time to contribute.

## Ground rules

1. **No new paid dependency.** The project's premise is a zero-budget stack; a
   proposal that requires a credit card fails review regardless of quality.
2. **Every integration must degrade gracefully.** If a provider is unreachable,
   the pipeline records a note and continues. Never raise out of a service
   client on a network error — return the input bytes and explain what happened.
3. **Secrets stay out of git.** API keys belong in `.env` (git-ignored). Tests
   must never need a real key.

## Workflow

```bash
git switch -c feat/short-description
make setup
make test          # must pass
make lint          # must be clean
```

Commit messages follow the imperative mood with a short subject line:

```
add Stable Horde image provider

Falls back after Pollinations when both free tiers are rate-limited.
```

## Adding a provider

- **LLM**: add a function in `app/services/llm.py` and return
  `{"headline", "image_prompt", "provider", "notes"}`. Insert it into the
  provider chain in `generate_copy()`.
- **Image generation**: add a `_via_*` function in `app/services/imagegen.py`
  returning `bytes | None`, and call it from `generate_image()`.
- **Cleanup / upscale**: add an engine function in `cleanup-service/main.py` and
  include it in the engine tuple. The Pillow fallback must remain last.
- Document any new environment variable in both `README.md` and
  `.env.example`, and add it to `app/config.py`.

## Tests

Tests live in `tests/` and must stay offline and deterministic — no network, no
GPU, no API keys. Use `monkeypatch` for provider calls. New behaviour needs a
test; a pure refactor does not.
