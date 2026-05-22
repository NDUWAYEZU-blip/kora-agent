# Kora Local Dev Bootstrap Agent — MVP V1

A single-command automation tool that reliably boots the entire Kora development environment on Windows.

```
start-kora
```

---

## What it does

In order:

| Step | Service | Critical |
|------|---------|----------|
| 1 | Verify / launch Docker Desktop | ✅ Yes |
| 2 | Start Redis in Docker | ✅ Yes |
| 3 | Open pgAdmin 4 | ⚪ No |
| 4 | Open VS Code | ⚪ No |
| 5 | Start FastAPI backend (uvicorn) | ✅ Yes |
| 6 | Start Next.js frontend (npm run dev) | ✅ Yes |

Non-critical steps (pgAdmin, VS Code) log a warning on failure and continue. Critical steps abort the bootstrap if they fail.

---

## Prerequisites

- Windows 10 / 11
- Python 3.12+
- Docker Desktop installed
- Git Bash installed (`C:\Program Files\Git\bin\bash.exe`)
- Node.js + npm (for the frontend)
- pgAdmin 4 (optional)
- VS Code (optional)

---

## Installation

### 1 — Clone / copy the agent

```bat
git clone <repo-url> C:\tools\kora-agent
cd C:\tools\kora-agent
```

### 2 — Install Python dependencies

```bat
pip install -r requirements.txt
```

### 3 — Configure paths

```bat
copy .env.example .env
notepad .env
```

Edit every path in `.env` to match your machine:

```env
BACKEND_PATH=C:\Projects\kora-backend
FRONTEND_PATH=C:\Projects\kora-frontend
VSCODE_PATH=C:\Users\YourName\AppData\Local\Programs\Microsoft VS Code\Code.exe
PGADMIN_PATH=C:\Program Files\pgAdmin 4\runtime\pgAdmin4.exe
GIT_BASH_PATH=C:\Program Files\Git\bin\bash.exe
DOCKER_DESKTOP_PATH=C:\Program Files\Docker\Docker\Docker Desktop.exe
```

### 4 — (Optional) Add `start-kora` to PATH

To run `start-kora` from any terminal:

**Option A — Copy the batch file to a directory already on PATH:**
```bat
copy start-kora.bat C:\Windows\System32\start-kora.bat
```

**Option B — Add the agent directory to your user PATH:**
1. Win + R → `sysdm.cpl` → Advanced → Environment Variables
2. Under "User variables", edit `Path`
3. Add `C:\tools\kora-agent`

Now open a new terminal and run:
```
start-kora
```

---

## Running manually

```bat
cd C:\tools\kora-agent
python main.py
```

---

## Configuration reference

All settings live in `.env`.  Defaults are shown in `.env.example`.

| Variable | Default | Description |
|---|---|---|
| `BACKEND_PATH` | *(required)* | Absolute path to your FastAPI project |
| `FRONTEND_PATH` | *(required)* | Absolute path to your Next.js project |
| `VSCODE_PATH` | see `.env.example` | Path to `Code.exe` |
| `PGADMIN_PATH` | see `.env.example` | Path to `pgAdmin4.exe` |
| `GIT_BASH_PATH` | `C:\Program Files\Git\bin\bash.exe` | Path to `bash.exe` |
| `DOCKER_DESKTOP_PATH` | see `.env.example` | Path to Docker Desktop |
| `BACKEND_PORT` | `8000` | uvicorn listen port |
| `FRONTEND_PORT` | `3000` | Next.js listen port |
| `REDIS_PORT` | `6379` | Redis port |
| `REDIS_CONTAINER_NAME` | `kora-redis` | Docker container name |
| `DOCKER_BOOT_TIMEOUT` | `120` | Seconds to wait for Docker engine |
| `BACKEND_STARTUP_TIMEOUT` | `60` | Seconds to wait for uvicorn |
| `FRONTEND_STARTUP_TIMEOUT` | `90` | Seconds to wait for Next.js |
| `LOG_LEVEL` | `INFO` | `DEBUG` / `INFO` / `WARNING` / `ERROR` |

---

## Logs

Structured logs are written to `./logs/kora_YYYYMMDD.log`.

Example output:

```
[INFO    ] ────────────────────────────────────────────────────────
[INFO    ]   KORA DEV ENVIRONMENT BOOTSTRAP AGENT
[INFO    ] ────────────────────────────────────────────────────────
[INFO    ] ── STEP: Docker Desktop ──
[INFO    ] Docker Desktop already running and engine ready.
[INFO    ] [OK] Docker Desktop
[INFO    ] ── STEP: Redis ──
[INFO    ] Redis already reachable on port 6379.
[INFO    ] [OK] Redis
[INFO    ] ── STEP: pgAdmin ──
[INFO    ] pgAdmin is already running.
[INFO    ] [OK] pgAdmin
[INFO    ] ── STEP: VS Code ──
[INFO    ] VS Code is already running.
[INFO    ] [OK] VS Code
[INFO    ] ── STEP: Backend (FastAPI) ──
[INFO    ] Starting backend in: C:\Projects\kora-backend
[INFO    ] Backend is active on port 8000.
[INFO    ] [OK] Backend (FastAPI)
[INFO    ] ── STEP: Frontend (Next.js) ──
[INFO    ] Starting frontend in: C:\Projects\kora-frontend
[INFO    ] Frontend is active on port 3000.
[INFO    ] [OK] Frontend (Next.js)
[INFO    ] ── STARTUP SUMMARY ──
[INFO    ]   ✓  Docker Desktop
[INFO    ]   ✓  Redis
[INFO    ]   ✓  pgAdmin
[INFO    ]   ✓  VS Code
[INFO    ]   ✓  Backend (FastAPI)
[INFO    ]   ✓  Frontend (Next.js)
[INFO    ] ────────────────────────────────────────────────────────
[INFO    ]   ALL SERVICES STARTED SUCCESSFULLY
[INFO    ]   Kora dev environment is ready.
[INFO    ] ────────────────────────────────────────────────────────
```

---

## Troubleshooting

### Docker times out
- Make sure Docker Desktop is installed and you've accepted the license.
- Increase `DOCKER_BOOT_TIMEOUT` in `.env` (default 120 s).

### Redis: "port already allocated"
- Another process is using port 6379.  The agent detects this and continues if Redis is actually reachable.
- To find the process: `netstat -ano | findstr :6379`

### Backend fails to start
- Ensure your virtual environment exists at `kora-backend/.venv`, `kora-backend/venv`, or `kora-backend/env`.
- Verify `uvicorn` is installed inside the venv.
- Check `logs/kora_*.log` for the detailed error.

### Frontend fails to start
- Run `npm install` inside your frontend directory first.
- Ensure Node.js ≥ 18 is installed.

### VS Code or pgAdmin not found
- Update `VSCODE_PATH` / `PGADMIN_PATH` in `.env`.
- These are non-critical; the rest of the stack will still boot.

---

## Project structure

```
kora-agent/
├── main.py                  ← Entry point
├── config.py                ← All settings from .env
├── requirements.txt
├── start-kora.bat           ← Windows launcher script
├── .env.example             ← Copy to .env and customise
│
├── core/
│   ├── orchestrator.py      ← Runs steps in order, tracks results
│   ├── logger.py            ← Coloured console + file logger
│   └── healthcheck.py       ← Port & Docker readiness checks
│
├── modules/
│   ├── docker_manager.py    ← Docker Desktop detection & boot
│   ├── redis_manager.py     ← Redis container lifecycle
│   ├── pgadmin_manager.py   ← pgAdmin launch & process check
│   ├── vscode_manager.py    ← VS Code launch
│   ├── backend_manager.py   ← FastAPI / uvicorn startup
│   └── frontend_manager.py  ← Next.js / npm run dev startup
│
├── utils/
│   ├── terminal.py          ← ManagedProcess, Git Bash runner
│   ├── process_utils.py     ← psutil helpers
│   └── paths.py             ← Path resolution helpers
│
└── logs/                    ← Auto-created; daily log files
```

---

## Roadmap (not in MVP)

- **V2** — Local LLM (Ollama) for intelligent error interpretation
- **V3** — Autonomous repair, multi-project orchestration, natural-language commands
