# translator_agent.py
from typing import Optional
import os

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq



def build_translation_chain():
    """Create a stateless, context-aware translation chain using Google Gemini."""
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",   # or "gemini-1.5-flash" for cheaper/faster
        temperature=0.2,
       api_key= os.getenv("GROQ_API_KEY")
    )

    system_prompt = """
You are a professional, context-aware translation AGENT.

Goals:
- Translate the given text from the source language to the target language.
- Preserve meaning, tone, and technical details.
- Use the provided domain/context (e.g., legal, medical, software, marketing) to choose correct terminology.
- If source language is "auto", detect it yourself.
- Do NOT explain the translation or add commentary.
- Output ONLY the translated text.
"""

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            (
                "human",
                """
Source language: {source_lang}
Target language: {target_lang}
Domain / Context: {domain}

Text to translate:
```text
{text}
```""",
            ),
        ]
    )

    chain = prompt | llm | StrOutputParser()
    return chain


def translate(
    text: str,
    source_lang: str,
    target_lang: str,
    domain: Optional[str],
) -> str:
    """Stateless translation (no history / memory used)."""
    if not domain or not domain.strip():
        domain = "general"

    chain = build_translation_chain()
    output = chain.invoke(
        {
            "source_lang": source_lang,
            "target_lang": target_lang,
            "domain": domain,
            "text": text,
        }
    )
    return output
