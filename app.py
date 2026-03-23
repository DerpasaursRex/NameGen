from flask import Flask, jsonify, render_template_string
import random
from pathlib import Path

app = Flask(__name__)
FIRST_NAMES_FILE = Path("random_names.txt")
LAST_NAMES_FILE = Path("random_surnames.txt")


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

    return f"{random.choice(first_names)} {random.choice(last_names)}", None


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
                body {
                    font-family: Arial, sans-serif;
                    max-width: 700px;
                    margin: 3rem auto;
                    padding: 0 1rem;
                }
                button {
                    padding: 0.6rem 1rem;
                    font-size: 1rem;
                    cursor: pointer;
                }
                #result {
                    margin-top: 1rem;
                    font-size: 1.2rem;
                    font-weight: 600;
                }
            </style>
        </head>
        <body>
            <h1>Random Name Chatbot</h1>
            <p>Click to generate a random name.</p>
            <button onclick="generateName()">Generate Name</button>
            <div id="result"></div>

            <script>
                async function generateName() {
                    const res = await fetch('/api/name');
                    const data = await res.json();
                    document.getElementById('result').textContent = data.name || data.error;
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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
