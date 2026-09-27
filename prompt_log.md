# Backend chat prompt log

Tool: OpenAI Codex desktop app. Model: GPT-6 (exact variant not exposed). Development AI is separate from the deployed chatbot model, Gemini 2.5 Flash-Lite.

## User — initial implementation request (verbatim)

i wanna add a text chatbox to y github pages website that allows people to chat with an AI versin of Sam altman, i wanna connenct to a python serice on render.com, that uses the chatGPT API. can u do this along with the hmtl file that implements the frontend. I have singed up on redner and am at the point where i have connected guptaveer00/**website**
[https://github.com/guptaveer00/website.git](https://github.com/guptaveer00/website.git)

## User — free-only constraint and provider change (verbatim)

make sure this is free can u do gemini api free then

## Development notes (assistant summary, not verbatim prompts)

Prepared a separate Flask backend to satisfy the assignment's separate-repository requirement, plus a static portfolio chat frontend. Switched the initial OpenAI draft to Gemini following the user's cost constraint. Added an explicit simulation label, server-only key configuration, bounded conversation history, validation, CORS, a basic in-memory quota, errors, and mocked tests. Deployment and actual provider replies require the user's free-tier Gemini key and Render setup; they are not claimed as verified by these notes.
