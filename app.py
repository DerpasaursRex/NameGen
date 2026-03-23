from flask import Flask, jsonify, render_template_string
import random
from pathlib import Path

app = Flask(__name__)
NAMES_FILE = Path("random_names.txt")


def load_names():
    if not NAMES_FILE.exists():
        return None, "Error: random_names.txt not found."

    names = [
        line.strip()
        for line in NAMES_FILE.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    if not names:
        return None, "No names found in the file."
    return names, None


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
    names, err = load_names()
    if err:
        return jsonify({"error": err}), 400
    return jsonify({"name": random.choice(names)})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
