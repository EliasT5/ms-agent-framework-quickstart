# Setup — from zero to running the first lesson

Follow these steps in order. Every command is copy-paste-ready. Estimated time: **~10 minutes** (plus one-time Node install if you don't have it).

## What you'll install

| Component | Why |
|---|---|
| Python 3.10+ | The SDK needs modern async features |
| Virtual environment (`.venv`) | Keeps dependencies isolated from other Python projects |
| `agent-framework` + helpers | The framework itself plus `.env` loader and Jupyter |
| `uv` | Launches local MCP servers in Unit 5 |
| Node.js | Launches the filesystem MCP server in Unit 7 |
| An `.env` file | Holds your API key and endpoint |

---

## 1. Open a terminal

On Windows, use **PowerShell** (press `Win`, type "powershell", open it) or **Git Bash** if you have it. Everything below works in PowerShell unless marked otherwise. On macOS/Linux use your normal shell.

If you're inside VS Code, open the integrated terminal with `` Ctrl+` `` (backtick).

## 2. Get the repo

If you've already cloned it, skip to step 3. Otherwise:

```powershell
git clone https://github.com/EliasT5/ms-agent-framework-quickstart.git
cd ms-agent-framework-quickstart
```

If you don't have `git`, download a ZIP from the GitHub page and extract it.

## 3. Check Python

```powershell
python --version
```

Expected: `Python 3.10.x`, `3.11.x`, `3.12.x`, or newer. If you see `2.x` or a "command not found" error, install Python from [python.org/downloads](https://www.python.org/downloads/) (check "Add Python to PATH" during install) and reopen the terminal.

> On Windows, `py --version` sometimes works when `python` doesn't — if so, substitute `py` for `python` in all commands below.

## 4. Create a virtual environment

Still inside the repo folder:

```powershell
python -m venv .venv
```

This creates a `.venv/` folder containing a private Python install. Now activate it:

**PowerShell:**
```powershell
.venv\Scripts\Activate.ps1
```

**Git Bash / WSL / macOS / Linux:**
```bash
source .venv/Scripts/activate    # Git Bash
# or
source .venv/bin/activate        # macOS/Linux
```

Your prompt should now start with `(.venv)`. **Keep this terminal open** — every remaining command assumes the venv is active. If you close and reopen the terminal, re-run the activate command.

> PowerShell may refuse with "running scripts is disabled on this system". Fix:
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
> ```
> then try the activate command again.

## 5. Install Python dependencies

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

First time takes ~30 seconds. You're installing:
- `agent-framework` — the main SDK
- `mcp` — the Model Context Protocol client (for Units 5 and 7)
- `python-dotenv` — reads `.env` files
- `jupyter` + `ipykernel` — for running the `lesson.ipynb` notebooks

Verify:

```powershell
python -c "import agent_framework; print(agent_framework.__version__ if hasattr(agent_framework, '__version__') else 'installed')"
```

You should see a version number (or `installed`).

## 6. Install `uv` (for Unit 5's local MCP server)

```powershell
pip install uv
```

Verify:

```powershell
uvx --version
```

If `uvx` isn't found, close and reopen your terminal (PowerShell sometimes caches PATH) and reactivate the venv.

## 7. Install Node.js (for Unit 7's filesystem MCP plugin)

Only needed for Unit 7. Skip if you don't care about the capstone.

1. Download the LTS installer from [nodejs.org](https://nodejs.org/).
2. Run it with defaults.
3. Verify:

```powershell
npx --version
```

## 8. Start a LiteLLM proxy

The curriculum talks to any **OpenAI-compatible** `/v1/chat/completions` endpoint. The recommended setup is a local **[LiteLLM proxy](https://docs.litellm.ai/docs/proxy/quick_start)** on port 4000 — LiteLLM translates OpenAI-format requests into calls to whatever upstream you've configured (OpenAI, Anthropic, Azure, Ollama, a private provider, etc.). You get one local endpoint, provider-agnostic code.

**Install LiteLLM and start the proxy in a separate terminal:**

```powershell
pip install "litellm[proxy]"
litellm --model gpt-4o-mini --port 4000
```

Replace `gpt-4o-mini` with whatever model your upstream access exposes. For more than one model or auth headers, use a `litellm.yaml` config file — see the LiteLLM quick-start.

Leave this terminal open — the curriculum scripts hit it at `http://localhost:4000/v1`.

> **Alternatives:** if your provider already exposes an OpenAI-compatible URL, you can skip the proxy — set `OPENAI_BASE_URL` to their URL. For OpenAI direct, remove `OPENAI_BASE_URL` entirely and use an `sk-proj-...` key.

## 9. Create your `.env`

Back in your main terminal:

**PowerShell:**
```powershell
Copy-Item .env.example .env
```

**Git Bash / macOS / Linux:**
```bash
cp .env.example .env
```

The defaults already point at the local LiteLLM proxy:

```
OPENAI_API_KEY=sk-any-value-for-local-proxy
OPENAI_BASE_URL=http://localhost:4000/v1
OPENAI_CHAT_COMPLETION_MODEL=gpt-4o-mini
```

- `OPENAI_API_KEY` — for the local proxy, any non-empty value works (the proxy auths upstream itself). For a direct provider, use your real key.
- `OPENAI_BASE_URL` — the LiteLLM proxy's OpenAI-compatible endpoint.
- `OPENAI_CHAT_COMPLETION_MODEL` — the model name your LiteLLM config exposes (e.g. `gpt-4o-mini` for OpenAI; other providers use their own names).

Save and close. `.env` is already in `.gitignore` — it will never be committed.

## 10. Sanity check — run Unit 0

```powershell
python unit-00-setup\agent.py
```

Expected output (wording varies):

```
Hello! How can I help you today?
```

**If you see that — you're done.** Head to [`unit-00-setup/README.md`](./unit-00-setup/README.md) to start the curriculum.

## VS Code extras (optional but recommended)

If you use VS Code:

1. Install the **Python** and **Jupyter** extensions.
2. Open the repo folder in VS Code.
3. `Ctrl+Shift+P` → **"Python: Select Interpreter"** → pick the one at `.venv/Scripts/python.exe`.
4. Open any `lesson.ipynb` file. When prompted for a kernel, pick `.venv` again.
5. Run cells with `Shift+Enter`.

## Full copy-paste block (everything in one go)

For the impatient — assuming Python and Node are already installed. **You need two terminals**: one for the LiteLLM proxy, one for the curriculum.

**Terminal A — LiteLLM proxy (keep running):**
```powershell
pip install "litellm[proxy]"
litellm --model gpt-4o-mini --port 4000
```

**Terminal B — curriculum:**
```powershell
git clone https://github.com/EliasT5/ms-agent-framework-quickstart.git
cd ms-agent-framework-quickstart
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
pip install uv
Copy-Item .env.example .env
# .env defaults already point at localhost:4000 — just edit the model name if needed
python unit-00-setup\agent.py
```

---

## When things break

| Symptom | Cause | Fix |
|---|---|---|
| `python: command not found` | Python not installed or not on PATH | Install from python.org; reopen terminal |
| `ModuleNotFoundError: agent_framework` | venv not active | `.venv\Scripts\Activate.ps1` |
| `Activate.ps1 cannot be loaded, running scripts is disabled` | PowerShell exec policy | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |
| `openai.AuthenticationError: Incorrect API key` | Typo in key, or wrong endpoint | Re-check `.env`; key goes next to `=` with no quotes |
| `openai.APIConnectionError` / `Connection refused` | LiteLLM proxy not running, or wrong `OPENAI_BASE_URL` | Start the proxy in another terminal (`litellm --model ... --port 4000`); verify the URL matches |
| `404 Not Found` at `/v1/chat/completions` | Model name unknown to upstream | Change `OPENAI_CHAT_COMPLETION_MODEL` to a model your LiteLLM config actually serves |
| `RuntimeError: asyncio.run() cannot be called from a running event loop` | Running `asyncio.run()` in Jupyter | In notebooks use `await` directly, no `asyncio.run()` |
| `uvx: command not found` | `uv` not on PATH | `pip install uv`; reopen terminal |
| MCP server hangs ~30s on first run | `uvx` is downloading | Wait; subsequent runs are instant |
| `FileNotFoundError: npx` | Node not installed | Install from nodejs.org |
| `Event loop is closed` warning at exit on Windows | Harmless shutdown noise | Ignore; the script worked |
| On Windows: agent says "my tools aren't working" / "Maximum consecutive function call errors" | Middleware `print()` hit a `UnicodeEncodeError` on `→` / `←` in cp1252 stdout; framework saw it as a tool failure | Each agent.py in this repo already calls `sys.stdout.reconfigure(encoding="utf-8")` on Windows. If you copy middleware into your own script, do the same. |
