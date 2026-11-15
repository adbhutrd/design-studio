# Security Policy

## Reporting a vulnerability

Open a private security advisory on the repository (Security → Report a
vulnerability) rather than a public issue. Please include reproduction steps and
the affected version/commit. Expect an initial response within a few days.

## Secret handling

- All credentials live in `.env`, which is git-ignored. Only `.env.example`
  (empty values, annotated) is tracked.
- Generate keys with the narrowest scope available and rotate them if a machine
  is lost.
- The bundled services are meant to run on a trusted local machine or LAN. Both
  `cleanup-service` and `comfyui-gateway` accept **unauthenticated** requests
  and enable permissive CORS, because they are designed to be reached only from
  the local app. Do not expose ports 8000, 8100 or 8501 directly to the public
  internet without putting an authenticating reverse proxy in front of them.
- `POST /upscale` and `POST /remove-bg` accept uploads up to the reverse proxy
  limit; add a body-size limit at the proxy if you expose them.

## If a key is exposed

1. Revoke it at the provider dashboard (Groq / OpenRouter / Hugging Face).
2. Replace the value in `.env` and restart the stack.
3. If it ever reached a commit, rewrite history before pushing — deleting the
   file in a later commit does not remove it from the history.
