"""
DocuMind AI — RAG Engine (Retriever, Agent, Memory)
"""
import streamlit as st
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever
from langchain.tools.retriever import create_retriever_tool
from langchain import hub
from langchain.agents import AgentExecutor, create_react_agent
from langchain.memory import ConversationBufferMemory
from langchain_core.documents import Document
from langchain.callbacks.base import BaseCallbackHandler
from langchain.tools import Tool
from config import EMBEDDING_MODEL, AVAILABLE_MODELS
from pdf_engine import modify_pdf_tool_func


# ============================================================
# CALLBACK HANDLER — Captures Agent Thought Process
# ============================================================
class ThoughtCaptureHandler(BaseCallbackHandler):
    def __init__(self):
        self.thoughts = []

    def on_agent_action(self, action, **kwargs):
        self.thoughts.append({
            "type": "action",
            "tool": action.tool,
            "input": str(action.tool_input)[:300],
            "log": action.log.strip()
        })

    def on_agent_finish(self, finish, **kwargs):
        self.thoughts.append({
            "type": "finish",
            "output": finish.return_values.get("output", "")
        })


# ============================================================
# HYBRID RETRIEVER
# ============================================================
def build_retriever(all_chunks: list[Document]):
    """Builds a Hybrid (Semantic + BM25) Retriever."""
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    vectorstore = Chroma.from_documents(
        documents=all_chunks,
        embedding=embeddings,
    )
    chroma_retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

    bm25_retriever = BM25Retriever.from_documents(all_chunks)
    bm25_retriever.k = 5

    return EnsembleRetriever(
        retrievers=[bm25_retriever, chroma_retriever],
        weights=[0.4, 0.6]
    )


# ============================================================
# REACT AGENT
# ============================================================
SYSTEM_PROMPT = """You are DocuMind AI — a context-aware document assistant that can both READ and EDIT documents.
The user has uploaded documents (PDFs, web pages, text notes) into a knowledge base.

ABSOLUTE RULES — NEVER BREAK THESE:
1. You MUST call the knowledge_base_search tool BEFORE answering ANY question. NEVER answer without searching first.
2. Even if the question seems vague (e.g. "tell me about this guy"), you MUST search the knowledge base first. Try broad search terms like "name", "experience", "summary", "skills", "education", "about".
3. If the first search doesn't return useful results, try 2-3 MORE searches with different keywords.
4. Your answers must ONLY come from the knowledge base results. NEVER use your own training data.
5. Cite sources: [PDF: filename, Page X] for PDFs, [WEB: domain] for web pages, [NOTE: title] for text notes.
6. If after 3+ searches you truly cannot find information, tell the user what you searched for and that it wasn't found.
7. Use markdown formatting (headers, bullet points, bold) for readability.

PDF EDITING RULES:
8. When the user asks to CHANGE, EDIT, MODIFY, or UPDATE text in a PDF:
   a. FIRST search the knowledge base to find the EXACT current text.
   b. THEN use the modify_pdf tool with the exact text found and the new replacement text.
   c. Input must be JSON: {"find": "exact old text", "replace": "new text"}
   d. Keep the replacement text reasonable in length — similar to what it replaces.
   e. After successful modification, tell the user they can download the modified PDF.
   f. To REMOVE a word, use {"find": "word to remove", "replace": "-"}

IMPORTANT: The user's documents are YOUR ONLY source of truth. Always search first, then answer or edit."""


def build_agent(retriever):
    """Creates a ReAct Agent with search and PDF editing tools."""
    search_tool = create_retriever_tool(
        retriever,
        "knowledge_base_search",
        "Searches the user's uploaded documents (PDFs, web pages, text notes). "
        "You MUST use this tool for EVERY user question — even simple ones. "
        "Search with different keywords if the first attempt returns nothing useful."
    )

    edit_tool = Tool(
        name="modify_pdf",
        func=modify_pdf_tool_func,
        description=(
            'Modifies the uploaded PDF by finding and replacing text. '
            'Input MUST be JSON: {"find": "exact text to find", "replace": "new text"}. '
            'To REMOVE text, set replace to "-". '
            'IMPORTANT: First use knowledge_base_search to find the EXACT text before modifying. '
            'Only use when the user explicitly asks to change/edit/modify/update/remove something.'
        )
    )

    tools = [search_tool, edit_tool]
    
    selected_model = st.session_state.get("selected_model", AVAILABLE_MODELS[0])
    llm = ChatGroq(model=selected_model, temperature=0)
    
    base_prompt = hub.pull("hwchase17/react-chat")
    prompt = base_prompt.partial(system_message=SYSTEM_PROMPT)
    agent = create_react_agent(llm, tools, prompt)

    if "memory" not in st.session_state:
        st.session_state.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )

    return AgentExecutor(
        agent=agent,
        tools=tools,
        memory=st.session_state.memory,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=8,
        return_intermediate_steps=True
    )


def rebuild_agent():
    """Rebuilds the retriever and agent from accumulated chunks."""
    all_chunks = st.session_state["all_chunks"]
    st.session_state["total_chunks"] = len(all_chunks)
    if not all_chunks:
        return
    if "memory" in st.session_state:
        del st.session_state["memory"]
    retriever = build_retriever(all_chunks)
    st.session_state["agent"] = build_agent(retriever)
    st.session_state["system_ready"] = True
