Here is the development timeline, sprint schedules, and milestone targets for the **[Personalized Networking Assistant](file:///c:/Users/91767/networking-assistant/README.md)** project.

---

### Phase 4: Project Planning Phase
This documents the development timeline, sprint schedules, and milestone targets for the platform.

### 1. Project Milestones

| Milestone | Target Deliverable | Completion Status |
| :--- | :--- | :--- |
| **Milestone 1** | **Backend Setup & Configurations**: Virtual environment configuration, python packaging structures, and config files. | Completed |
| **Milestone 2** | **Relational Database & ORM**: SQLite connection engine, SQLAlchemy schemas, and session utilities. | Completed |
| **Milestone 3** | **NLP Core Engine**: DistilBERT similarity theme extractor and GPT-2 generator pipeline. | Completed |
| **Milestone 4** | **API Route Integration**: FastAPI REST endpoints for generating starters, logging feedback, history, and verification. | Completed |
| **Milestone 5** | **Fact Checking Service**: Wikipedia API wrappers, search integration, content sanitization, and URL generators. | Completed |
| **Milestone 6** | **Frontend UI & Components**: Streamlit main frame, CSS variables, gradient cards, feedback buttons, and sidebar navigation. | Completed |
| **Milestone 7** | **Testing & Launch**: Pytest endpoint validation suite, DB transaction auditing, and full-stack runtime verification. | Completed |

---

### 2. Work Breakdown Structure (WBS)

#### Sprint 1: Backend Initialization & Database Modeling
* Set up FastAPI folder structure, define python dependency packages, and initialize virtual environment (`venv`).
* Establish configuration scripts in [config.py](file:///c:/Users/91767/networking-assistant/config/config.py) to read database and model constants.
* Define SQLAlchemy database models in [models.py](file:///c:/Users/91767/networking-assistant/backend/models/models.py) reflecting the core relational tables.
* Establish session makers and database engines inside [database.py](file:///c:/Users/91767/networking-assistant/backend/database.py).

#### Sprint 2: Core NLP Processing & Fallback Layer
* Implement semantic theme extraction algorithm in [nlp_service.py](file:///c:/Users/91767/networking-assistant/backend/services/nlp_service.py) using DistilBERT to compute document/candidate cosine similarities.
* Set up GPT-2 text-generator pipelines to process theme-interest prompts and return context-aware starters.
* Build resilient heuristic rules and fallback text templates to act as a failsafe when local transformer models fail to load.

#### Sprint 3: Verification Service & REST API Routing
* Integrate Wikipedia search and content retrieval inside [wiki_service.py](file:///c:/Users/91767/networking-assistant/backend/services/wiki_service.py) to extract clean intro summaries and hyperlink URLs.
* Implement FastAPI endpoints in [routes.py](file:///c:/Users/91767/networking-assistant/backend/routes/routes.py) for suggestions generating, feedback updates, search queries, and logs audit.
* Initialize FastAPI server CORS middleware and mount routers in [main.py](file:///c:/Users/91767/networking-assistant/backend/main.py).

#### Sprint 4: Frontend Development & Core Dashboard
* Scaffold the Streamlit frontend in [app.py](file:///c:/Users/91767/networking-assistant/frontend/app.py) with sidebar navigation links and backend connectivity checks.
* Inject global Token CSS scripts into Streamlit to apply the custom *Outfit* font styling, HSL gradients, and hover transitions.
* Develop the **Smart Starter Generator** form to collect event inputs and format the output themes, interests, and starters.

#### Sprint 5: Fact Checker, History & Feedback Components
* Build the **Quick Fact Check** interface to route concept lookups to the Wikipedia endpoint and display verified summaries in custom card patterns.
* Develop the **Networking History** page to fetch generated starters and feedback histories from the database.
* Build interactive thumbs up/down feedback button groups in Streamlit to submit rating requests and update DB states asynchronously.

#### Sprint 6: Testing, Restructuring & Deployments
* Write pytest unit testing scripts inside `tests/test_app.py` to verify API routing paths, fallbacks, and fact checking queries.
* Validate SQLAlchemy database operations to confirm feedback JSON changes write correctly to SQLite.
* Execute full-stack health checks to verify that Streamlit communicates cleanly with the local FastAPI ASGI server.