# app.py (or main2.py)
import os
from typing import List
import time

import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage

from translator_agent import translate

# -------------------- Setup --------------------
load_dotenv()

# --- Enhanced Page Config ---
st.set_page_config(
    page_title="AI Translation Studio",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for better UI
st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    .translation-box {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 10px 0;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 15px;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .stTextArea textarea {
        border-radius: 10px;
        border: 2px solid #667eea;
    }
    </style>
""", unsafe_allow_html=True)

# --- Title with Animation ---
st.markdown("""
    <h1 style='text-align: center; color: #667eea;'>
        🌐 AI Translation Studio
    </h1>
    <p style='text-align: center; font-size: 18px; color: #666;'>
        Powered by Google Gemini • Context-Aware • Multi-Domain
    </p>
""", unsafe_allow_html=True)

# --- Check API Key ---
if "GOOGLE_API_KEY" not in os.environ or not os.environ["GOOGLE_API_KEY"]:
    st.error("⚠️ `GOOGLE_API_KEY` not set. Please configure it in your .env file.")
    st.stop()

# -------------------- Session State --------------------
if "history" not in st.session_state:
    st.session_state["history"]: List = []
if "last_translation" not in st.session_state:
    st.session_state["last_translation"] = ""
if "last_input" not in st.session_state:
    st.session_state["last_input"] = ""
if "translation_time" not in st.session_state:
    st.session_state["translation_time"] = 0.0
if "translation_count" not in st.session_state:
    st.session_state["translation_count"] = 0
if "favorite_translations" not in st.session_state:
    st.session_state["favorite_translations"] = []
if "translation_mode" not in st.session_state:
    st.session_state["translation_mode"] = "Standard"
if "src_idx" not in st.session_state:
    st.session_state["src_idx"] = 0      # default: Auto-detect
if "tgt_idx" not in st.session_state:
    st.session_state["tgt_idx"] = 1      # default: English

# -------------------- Sidebar --------------------
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/000000/translation.png", width=80)
    st.title("⚙️ Settings")
    
    # Translation Mode Selection
    st.subheader("🎯 Translation Mode")
    translation_mode = st.radio(
        "Select Mode:",
        ["Standard", "Formal", "Casual", "Technical", "Creative"],
        index=["Standard", "Formal", "Casual", "Technical", "Creative"].index(
            st.session_state["translation_mode"]
        ),
        help="Choose the tone and style of translation",
    )
    st.session_state["translation_mode"] = translation_mode
    
    st.divider()
    
    # Language Selection with Flags
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
        "🇮🇹 Italian": "Italian",
        "🇷🇺 Russian": "Russian",
        "🇰🇷 Korean": "Korean",
        "🇵🇹 Portuguese": "Portuguese",
        "🌐 Other": "Other",
    }
    lang_labels = list(language_options.keys())

    # Controlled by indices in session_state (no key conflicts)
    source_label = st.selectbox(
        "From:",
        lang_labels,
        index=st.session_state["src_idx"],
    )
    target_label = st.selectbox(
        "To:",
        lang_labels,
        index=st.session_state["tgt_idx"],
    )

    # Swap just swaps indices
    if st.button("🔄 Swap Languages", use_container_width=True):
        s = st.session_state["src_idx"]
        t = st.session_state["tgt_idx"]
        st.session_state["src_idx"], st.session_state["tgt_idx"] = t, s
        st.experimental_rerun()

    source_lang = language_options[source_label]
    target_lang = language_options[target_label]
    
    st.divider()
    
    # Domain/Context Selection
    st.subheader("📋 Context")
    
    domain_presets = {
        "💬 General": "general conversation",
        "⚖️ Legal": "legal documents and contracts",
        "🏥 Medical": "medical and healthcare",
        "💻 Technical": "software and technology",
        "📱 Marketing": "marketing and advertising",
        "📚 Academic": "academic and research",
        "🎬 Entertainment": "movies and entertainment",
        "📰 News": "news and journalism",
        "✉️ Business": "business communication",
        "🎨 Creative": "creative writing and arts",
    }
    
    selected_preset = st.selectbox(
        "Domain:",
        list(domain_presets.keys()),
        index=0,
    )
    
    domain = domain_presets[selected_preset]
    
    custom_context = st.text_input(
        "Custom context (optional):",
        placeholder="e.g., technical manual, poetry, etc.",
    )
    
    if custom_context:
        domain = custom_context
    
    st.divider()
    
    # Statistics
    st.subheader("📊 Statistics")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Translations", st.session_state["translation_count"])
    with col2:
        st.metric("Favorites", len(st.session_state["favorite_translations"]))
    
    st.divider()
    
    # Actions
    if st.button("🗑️ Clear History", use_container_width=True):
        st.session_state["history"] = []
        st.session_state["last_translation"] = ""
        st.success("History cleared!")
    
    if st.button("🔄 Reset All", use_container_width=True):
        st.session_state.clear()
        st.experimental_rerun()

# -------------------- Main Tabs --------------------
tab1, tab2, tab3, tab4 = st.tabs(["🔤 Translate", "⭐ Favorites", "📜 History", "ℹ️ About"])

# ========== TAB 1: TRANSLATE ==========
with tab1:
    col1, col2 = st.columns(2)
    
    # ---- LEFT: INPUT ----
    with col1:
        st.markdown("### 📝 Input Text")
        input_text = st.text_area(
            "Enter text to translate:",
            height=250,
            placeholder="Type or paste your text here...",
            key="input_text",          # we NEVER assign to this key manually
            label_visibility="collapsed",
        )
        
        # Quick action buttons (no programmatic clear)
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            if st.button("📋 Paste from Clipboard", use_container_width=True):
                st.info("Use Ctrl+V to paste")
        with col_b:
            if st.button("🗑️ Clear (manual)", use_container_width=True):
                st.info("Select the text and press Delete / Backspace.")
        with col_c:
            char_count = len(input_text) if input_text else 0
            st.metric("Characters", char_count)
    
    # ---- RIGHT: OUTPUT / ACTION ----
    with col2:
        st.markdown("### ✨ Translation")
        
        translate_clicked = st.button(
            "🚀 Translate Now",
            use_container_width=True,
            type="primary",
        )

        if translate_clicked:
            # ⭐ This always uses the CURRENT content of the input box
            current_text = input_text

            if not current_text.strip():
                st.error("⚠️ Please enter some text to translate.")
            else:
                with st.spinner("🔄 Translating with AI..."):
                    try:
                        mode_instructions = {
                            "Formal": "Use formal and professional language.",
                            "Casual": "Use casual and conversational language.",
                            "Technical": "Maintain technical terminology and precision.",
                            "Creative": "Be creative and expressive in translation.",
                        }
                        final_domain = domain
                        if translation_mode in mode_instructions:
                            final_domain += f" {mode_instructions[translation_mode]}"

                        start_time = time.time()
                        # NOTE: translator is stateless; no history passed
                        output = translate(
                            text=current_text,
                            source_lang=source_lang,
                            target_lang=target_lang,
                            domain=final_domain,
                        )
                        end_time = time.time()

                        # update UI state
                        st.session_state["last_translation"] = output
                        st.session_state["last_input"] = current_text
                        st.session_state["translation_time"] = end_time - start_time
                        st.session_state["translation_count"] += 1

                        # history just for UI / context display
                        st.session_state["history"].append(
                            HumanMessage(
                                content=f"[{translation_mode}] "
                                        f"{source_lang} → {target_lang}: "
                                        f"{current_text}"
                            )
                        )
                        st.session_state["history"].append(AIMessage(content=output))

                        st.success(
                            f"✅ Translated in {st.session_state['translation_time']:.2f}s"
                        )

                    except Exception as e:
                        st.error(f"❌ Translation error: {e}")

        # Show last translation
        if st.session_state["last_translation"]:
            st.markdown("**Source text used for this translation:**")
            st.code(st.session_state["last_input"])

            st.markdown("**Translation result:**")
            st.text_area(
                "Translation result:",
                value=st.session_state["last_translation"],
                height=250,
                key="output_text",      # we never write to this key
                label_visibility="collapsed",
            )

            # Action buttons
            col_x, col_y, col_z = st.columns(3)
            with col_x:
                if st.button("📋 Copy", use_container_width=True):
                    st.info("Use Ctrl+C to copy the text above")
            with col_y:
                if st.button("⭐ Save to Favorites", use_container_width=True):
                    st.session_state["favorite_translations"].append({
                        "input": st.session_state["last_input"],
                        "output": st.session_state["last_translation"],
                        "from": source_lang,
                        "to": target_lang,
                        "mode": translation_mode,
                        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    })
                    st.success("Saved to favorites!")
            with col_z:
                if st.button("🔁 Use Translation as Input", use_container_width=True):
                    st.info("Copy the translation and paste it into the input box.")

# ========== TAB 2: FAVORITES ==========
with tab2:
    st.markdown("### ⭐ Favorite Translations")
    
    if st.session_state["favorite_translations"]:
        for idx, fav in enumerate(reversed(st.session_state["favorite_translations"])):
            with st.expander(
                f"{fav['from']} → {fav['to']} | {fav['timestamp']}",
                expanded=False,
            ):
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("**Original:**")
                    st.info(fav["input"])
                with c2:
                    st.markdown("**Translation:**")
                    st.success(fav["output"])
                st.caption(f"Mode: {fav['mode']}")
                
                if st.button("🗑️ Remove", key=f"remove_{idx}"):
                    st.session_state["favorite_translations"].remove(fav)
                    st.experimental_rerun()
    else:
        st.info("No favorites yet. Start translating and save your favorites!")

# ========== TAB 3: HISTORY ==========
with tab3:
    st.markdown("### 📜 Translation History")
    
    if st.session_state["history"]:
        st.info(f"Context length: {len(st.session_state['history'])} messages")
        
        for msg in reversed(st.session_state["history"][-20:]):
            if isinstance(msg, HumanMessage):
                st.markdown("**👤 Request:**")
                text = msg.content
                st.text(text[:200] + "..." if len(text) > 200 else text)
            else:
                st.markdown("**🤖 Response:**")
                text = msg.content
                st.success(text[:200] + "..." if len(text) > 200 else text)
            st.divider()
    else:
        st.info("No translation history yet. Start translating!")

# ========== TAB 4: ABOUT ==========
with tab4:
    st.markdown("""
    ### About AI Translation Studio
    
    **Features:**
    - 🤖 Powered by Google Gemini AI
    - 🌍 Support for 12+ languages
    - 🎯 Multiple translation modes (Formal, Casual, Technical, etc.)
    - 📋 10+ domain presets
    - ⭐ Save favorite translations
    - 📜 Maintain history (UI only; model is stateless)
    - 🚀 Fast and accurate
    
    **Tips:**
    - Use domain/context for better accuracy
    - Try different tones (Formal, Casual, Technical)
    - Save good translations to Favorites
    """)

# -------------------- Footer --------------------
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>🌐 AI Translation Studio | Powered by Google Gemini</p>
    <p style='font-size: 12px;'>Each translation uses exactly the current input text box content.</p>
</div>
""", unsafe_allow_html=True)
