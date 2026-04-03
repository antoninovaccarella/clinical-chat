# Clinical Chat

Clinical Chat is a web application for exploring clinical and biomedical questions through a conversational interface. It combines a Flask web UI, multiple selectable LLM backends, a LangGraph workflow, and domain-specific tools for ClinicalTrials.gov and PubMed.

The project is designed for research and prototyping workflows where clinicians, biomedical researchers, and developers need a shared interface to ask questions, inspect clinical trial information, and compare model behavior.

## What The Application Does

Clinical Chat can help with tasks such as:

- exploring clinical trials related to diseases, drugs, devices, or interventions;
- retrieving protocol details, outcomes, and available trial results;
- using different LLM providers from the same UI;
- optionally consulting PubMed when trial data alone is not enough;
- exposing the same backend to an optional Telegram bot.

The application is not a medical device and does not replace clinical judgment, literature review, or methodological validation. Generated answers must always be checked against the original sources.

## Important Safety Notes

- Do not submit personal data, patient-identifiable information, or sensitive health data.
- Requests are sent to external LLM providers.
- Answers may contain errors, omissions, or incomplete reasoning.
- The files in [`db/`](/Users/antoninovaccarella/Documents/GitHub/clinical-chat/db) are temporary working files, not a validated clinical database.

## How It Works

At a high level, the request flow is:

1. A user enters a question in the web UI.
2. The browser sends a `POST /chat` request to the Flask backend.
3. Flask validates the payload and forwards it to the chatbot workflow.
4. LangGraph runs a ReAct-style agent backed by the selected LLM.
5. The agent decides whether to:
   - answer directly;
   - retrieve trial data from ClinicalTrials.gov;
   - inspect the local CSV cache with Python and Pandas;
   - use PubMed for medical literature support.
6. The final answer is returned as JSON and rendered in the chat UI.

The main pieces of the system are:

- [`main.py`](/Users/antoninovaccarella/Documents/GitHub/clinical-chat/main.py): application entry point;
- [`app/__init__.py`](/Users/antoninovaccarella/Documents/GitHub/clinical-chat/app/__init__.py): Flask app factory;
- [`app/client/routes.py`](/Users/antoninovaccarella/Documents/GitHub/clinical-chat/app/client/routes.py): HTTP endpoints, including `/chat`;
- [`app/client/chatbot.py`](/Users/antoninovaccarella/Documents/GitHub/clinical-chat/app/client/chatbot.py): chatbot wrapper around the workflow;
- [`app/rag_agent/workflow.py`](/Users/antoninovaccarella/Documents/GitHub/clinical-chat/app/rag_agent/workflow.py): LangGraph orchestration;
- [`app/rag_agent/react_agent.py`](/Users/antoninovaccarella/Documents/GitHub/clinical-chat/app/rag_agent/react_agent.py): ReAct agent and tool selection rules;
- [`app/rag_agent/clinical_tool/`](/Users/antoninovaccarella/Documents/GitHub/clinical-chat/app/rag_agent/clinical_tool): ClinicalTrials.gov integration and local dataset utilities;
- [`app/templates/index.html`](/Users/antoninovaccarella/Documents/GitHub/clinical-chat/app/templates/index.html) and [`app/static/style.css`](/Users/antoninovaccarella/Documents/GitHub/clinical-chat/app/static/style.css): web UI.

## Runtime Behavior

Clinical Chat maintains two temporary files under [`db/`](/Users/antoninovaccarella/Documents/GitHub/clinical-chat/db):

- `ClinicalTrialsDB.csv`
- `ClinicalTrialsDB.json`

These files are cleared automatically every time the application starts, both locally and in Docker. This means each new app startup begins with a fresh working session.

## Supported Models

The UI currently exposes these model options:

- `gemini` -> `gemini-3-flash-preview`
- `chatgpt` -> `gpt-4o-mini` through a ChatOpenAI-compatible client
- `deepseek-v3` -> `deepseek-chat`
- `deepseek-r1` -> `deepseek-reasoner`

An API key can be supplied in either of these ways:

- directly in the web UI;
- through environment variables.

The main environment variable mappings used by the code are:

- `GEMINI_API` or `GEMINI_API_2` for Gemini;
- `DEEPSEEK_API_KEY` for DeepSeek V3 and DeepSeek R1;
- `DEEPBRICKS_API_KEY` for the default `chatgpt` setup;
- `OPENAI_API_BASE` if you want the `chatgpt` option to use a custom OpenAI-compatible endpoint.

## Requirements

For Docker execution:

- Docker
- Docker Compose

For local execution:

- Python 3.11 recommended
- `venv`
- internet access
- at least one valid API key for a supported model

Python 3.11 is the recommended local version because it matches the base image used in the [`Dockerfile`](/Users/antoninovaccarella/Documents/GitHub/clinical-chat/Dockerfile). Local installs also work on Python 3.12 and 3.13 because [`requirements.txt`](/Users/antoninovaccarella/Documents/GitHub/clinical-chat/requirements.txt) selects compatible `pandas` and `numpy` builds for newer interpreters.

## Environment Variables

The repository includes an example file:

```bash
cp .env.example .env
```

The most important variables are:

- `FLASK_HOST`: host bound by the Flask process;
- `FLASK_PORT`: port used by Flask inside the Python process;
- `HOST_PORT`: host port published by Docker Compose;
- `SECRET_KEY`: Flask secret key;
- `GEMINI_API`, `DEEPSEEK_API_KEY`, `DEEPBRICKS_API_KEY`: model API keys;
- `TELEGRAM_API_KEY`: only required for the optional Telegram bot;
- `CSV_PATH`, `JSON_PATH`: paths for the temporary trial files.

The default template is:

```env
# Flask
FLASK_HOST=0.0.0.0
FLASK_PORT=7860
HOST_PORT=5000
FLASK_DEBUG=false
SECRET_KEY=dev-secret-key

# Data sources
CLINICAL_API=https://clinicaltrials.gov/api/v2/
CSV_PATH=./db/ClinicalTrialsDB.csv
JSON_PATH=./db/ClinicalTrialsDB.json

# LLM providers
GEMINI_API=
GEMINI_API_2=
GEMINI_API_3=
DEEPSEEK_API_KEY=
DEEPBRICKS_API_KEY=
OPENAI_API_BASE=

# Reserved for future integrations
MISTRAL_AI_API=
GROQ_API_KEY=
OPEN_ROUTER_API_KEY=

# Optional Telegram bot
TELEGRAM_API_KEY=
```

Important note for local execution: `python main.py` does not automatically load `.env`, so you must export the variables in your shell first if you want to rely on them locally.

## Running With Docker

Docker is the easiest way to start the project with a reproducible environment.

### 1. Verify Docker

```bash
docker --version
docker compose version
```

### 2. Create the environment file

```bash
cp .env.example .env
```

Fill in at least one API key if you want the backend to work immediately. If needed, you can still enter a key manually in the web UI.

### 3. Start the web application

```bash
docker compose up --build web
```

By default:

- Flask runs on port `7860` inside the container;
- Docker publishes it on host port `5000`.

Open:

```text
http://127.0.0.1:5000
```

### 4. Stop the containers

```bash
docker compose down
```

### 5. Change the exposed host port

If port `5000` is already in use:

```bash
HOST_PORT=5001 docker compose up --build web
```

Then open:

```text
http://127.0.0.1:5001
```

### 6. View logs

```bash
docker compose logs -f web
```

### 7. Start the optional Telegram bot

```bash
docker compose --profile telegram up --build
```

This starts:

- `web`
- `telegram`

The Telegram service requires `TELEGRAM_API_KEY` in `.env`.

## Running Locally Without Docker

This mode is useful for development, debugging, and source-level inspection.

### 1. Create a virtual environment

Recommended:

```bash
python3.11 -m venv .venv
```

If `python3.11` is not available but `python3` already points to Python 3.11, 3.12, or 3.13:

```bash
python3 -m venv .venv
```

### 2. Activate the virtual environment

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 4. Create `.env`

```bash
cp .env.example .env
```

### 5. Export the environment variables

Because the app does not auto-load `.env` outside Docker, export it before starting Flask:

```bash
set -a
source .env
set +a
```

If you do not want to export `.env`, you can also set variables manually in your shell.

### 6. Start the application

```bash
python main.py
```

By default the local server listens on:

```text
http://127.0.0.1:7860
```

If `FLASK_PORT` is set to a different value, use that port instead.

## Optional Telegram Bot

The repository also contains [`main_telegram_bot.py`](/Users/antoninovaccarella/Documents/GitHub/clinical-chat/main_telegram_bot.py), which forwards Telegram messages to the same Flask `/chat` endpoint.

Typical uses:

- demoing the same assistant outside the browser;
- running a lightweight chat bridge without changing backend logic.

For Docker, use the `telegram` profile shown above.

For a local run, make sure:

- the Flask app is already running;
- `TELEGRAM_API_KEY` is exported;
- `CHATBOT_ENDPOINT` points to the Flask `/chat` URL if you are not using the default.

Example local start:

```bash
set -a
source .env
set +a
export CHATBOT_ENDPOINT=http://127.0.0.1:7860/chat
python main_telegram_bot.py
```

## HTTP API

The main backend endpoint is:

```text
POST /chat
```

Example request:

```bash
curl -X POST http://127.0.0.1:7860/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the main outcomes of trials on pembrolizumab in lung cancer?",
    "model": "gemini",
    "api_key": "YOUR_API_KEY"
  }'
```

Example response shape:

```json
{
  "response": "..."
}
```

## Project Structure

```text
clinical-chat/
├── app/
│   ├── client/                    # Flask routes and chatbot wrapper
│   ├── large_language_models/     # Model connectors
│   ├── rag_agent/                 # LangGraph workflow and tools
│   ├── static/                    # CSS and static assets
│   └── templates/                 # HTML templates
├── db/                            # Temporary ClinicalTrials working files
├── Dockerfile
├── docker-compose.yml
├── main.py
├── main_telegram_bot.py
├── requirements.txt
└── README.md
```

## Notes For Contributors

- The web UI is rendered by Flask and enhanced with client-side JavaScript.
- ClinicalTrials.gov data is downloaded on demand and written to local working files in [`db/`](/Users/antoninovaccarella/Documents/GitHub/clinical-chat/db).
- Those working files are reset at every application startup.
- If you run locally, remember that `.env` is not auto-loaded by the app.

## License

No license file is currently included in the repository. Add one if you plan to distribute or publish the project more broadly.
