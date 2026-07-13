# 🚀 DocAi — Manual Run Guide (PowerShell)

> All commands below work directly in **PowerShell** — no `activate.bat`, no `&&`, no admin rights needed.

---

## ✅ Quick Start (App Already Set Up)

**Just paste this one line in PowerShell:**

```powershell
C:\Users\RuchaParmar\Downloads\DocAi\.venv\Scripts\python.exe -m streamlit run C:\Users\RuchaParmar\Downloads\DocAi\DocAi\ui\app.py
```

Then open **http://localhost:8501** in your browser.

---

## 📋 Full Setup (First Time Only)

### Step 1 — Install dependencies

```powershell
C:\Users\RuchaParmar\Downloads\DocAi\.venv\Scripts\pip.exe install -r C:\Users\RuchaParmar\Downloads\DocAi\DocAi\requirements.txt
```

> ⏳ Takes 3–5 minutes. Only needed once (or after deleting `.venv`).

---

### Step 2 — (Optional) Install Playwright browser for Crawl4AI

> Skip this if you use the default `trafilatura` crawler (already configured).

```powershell
C:\Users\RuchaParmar\Downloads\DocAi\.venv\Scripts\python.exe -m playwright install chromium
```

---

### Step 3 — Check your `.env` config

File: `C:\Users\RuchaParmar\Downloads\DocAi\DocAi\.env`

Key settings already configured:
```env
LLM_PROVIDER=groq
LLM_MODEL=llama-3.1-8b-instant
GROQ_API_KEY=<set>          ✅
FIRECRAWL_API_KEY=<set>     ✅
CRAWLER_TYPE=trafilatura     ✅  (fast, no browser needed)
EMBEDDING_MODEL=BAAI/bge-small-en-v1.5
VECTOR_DB_TYPE=chroma
```

---

## ▶️ Run the App

```powershell
C:\Users\RuchaParmar\Downloads\DocAi\.venv\Scripts\python.exe -m streamlit run C:\Users\RuchaParmar\Downloads\DocAi\DocAi\ui\app.py
```

Open browser at: **http://localhost:8501**

To stop: press `Ctrl + C` in PowerShell.

---

## 📚 Ingesting Documentation

1. Open the app at **http://localhost:8501**
2. In the left sidebar, click **"Crawl & Index New Documentation"**
3. Paste a documentation URL (e.g. `https://python.langchain.com/docs/`)
4. Set Depth (2–3 recommended) and Max Pages (20–50)
5. Click **🚀 Start Ingestion**
6. Wait for the status messages:
   - 🕷️ Crawling… → ✅ Crawled N pages
   - 🔢 Embedding… → 🎉 Ingestion complete!

---

## 🛠️ Troubleshooting

| Problem | Fix |
|---------|-----|
| `ModuleNotFoundError` on startup | Run Step 1 (install deps) |
| `&&` not recognized | You're in PowerShell — use the one-liner above, not `&&` |
| `activate.bat` fails | Don't use `activate.bat` in PowerShell — use full path to `python.exe` instead |
| Python 3.14 venv creation fails | Use `python -m venv .venv --copies` or install Python 3.12 from python.org |
| Ingestion hangs forever | Make sure `CRAWLER_TYPE=trafilatura` in `.env` (not `crawl4ai`) |
| Ingestion shows 0 pages | Try a simpler URL (e.g. the root docs page, not a deep sub-page) |
| No response to questions | You need to ingest docs first via the sidebar |
| ChromaDB migration error | Delete `vectordb_storage\` folder and re-ingest |
| App crashes on query | Check `DocAi\logs\app.log` for error details |

---

## 📝 Logs

```
C:\Users\RuchaParmar\Downloads\DocAi\DocAi\logs\app.log
```

---

## 🗂️ Project Layout

```
C:\Users\RuchaParmar\Downloads\DocAi\
├── .venv\                   ← Virtual environment (always use this Python)
│   └── Scripts\
│       ├── python.exe       ← Use this for all commands
│       └── pip.exe          ← Use this for installs
└── DocAi\                   ← Source code
    ├── ui\app.py            ← Streamlit app entry point
    ├── .env                 ← API keys & config
    ├── requirements.txt     ← Python dependencies
    ├── knowledge_base\      ← Crawled docs (auto-created)
    └── vectordb_storage\    ← Vector index (auto-created)
```

---

*Updated July 2026 — PowerShell compatible*
