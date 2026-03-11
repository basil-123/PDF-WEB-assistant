"""
DocuMind AI — Main Entrypoint
"""
import streamlit as st

# Import layout elements early if needed
from config import APP_TITLE, APP_ICON, APP_PASSWORD
from styles import CUSTOM_CSS
from ui_components import (
    init_session,
    render_sidebar,
    render_hero,
    render_welcome,
    render_stats,
    render_source_badges,
    render_agent_thoughts
)
from rag_engine import ThoughtCaptureHandler


def main():
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon=APP_ICON,
        layout="wide",
        initial_sidebar_state="expanded"
    )

    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    init_session()

    if APP_PASSWORD and not st.session_state.get("authenticated", False):
        st.markdown("<div style='max-width: 400px; margin: 100px auto; padding: 30px; border-radius: 12px; background: rgba(30,30,40,0.8); border: 1px solid rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='text-align:center;'>{APP_ICON} {APP_TITLE}</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; color: #a1a1aa;'>This application is password protected.</p>", unsafe_allow_html=True)
        pwd = st.text_input("Password", type="password", label_visibility="collapsed", placeholder="Enter Password")
        if st.button("Unlock 🔓", use_container_width=True):
            if pwd == APP_PASSWORD:
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("Incorrect password.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    render_sidebar()

    # --- Main Content Area ---
    render_hero()

    if st.session_state["system_ready"]:
        render_stats()
        render_source_badges()

        st.markdown("---")

        # Display existing chat
        for i, msg in enumerate(st.session_state["messages"]):
            with st.chat_message(msg["role"], avatar="🧑‍💻" if msg["role"] == "user" else "🧠"):
                st.markdown(msg["content"])
                if msg.get("thoughts"):
                    render_agent_thoughts(msg["thoughts"])
                # Re-render download button for past messages that had PDF edits
                if msg.get("has_download") and msg["role"] == "assistant":
                    pdf_store = st.session_state.get("pdf_bytes_store", {})
                    if pdf_store:
                        latest_name = list(pdf_store.keys())[0]
                        st.download_button(
                            label="📥 Download Modified PDF",
                            data=pdf_store[latest_name],
                            file_name=f"modified_{latest_name}",
                            mime="application/pdf",
                            key=f"dl_history_{i}"
                        )

        # Chat Input
        if prompt := st.chat_input("Ask anything about your knowledge base..."):
            # User message
            st.chat_message("user", avatar="🧑‍💻").markdown(prompt)
            st.session_state["messages"].append({"role": "user", "content": prompt})

            # Agent response
            with st.chat_message("assistant", avatar="🧠"):
                with st.spinner("🧠 DocuMind is reasoning..."):
                    try:
                        thought_handler = ThoughtCaptureHandler()
                        response = st.session_state["agent"].invoke(
                            {"input": prompt},
                            {"callbacks": [thought_handler]}
                        )
                        answer = response["output"]
                        intermediate = response.get("intermediate_steps", [])

                        st.markdown(answer)
                        render_agent_thoughts(intermediate)

                        # Check if a PDF was modified — show download button
                        modified = st.session_state.get("modified_pdf")
                        if modified:
                            st.download_button(
                                label="📥 Download Modified PDF",
                                data=modified["bytes"],
                                file_name=modified["name"],
                                mime="application/pdf",
                                key=f"dl_{st.session_state['query_count']}"
                            )

                        st.session_state["messages"].append({
                            "role": "assistant",
                            "content": answer,
                            "thoughts": intermediate,
                            "has_download": bool(modified)
                        })
                        st.session_state["query_count"] += 1
                        # Clear the modified flag so it doesn't re-show
                        if "modified_pdf" in st.session_state:
                            st.session_state.pop("modified_pdf", None)

                    except Exception as e:
                        error_msg = str(e).lower()
                        if "rate limit" in error_msg or "429" in error_msg:
                            st.warning(
                                "⚠️ **Rate Limit Reached!**\n\n"
                                "The current AI model has reached its usage limit on your Groq API key.\n\n"
                                "**Please expand the '⚙️ Settings' section in the sidebar and select a different AI Model to continue.**"
                            )
                        else:
                            st.error(f"Agent error: {e}")
        render_welcome()


if __name__ == "__main__":
    main()
