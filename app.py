from flask import Flask, jsonify, render_template_string, send_from_directory
import random
from pathlib import Path

app = Flask(__name__)
FIRST_NAMES_FILE = Path("random_names.txt")
LAST_NAMES_FILE = Path("random_surnames.txt")

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
    return send_from_directory(".", "picrewlogo.png")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
