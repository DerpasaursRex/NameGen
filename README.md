# NameGen

Small Flask web app that generates names (plus an optional Ollama chat + name generator panel).

## Run locally

```bash
python -m pip install -r requirements.txt
python app.py
```

Then open `http://127.0.0.1:5000`.

## Deploy on Railway (same GitHub repo)

1. Go to Railway and choose **New Project** → **Deploy from GitHub repo**.
2. Select this repo.
3. Railway will detect Python and install `requirements.txt`.
4. The app starts via the included `Procfile`:
   - `web: gunicorn app:app`
5. When deploy finishes, open the Railway **Domain** URL (your “working link”).

### Ollama note

On a deployed site, `http://127.0.0.1:11434` points to the Railway server (not your PC).
To use Ollama on the live link you’d need Ollama running on that server or an Ollama base URL you can reach from Railway.

