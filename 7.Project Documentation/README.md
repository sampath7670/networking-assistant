Here is the operational documentation, installation instructions, user manuals, and run guides for the **[Personalized Networking Assistant](file:///c:/Users/91767/networking-assistant/README.md)**.

---

### Phase 7: Project Documentation
This documents the operational instructions, user manuals, installation guides, and core feature references for the platform.

### 1. System Requirements
* **Operating System:** Windows, macOS, or Linux.
* **Python Environment:** Python 3.10 or newer (tested on Python 3.11.8).
* **Hardware Memory / Storage:** Minimum 4GB RAM and 2GB free disk space (required to cache the local transformer models `distilbert-base-uncased` and `gpt2` on first startup).
* **Network Connection:** Active internet connection is required for initial model downloads from Hugging Face and for querying the live Wikipedia API during fact checks.

---

### 2. Installation & Local Setup

#### Step 1: Clone the Repository
Open a terminal and clone the project directory:
```powershell
git clone https://github.com/sampath7670/networking-assistant.git
cd networking-assistant
```

#### Step 2: Configure the Environment & Dependencies
Create and configure a unified Python virtual environment:
1. **Create the virtual environment:**
   ```powershell
   python -m venv venv
   ```
2. **Activate the virtual environment:**
   * **Windows (PowerShell):** `.\venv\Scripts\Activate.ps1`
   * **macOS / Linux:** `source venv/bin/activate`
3. **Install the required packages:**
   ```powershell
   pip install -r backend/requirements.txt
   ```
   *(This installs core dependencies including FastAPI, Streamlit, PyTorch, Transformers, and Wikipedia-API.)*

---

### 3. Running the Applications Locally
To run the full stack locally, you must launch both the backend ASGI API server and the Streamlit frontend server:

#### 1. Launch the Backend API (Terminal 1)
Ensure you are in the root directory and your virtual environment is active, then run:
```powershell
python backend/main.py
```
*(Alternatively, you can run: `uvicorn backend.main:app --reload`)*

The FastAPI server will boot and begin listening on **`http://127.0.0.1:8000`**. You can inspect the interactive Swagger API specifications at **`http://127.0.0.1:8000/docs`**.

#### 2. Launch the Streamlit Frontend Client (Terminal 2)
Open a new terminal window, navigate to the root directory, activate the virtual environment, and run:
```powershell
streamlit run frontend/app.py
```

Streamlit will boot the client interface and serve it at **`http://localhost:8501`**. Open this address in your web browser to interact with the platform.

---

### 4. User Guide & Core Features

#### 1. Generating Smart Conversation Starters
* Navigate to the **🌟 Smart Starter Generator** tab via the sidebar navigation.
* Paste the official summary, abstract, or themes of your upcoming event in the **Event Description** box (e.g., *"Symposium on AI and Sustainable Infrastructure. Discussing renewable grids and smart city planning"*).
* Input key personal or technical interests in the **Your Specific Interests** field, separated by commas (e.g., *"renewable energy, carbon offset"*).
* Click **Generate Tailored Starters**. The backend extracts themes using DistilBERT, passes them to GPT-2, and displays three context-aware icebreakers.

#### 2. Tracking Feedback loops
* Review the generated suggestions in the results cards on the generator page.
* Next to each recommendation, click **👍 Useful** to log a helpful starter, or **👎 Not Useful** to flag a generic one.
* Ratings update the backend SQLite entries in real-time, helping optimize future generation prompts.

#### 3. Real-Time Fact Verification
* Navigate to the **🔍 Quick Fact Check** tab.
* If you hear an unfamiliar term or need to brush up on a concept before a chat, enter the query in the **Enter Topic** search input (e.g., *"Smart Grid"*).
* Click **Query Wikipedia API**.
* The page displays a verified 600-character introduction summary along with a direct reference link to the full Wikipedia article for rapid prep.

#### 4. Audit History & Logs
* Navigate to the **📜 Networking History** tab.
* Scroll through all past events, extracted themes, matching interests, and generated starters chronologically.
* You can view and edit your thumbs-up/down feedback on past generations, allowing you to easily review which icebreakers were successful at prior events.