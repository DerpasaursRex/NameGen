# NameGen

Small Flask web app that generates names.

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

