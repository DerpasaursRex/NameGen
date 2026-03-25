from flask import Flask, jsonify, render_template_string, send_from_directory, request
import random
from pathlib import Path
import json
import urllib.request
import urllib.parse
import os

app = Flask(__name__)
BASE_DIR = Path(__file__).resolve().parent
FIRST_NAMES_FILE = BASE_DIR / "random_names.txt"
LAST_NAMES_FILE = BASE_DIR / "random_surnames.txt"

DEFAULT_OLLAMA_BASE_URL = "http://127.0.0.1:11434"
DEFAULT_OLLAMA_MODEL = "llama3"

# Default safety: only allow localhost Ollama to avoid SSRF.
# Set env var `OLLAMA_ALLOW_REMOTE=1` to allow other hosts.
OLLAMA_ALLOWED_HOSTS = {"127.0.0.1", "localhost"}
OLLAMA_ALLOW_REMOTE = os.environ.get("OLLAMA_ALLOW_REMOTE") == "1"


def _validate_ollama_base_url(base_url: str):
    if not base_url:
        return None, "Ollama base URL is required."

    parsed = urllib.parse.urlparse(base_url)
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        return None, "Ollama base URL must be http(s)://<host>[:port]."

    if not OLLAMA_ALLOW_REMOTE and parsed.hostname not in OLLAMA_ALLOWED_HOSTS:
        return None, "Ollama base URL must be localhost/127.0.0.1 (safety restriction)."

    # Normalize without trailing slash.
    normalized = f"{parsed.scheme}://{parsed.hostname}"
    if parsed.port:
        normalized += f":{parsed.port}"
    return normalized, None


def _ollama_post_json(url: str, payload: dict, timeout_s: int = 60):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout_s) as resp:
        body = resp.read().decode("utf-8")
    return json.loads(body)

FANTASY_FIRST_START = [
    "ae",
    "al",
    "ar",
    "bel",
    "cae",
    "cor",
    "dae",
    "el",
    "fae",
    "gal",
    "hal",
    "is",
    "kae",
    "lae",
    "mor",
    "ny",
    "or",
    "rae",
    "syl",
    "tha",
    "vae",
    "wyn",
    "xe",
    "yor",
]
FANTASY_FIRST_MIDDLE = [
    "la",
    "ri",
    "na",
    "dor",
    "ven",
    "lin",
    "the",
    "mir",
    "dra",
    "sha",
    "nor",
    "qu",
]
FANTASY_FIRST_END = [
    "a",
    "an",
    "ar",
    "el",
    "en",
    "eth",
    "ia",
    "ion",
    "is",
    "or",
    "ra",
    "yn",
]
FANTASY_LAST_START = [
    "ash",
    "black",
    "bright",
    "cinder",
    "dawn",
    "dusk",
    "ember",
    "frost",
    "gold",
    "gray",
    "iron",
    "moon",
    "night",
    "oak",
    "raven",
    "river",
    "silver",
    "star",
    "storm",
    "sun",
    "thorn",
    "vale",
    "whisper",
    "wind",
]
FANTASY_LAST_END = [
    "bane",
    "bloom",
    "brook",
    "crest",
    "fall",
    "field",
    "flame",
    "forge",
    "glen",
    "guard",
    "haven",
    "heart",
    "keep",
    "leaf",
    "rider",
    "shade",
    "song",
    "spire",
    "stone",
    "vale",
    "walker",
    "ward",
    "weaver",
    "wind",
    "wood",
]


def load_name_list(path: Path, missing_message: str, empty_message: str):
    if not path.exists():
        return None, missing_message

    names = [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    if not names:
        return None, empty_message
    return names, None


def build_fantasy_name_pool():
    first_pool = [
        f"{start}{middle}{end}".title()
        for start in FANTASY_FIRST_START
        for middle in FANTASY_FIRST_MIDDLE
        for end in FANTASY_FIRST_END
    ]
    last_pool = [
        f"{start}{end}".title()
        for start in FANTASY_LAST_START
        for end in FANTASY_LAST_END
    ]
    return first_pool, last_pool


def generate_full_name():
    first_names, first_err = load_name_list(
        FIRST_NAMES_FILE,
        "Error: random_names.txt not found.",
        "No first names found in random_names.txt.",
    )
    if first_err:
        return None, first_err

    last_names, last_err = load_name_list(
        LAST_NAMES_FILE,
        "Error: random_surnames.txt not found.",
        "No last names found in random_surnames.txt.",
    )
    if last_err:
        return None, last_err

    fantasy_first, fantasy_last = build_fantasy_name_pool()

    # Keep real-world and themed file-based names prominent.
    use_file_first = random.random() < 0.75
    use_file_last = random.random() < 0.75
    selected_first = random.choice(first_names if use_file_first else fantasy_first)
    selected_last = random.choice(last_names if use_file_last else fantasy_last)
    return f"{selected_first} {selected_last}", None


def ollama_chat(base_url: str, model: str, messages: list):
    url = base_url.rstrip("/") + "/api/chat"
    payload = {"model": model, "messages": messages, "stream": False}
    resp = _ollama_post_json(url, payload)
    content = resp.get("message", {}).get("content", "")
    return content.strip()


def ollama_generate(base_url: str, model: str, prompt: str):
    url = base_url.rstrip("/") + "/api/generate"
    payload = {"model": model, "prompt": prompt, "stream": False}
    resp = _ollama_post_json(url, payload)
    return str(resp.get("response", "")).strip()


@app.route("/api/ollama/chat", methods=["POST"])
def api_ollama_chat():
    data = request.get_json(silent=True) or {}

    base_url = data.get("base_url", DEFAULT_OLLAMA_BASE_URL)
    model = data.get("model", DEFAULT_OLLAMA_MODEL)
    messages = data.get("messages", [])

    valid_base_url, err = _validate_ollama_base_url(str(base_url))
    if err:
        return jsonify({"error": err}), 400
    if not isinstance(messages, list) or not messages:
        return jsonify({"error": "messages must be a non-empty array."}), 400

    try:
        reply = ollama_chat(valid_base_url, str(model), messages)
        if not reply:
            return jsonify({"error": "Ollama returned an empty reply."}), 502
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"error": f"Ollama chat failed: {e}"}), 502


@app.route("/api/ollama/name", methods=["POST"])
def api_ollama_name():
    data = request.get_json(silent=True) or {}

    base_url = data.get("base_url", DEFAULT_OLLAMA_BASE_URL)
    model = data.get("model", DEFAULT_OLLAMA_MODEL)
    prompt = data.get(
        "prompt",
        "Generate a fantasy character full name (first and last), separated by a single space. "
        "Output only the name. No quotes. No extra text.",
    )

    valid_base_url, err = _validate_ollama_base_url(str(base_url))
    if err:
        return jsonify({"error": err}), 400

    prompt = str(prompt).strip()
    if not prompt:
        return jsonify({"error": "prompt is required."}), 400

    try:
        raw = ollama_generate(valid_base_url, str(model), prompt)
        cleaned = raw.strip()
        cleaned = cleaned.splitlines()[0].strip() if cleaned else cleaned
        cleaned = cleaned.strip('"').strip("'").strip()
        if not cleaned:
            return jsonify({"error": "Ollama returned an empty name."}), 502
        return jsonify({"name": cleaned})
    except Exception as e:
        return jsonify({"error": f"Ollama generate failed: {e}"}), 502


@app.route("/")
def index():
    return render_template_string(
        """
        <!doctype html>
        <html>
        <head>
            <meta charset="utf-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1" />
            <title>Name Chatbot</title>
            <link rel="icon" href="data:,">
            <style>
                :root {
                    --bg1: #ff4d6d;
                    --bg2: #ff9e00;
                    --bg3: #ffd60a;
                    --bg4: #2dc653;
                    --bg5: #2ec4ff;
                    --bg6: #5a4cff;
                    --bg7: #c77dff;
                    --surface: rgba(255, 255, 255, 0.2);
                    --surface-strong: rgba(255, 255, 255, 0.28);
                    --text: #111111;
                    --shadow: rgba(0, 0, 0, 0.22);
                }

                * { box-sizing: border-box; }

                body {
                    font-family: "Segoe UI", Tahoma, sans-serif;
                    min-height: 100vh;
                    margin: 0;
                    padding: 1.25rem;
                    color: var(--text);
                    background: linear-gradient(
                        120deg,
                        var(--bg1),
                        var(--bg2),
                        var(--bg3),
                        var(--bg4),
                        var(--bg5),
                        var(--bg6),
                        var(--bg7)
                    );
                    background-size: 350% 350%;
                    animation: rainbowShift 16s ease infinite;
                }

                .card {
                    width: min(1100px, 100%);
                    margin: 0 auto;
                    border-radius: 22px;
                    padding: 1.25rem;
                    background: var(--surface);
                    backdrop-filter: blur(10px);
                    box-shadow: 0 16px 45px var(--shadow);
                }

                h1 {
                    margin: 0;
                    font-size: 2.1rem;
                    text-shadow: none;
                    text-align: center;
                }

                .layout {
                    margin-top: 1rem;
                    display: grid;
                    grid-template-columns: 1.25fr 0.75fr;
                    gap: 1rem;
                }

                .panel {
                    border-radius: 16px;
                    background: var(--surface-strong);
                    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
                    padding: 1rem;
                }

                .panel-title {
                    margin: 0 0 0.75rem 0;
                    font-size: 1.05rem;
                    font-weight: 700;
                }

                button {
                    padding: 0.75rem 1.25rem;
                    font-size: 1rem;
                    border: 0;
                    border-radius: 12px;
                    cursor: pointer;
                    font-weight: 700;
                    color: #111111;
                    background: linear-gradient(90deg, #ffffff, #fff3bf);
                    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
                    transition: transform 0.18s ease, box-shadow 0.18s ease;
                }

                button:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 12px 24px rgba(0, 0, 0, 0.28);
                }

                .actions {
                    display: flex;
                    gap: 0.6rem;
                    justify-content: center;
                    flex-wrap: wrap;
                }

                .secondary-btn {
                    padding: 0.75rem 1rem;
                    font-size: 0.95rem;
                    border: 0;
                    border-radius: 12px;
                    cursor: pointer;
                    font-weight: 700;
                    color: #111111;
                    background: linear-gradient(90deg, #ffe1e8, #ffffff);
                    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
                    transition: transform 0.18s ease, box-shadow 0.18s ease;
                }

                .secondary-btn:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 12px 24px rgba(0, 0, 0, 0.22);
                }

                .name-box {
                    margin-top: 0.85rem;
                    min-height: 82px;
                    border-radius: 14px;
                    display: grid;
                    place-items: center;
                    padding: 0.75rem;
                    text-align: center;
                    background: rgba(255, 255, 255, 0.2);
                }

                #result {
                    font-size: 1.35rem;
                    font-weight: 700;
                    letter-spacing: 0.3px;
                    text-shadow: none;
                }

                .history-wrap {
                    margin-top: 0.85rem;
                    border-radius: 14px;
                    padding: 0.6rem;
                    background: rgba(255, 255, 255, 0.17);
                }

                #history {
                    margin: 0;
                    padding-left: 1.25rem;
                    max-height: 260px;
                    overflow: auto;
                    line-height: 1.5;
                }

                #history li {
                    margin-bottom: 0.2rem;
                    word-break: break-word;
                }

                .inspired {
                    margin-top: 0.8rem;
                    text-align: center;
                    font-size: 0.95rem;
                }

                .inspired a {
                    color: #111111;
                    font-weight: 700;
                }

                .picrew-logo {
                    width: 100%;
                    margin-top: 0.75rem;
                    border-radius: 12px;
                    object-fit: cover;
                    max-height: 240px;
                    background: rgba(255, 255, 255, 0.2);
                }

                .field-row {
                    display: flex;
                    flex-direction: column;
                    gap: 0.35rem;
                    margin-bottom: 0.6rem;
                }

                .field-row label {
                    font-size: 0.92rem;
                    font-weight: 800;
                }

                .input {
                    width: 100%;
                    padding: 0.6rem 0.7rem;
                    border-radius: 12px;
                    border: 0;
                    outline: none;
                    background: rgba(255, 255, 255, 0.65);
                    color: #111111;
                    font-size: 0.98rem;
                }

                .input::placeholder {
                    color: rgba(17, 17, 17, 0.55);
                }

                .chat-box {
                    border-radius: 14px;
                    padding: 0.6rem;
                    background: rgba(255, 255, 255, 0.17);
                    max-height: 240px;
                    overflow: auto;
                    line-height: 1.35;
                }

                .chat-message {
                    margin: 0.55rem 0;
                }

                .chat-message .bubble {
                    display: inline-block;
                    padding: 0.55rem 0.7rem;
                    border-radius: 12px;
                    max-width: 100%;
                    word-break: break-word;
                }

                .chat-message.user {
                    text-align: right;
                }

                .chat-message.user .bubble {
                    background: rgba(255, 255, 255, 0.72);
                }

                .chat-message.assistant {
                    text-align: left;
                }

                .chat-message.assistant .bubble {
                    background: rgba(255, 255, 255, 0.36);
                }

                .chat-message .role {
                    display: block;
                    font-size: 0.9rem;
                    font-weight: 900;
                    margin-bottom: 0.25rem;
                    opacity: 0.9;
                }

                .input-row {
                    display: flex;
                    gap: 0.6rem;
                    align-items: center;
                    margin-top: 0.6rem;
                }

                .input-row .input {
                    flex: 1;
                }

                @media (max-width: 900px) {
                    .layout {
                        grid-template-columns: 1fr;
                    }
                }

                @keyframes rainbowShift {
                    0% { background-position: 0% 50%; }
                    50% { background-position: 100% 50%; }
                    100% { background-position: 0% 50%; }
                }
            </style>
        </head>
        <body>
            <main class="card">
                <h1>Let's Party!</h1>
                <section class="layout">
                    <section class="panel">
                        <h2 class="panel-title">Name Generator</h2>
                        <div class="actions">
                            <button onclick="generateName()">Generate Name</button>
                                <button onclick="generateOllamaName()">Generate with Ollama</button>
                            <button class="secondary-btn" onclick="clearHistory()">Clear History</button>
                        </div>
                        <div class="name-box">
                            <div id="result">Click "Generate Name" to start.</div>
                        </div>
                        <div class="history-wrap">
                            <h2 class="panel-title">Name History</h2>
                            <ol id="history"></ol>
                        </div>
                    </section>

                    <section class="panel">
                        <h2 class="panel-title">Picrew Character Creator</h2>
                        <p>
                            Open Picrew in a new tab:
                            <a href="https://picrew.me/en" target="_blank" rel="noopener noreferrer">picrew.me/en</a>
                        </p>
                        <img
                            class="picrew-logo"
                            src="/picrewlogo.png"
                            alt="Picrew logo"
                            onerror="this.style.display='none';"
                        />
                        <hr style="border: 0; border-top: 1px solid rgba(0, 0, 0, 0.15); margin: 1rem 0;" />

                        <h2 class="panel-title">Ollama Chat</h2>

                        <div class="field-row">
                            <label for="ollamaBaseUrl">Ollama Base URL</label>
                            <input
                                id="ollamaBaseUrl"
                                class="input"
                                value="http://127.0.0.1:11434"
                                placeholder="http://127.0.0.1:11434"
                            />
                        </div>

                        <div class="field-row">
                            <label for="ollamaModel">Model</label>
                            <input
                                id="ollamaModel"
                                class="input"
                                value="llama3"
                                placeholder="llama3"
                            />
                        </div>

                        <div id="ollamaChatMessages" class="chat-box"></div>

                        <div class="input-row">
                            <input
                                id="ollamaChatInput"
                                class="input"
                                placeholder="Ask for names, backstory ideas, etc."
                                onkeydown="if (event.key === 'Enter') sendOllamaChat();"
                            />
                            <button onclick="sendOllamaChat()">Send</button>
                        </div>
                    </section>
                </section>
                <div class="inspired">
                    Inspired by
                    <a href="https://www.fantasynamegenerators.com/" target="_blank" rel="noopener noreferrer">
                        Fantasy Name Generators
                    </a>
                </div>
            </main>

            <script>
                const historyLimit = 15;
                const historyEl = document.getElementById('history');

                function addToHistory(name) {
                    const li = document.createElement('li');
                    li.textContent = name;
                    historyEl.prepend(li);

                    while (historyEl.children.length > historyLimit) {
                        historyEl.removeChild(historyEl.lastElementChild);
                    }
                }

                function clearHistory() {
                    historyEl.innerHTML = '';
                }

                async function generateName() {
                    const res = await fetch('/api/name');
                    const data = await res.json();
                    const value = data.name || data.error;
                    document.getElementById('result').textContent = value;
                    if (data.name) {
                        addToHistory(data.name);
                    }
                }

                function getOllamaConfig() {
                    return {
                        base_url: document.getElementById('ollamaBaseUrl').value,
                        model: document.getElementById('ollamaModel').value
                    };
                }

                async function generateOllamaName() {
                    const { base_url, model } = getOllamaConfig();
                    const res = await fetch('/api/ollama/name', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ base_url, model })
                    });
                    const data = await res.json();
                    const value = data.name || data.error;
                    document.getElementById('result').textContent = value;
                    if (data.name) {
                        addToHistory(data.name);
                    }
                }

                const ollamaSystemPrompt = 'You are a helpful creative assistant for fantasy roleplaying character creation. Keep responses concise and directly useful.';
                let ollamaChatLog = [];

                function addOllamaChatMessage(role, text) {
                    const container = document.getElementById('ollamaChatMessages');
                    const msg = document.createElement('div');
                    msg.className = `chat-message ${role}`;

                    const roleEl = document.createElement('span');
                    roleEl.className = 'role';
                    roleEl.textContent = role === 'user' ? 'You' : 'Ollama';

                    const bubble = document.createElement('div');
                    bubble.className = 'bubble';
                    bubble.textContent = text;

                    msg.appendChild(roleEl);
                    msg.appendChild(bubble);
                    container.appendChild(msg);
                    container.scrollTop = container.scrollHeight;
                }

                async function sendOllamaChat() {
                    const inputEl = document.getElementById('ollamaChatInput');
                    const message = inputEl.value.trim();
                    if (!message) return;

                    addOllamaChatMessage('user', message);
                    ollamaChatLog.push({ role: 'user', content: message });
                    inputEl.value = '';

                    const { base_url, model } = getOllamaConfig();
                    const messages = [{ role: 'system', content: ollamaSystemPrompt }, ...ollamaChatLog];

                    const res = await fetch('/api/ollama/chat', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ base_url, model, messages })
                    });

                    const data = await res.json();
                    if (!res.ok) {
                        const errText = data.error || 'Ollama error.';
                        addOllamaChatMessage('assistant', errText);
                        return;
                    }

                    const reply = data.reply || '';
                    addOllamaChatMessage('assistant', reply);
                    ollamaChatLog.push({ role: 'assistant', content: reply });

                    // Keep the last few turns to limit token usage.
                    if (ollamaChatLog.length > 10) {
                        ollamaChatLog = ollamaChatLog.slice(-10);
                    }
                }
            </script>
        </body>
        </html>
        """
    )


@app.route("/api/name")
def api_name():
    full_name, err = generate_full_name()
    if err:
        return jsonify({"error": err}), 400
    return jsonify({"name": full_name})


@app.route("/favicon.ico")
def favicon():
    # Return an empty success response to avoid noisy 404s in browser devtools.
    return ("", 204)


@app.route("/picrewlogo.png")
def picrew_logo():
    return send_from_directory(BASE_DIR, "picrewlogo.png")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
