"""Minimal Streamlit frontend for the stock research MVP."""

from __future__ import annotations

import ipaddress
import os
import sys
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse
from uuid import uuid4

import requests
import streamlit as st
from dotenv import load_dotenv

# Ensure the project root is importable when Streamlit runs this file directly.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.services.mock_data import build_mock_documents

# Load local environment variables for developer convenience.
load_dotenv()

API_BASE_URL = os.getenv("STREAMLIT_API_BASE_URL", "http://127.0.0.1:8000")
FORCE_BACKEND_API = os.getenv("STREAMLIT_FORCE_BACKEND_API", "").lower() == "true"
QUERY_TYPE_OPTIONS = ["company", "stock", "industry", "topic"]
QUERY_TYPE_LABELS = {
    "company": "Company",
    "stock": "Ticker",
    "industry": "Industry",
    "topic": "Theme",
}
DOC_TYPE_CONFIG = {
    "report": {"label": "Reports", "accent": "#315c96"},
    "filing": {"label": "Filings", "accent": "#5f6b7a"},
    "news": {"label": "News", "accent": "#2f7a6b"},
    "article": {"label": "Articles", "accent": "#4d648d"},
}

st.set_page_config(page_title="Signal Desk", page_icon="SD", layout="wide")


def is_private_or_local_url(url: str) -> bool:
    """Return whether the configured API base URL points to localhost/private IP."""
    parsed = urlparse(url)
    hostname = parsed.hostname
    if hostname is None:
        return True
    if hostname in {"localhost", "127.0.0.1", "0.0.0.0"}:
        return True
    try:
        ip = ipaddress.ip_address(hostname)
    except ValueError:
        return False
    return ip.is_private or ip.is_loopback or ip.is_link_local


USE_EMBEDDED_MOCK = not FORCE_BACKEND_API and is_private_or_local_url(API_BASE_URL)


def inject_styles() -> None:
    """Apply a restrained visual style with minimal distraction."""
    st.markdown(
        """
        <style>
            .stApp {
                background:
                    radial-gradient(circle at top, rgba(255, 255, 255, 0.95), rgba(244, 244, 246, 0.96) 48%, rgba(239, 240, 242, 1) 100%);
                color: #111214;
            }
            .block-container {
                max-width: 1080px;
                padding-top: 1.5rem;
                padding-bottom: 2.4rem;
            }
            h1, h2, h3 {
                color: #111214;
                letter-spacing: -0.02em;
            }
            .app-header {
                margin-bottom: 1rem;
            }
            .app-title {
                font-size: 2rem;
                font-weight: 800;
                margin-bottom: 0.15rem;
            }
            .app-subtitle {
                color: #62666d;
                font-size: 0.94rem;
                max-width: 52ch;
            }
            .search-shell, .summary-shell, .empty-shell, .starter-shell {
                background: rgba(255, 255, 255, 0.78);
                border: 1px solid rgba(17, 18, 20, 0.07);
                border-radius: 18px;
                padding: 0.9rem 1rem;
                box-shadow: 0 10px 28px rgba(30, 41, 59, 0.05);
            }
            .summary-shell {
                margin-top: 0.7rem;
                margin-bottom: 0.85rem;
            }
            .summary-grid {
                display: grid;
                grid-template-columns: repeat(3, minmax(0, 1fr));
                gap: 0.65rem;
            }
            .summary-card {
                background: rgba(247, 248, 250, 0.95);
                border-radius: 14px;
                padding: 0.8rem 0.9rem;
                border: 1px solid rgba(17, 18, 20, 0.05);
            }
            .summary-label {
                color: #737984;
                font-size: 0.76rem;
                text-transform: uppercase;
                letter-spacing: 0.08em;
                margin-bottom: 0.25rem;
            }
            .summary-value {
                font-size: 1.15rem;
                font-weight: 800;
            }
            .results-toolbar {
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 1rem;
                margin: 0.5rem 0 0.85rem 0;
            }
            .results-title {
                font-size: 1rem;
                font-weight: 700;
                color: #1a1d22;
            }
            .section-row {
                display: flex;
                align-items: center;
                justify-content: space-between;
                margin: 0.9rem 0 0.55rem 0;
            }
            .section-pill {
                border-radius: 999px;
                padding: 0.22rem 0.55rem;
                background: #eef3f8;
                color: #42566f;
                font-size: 0.76rem;
                font-weight: 700;
            }
            .doc-card {
                background: rgba(255, 255, 255, 0.84);
                border: 1px solid rgba(17, 18, 20, 0.07);
                border-radius: 16px;
                padding: 0.95rem 1rem 0.85rem 1rem;
                margin-bottom: 0.65rem;
                box-shadow: 0 8px 18px rgba(30, 41, 59, 0.035);
            }
            .doc-title {
                font-size: 1.04rem;
                font-weight: 700;
                margin-bottom: 0.22rem;
            }
            .doc-meta {
                color: #6e7682;
                font-size: 0.84rem;
                margin-bottom: 0.45rem;
            }
            .doc-summary {
                color: #272b31;
                margin-bottom: 0.55rem;
                line-height: 1.45;
            }
            .tag-chip {
                display: inline-block;
                background: #edf4ff;
                color: #416083;
                border-radius: 999px;
                padding: 0.14rem 0.48rem;
                margin-right: 0.3rem;
                margin-bottom: 0.22rem;
                font-size: 0.72rem;
                font-weight: 600;
            }
            .empty-copy {
                color: #5f6670;
                font-size: 0.96rem;
            }
            .doc-accent {
                width: 36px;
                height: 4px;
                border-radius: 999px;
                background: var(--accent);
                margin-bottom: 0.65rem;
            }
            .starter-grid {
                display: grid;
                grid-template-columns: repeat(2, minmax(0, 1fr));
                gap: 0.8rem;
                margin-top: 0.9rem;
            }
            .starter-card {
                background: rgba(249, 250, 251, 0.95);
                border: 1px solid rgba(17, 18, 20, 0.06);
                border-radius: 16px;
                padding: 0.95rem 1rem;
                min-height: 144px;
            }
            .starter-label {
                color: #7a808c;
                font-size: 0.74rem;
                text-transform: uppercase;
                letter-spacing: 0.08em;
                margin-bottom: 0.35rem;
            }
            .starter-title {
                font-size: 1.04rem;
                font-weight: 700;
                margin-bottom: 0.35rem;
                color: #111214;
            }
            .starter-copy {
                color: #5b6370;
                font-size: 0.9rem;
                line-height: 1.45;
            }
            .starter-list {
                margin-top: 0.9rem;
                display: grid;
                grid-template-columns: repeat(3, minmax(0, 1fr));
                gap: 0.7rem;
            }
            .starter-mini {
                background: rgba(255, 255, 255, 0.9);
                border: 1px solid rgba(17, 18, 20, 0.06);
                border-radius: 14px;
                padding: 0.8rem 0.85rem;
            }
            .starter-mini-title {
                font-weight: 700;
                font-size: 0.92rem;
                margin-bottom: 0.18rem;
            }
            .starter-mini-copy {
                color: #66707c;
                font-size: 0.84rem;
                line-height: 1.4;
            }
            div[data-testid="stButton"] > button[kind="primary"] {
                background: linear-gradient(180deg, #2583ff 0%, #0a66ff 100%);
                color: white;
                border: none;
                box-shadow: 0 10px 20px rgba(37, 131, 255, 0.22);
            }
            div[data-testid="stButton"] > button[kind="primary"]:hover {
                background: linear-gradient(180deg, #3c93ff 0%, #1d73ff 100%);
                color: white;
            }
            div[data-testid="stButton"] > button {
                border-radius: 12px;
            }
            div[data-testid="stBaseButton-secondary"] > button,
            div[data-testid="stButton"] > button[kind="secondary"] {
                background: rgba(255, 255, 255, 0.88);
                border: 1px solid rgba(17, 18, 20, 0.08);
                color: #1d2733;
            }
            [data-testid="stSidebar"] {
                display: none;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def create_task(query: str, query_type: str) -> dict:
    """Call the backend to create a new mock crawl task."""
    if USE_EMBEDDED_MOCK:
        return {
            "task_id": str(uuid4()),
            "status": "success",
            "message": "Embedded mock task created.",
        }
    response = requests.post(
        f"{API_BASE_URL}/api/tasks",
        json={"query": query, "query_type": query_type},
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


def get_task(task_id: str) -> dict:
    """Retrieve task status from the backend."""
    if USE_EMBEDDED_MOCK:
        return st.session_state.embedded_task_map.get(task_id, {})
    response = requests.get(f"{API_BASE_URL}/api/tasks/{task_id}", timeout=10)
    response.raise_for_status()
    return response.json()


def get_documents(task_id: str) -> dict:
    """Retrieve normalized documents for a finished task."""
    if USE_EMBEDDED_MOCK:
        return st.session_state.embedded_document_map.get(
            task_id, {"task_id": task_id, "count": 0, "items": []}
        )
    response = requests.get(f"{API_BASE_URL}/api/tasks/{task_id}/documents", timeout=10)
    response.raise_for_status()
    return response.json()


def poll_until_complete(task_id: str, timeout_seconds: int = 10) -> dict:
    """Poll the backend until the task reaches a terminal status."""
    if USE_EMBEDDED_MOCK:
        time.sleep(0.5)
        return get_task(task_id)
    deadline = time.time() + timeout_seconds
    latest = {}
    while time.time() < deadline:
        latest = get_task(task_id)
        if latest["status"] in {"success", "partial_success", "failed"}:
            return latest
        time.sleep(0.8)
    return latest


def format_publish_time(raw_value: str) -> str:
    """Convert backend timestamps into a readable UI format."""
    try:
        return datetime.fromisoformat(raw_value.replace("Z", "+00:00")).strftime(
            "%Y-%m-%d %H:%M"
        )
    except ValueError:
        return raw_value


def summarize_counts(items: list[dict]) -> dict[str, int]:
    """Count documents by type for lightweight filters."""
    counts = {key: 0 for key in DOC_TYPE_CONFIG}
    for item in items:
        counts[item["doc_type"]] = counts.get(item["doc_type"], 0) + 1
    return counts


def run_embedded_research(query: str, query_type: str) -> tuple[dict, dict]:
    """Generate a complete mock result package without an external backend."""
    task_id = str(uuid4())
    documents = [doc.model_dump(mode="json") for doc in build_mock_documents(query)]
    task = {
        "id": task_id,
        "query": query,
        "query_type": query_type,
        "status": "success",
        "progress": 100,
        "result_count": len(documents),
        "error_message": None,
        "created_at": datetime.utcnow().isoformat(),
        "started_at": datetime.utcnow().isoformat(),
        "finished_at": datetime.utcnow().isoformat(),
    }
    document_payload = {"task_id": task_id, "count": len(documents), "items": documents}
    st.session_state.embedded_task_map[task_id] = task
    st.session_state.embedded_document_map[task_id] = document_payload
    return (
        {"task_id": task_id, "status": "success", "message": "Embedded mock task created."},
        document_payload,
    )


def render_header() -> None:
    """Render a simple top header."""
    st.markdown(
        """
        <div class="app-header">
            <div class="app-title">Signal Desk</div>
            <div class="app-subtitle">
                Search a company, ticker, industry, or theme and review a compact research pack.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_summary(task: dict, items: list[dict]) -> None:
    """Render only the essential task summary."""
    st.markdown(
        f"""
        <div class="summary-shell">
            <div class="summary-grid">
                <div class="summary-card">
                    <div class="summary-label">Query</div>
                    <div class="summary-value">{task['query']}</div>
                </div>
                <div class="summary-card">
                    <div class="summary-label">Status</div>
                    <div class="summary-value">{task['status']}</div>
                </div>
                <div class="summary-card">
                    <div class="summary-label">Results</div>
                    <div class="summary-value">{len(items)}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_document_card(doc: dict) -> None:
    """Render one compact document card."""
    accent = DOC_TYPE_CONFIG[doc["doc_type"]]["accent"]
    tags_html = "".join(
        f'<span class="tag-chip">{tag}</span>' for tag in doc["summary"]["tags"]
    )

    st.markdown(
        f"""
        <div class="doc-card" style="--accent: {accent};">
            <div class="doc-accent"></div>
            <div class="doc-title">{doc['title']}</div>
            <div class="doc-meta">
                {doc['source_name']} · {format_publish_time(doc['publish_time'])}
            </div>
            <div class="doc-summary">{doc['summary']['summary_text']}</div>
            <div>{tags_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    action_columns = st.columns([1, 1, 5])
    with action_columns[0]:
        st.link_button("Source", doc["url"], use_container_width=True)

    pdf_attachments = [
        attachment
        for attachment in doc["attachments"]
        if attachment["file_type"].lower() == "pdf"
    ]
    with action_columns[1]:
        if pdf_attachments:
            st.link_button("PDF", pdf_attachments[0]["file_url"], use_container_width=True)


def render_documents(items: list[dict]) -> None:
    """Render grouped documents with a simple type filter."""
    counts = summarize_counts(items)
    filter_options = ["all"] + [doc_type for doc_type, count in counts.items() if count > 0]
    st.markdown(
        f"""
        <div class="results-toolbar">
            <div class="results-title">Research Results</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    selected_filter = st.segmented_control(
        "Content type",
        options=filter_options,
        default="all",
        format_func=lambda value: "All" if value == "all" else DOC_TYPE_CONFIG[value]["label"],
    )

    grouped: dict[str, list[dict]] = defaultdict(list)
    for item in items:
        if selected_filter == "all" or item["doc_type"] == selected_filter:
            grouped[item["doc_type"]].append(item)

    for doc_type in ["report", "filing", "news", "article"]:
        documents = grouped.get(doc_type, [])
        if not documents:
            continue

        st.markdown(
            f"""
            <div class="section-row">
                <h3>{DOC_TYPE_CONFIG[doc_type]['label']}</h3>
                <div class="section-pill">{len(documents)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        for doc in documents:
            render_document_card(doc)


def render_starter_content() -> None:
    """Fill the first-screen empty state with useful starter content."""
    st.markdown(
        """
        <div class="starter-shell">
            <div class="results-title">Start with a useful angle</div>
            <div class="starter-grid">
                <div class="starter-card">
                    <div class="starter-label">Company Check</div>
                    <div class="starter-title">Review the latest filings and coverage</div>
                    <div class="starter-copy">
                        Try a single company or ticker when you want a quick pack with filings,
                        news, and a few higher-level reads.
                    </div>
                </div>
                <div class="starter-card">
                    <div class="starter-label">Theme Scan</div>
                    <div class="starter-title">Scan a sector before going deep</div>
                    <div class="starter-copy">
                        Use a theme like AI chips or cloud security to see how the product behaves
                        when the query is broader than one stock.
                    </div>
                </div>
            </div>
            <div class="starter-list">
                <div class="starter-mini">
                    <div class="starter-mini-title">Reports</div>
                    <div class="starter-mini-copy">Quarterly and annual materials with PDF entry points.</div>
                </div>
                <div class="starter-mini">
                    <div class="starter-mini-title">News</div>
                    <div class="starter-mini-copy">Faster updates that help explain recent moves.</div>
                </div>
                <div class="starter-mini">
                    <div class="starter-mini-title">Articles</div>
                    <div class="starter-mini-copy">Longer-form analysis for context beyond headlines.</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


inject_styles()

if "latest_task" not in st.session_state:
    st.session_state.latest_task = None
if "query_value" not in st.session_state:
    st.session_state.query_value = ""
if "query_type_value" not in st.session_state:
    st.session_state.query_type_value = "company"
if "embedded_task_map" not in st.session_state:
    st.session_state.embedded_task_map = {}
if "embedded_document_map" not in st.session_state:
    st.session_state.embedded_document_map = {}

render_header()

st.markdown('<div class="search-shell">', unsafe_allow_html=True)
query_col, type_col, action_col = st.columns([2.8, 1.1, 1.1])
with query_col:
    query = st.text_input(
        "Query",
        value=st.session_state.query_value,
        placeholder="NVDA, Tesla, AI chips...",
        label_visibility="collapsed",
    )
with type_col:
    query_type = st.selectbox(
        "Type",
        QUERY_TYPE_OPTIONS,
        index=QUERY_TYPE_OPTIONS.index(st.session_state.query_type_value),
        format_func=lambda value: QUERY_TYPE_LABELS[value],
        label_visibility="collapsed",
    )
with action_col:
    run_clicked = st.button("Search", type="primary", use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

sample_cols = st.columns(4)
for column, (sample_query, sample_type) in zip(
    sample_cols,
    [("NVDA", "stock"), ("Tesla", "company"), ("AI chips", "industry"), ("Cloud", "topic")],
):
    with column:
        if st.button(sample_query, key=f"sample-{sample_query}", use_container_width=True):
            st.session_state.query_value = sample_query
            st.session_state.query_type_value = sample_type
            st.rerun()

if run_clicked:
    if not query.strip():
        st.warning("Enter a query first.")
    else:
        st.session_state.query_value = query.strip()
        st.session_state.query_type_value = query_type
        with st.spinner("Preparing results..."):
            try:
                if USE_EMBEDDED_MOCK:
                    created, documents = run_embedded_research(query.strip(), query_type)
                    task = get_task(created["task_id"])
                else:
                    created = create_task(query.strip(), query_type)
                    task = poll_until_complete(created["task_id"])
                    documents = get_documents(created["task_id"])
                st.session_state.latest_task = {
                    "created": created,
                    "task": task,
                    "documents": documents,
                }
                st.rerun()
            except requests.RequestException as exc:
                st.error(f"Backend request failed: {exc}")

latest_task = st.session_state.latest_task

if latest_task:
    task = latest_task["task"]
    items = latest_task["documents"]["items"]
    render_summary(task, items)
    render_documents(items)
else:
    render_starter_content()
