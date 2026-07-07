Here is the requirement analysis, technology stack selection, customer journey map, and data flow architecture tailored to the **[Personalized Networking Assistant](file:///c:/Users/91767/networking-assistant/README.md)** project.

---

### Phase 2: Requirement Analysis
This documents the requirements, technical choices, customer journeys, and data flow architectures for the platform.

### 1. Technology Stack Selection
The platform is built using a lightweight, performant, and responsive stack designed to support local natural language processing and external API integrations:

* **Frontend:**
  * **Streamlit**: Python-based web framework allowing rapid prototyping of data-driven user interfaces.
  * **Vanilla CSS**: Custom styling with a modern typography token configuration (e.g., Google Font *Outfit*), CSS variables, custom badge styles (`theme-badge`, `interest-badge`), linear gradients, hover effects, and cards configured in [app.py](file:///c:/Users/91767/networking-assistant/frontend/app.py#L580-L656).
* **Backend:**
  * **FastAPI (Python)**: High-performance, asynchronous REST API defining clean routing endpoints in [routes.py](file:///c:/Users/91767/networking-assistant/backend/routes/routes.py#L424) and serving the app via [main.py](file:///c:/Users/91767/networking-assistant/backend/main.py#L521).
  * **Uvicorn**: High-performance ASGI web server.
* **Database & ORM:**
  * **SQLite**: Serverless relational database for local persistence of search histories and user logs, saved to `networking_assistant.db`.
  * **SQLAlchemy ORM**: Maps database tables to Python objects using [Base](file:///c:/Users/91767/networking-assistant/backend/database.py#L125) and handles connections in [database.py](file:///c:/Users/91767/networking-assistant/backend/database.py).
* **Generative AI & NLP Layer:**
  * **DistilBERT (`distilbert-base-uncased`)**: Local Hugging Face transformer model used inside [NLPService](file:///c:/Users/91767/networking-assistant/backend/services/nlp_service.py#L204) to extract event themes by computing cosine similarity scores between word and document embeddings.
  * **GPT-2 (`gpt2`)**: Local text-generation pipeline utilized to construct context-aware conversation starters based on the structured input prompt.
  * **Fallback Heuristic Engine**: Rule-based template generator acting as a resilient fallback in resource-constrained environments if the local transformers models fail to load.
* **External Integrations:**
  * **Wikipedia API (`wikipedia-api` and MediaWiki REST endpoints)**: Programmatic verification engine configured in [WikiService](file:///c:/Users/91767/networking-assistant/backend/services/wiki_service.py#L354) to fetch verified page introductions and full article URLs.

---

### 2. Customer Journey Map
This journey traces how a typical user, **Alex Smith** (an introverted developer), utilizes the networking assistant before and during a professional conference:

```
[Event Discovery] ➔ [Interest Mapping] ➔ [Theme Extraction] ➔ [AI Starter Generation] ➔ [Fact Check & Prep] ➔ [In-person Connection & Feedback]
```

1. **Event Discovery**: Alex is attending an upcoming workshop titled *"AI for Sustainable Cities"* but feels anxious about speaking with industry experts. He launches the Personalized Networking Assistant.
2. **Interest Mapping**: Alex copies the event summary into the description box in the [Smart Starter Generator](file:///c:/Users/91767/networking-assistant/frontend/app.py#L702) and inputs his niche interests, such as *"climate change, urban planning"*.
3. **Theme Extraction**: The backend's [NLPService.extract_themes](file:///c:/Users/91767/networking-assistant/backend/services/nlp_service.py#L236) uses DistilBERT to analyze the description and extracts core contextual themes like *"Sustainable"*, *"Cities"*, and *"Infrastructure"*.
4. **AI Starter Generation**: Alex triggers the generator. The app coordinates a GPT-2 prompt combining the themes and interests, delivering three structured, polite, and context-focused icebreakers on his dashboard.
5. **Fact Check & Prep**: Anxious that he might misremember a term like *"smart grid infrastructure"*, Alex switches to the [Quick Fact Check](file:///c:/Users/91767/networking-assistant/frontend/app.py#L777) tab, searches Wikipedia, and reads a verified summary to build confidence.
6. **In-person Connection & Feedback**: Alex uses the starters at the event to introduce himself to a speaker. He later opens his [Networking History](file:///c:/Users/91767/networking-assistant/frontend/app.py#L676) and submits a "Thumbs Up" rating for the starter that worked, saving the feedback to the database.

---

### 3. Data Flow Diagram (DFD)

#### Level 0 DFD: Context Diagram
```
                     +----------------------------+
                     |                            |
                     |                            | <--- [Event Description, Interests]
                     |                            |
                     |                            | ---> [Extracted Themes, Starters]
                     |                            |
                     |        PERSONALIZED        |
      [Event User]   |         NETWORKING         |
                     |         ASSISTANT          |
                     |                            | <--- [Fact Queries, Feedback Ratings]
                     |                            |
                     |                            | ---> [Wikipedia Summaries & URLs]
                     |                            |
                     +----------------------------+
                           ^                    ^
                           | (DB Queries)       | (External API Requests)
                           v                    v
                 +-------------------+    +---------------+
                 |      SQLite       |    |   Wikipedia   |
                 |     Database      |    |      API      |
                 +-------------------+    +---------------+
```

#### Level 1 DFD: Functional Decomposition
* **Process 1.0 (NLP Theme Extractor)**: Tokenizes the event description via `DistilBERT` and computes cosine similarity with word candidates, returning top `N` event themes.
* **Process 2.0 (Starter Generator)**: Gathers user inputs and themes, prompting the `GPT-2` text generator (or fallback template engine) to output three conversation-starting messages.
* **Process 3.0 (Wikipedia Fact Checker)**: Intercepts concept keywords and routes them to the Wikipedia MediaWiki query API, returning clean summary extracts and hyperlink references.
* **Process 4.0 (History & Feedback Logger)**: Formats results, writes transaction records to SQLAlchemy models, fetches historic logs chronologically, and logs rating changes.
* **Process 5.0 (Data Persistence)**: Executes SQLite read/write operations to commit suggestions, themes, generated strings, and active thumbs-up/down states.