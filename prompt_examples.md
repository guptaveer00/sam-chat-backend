# Prompt Log

These retrospective examples were written after development with AI assistance. They are not the actual prompts used during development. See [the original development log](prompt_log.md) for recorded user prompts.

**Development tool:** OpenAI Codex desktop app
**Chatbot API:** Google Gemini API
**Frontend:** HTML, CSS, and JavaScript on GitHub Pages
**Backend:** Python with Flask on Render

## 1. Define the project and architecture

> I want to add a text chatbot to my portfolio that lets visitors talk with an unofficial AI simulation inspired by Sam Altman’s public discussions of startups and technology. Clearly identify it as an AI simulation, not the real person or an endorsed product.
>
> Keep the frontend in my existing `guptaveer00/website` repository, inside a new `sam-chat/` folder. Create a separate public repository for the Python backend, as required by my assignment. Host the frontend on GitHub Pages and the backend on Render. Before coding, explain how a message will travel from the browser to the backend, then to the AI provider and back.

## 2. Choose an API within the free-only constraint

> This project must run without paid services. Investigate the Gemini Developer API’s current free-tier options using Google’s official documentation. Check both pricing and model availability for new projects; don’t assume that a model listed in documentation is available to my API key.
>
> Use a free-tier text model and Render’s Free instance. Do not enable billing, add paid services, or implement an automatic paid fallback. Explain what happens when the free quota is exhausted and any relevant free-tier data-use policies.

## 3. Implement the Python backend

> Build a small Flask service with two main endpoints:
>
> - `GET /health` should return JSON indicating whether the server is running and whether an API key is configured. It must not expose the key or claim the key works merely because it exists.
> - `POST /chat` should accept a JSON object containing `message` and optional `history`, call Gemini, and return a JSON object containing `reply`.
>
> Read `GEMINI_API_KEY` and `GEMINI_MODEL` from environment variables. Include a requirements file, `.gitignore`, and `.env.example` containing placeholders only. Keep real credentials out of the frontend, repository, logs, and error responses.

## 4. Define the simulation’s behavior

> Write a server-side instruction for an unofficial Sam Altman-inspired AI simulation. Its tone should be direct, thoughtful, and useful for a student asking about startups, AI, and building products.
>
> It should clarify its fictional identity in its first response and whenever asked. It must not invent personal experiences, private information, endorsements, or quotations from Sam Altman. It should acknowledge uncertainty about current events and avoid claiming access to live information. Keep responses concise enough for a chat interface.

## 5. Validate input and manage conversation context

> Validate requests before contacting Gemini. Reject empty messages, malformed JSON, unsupported message roles, oversized inputs, and invalid conversation history with useful JSON errors.
>
> Limit new messages to 1,500 characters. Accept at most five complete previous conversation turns, with alternating user and assistant messages and a total history limit of 12,000 characters. Keep the persona instruction controlled by the server rather than allowing the browser to supply it.
>
> Do not add a database. Keep conversation history in browser memory and clear it when the visitor starts a new chat or reloads the page.

## 6. Build the portfolio chat page

> Create an HTML/CSS/JavaScript chat interface that matches my portfolio’s existing theme. Include a visible simulation disclosure, labeled message input, Send button, conversation area, suggested questions, and New Chat button.
>
> Support Enter to send and Shift+Enter for a new line. Disable duplicate submissions while a request is pending. Display messages as text rather than inserting model-generated HTML. If a request fails, preserve the visitor’s draft so they can retry.
>
> Make the layout usable on mobile and with a keyboard. Add a project entry linking to the chat without changing unrelated portfolio content.

## 7. Connect the frontend and backend

> Use `fetch()` to send messages to the backend’s `/chat` endpoint. Put the public backend URL in a separate frontend configuration file; this file must never contain the Gemini API key.
>
> For local development, connect the frontend on port 8765 to Flask on port 5050. For production, connect GitHub Pages to the actual Render URL.
>
> Configure CORS for `https://guptaveer00.github.io` and the local development origins. Explain that the origin excludes `/website/`, and that CORS does not authenticate users or prevent non-browser clients from calling a public endpoint.

## 8. Handle failures and free-service limitations

> Add timeouts and clear messages for connection failures, missing configuration, unavailable models, provider errors, and exhausted quotas. Account for Render’s free service taking time to wake up by displaying a loading message rather than appearing frozen.
>
> Add a basic shared request limit to reduce accidental overuse. Document that an in-memory limit resets when the server restarts and is not a permanent spending guarantee. Never return raw provider errors containing sensitive information or silently substitute a fabricated AI response.

## 9. Test locally before deployment

> Write focused backend tests that mock the Gemini API so testing does not consume the free quota. Cover valid requests, invalid inputs, conversation-role mapping, missing keys, CORS, oversized bodies, provider failures, empty replies, and request limits.
>
> Test the frontend in a browser: suggested questions, submitting a message, loading state, draft restoration after failure, New Chat, keyboard controls, and mobile overflow.
>
> Report mocked tests separately from real API tests. Passing mocked tests must not be described as proof that the deployed API connection works.

## 10. Deploy the correct repository to Render

> Upload the backend to its separate public GitHub repository. Render is currently connected to my frontend repository, so help me change its source to the backend repository.
>
> Use `pip install -r requirements.txt` as the build command and:
>
> ```sh
> gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --threads 4 --timeout 90
> ```
>
> as the start command. Leave the root directory blank and use `/health` for the health check. Keep the service on the Free plan. Guide me to enter the Gemini key privately in Render’s environment settings.

## 11. Diagnose model errors using evidence

> The server’s health check succeeds, but chat requests return “model not found.” Don’t assume this is a typo or repeatedly recommend the same configuration.
>
> Check which deployment is running, the exact configured model, and the models available to the project. Distinguish server health from a successful provider request. Use safe diagnostics that reveal model identifiers or status codes without exposing credentials.
>
> If a replacement is necessary, verify its current free-tier eligibility and test an actual generated reply after redeployment.

## 12. Verify the published integration and document it

> After deployment, open the chat through my portfolio’s Projects section and send a real message from GitHub Pages. Confirm that the browser receives a generated response from Render, that follow-up context works, and that errors are displayed clearly.
>
> Write a backend README describing the endpoints, request and response formats, local setup, environment variables, frontend communication, deployment steps, and known limitations. Keep the actual prompt log verbatim and label summaries separately.
>
> Give me the frontend URL, backend URL, and both repository links for submission. Identify anything still unverified, and remind me to record the short demonstration video required by the assignment.
