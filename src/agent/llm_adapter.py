import os
import json
import logging
import urllib.request
import urllib.error
from typing import Dict, Any, Optional

logger = logging.getLogger("scheme_finder.llm_adapter")

class CloudLLMAdapter:
    """
    Adapter for Cloud LLM APIs (Google Gemini, Groq, OpenAI).
    Activated whenever an API key is provided in environment variables.
    """

    def __init__(self):
        self.gemini_key = os.environ.get("GEMINI_API_KEY")
        self.groq_key = os.environ.get("GROQ_API_KEY")
        self.openai_key = os.environ.get("OPENAI_API_KEY")

    def is_available(self) -> bool:
        return bool(self.gemini_key or self.groq_key or self.openai_key)

    def generate_response(self, user_message: str, lang: str, tool_data: Dict[str, Any], intent: str) -> Optional[str]:
        if not self.is_available():
            return None

        prompt = self._build_prompt(user_message, lang, tool_data, intent)

        if self.gemini_key:
            return self._call_gemini(prompt)
        elif self.groq_key:
            return self._call_groq(prompt)
        elif self.openai_key:
            return self._call_openai(prompt)

        return None

    def _build_prompt(self, user_message: str, lang: str, tool_data: Dict[str, Any], intent: str) -> str:
        lang_names = {"en": "English", "hi": "Hindi", "bn": "Bengali"}
        target_lang = lang_names.get(lang.lower(), "English")

        return f"""You are SchemeFinder AI, an empathetic and highly accurate government scheme assistant for India.

Target Language: {target_lang}
User Query: "{user_message}"
Intent: {intent}

Tool Execution Data (Source of Truth):
{json.dumps(tool_data, indent=2, ensure_ascii=False)}

Instructions:
1. Respond exclusively in {target_lang}.
2. Synthesize the tool execution data cleanly and accurately.
3. Highlight eligible scheme names, key benefits, required documents, and official application URLs (apply_link).
4. Use clean Markdown formatting with bullet points and emojis.
"""

    def _call_gemini(self, prompt: str) -> Optional[str]:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_key}"
            payload = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }]
            }
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=data,
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                res_data = json.loads(resp.read().decode("utf-8"))
                candidates = res_data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts:
                        return parts[0].get("text")
        except Exception as e:
            logger.warning(f"Gemini API call failed: {e}")
        return None

    def _call_groq(self, prompt: str) -> Optional[str]:
        try:
            url = "https://api.groq.com/openai/v1/chat/completions"
            payload = {
                "model": "llama-3.1-8b-instant",
                "messages": [{"role": "user", "content": prompt}]
            }
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=data,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.groq_key}"
                },
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                res_data = json.loads(resp.read().decode("utf-8"))
                choices = res_data.get("choices", [])
                if choices:
                    return choices[0].get("message", {}).get("content")
        except Exception as e:
            logger.warning(f"Groq API call failed: {e}")
        return None

    def _call_openai(self, prompt: str) -> Optional[str]:
        try:
            url = "https://api.openai.com/v1/chat/completions"
            payload = {
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": prompt}]
            }
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=data,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.openai_key}"
                },
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                res_data = json.loads(resp.read().decode("utf-8"))
                choices = res_data.get("choices", [])
                if choices:
                    return choices[0].get("message", {}).get("content")
        except Exception as e:
            logger.warning(f"OpenAI API call failed: {e}")
        return None
