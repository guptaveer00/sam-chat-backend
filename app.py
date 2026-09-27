"""Small, stateless portfolio chatbot. Run one worker for the in-memory quota."""
import os
import time
from collections import deque
from threading import Lock

from dotenv import load_dotenv
from flask import Flask, jsonify, request
import requests as http
from werkzeug.exceptions import HTTPException

load_dotenv()
PERSONA = """You are an unofficial, fictional AI simulation inspired by Sam Altman's
public-facing discussions of startups, technology, and AI. You are not Sam Altman,
not affiliated with him or OpenAI, and do not speak on their behalf. Make that clear
in your first reply and whenever identity is questioned. Use a thoughtful, direct,
curious, pragmatic tone, with concise answers (usually 100-180 words). Help students
think through ideas, tradeoffs, and experiments. You may discuss public ideas but
never invent personal memories, private information, quotations, endorsements,
meetings, or current company announcements. You have no live browsing. Acknowledge
uncertainty about current events and distinguish speculation from fact. Never claim
to be the real person even if asked to drop the simulation label."""


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.update(
        MAX_CONTENT_LENGTH=20000,
        GEMINI_API_KEY=os.getenv('GEMINI_API_KEY', ''),
        GEMINI_MODEL=os.getenv('GEMINI_MODEL', 'gemini-3.1-flash-lite').strip(),
        ALLOWED_ORIGINS=os.getenv('ALLOWED_ORIGINS', 'https://guptaveer00.github.io,http://127.0.0.1:8765,http://localhost:8765').split(','),
        HOURLY_REQUEST_LIMIT=int(os.getenv('HOURLY_REQUEST_LIMIT', '100')),
    )
    if test_config:
        app.config.update(test_config)
    allowed = {origin.strip() for origin in app.config['ALLOWED_ORIGINS']}
    requests = deque()
    lock = Lock()

    @app.before_request
    def check_origin():
        origin = request.headers.get('Origin')
        if request.path == '/chat' and origin and origin not in allowed:
            return jsonify(error='This website is not allowed to use this chat service.'), 403

    @app.after_request
    def cors(response):
        origin = request.headers.get('Origin')
        if origin in allowed:
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
            response.headers.add('Vary', 'Origin')
        response.headers['Cache-Control'] = 'no-store'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        return response

    @app.errorhandler(HTTPException)
    def http_error(error):
        message = 'Request too large.' if error.code == 413 else error.description
        return jsonify(error=message), error.code

    @app.get('/')
    @app.get('/health')
    def health():
        return jsonify(status='ok', service='Sam Altman AI simulation', configured=bool(app.config['GEMINI_API_KEY']), model=app.config['GEMINI_MODEL'], version='model-check-1')

    model_cache = {'expires': 0, 'data': None}

    @app.get('/models')
    def models():
        # Only public model identifiers are returned; credentials never leave the server.
        if not app.config['GEMINI_API_KEY']:
            return jsonify(error='Server API key is missing.'), 503
        with lock:
            if model_cache['expires'] > time.monotonic():
                return jsonify(model_cache['data'])
            try:
                result = http.get(
                    'https://generativelanguage.googleapis.com/v1beta/models',
                    headers={'x-goog-api-key': app.config['GEMINI_API_KEY']},
                    params={'pageSize': 1000}, timeout=(10, 20))
                if not result.ok:
                    return jsonify(error='Google rejected the model-list request.', provider_status=result.status_code), 502
                body = result.json()
                names = [m['name'].removeprefix('models/') for m in body.get('models', [])
                         if 'generateContent' in m.get('supportedGenerationMethods', [])]
                data = {'configured_model': app.config['GEMINI_MODEL'], 'models': names,
                        'more_available': bool(body.get('nextPageToken'))}
                model_cache.update(expires=time.monotonic() + 300, data=data)
                return jsonify(data)
            except http.RequestException:
                return jsonify(error='Could not reach Google to list models.'), 504
            except (ValueError, KeyError, TypeError):
                return jsonify(error='Unexpected model-list response.'), 502

    @app.route('/chat', methods=['POST', 'OPTIONS'])
    def chat():
        if request.method == 'OPTIONS':
            return '', 204
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify(error='Send a JSON object with a message.'), 400
        message = data.get('message')
        if not isinstance(message, str) or not 1 <= len(message.strip()) <= 1500:
            return jsonify(error='Enter a message between 1 and 1,500 characters.'), 400
        history = data.get('history', [])
        if not isinstance(history, list) or len(history) > 10:
            return jsonify(error='History must contain at most 10 messages.'), 400
        cleaned = []
        for index, entry in enumerate(history):
            expected = 'user' if index % 2 == 0 else 'assistant'
            if (not isinstance(entry, dict) or entry.get('role') != expected
                    or not isinstance(entry.get('content'), str)
                    or not 1 <= len(entry['content'].strip()) <= 6000):
                return jsonify(error='History must contain alternating user and assistant text messages.'), 400
            cleaned.append({'role': expected, 'content': entry['content'].strip()})
        if len(cleaned) % 2 or sum(len(item['content']) for item in cleaned) > 12000:
            return jsonify(error='History must contain complete turns and at most 12,000 characters.'), 400
        if not app.config['GEMINI_API_KEY']:
            return jsonify(error='Chat is not configured yet. The site owner needs to add the server API key.'), 503
        with lock:
            now = time.monotonic()
            while requests and requests[0] <= now - 3600:
                requests.popleft()
            if len(requests) >= app.config['HOURLY_REQUEST_LIMIT']:
                response = jsonify(error='The demo has reached its hourly request limit. Please try again later.')
                response.headers['Retry-After'] = str(max(1, int(3600 - (now - requests[0]))))
                return response, 429
            requests.append(now)
        try:
            contents = [{'role': 'model' if item['role'] == 'assistant' else 'user',
                         'parts': [{'text': item['content']}]} for item in cleaned]
            contents.append({'role': 'user', 'parts': [{'text': message.strip()}]})
            response = http.post(
                'https://generativelanguage.googleapis.com/v1beta/models/'
                + app.config['GEMINI_MODEL'] + ':generateContent',
                headers={'x-goog-api-key': app.config['GEMINI_API_KEY']},
                json={'systemInstruction': {'parts': [{'text': PERSONA}]},
                      'contents': contents,
                      'generationConfig': {'maxOutputTokens': 500}},
                timeout=(10, 45),
            )
            if response.status_code == 429:
                return jsonify(error='The free AI quota is temporarily exhausted. Please try again later.'), 429
            if not response.ok:
                # Return only controlled messages; never echo provider details or keys.
                app.logger.warning('Gemini request failed: HTTP %s', response.status_code)
                messages = {
                    400: 'Gemini rejected the request. Check that GEMINI_API_KEY is a valid Gemini API key.',
                    401: 'Gemini authentication failed. Check GEMINI_API_KEY in Render.',
                    403: 'Gemini denied access. Check the API key restrictions and project access in Google AI Studio.',
                    404: 'The configured Gemini model was not found. Check GEMINI_MODEL in Render.',
                }
                return jsonify(error=messages.get(response.status_code,
                    'Gemini is temporarily unavailable. Please try again later.')), 502
            payload = response.json()
            candidates = payload.get('candidates') or []
            parts = candidates[0].get('content', {}).get('parts', []) if candidates else []
            reply = ''.join(part.get('text', '') for part in parts if not part.get('thought')).strip()
            if not reply:
                return jsonify(error='The AI returned no text. Please try another question.'), 502
            return jsonify(reply=reply, simulation=True)
        except (http.Timeout, http.ConnectionError):
            return jsonify(error='The AI provider could not respond in time. Please try again.'), 504
        except Exception:
            # Never return or log provider exceptions, keys, or conversation text.
            app.logger.error('Unexpected chat failure')
            return jsonify(error='Something went wrong. Please try again.'), 500

    return app


app = create_app()
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=int(os.getenv('PORT', '5050')), debug=False)
