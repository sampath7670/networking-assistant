Here is the system architecture, database schema, and problem-solution fits for the **[Personalized Networking Assistant](file:///c:/Users/91767/networking-assistant/README.md)**.

---

### Phase 3: Project Design Phase
This documents the system architecture, database schema, and problem-solution fits for the platform.

### 1. Problem-Solution Fit Matrix

| Customer Pain | Pain Reliever / Feature | Value Created |
| :--- | :--- | :--- |
| **High social anxiety and "freeze" at networking events** | Smart Starter Generator Dashboard | Gives the attendee high-quality, pre-computed icebreakers tailored directly to the event context. |
| **Struggles to relate personal interests to event themes** | Local NLP Theme Extractor (DistilBERT) | Automatically correlates and highlights thematic crossovers so the user knows why a prompt is relevant. |
| **Inability to write engaging, organic introduction lines** | AI Starter Generator (GPT-2) | Generates three natural-sounding, professional conversation starters ready to be spoken or modified. |
| **Fear of stating incorrect facts about concepts during chat** | Quick Fact Verification Tab (Wikipedia API) | Retrieves clean, verified 600-character Wikipedia summaries and reference links for real-time prep. |
| **Forgets what worked in previous events or wants to review** | History & Feedback Loop (SQLite + Thumbs Up/Down) | Persistently logs all previous prompts, allows feedback submission, and saves successful starter outcomes. |

---

### 2. Solution Architecture Flow
The platform is designed using a decoupled client-server architecture:

```
[USER LAYER] 
      │ (Interacts with Streamlit Web Client)
      ▼
[PRESENTATION LAYER] ➔ Streamlit Dashboard UI (Single-page navigation, custom CSS HSL theme, Outfit font)
      │ (HTTPS REST API Queries / JSON payloads)
      ▼
[API ROUTER LAYER] ➔ FastAPI Backend Services (CORS validation, REST routing in routes.py)
      │
      ├─➔ [THEME EXTRACTOR SERVICE] (DistilBERT semantic embedding candidate comparisons)
      │
      ├─➔ [TEXT GENERATOR SERVICE] (GPT-2 pipeline structured generator with fallback heuristics)
      │
      └─➔ [WIKIPEDIA SERVICE] (Real-time fact verification and HTML-to-markdown API parser)
      │
      ▼
[DATABASE PERSISTENCE LAYER] ➔ SQLAlchemy ORM ➔ SQLite Database (networking_assistant.db)
```

---

### 3. Database Schema Reference
The persistence layer is structured with a central log table in [models.py](file:///c:/Users/91767/networking-assistant/backend/models/models.py) to manage the relationship between user entries, AI output, and performance reviews:

#### 1. suggestions (Primary Suggestion Log)
* **id** (Integer, Primary Key) - Unique identifier for the suggestion generation transaction.
* **event_description** (String, Non-Nullable) - Full text description of the event entered by the user.
* **interests** (String, Non-Nullable) - Comma-separated list of user interests.
* **themes** (String, Non-Nullable) - Comma-separated list of extracted themes calculated by the DistilBERT model.
* **starters_json** (String/Text, Non-Nullable) - JSON-encoded string representation containing the list of the three generated conversation starters (e.g., `["starter 1", "starter 2", "starter 3"]`).
* **feedback_json** (String/Text, Non-Nullable) - JSON-encoded string representation storing thumbs-up/down ratings for each starter (e.g., `[true, false, null]`).
* **created_at** (DateTime, Default: UTC Now) - Timestamp when the suggestion was generated.