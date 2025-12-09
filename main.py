# app.py
import os
from typing import List

import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage

from dotenv import load_dotenv

load_dotenv()

from translator_agent import translate

# --- Basic page config ---
st.set_page_config(
    page_title="Grok Context Translator",
    page_icon="🌍",
    layout="wide",
)

st.title("🌍 Grok Context Translator (Agentic, Context-Aware)")

st.markdown(
    """
Use **xAI Grok** + **LangChain** to translate text with context understanding.

- English ↔ Any language
- Domain-aware (legal, technical, marketing, etc.)
- Keeps context across this session for more consistent terminology.
"""
)

# --- Check API key ---
if "GOOGLE_API_KEY" not in os.environ or not os.environ["GOOGLE_API_KEY"]:
    st.warning(
        "⚠️ `GOOGLE_API_KEY` environment variable is not set. "
        "Set it locally before running, and as a secret when deploying."
    )

# --- Session state for history ---
if "history" not in st.session_state:
    st.session_state.history: List = []

if "last_translation" not in st.session_state:
    st.session_state.last_translation = ""


# --- Sidebar controls ---
st.sidebar.header("Translation Settings")

source_lang = st.sidebar.selectbox(
    "Source language",
    [
        "auto",
        "English",
        "Hindi",
        "French",
        "German",
        "Spanish",
        "Chinese",
        "Japanese",
        "Arabic",
        "Other",
    ],
    index=0,
)

target_lang = st.sidebar.selectbox(
    "Target language",
    [
        "English",
        "Hindi",
        "French",
        "German",
        "Spanish",
        "Chinese",
        "Japanese",
        "Arabic",
        "Other",
    ],
    index=1,
)

if st.sidebar.button("Swap languages"):
    src_tmp = source_lang
    source_lang = target_lang
    target_lang = src_tmp
    st.sidebar.info(f"Swapped: {source_lang} → {target_lang}")

domain = st.sidebar.text_input(
    "Domain / Context (optional)",
    value="general conversation",
    help="e.g. legal contract, software documentation, marketing copy, medical report...",
)

if st.sidebar.button("Clear session context"):
    st.session_state.history = []
    st.session_state.last_translation = ""
    st.sidebar.success("Cleared conversation context.")


# --- Main input area ---
st.subheader("Enter text to translate")

input_text = st.text_area(
    "Text",
    height=200,
    placeholder="Type or paste the text you want to translate...",
)

col1, col2 = st.columns([1, 2])

with col1:
    translate_clicked = st.button("🚀 Translate")

with col2:
    st.write("")  # spacing

if translate_clicked:
    if not input_text.strip():
        st.error("Please enter some text to translate.")
    else:
        with st.spinner("Translating with Grok..."):
            try:
                history_msgs: List = st.session_state.history

                output = translate(
                    text=input_text,
                    source_lang=source_lang,
                    target_lang=target_lang,
                    domain=domain,
                    history=history_msgs,
                )

                # Update history (agentic context)
                history_msgs.append(
                    HumanMessage(
                        content=f"Translate ({source_lang} → {target_lang}, domain={domain}): {input_text}"
                    )
                )
                history_msgs.append(AIMessage(content=output))

                st.session_state.history = history_msgs
                st.session_state.last_translation = output

            except Exception as e:
                st.error(f"Error during translation: {e}")

# --- Show output ---
if st.session_state.last_translation:
    st.subheader("✅ Translation")
    st.write(st.session_state.last_translation)

# --- Show minimal history so user sees context ---
if st.session_state.history:
    with st.expander("Conversation context used by the agent"):
        for msg in st.session_state.history[-6:]:
            role = "👤 User" if isinstance(msg, HumanMessage) else "🤖 Grok"
            st.markdown(f"**{role}:** {msg.content}")
