# TrustEval

Sequential trust evaluation for health AI. Build patient prompt sequences, add rubrics, run the model, and see position/uncertainty/limitation scores.

**By Jiahui Jin**

---

## Run locally

1. **Clone and install**
   ```bash
   cd benchmarker
   pip install -r requirements.txt
   ```

2. **Add your API key**  
   Copy `.env.example` to `.env` and set:
   ```
   ANTHROPIC_API_KEY=your-key-here
   ```

3. **Start the server**
   ```bash
   python server.py
   ```

4. **Open in browser**  
   http://localhost:8765

---

## Deploy to production (one app = UI + API)

The repo is set up to deploy the **whole app** (frontend + API) to one host. After deploy, open the service URL — no extra config.

### Option A: Railway

1. Go to [railway.app](https://railway.app) and sign in (e.g. with GitHub).
2. **New Project** → **Deploy from GitHub repo** → choose `jjin18/trusteval` (or your fork).
3. **Variables** → **New variable** → `ANTHROPIC_API_KEY` = your Anthropic API key.
4. Railway will build and deploy. Open the **Generated URL** (e.g. `https://trusteval-production.up.railway.app`).
5. Use that URL; the app and API run on the same host.

### Option B: Render

1. Go to [render.com](https://render.com) and sign in with GitHub.
2. **New** → **Blueprint** → connect the repo and select `render.yaml` (or **New** → **Web Service** and connect the repo).
3. **Environment** → add `ANTHROPIC_API_KEY` = your Anthropic API key.
4. **Create** / **Deploy**. When it’s live, open the service URL (e.g. `https://trusteval.onrender.com`).

---

## If you host the frontend elsewhere (e.g. GitHub Pages)

Set your backend URL in `index.html` so the app can call the API:

```html
<script>window.TRUSTEVAL_API_BASE = 'https://your-backend-url.up.railway.app';</script>
```

Replace with the URL where `server.py` is deployed (Railway, Render, etc.).
