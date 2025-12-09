# app.py
import os
import time

import streamlit as st
from dotenv import load_dotenv

from translator_agent import translate

# ----------------------
# Setup
# ----------------------
load_dotenv()

st.set_page_config(
    page_title="AI Translation Studio",
    page_icon="🌐",
    layout="wide",
)

st.markdown(
    "<h2 style='text-align:center;'>🌐 AI Translation Studio</h2>"
    "<p style='text-align:center;'>Powered by Groq • Stateless Translation</p>",
    unsafe_allow_html=True,
)

# --- Check API Key ---
if "GOOGLE_API_KEY" not in os.environ or not os.environ["GOOGLE_API_KEY"]:
    st.error("⚠️ `GOOGLE_API_KEY` not set. Please configure it in your .env file.")
    st.stop()

# ----------------------
# Sidebar: Settings
# ----------------------
with st.sidebar:
    st.header("⚙️ Settings")

    # Languages
    st.subheader("🌍 Languages")
    language_options = {
        "🔄 Auto-detect": "auto",
        "🇺🇸 English": "English",
        "🇮🇳 Hindi": "Hindi",
        "🇫🇷 French": "French",
        "🇩🇪 German": "German",
        "🇪🇸 Spanish": "Spanish",
        "🇨🇳 Chinese": "Chinese",
        "🇯🇵 Japanese": "Japanese",
        "🇸🇦 Arabic": "Arabic",
        "🌐 Other": "Other",
    }
    lang_labels = list(language_options.keys())

    source_label = st.selectbox("From", lang_labels, index=0)
    target_label = st.selectbox("To",   lang_labels, index=1)

    source_lang = language_options[source_label]
    target_lang = language_options[target_label]

    st.subheader("📋 Context / Domain")
    domain = st.text_input(
        "Domain (optional)",
        value="general conversation",
        placeholder="e.g. legal contract, technical documentation, marketing copy...",
    )

# ----------------------
# Main Layout
# ----------------------
col1, col2 = st.columns(2)

# Left: Input
with col1:
    st.markdown("### 📝 Input Text")
    input_text = st.text_area(
        "Enter text to translate:",
        key="input_text_field",        # IMPORTANT: we only READ this from session_state
        height=250,
        label_visibility="collapsed",
        placeholder="Type or paste text here...",
    )
    st.caption("To clear: select all and delete (Ctrl + A → Del).")

# Right: Translation
with col2:
    st.markdown("### ✨ Translation")

    translate_clicked = st.button("🚀 Translate Now", use_container_width=True)

    # A container to show messages + output
    status_container = st.empty()
    output_container = st.empty()

    if translate_clicked:
        # ⭐ ALWAYS read the latest content from the text area using session_state
        text_to_translate = st.session_state["input_text_field"]

        if not text_to_translate.strip():
            status_container.error("⚠️ Please enter some text to translate.")
        else:
            with status_container, st.spinner("🔄 Translating with AI..."):
                start = time.time()
                try:
                    result = translate(
                        text=text_to_translate,
                        source_lang=source_lang,
                        target_lang=target_lang,
                        domain=domain,
                    )
                    elapsed = time.time() - start

                    st.success(f"✅ Translated in {elapsed:.2f}s")

                    # Show what text was actually used
                    st.markdown("**Source text used for this translation:**")
                    st.code(text_to_translate)

                    st.markdown("**Translation result:**")
                    output_container.text_area(
                        "Result:",
                        value=result,
                        height=250,
                        label_visibility="collapsed",
                    )
                except Exception as e:
                    status_container.error(f"❌ Error during translation: {e}")
                    output_container.empty()
    else:
        # If button not clicked yet, but you still want a box reserved:
        output_container.text_area(
            "Result:",
            value="",
            height=250,
            label_visibility="collapsed",
        )

# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align:center; font-size:12px; color:#666;'>"
    "Developed: Rajesh Hugar "
    "Version 0.1</p>",
    unsafe_allow_html=True,
)
