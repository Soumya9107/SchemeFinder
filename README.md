# SchemeFinder

SchemeFinder is a lightweight, multilingual assistant that helps users discover Indian government schemes and check their eligibility based on demographic factors (age, income, gender, occupation, state, category).

It runs completely offline using a local rule engine and fallback search, but can optionally connect to OpenSearch for full-text indexing or cloud LLMs (Gemini, Groq, OpenAI) for enhanced natural language responses.

---

## Quick Start

### 1. Prerequisites
- Python 3.10+
- (Optional) Docker & Docker Compose if using OpenSearch locally

### 2. Installation
Clone the repository and install the dependencies:
```bash
pip install -r requirements.txt
```

### 3. Running the Server

**On Windows:**
Double-click `run.bat` or run:
```cmd
python local_server.py
```

**On Linux / macOS:**
```bash
python3 local_server.py
```

Open `http://localhost:8000` in your browser.

---

## Architecture & Design

```
Browser UI (HTML/CSS/JS)
      │
      ▼
local_server.py (HTTP Server / Lambda emulator)
      │
      ▼
src/app.py (AWS Lambda Handler)
      │
      ▼
src/agent/strands_agent.py (Orchestrator)
  ├── Local NLP & Rule Engine (src/agent/local_engine.py)
  ├── OpenSearch / Keyword Fallback (src/agent/tools.py)
  └── Cloud LLM Adapter (Optional: Gemini / Groq / OpenAI)
```

The application is structured around an AWS Lambda handler (`src/app.py`). `local_server.py` wraps the handler into a standard `http.server` for local development without needing Docker or SAM CLI.

### Data & Search Flow
1. **Eligibility Engine (`check_eligibility`)**: Evaluates demographic rules (age boundaries, income ceilings, target occupations, state residency) against `data/schemes.json`.
2. **Search (`search_schemes`)**: Queries an OpenSearch node if reachable (`http://localhost:9200`). If offline, it falls back to token scoring over scheme titles, objectives, and categories.
3. **Multilingual Response Generation**: The built-in rule engine formats responses natively in English, Hindi (`hi`), or Bengali (`bn`). If `GEMINI_API_KEY`, `GROQ_API_KEY`, or `OPENAI_API_KEY` is present in the environment, the response is enriched using the cloud LLM.

---

## Environment Variables

Copy `.env.example` or set the following variables as needed:

| Variable | Default | Description |
|---|---|---|
| `PORT` | `8000` | Port for `local_server.py` |
| `OPENSEARCH_URL` | `http://localhost:9200` | Endpoint for OpenSearch service |
| `GEMINI_API_KEY` | - | (Optional) Google Gemini API key |
| `GROQ_API_KEY` | - | (Optional) Groq API key |
| `OPENAI_API_KEY` | - | (Optional) OpenAI API key |

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/schemes` | Returns list of all available schemes in `schemes.json` |
| `POST` | `/check` | Evaluates eligibility for a profile payload `{ age, income, gender, occupation, state, category }` |
| `POST` | `/chat` | Conversational interface returning formatted agent responses in target language (`en`, `hi`, `bn`) |

---

## Running with OpenSearch (Optional)

SchemeFinder features an optional enterprise full-text search capability powered by **OpenSearch** and **OpenSearch Dashboards**.

### 1. Overview & Search Architecture
- **Full-Text Multi-Match**: When OpenSearch is active, search queries perform weighted multi-field matching:
  - `name.*` (3x weight multiplier)
  - `objective.*` (2x weight multiplier)
  - `category`, `benefits.*`, and `documents`
- **Automatic Auto-Indexing**: Upon starting `local_server.py`, the application checks connection to OpenSearch on `http://localhost:9200`. If available, it automatically creates/updates the `government_schemes` index with scheme records from `data/schemes.json`.
- **Graceful Local Fallback**: If OpenSearch is stopped or unreachable, SchemeFinder transparently falls back to its built-in local token-matching algorithm without disruption or code changes.

### 2. How to Run OpenSearch

#### Step 1: Start Docker Containers
Ensure Docker Desktop or Docker engine is running, then launch the single-node OpenSearch cluster and Dashboards container:
```bash
docker-compose up -d
```

#### Step 2: Access Endpoints
- **OpenSearch Cluster API**: `http://localhost:9200`
- **OpenSearch Dashboards**: `http://localhost:5601`

#### Step 3: Run SchemeFinder
Start the backend server as usual:
```bash
python local_server.py
```
You will see log confirmation that SchemeFinder successfully connected to OpenSearch and indexed `data/schemes.json`.

### 3. Service Management & Troubleshooting
- **Check Container Status**:
  ```bash
  docker-compose ps
  ```
- **View Container Logs**:
  ```bash
  docker-compose logs -f opensearch-node
  ```
- **Stop Containers**:
  ```bash
  docker-compose down
  ```

---

## Testing

Run unit tests with pytest:
```bash
pytest
```

---

## Deployment (AWS SAM)

The project includes an AWS SAM template (`template.yaml`) for deploying as an AWS Lambda function behind Amazon API Gateway:

```bash
sam build
sam deploy --guided
```

---

## Project Structure

```
SchemeFinder/
├── data/
│   └── schemes.json          # Scheme records and eligibility rules database
├── public/
│   ├── index.html            # Web interface
│   ├── style.css             # Stylesheet
│   └── app.js                # Frontend logic & API client
├── src/
│   ├── app.py                # AWS Lambda handler entrypoint
│   └── agent/
│       ├── strands_agent.py   # Main agent orchestrator
│       ├── local_engine.py    # Local NLP, intent parser, & multilingual formatter
│       ├── llm_adapter.py     # Cloud LLM integration (Gemini/Groq/OpenAI)
│       ├── tools.py           # Eligibility check, scheme details & search tools
│       └── opensearch_client.py # OpenSearch connector
├── tests/                    # Unit tests
├── docker-compose.yml        # Local OpenSearch container spec
├── local_server.py           # Standalone Python HTTP server
├── template.yaml             # AWS SAM Infrastructure template
└── requirements.txt          # Python dependencies
```
