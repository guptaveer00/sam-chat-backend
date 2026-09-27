# Sam Altman AI simulation — backend

An unofficial educational chatbot inspired by public discussions of startups and AI. It is not Sam Altman, does not speak for him, and has no affiliation or endorsement. The frontend clearly labels every AI reply. The backend uses Python/Flask and the Gemini Developer API (changed from the originally requested OpenAI API to meet the user's free-only constraint).

## Architecture

GitHub Pages (`VeerWebsite/sam-chat/`) sends JSON to this separate Render service. This service validates input, supplies a fixed persona instruction, calls Gemini, and returns a text reply. The browser receives no API key. There is no database or account system.

## Endpoints

- `GET /health` (also `/`): `{ "status": "ok", "service": "Sam Altman AI simulation", "configured": true }`. Configured only indicates a key exists; it does not test key validity or model access.
- `POST /chat`: JSON `{ "message": "How do I test an idea?", "history": [] }`. Returns `{ "reply": "...", "simulation": true }`.
- Optional history contains at most 10 alternating `user`/`assistant` messages in complete pairs. A new message must be 1–1,500 characters; history is limited to 12,000 characters total, 6,000 per item; requests to 20KB. Only text and supported roles are accepted.
- Failures return `{ "error": "Helpful message" }` with 400 (input), 403 (origin), 413 (body too big), 429 (local/provider quota), 502 (provider failure/no reply), 503 (missing key), or 504 (connection/timeout).
- `OPTIONS /chat` handles browser CORS preflight. Allowed origins are exact website origins, without paths (use `https://guptaveer00.github.io`, not `/website/`).

The frontend sends the latest five complete turns when the visitor presses Send or Enter, displays replies with `textContent`, and restores the draft on failure. New chat/reload clears client history. The backend does not persist chats or log message content; Google handles requests under its terms. Free-tier content may be used to improve Google products. Do not enter sensitive information.

## Run locally

```sh
cd /Users/veergupta/Desktop/sam-chat-backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env privately to set GEMINI_API_KEY. Never commit it.
python app.py
```

Backend: `http://127.0.0.1:5050`. In another terminal run the frontend from the website root:

```sh
cd /Users/veergupta/Desktop/VeerWebsite
python3 -m http.server 8765 --bind 127.0.0.1
```

Open `http://127.0.0.1:8765/sam-chat/`. Its config selects the local backend automatically on localhost.

```sh
curl http://127.0.0.1:5050/health
curl -X POST http://127.0.0.1:5050/chat -H 'Content-Type: application/json' -d '{"message":"How can a student test a startup idea?","history":[]}'
python -m unittest -v
```

Tests mock Gemini, incur no API charges, and verify validation, CORS, history mapping, quota, missing keys, and provider failure responses. A real key and deployed URL are needed for the final live integration test.

## Keep this free

Use a Gemini API project that is on the **Free tier**, without enabling Cloud Billing, and choose Render's **Free** instance. Default model: `gemini-2.5-flash-lite`, listed with free standard text input/output when checked September 27, 2026. Availability and quotas vary; check your AI Studio project. The application cannot determine your account billing tier: a billing-enabled API key could incur charges. No paid fallback, search grounding, or extra service is used. Quota exhaustion produces an error instead of upgrading anything.

Docs: https://ai.google.dev/gemini-api/docs/pricing and https://ai.google.dev/gemini-api/docs/billing

## Render deployment (separate repository)

1. Create a public GitHub repository such as `sam-chat-backend` and upload the contents of this folder, excluding `.env` and `.venv`. Keep the frontend in `website`.
2. Create a Render Web Service connected to that **backend repository**. The previously connected `website` repo is the frontend, so it is not the correct source for this service. Do not delete or change GitHub Pages.
3. Runtime Python; branch `main`; root directory blank; **Free** instance.
4. Build command: `pip install -r requirements.txt`
5. Start command: `gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --threads 4 --timeout 90`
6. Add environment variables privately: `GEMINI_API_KEY` from Google AI Studio, `GEMINI_MODEL=gemini-2.5-flash-lite`, `ALLOWED_ORIGINS=https://guptaveer00.github.io`, `PYTHON_VERSION=3.13.7`, `HOURLY_REQUEST_LIMIT=100`.
7. Set health check `/health`. `render.yaml` also contains this configuration for Blueprint deployments.
8. Copy the actual public Render URL into the production value in `VeerWebsite/sam-chat/config.js`. Commit/push the frontend and Projects entry, then test from GitHub Pages.

Free Render services can sleep: the frontend waits up to 110 seconds and shows a wake-up message. Provider calls use a 45-second read timeout. The shared 100-request/hour in-memory limiter resets on restart and requires one worker. It is a small-demo safeguard, not durable abuse protection. CORS is a browser restriction, not authentication; non-browser clients can call this public API. Keeping Cloud Billing disabled is what prevents Gemini charges.

## Submission

Include the frontend URL/repository, backend Render URL/repository, and a brief screen recording showing a real reply and error handling. Complete the course form. This repository includes the README and verbatim prompt log; no credentials belong in either repository.
