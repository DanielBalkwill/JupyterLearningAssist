# AI Notebook

A single-file, in-browser Jupyter-style notebook with an AI assistant. Real Python
(numpy / pandas / matplotlib / scikit-learn / scipy / networkx) runs **entirely in
your browser** via [Pyodide](https://pyodide.org) — no Python kernel, no server to
manage. The assistant turns plain English into cells you run and sanity-check.

Your API keys live **only in your browser** (localStorage). Nothing is uploaded.

## Run it

```bash
python serve.py
```

Then open the URL it prints (`http://127.0.0.1:8787/index.html`). It opens your
browser automatically.

> You *can* also just double-click `index.html`, but running `serve.py` is
> recommended: a stable `http://127.0.0.1` origin makes your saved keys/notebook
> persist reliably, and it gives you the CORS relay (below). `file://` is flaky for
> both.

First run downloads the Python runtime (~10 MB) once; it's cached after that.

## Add API keys (the AI panel)

Click **⚙ Keys** (top-right) and paste one or more keys. They're tried **top to
bottom**; on a rate-limit (HTTP 429) the assistant rotates to the next key and parks
the tired one on a 60-second cooldown. Mix providers freely.

Where to get free keys:

| Provider | Get a key | Notes |
|---|---|---|
| **OpenRouter** | openrouter.ai/keys | One key → many free models (slugs ending `:free`). Does its own upstream failover. Most browser-friendly. |
| **Groq** | console.groq.com/keys | Very fast free tier. May need the proxy (CORS). |
| **Cerebras** | cloud.cerebras.ai | Fast free tier, OpenAI-compatible. |
| **Google Gemini** | aistudio.google.com/apikey | Generous free tier. |
| **OpenAI-compatible** | — | Any custom endpoint: set provider = *OpenAI-compatible*, fill base URL + model. |

Model IDs are editable per row (free model slugs change often — grab the current one
from the provider's model list). Defaults are filled in as placeholders.

> **One honest note:** stacking *many keys from the same provider* to beat its
> free-tier limit usually violates that provider's ToS, and keys on one account
> often share the limit anyway. The clean pattern is **one key each across different
> providers** — that's genuine failover.

## CORS / the proxy

Some providers refuse API calls made straight from a browser page (CORS). If a key
fails with a *network* error, enable **"Route calls through local proxy"** in ⚙ Keys.
All calls then go through `serve.py`'s localhost-only `/relay`, and CORS no longer
applies. (OpenRouter and Gemini usually work direct; Groq/Cerebras often need the
proxy.)

## Using it

- **Write + run cells** — `Shift+Enter` (or the ▶ button). Variables persist across
  cells, just like a kernel. The last expression in a cell is echoed; DataFrames
  render as tables; matplotlib figures render inline automatically (no `plt.show()`).
- **Markdown cells** — hit **+ Markdown** (or import a notebook that has them).
  Double-click to edit, `Shift+Enter` to render.
- **Open data files** — drag any file onto the window, or use **📁 Files**. Data
  files (CSV/JSON/…) are written into the notebook's working directory, so
  `pd.read_csv('name.csv')` just works. In the Files panel you can rename a file's
  path (e.g. to `datasets/nb15/UNSW-NB15_4.csv`) so existing notebook code finds it,
  or click **⤵ read cell** to drop in a ready-made loader.
- **Open / Export `.ipynb`** — drag a `.ipynb` in (or **Open .ipynb**) to load it,
  **code and markdown** cells included; **Export .ipynb** writes both back out.
- **Ask the assistant** — type what you want ("load UNSW-NB15_4(1).csv with no
  header and chart missing values per column"); it knows which files you've loaded
  and drops runnable code into a cell (toggle *insert as cell* / *auto-run*).
- **Fix errors** — any errored cell gets a **🔧 Fix with AI** button.

## Limits (it's Pyodide, in a browser)

- Only packages compiled for Pyodide work. numpy, pandas, matplotlib, scikit-learn,
  scipy, networkx: yes. polars, torch, tensorflow: no.
- Files you drag in live in an **in-memory** filesystem for the session — they're
  not written to disk and are gone on reload (re-add them). Read them by the path
  shown in the Files panel.
- Big datasets are bounded by browser memory. A ~90 MB CSV will load but parsing it
  with pandas can get heavy — sample it (`nrows=` / `.sample()`) for interactive
  work; for a 20 GB log crunch, point a real kernel at the data instead.

## Files

- `index.html` — the whole app (UI, Pyodide engine, AI client, key rotation).
- `serve.py` — local static server + CORS relay (stdlib only, binds 127.0.0.1).
- `README.md` — this file.
