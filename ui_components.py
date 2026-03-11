"""
DocuMind AI — UI Components
"""
import streamlit as st
import hashlib
from datetime import datetime
from config import APP_TITLE, AVAILABLE_MODELS
from pdf_engine import process_pdf, process_text, chunk_documents
from web_scraper import scrape_url
from rag_engine import rebuild_agent


# ============================================================
# INITIALIZATION
# ============================================================
def init_session():
    """Initializes Streamlit session state."""
    defaults = {
        "messages": [],
        "all_chunks": [],
        "sources": [],
        "agent": None,
        "system_ready": False,
        "query_count": 0,
        "total_chunks": 0,
        "pdf_bytes_store": {},
        "selected_model": AVAILABLE_MODELS[0],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# ============================================================
# RENDERING FUNCTIONS
# ============================================================
def render_hero():
    st.markdown(f"""
    <div class="hero-header">
        <div class="hero-title">DocuMind AI</div>
        <div class="hero-subtitle">Your Context-Aware Knowledge Assistant ✨</div>
    </div>
    """, unsafe_allow_html=True)


def render_welcome():
    st.markdown("""
    <div class="welcome-card glass-card">
        <div class="welcome-icon">🧠</div>
        <h2 style="color: #e0e0ff; margin-bottom: 8px;">Welcome to DocuMind AI</h2>
        <p class="welcome-text">Your intelligent assistant is ready. To get started, upload a document, paste a web link, or add a raw text note using the sidebar menu.</p>
        <div class="feature-tags">
            <span class="feature-tag">PDF Support</span>
            <span class="feature-tag">Web Scraping</span>
            <span class="feature-tag">Text Notes</span>
            <span class="feature-tag">Smart RAG</span>
            <span class="feature-tag">PDF Editing</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_stats():
    st.markdown(f"""
    <div class="stats-container">
        <div class="stat-item">
            <div class="stat-value">{len(st.session_state['sources'])}</div>
            <div class="stat-label">Sources</div>
        </div>
        <div class="stat-item">
            <div class="stat-value">{st.session_state['total_chunks']}</div>
            <div class="stat-label">Knowledge Chunks</div>
        </div>
        <div class="stat-item">
            <div class="stat-value">{st.session_state['query_count']}</div>
            <div class="stat-label">Queries</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_source_badges():
    sources = st.session_state.get("sources", [])
    if not sources:
        return
    html = '<div style="text-align: center; margin-bottom: 20px;">'
    for s in sources:
        icon = {"pdf": "📄", "web": "🌐", "text": "📝"}.get(s["type"], "📁")
        css_class = "source-badge-web" if s["type"] == "web" else "source-badge-text" if s["type"] == "text" else ""
        html += f"<span class='source-badge {css_class}'>{icon} {s['name']}</span>"
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


def render_agent_thoughts(intermediate_steps):
    if not intermediate_steps:
        return
    with st.expander("🧠 Agent Reason Process", expanded=False):
        for step in intermediate_steps:
            if isinstance(step, dict):
                if step.get("type") == "action":
                    st.markdown(f"""
                    <div class="thought-step">
                        <div class="thought-label">Action: {step['tool']}</div>
                        <div>Input: {step['input']}</div>
                    </div>
                    """, unsafe_allow_html=True)
            elif isinstance(step, tuple):
                action, observation = step
                st.markdown(f"""
                <div class="thought-step">
                    <div class="thought-label">Action: {action.tool}</div>
                    <div>Input: {action.tool_input}</div>
                </div>
                """, unsafe_allow_html=True)
                st.markdown(f"""
                <div class="thought-step" style="border-left-color: #10b981; background: rgba(16,185,129,0.05);">
                    <div class="thought-label" style="color: #34d399;">Observation</div>
                    <div>{str(observation)[:500]}...</div>
                </div>
                """, unsafe_allow_html=True)


# ============================================================
# SOURCE ADDITION ACTIONS
# ============================================================
def _add_pdfs(uploaded_files):
    with st.spinner("Processing PDFs..."):
        for f in uploaded_files:
            file_id = hashlib.md5(f.name.encode()).hexdigest()[:8]
            if any(s["id"] == file_id for s in st.session_state["sources"]):
                st.warning(f"{f.name} already added.")
                continue
            docs = process_pdf(f.read(), f.name)
            chunks = chunk_documents(docs)
            st.session_state["all_chunks"].extend(chunks)
            st.session_state["sources"].append({"type": "pdf", "name": f.name, "id": file_id})
        rebuild_agent()
        st.success(f"Added {len(uploaded_files)} PDF(s)!")
        st.rerun()


def _add_url(url: str):
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    with st.spinner("Scraping webpage..."):
        try:
            url_id = hashlib.md5(url.encode()).hexdigest()[:8]
            if any(s["id"] == url_id for s in st.session_state["sources"]):
                st.warning(f"URL already added: {url}")
                return

            docs = scrape_url(url)
            chunks = chunk_documents(docs)
            title = docs[0].metadata["source_file"]

            st.session_state["all_chunks"].extend(chunks)
            st.session_state["sources"].append({"type": "web", "name": title[:30] + "..." if len(title)>30 else title, "id": url_id})
            rebuild_agent()
            st.success(f"Scraped and added: {title}")
            st.rerun()
        except Exception as e:
            st.error(f"Failed to scrape URL: {str(e)}")


def _add_text(text: str, title: str):
    with st.spinner("Processing text..."):
        text_id = hashlib.md5(text.encode()).hexdigest()[:8]
        if any(s["id"] == text_id for s in st.session_state["sources"]):
            st.warning("This text note is exactly the same as an existing one.")
            return

        docs = process_text(text, title)
        chunks = chunk_documents(docs)
        st.session_state["all_chunks"].extend(chunks)
        st.session_state["sources"].append({"type": "text", "name": title, "id": text_id})
        rebuild_agent()
        st.success(f"Added note: {title}")
        st.rerun()


# ============================================================
# SIDEBAR
# ============================================================
def render_sidebar():
    with st.sidebar:
        st.markdown("### 📚 Knowledge Base Sources")
        source_type = st.selectbox(
            "Source Type",
            options=["📄 PDF Upload", "🌐 Web URL", "📝 Text Note"],
            label_visibility="collapsed"
        )

        if source_type == "📄 PDF Upload":
            uploaded_files = st.file_uploader(
                "Drop PDFs here",
                type=["pdf"],
                accept_multiple_files=True,
                label_visibility="collapsed"
            )
            if uploaded_files:
                if st.button("➕ Add PDFs to Knowledge Base", use_container_width=True):
                    _add_pdfs(uploaded_files)

        elif source_type == "🌐 Web URL":
            url = st.text_input("Enter URL to scrape", placeholder="https://example.com/docs")
            if url:
                if st.button("➕ Scrape & Add to Knowledge Base", use_container_width=True):
                    _add_url(url)

        elif source_type == "📝 Text Note":
            note_title = st.text_input("Note title", placeholder="Meeting Notes")
            note_text = st.text_area("Paste your text", height=120, placeholder="Paste raw text, notes, or context here...")
            if note_text and note_title:
                if st.button("➕ Add Note to Knowledge Base", use_container_width=True):
                    _add_text(note_text, note_title)

        # --- Active Sources ---
        st.divider()
        st.markdown("### 🗂️ Active Sources")
        sources = st.session_state.get("sources", [])
        if sources:
            for s in sources:
                icon = {"pdf": "📄", "web": "🌐", "text": "📝"}.get(s["type"], "📁")
                st.markdown(f"<span class='source-badge{' source-badge-web' if s['type']=='web' else ' source-badge-text' if s['type']=='text' else ''}'>{icon} {s['name']}</span>", unsafe_allow_html=True)
        else:
            st.caption("No sources added yet.")

        # --- Reset ---
        st.divider()
        if st.button("🗑️ Reset Knowledge Base", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

        # --- Settings ---
        st.divider()
        st.markdown("### ⚙️ Settings")
        selected_index = AVAILABLE_MODELS.index(st.session_state["selected_model"]) if st.session_state["selected_model"] in AVAILABLE_MODELS else 0
        new_model = st.selectbox(
            "AI Agent Model",
            options=AVAILABLE_MODELS,
            index=selected_index,
            help="If you encounter a Rate Limit Error, switch to another model to continue immediately."
        )
        if new_model != st.session_state["selected_model"]:
            st.session_state["selected_model"] = new_model
            if st.session_state.get("all_chunks"):
                rebuild_agent()
            st.rerun()
