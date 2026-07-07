import streamlit as st
import requests
import json
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Personalized Networking Assistant",
    page_icon="🌟",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Backend Base URL
API_BASE_URL = "http://127.0.0.1:8000/api"

# Inject beautiful CSS for modern styling
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');

/* Apply font family */
html, body, [class*="css"], .stApp {
    font-family: 'Outfit', sans-serif !important;
}

/* Main title styling */
.gradient-title {
    background: linear-gradient(135deg, #6366f1, #a855f7, #ec4899);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 700;
    font-size: 2.6rem;
    margin-bottom: 0.5rem;
    text-align: left;
}

.subtitle {
    color: #94a3b8;
    font-size: 1.1rem;
    margin-bottom: 2rem;
}

/* Card design */
.custom-card {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 20px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    color: #ffffff !important;
}
.custom-card p, .custom-card span {
    color: #ffffff !important;
}
.custom-card:hover {
    transform: translateY(-2px);
    border-color: #6366f1;
    box-shadow: 0 10px 15px -3px rgba(99, 102, 241, 0.15), 0 4px 6px -2px rgba(99, 102, 241, 0.1);
}

/* Theme badge design */
.theme-badge {
    background: linear-gradient(135deg, #4f46e5, #7c3aed);
    color: #ffffff;
    padding: 6px 14px;
    border-radius: 20px;
    font-weight: 500;
    font-size: 0.85rem;
    display: inline-block;
    margin-right: 8px;
    margin-bottom: 10px;
    box-shadow: 0 2px 4px rgba(124, 58, 237, 0.25);
}

.interest-badge {
    background: #0f172a;
    border: 1px solid #6366f1;
    color: #a5b4fc;
    padding: 4px 10px;
    border-radius: 15px;
    font-size: 0.8rem;
    display: inline-block;
    margin-right: 6px;
    margin-bottom: 6px;
}

/* Custom separator */
.separator {
    height: 1px;
    background: linear-gradient(90deg, transparent, #334155, transparent);
    margin: 25px 0;
}

/* Info card styling */
.info-box {
    background: rgba(30, 41, 59, 0.5);
    border-left: 4px solid #6366f1;
    border-radius: 0 8px 8px 0;
    padding: 15px;
    margin-bottom: 15px;
}

.success-badge {
    background-color: rgba(34, 197, 94, 0.1);
    color: #4ade80;
    border: 1px solid rgba(34, 197, 94, 0.2);
    padding: 4px 10px;
    border-radius: 8px;
    font-size: 0.8rem;
    display: inline-block;
}

.fail-badge {
    background-color: rgba(239, 68, 68, 0.1);
    color: #f87171;
    border: 1px solid rgba(239, 68, 68, 0.2);
    padding: 4px 10px;
    border-radius: 8px;
    font-size: 0.8rem;
    display: inline-block;
}
</style>
""", unsafe_allow_html=True)

# Helper function to submit feedback to backend
def submit_feedback(suggestion_id, index, is_useful):
    try:
        url = f"{API_BASE_URL}/history/{suggestion_id}/feedback"
        payload = {"starter_index": index, "is_useful": is_useful}
        res = requests.post(url, json=payload)
        return res.status_code == 200
    except Exception as e:
        st.error(f"Error submitting feedback: {e}")
        return False

# Helper function to fetch history
def fetch_history():
    try:
        res = requests.get(f"{API_BASE_URL}/history")
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    return []

# Sidebar navigation
with st.sidebar:
    st.markdown('<h2 style="font-weight:600;">Networking Assistant</h2>', unsafe_allow_html=True)
    st.markdown("---")
    menu = st.radio(
        "Navigation",
        ["🌟 Smart Starter Generator", "🔍 Quick Fact Check", "📜 Networking History"],
        index=0
    )
    st.markdown("---")
    st.markdown("### Technical Stack")
    st.info("FastAPI • Streamlit • DistilBERT (Themes) • GPT-2 (Starters) • Wikipedia API • SQLite")

# Test backend connection
backend_connected = True
try:
    health_check = requests.get("http://127.0.0.1:8000/", timeout=2)
    if health_check.status_code != 200:
        backend_connected = False
except Exception:
    backend_connected = False

if not backend_connected:
    st.error("⚠️ Cannot connect to the FastAPI backend server!")
    st.markdown("""
    Please ensure the backend is running by executing:
    ```powershell
    .\\venv\\Scripts\\uvicorn backend.main:app --reload
    ```
    """)
    st.stop()

# ----------------- SCENARIO 1: SMART STARTER GENERATOR -----------------
if menu == "🌟 Smart Starter Generator":
    st.markdown('<h1 class="gradient-title">Personalized Networking Assistant</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Enter event details to extract themes and generate targeted conversation starters.</p>', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("### 📝 Enter Event Info")
        with st.form("starter_form"):
            event_description = st.text_area(
                "Event Description",
                placeholder="e.g. AI for Sustainable Cities. Discussing climate change, smart infrastructure, and urban planning solutions.",
                height=150,
                help="Describe the event, summit, panel or workshop in detail."
            )
            interests_input = st.text_input(
                "Your Specific Interests",
                placeholder="e.g. climate change, urban planning, machine learning",
                help="Enter comma-separated keywords representing your technical interests or career goals."
            )
            
            submit_btn = st.form_submit_type = st.form_submit_button("Generate Tailored Starters")

    if submit_btn:
        if not event_description.strip():
            st.error("Please enter an event description.")
        elif not interests_input.strip():
            st.error("Please specify at least one interest.")
        else:
            interests = [i.strip() for i in interests_input.split(",") if i.strip()]
            
            with col2:
                st.markdown("### ⚙️ Processing AI Pipeline")
                with st.spinner("Loading NLP Models & generating content... This might take a few moments on the first execution."):
                    try:
                        payload = {
                            "event_description": event_description,
                            "interests": interests
                        }
                        res = requests.post(f"{API_BASE_URL}/suggestions", json=payload)
                        
                        if res.status_code == 200:
                            data = res.json()
                            st.session_state["last_suggestion"] = data
                            st.success("Successfully generated starters!")
                        else:
                            st.error(f"Error {res.status_code}: {res.json().get('detail', 'Generation failed.')}")
                    except Exception as e:
                        st.error(f"An unexpected error occurred: {e}")

    # Render results on the right column if available
    with col2:
        if "last_suggestion" in st.session_state:
            data = st.session_state["last_suggestion"]
            st.markdown("### 🎯 Generated Results")
            
            # Display themes
            st.markdown("##### Extracted Event Themes (via DistilBERT)")
            for theme in data["themes"]:
                st.markdown(f'<span class="theme-badge">{theme}</span>', unsafe_allow_html=True)
            
            st.markdown("##### Matching Interests")
            for interest in data["interests"]:
                st.markdown(f'<span class="interest-badge">{interest}</span>', unsafe_allow_html=True)
                
            st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
            st.markdown("##### Tailored Conversation Prompts (via GPT-2)")
            
            for idx, starter in enumerate(data["starters"]):
                # Create a clean layout card for the starter
                feedback_state = data["feedback"][idx] if idx < len(data["feedback"]) else None
                
                # HTML Container
                st.markdown(f"""
                <div class="custom-card">
                    <p style="font-size: 1.05rem; line-height: 1.5; font-style: italic; color: #ffffff !important;">"{starter}"</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Feedback UI Buttons
                col_f1, col_f2, col_f3 = st.columns([1, 1, 6])
                
                with col_f1:
                    # Color feedback button differently if selected
                    up_label = "👍 Useful" if feedback_state is True else "👍"
                    if st.button(up_label, key=f"gen_up_{data['id']}_{idx}"):
                        if submit_feedback(data["id"], idx, True):
                            data["feedback"][idx] = True
                            st.session_state["last_suggestion"] = data
                            st.rerun()
                
                with col_f2:
                    down_label = "👎 Not Useful" if feedback_state is False else "👎"
                    if st.button(down_label, key=f"gen_down_{data['id']}_{idx}"):
                        if submit_feedback(data["id"], idx, False):
                            data["feedback"][idx] = False
                            st.session_state["last_suggestion"] = data
                            st.rerun()
                
                with col_f3:
                    if feedback_state is True:
                        st.markdown('<span class="success-badge">Saved as helpful strategy!</span>', unsafe_allow_html=True)
                    elif feedback_state is False:
                        st.markdown('<span class="fail-badge">Marked unhelpful</span>', unsafe_allow_html=True)
                        
                st.markdown("<br>", unsafe_allow_html=True)

# ----------------- SCENARIO 2: QUICK FACT CHECK -----------------
elif menu == "🔍 Quick Fact Check":
    st.markdown('<h1 class="gradient-title">Quick Fact Verification</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Instantly verify technical concepts or topics via Wikipedia before engaging in conversations.</p>', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("### 🔍 Search Topic")
        search_query = st.text_input(
            "Enter Concept / Technology name",
            placeholder="e.g. blockchain in healthcare",
            help="Enter a tech concept, standard, or networking topic you want to query."
        )
        search_btn = st.button("Query Wikipedia API")

    if search_btn:
        if not search_query.strip():
            st.error("Please enter a search query.")
        else:
            with col2:
                with st.spinner("Fetching verified summary..."):
                    try:
                        res = requests.get(f"{API_BASE_URL}/verify", params={"query": search_query})
                        if res.status_code == 200:
                            st.session_state["last_fact"] = res.json()
                            st.success("Verification complete.")
                        else:
                            st.error(f"Could not verify fact: {res.json().get('detail', 'No search results.')}")
                    except Exception as e:
                        st.error(f"Network error querying API: {e}")

    with col2:
        if "last_fact" in st.session_state:
            fact_data = st.session_state["last_fact"]
            st.markdown("### 📋 Verified Summary")
            
            st.markdown(f"""
            <div class="custom-card">
                <h4 style="color:#a855f7; margin-top:0;">{fact_data['title']}</h4>
                <p style="font-size:0.95rem; line-height:1.6; color:#e2e8f0;">{fact_data['summary']}</p>
                <div class="separator" style="margin:15px 0 10px 0;"></div>
                <a href="{fact_data['url']}" target="_blank" style="color:#6366f1; text-decoration:none; font-weight:500;">
                    Read full Wikipedia Article ↗
                </a>
            </div>
            """, unsafe_allow_html=True)

# ----------------- SCENARIO 3: NETWORKING HISTORY -----------------
elif menu == "📜 Networking History":
    st.markdown('<h1 class="gradient-title">Networking Strategy Log</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Review your past generated strategies, and see which starters were marked as useful.</p>', unsafe_allow_html=True)

    history = fetch_history()

    if not history:
        st.info("No networking strategies generated yet. Head over to the 'Smart Starter Generator' to create one!")
    else:
        # Calculate statistics
        total_suggestions = len(history)
        total_starters = total_suggestions * 3
        thumbs_up = sum(1 for item in history for f in item["feedback"] if f is True)
        thumbs_down = sum(1 for item in history for f in item["feedback"] if f is False)
        
        # Display Stats Row
        st.markdown("### 📊 Helpfulness Overview")
        stat_col1, stat_col2, stat_col3 = st.columns(3)
        with stat_col1:
            st.metric("Total Events Analyzed", total_suggestions)
        with stat_col2:
            st.metric("Useful Strategies 👍", thumbs_up)
        with stat_col3:
            st.metric("Not Useful 👎", thumbs_down)
            
        st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
        st.markdown("### 📜 Past Sessions")

        for s_idx, item in enumerate(history):
            # Parse Date
            dt = datetime.fromisoformat(item["created_at"])
            date_str = dt.strftime("%B %d, %Y - %I:%M %p")
            
            expander_title = f"📅 {date_str} | Event: {item['event_description'][:60]}..."
            
            with st.expander(expander_title):
                st.markdown(f"**Full Event Description:** {item['event_description']}")
                
                # Render themes and interests
                c_t, c_i = st.columns(2)
                with c_t:
                    st.markdown("**Themes (DistilBERT):**")
                    for t in item["themes"]:
                        st.markdown(f'<span class="theme-badge">{t}</span>', unsafe_allow_html=True)
                with c_i:
                    st.markdown("**Your Interests:**")
                    for i in item["interests"]:
                        st.markdown(f'<span class="interest-badge">{i}</span>', unsafe_allow_html=True)
                        
                st.markdown("---")
                st.markdown("**Conversation Starters & Feedback:**")
                
                for idx, starter in enumerate(item["starters"]):
                    feedback_state = item["feedback"][idx] if idx < len(item["feedback"]) else None
                    
                    st.markdown(f"""
                    <div style="background-color: rgba(15, 23, 42, 0.4); border-left: 3px solid #7c3aed; padding: 12px 18px; margin-bottom: 8px; border-radius:0 6px 6px 0;">
                        <span style="font-style:italic; color: #ffffff !important;">"{starter}"</span>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Feedback columns
                    c1, c2, c3 = st.columns([1, 1, 10])
                    with c1:
                        up_lbl = "👍 Useful" if feedback_state is True else "👍"
                        if st.button(up_lbl, key=f"hist_up_{item['id']}_{idx}_{s_idx}"):
                            if submit_feedback(item["id"], idx, True):
                                st.rerun()
                    with c2:
                        down_lbl = "👎 Not Useful" if feedback_state is False else "👎"
                        if st.button(down_lbl, key=f"hist_down_{item['id']}_{idx}_{s_idx}"):
                            if submit_feedback(item["id"], idx, False):
                                st.rerun()
                    with c3:
                        if feedback_state is True:
                            st.markdown('<span class="success-badge">Saved as helpful strategy!</span>', unsafe_allow_html=True)
                        elif feedback_state is False:
                            st.markdown('<span class="fail-badge">Marked unhelpful</span>', unsafe_allow_html=True)
                    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)