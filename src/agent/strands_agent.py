import logging
from typing import Dict, Any
from src.agent.local_engine import LocalRuleAgentEngine
from src.agent.llm_adapter import CloudLLMAdapter

logger = logging.getLogger("scheme_finder.strands_agent")

class StrandsAgent:
    """
    Strands Agent orchestrator for SchemeFinder.
    
    Executes tool calling (`check_eligibility`, `get_scheme_details`, `search_schemes`)
    and utilizes either the built-in local NLP engine or an optional Cloud LLM provider
    (Google Gemini / Groq / OpenAI) if an API key is supplied.
    """

    def __init__(self):
        self.local_engine = LocalRuleAgentEngine()
        self.cloud_llm = CloudLLMAdapter()

    def run(self, message: str, lang: str = "en", profile: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process incoming user chat message or eligibility questionnaire payload.
        """
        logger.info(f"Processing message in language '{lang}': '{message}'")
        
        # Execute tool calls and generate baseline output with local engine
        result = self.local_engine.process_message(message, lang=lang, profile=profile)

        # If Cloud LLM API key is present, enhance the natural language response
        if self.cloud_llm.is_available():
            cloud_reply = self.cloud_llm.generate_response(
                user_message=message,
                lang=lang,
                tool_data=result.get("data", {}),
                intent=result.get("intent", "search")
            )
            if cloud_reply:
                result["response"] = cloud_reply
                result["llm_provider"] = "cloud_api"
            else:
                result["llm_provider"] = "local_engine"
        else:
            result["llm_provider"] = "local_engine"

        return result
