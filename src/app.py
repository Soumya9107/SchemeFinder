import json
import logging
from typing import Dict, Any
from src.agent.strands_agent import StrandsAgent
from src.agent.tools import load_schemes, check_eligibility, get_scheme_details, search_schemes

# Setup logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

agent = StrandsAgent()

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
    "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
    "Content-Type": "application/json"
}

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler function invoked by SAM CLI or API Gateway.
    """
    http_method = event.get("httpMethod") or event.get("requestContext", {}).get("http", {}).get("method", "POST")
    path = event.get("path") or event.get("rawPath", "/chat")

    if http_method == "OPTIONS":
        return {
            "statusCode": 200,
            "headers": CORS_HEADERS,
            "body": json.dumps({"status": "ok"})
        }

    try:
        # Route 1: GET /schemes
        if http_method == "GET" and "/schemes" in path:
            schemes = load_schemes()
            return {
                "statusCode": 200,
                "headers": CORS_HEADERS,
                "body": json.dumps({"status": "success", "count": len(schemes), "schemes": schemes}, ensure_ascii=False)
            }

        # Parse request body for POST endpoints
        body_raw = event.get("body", "{}")
        if isinstance(body_raw, str):
            try:
                body = json.loads(body_raw) if body_raw else {}
            except Exception:
                body = {}
        else:
            body = body_raw or {}

        # Route 2: POST /check (Direct eligibility questionnaire)
        if "/check" in path:
            profile = body.get("profile", body)
            res = check_eligibility(profile)
            return {
                "statusCode": 200,
                "headers": CORS_HEADERS,
                "body": json.dumps(res, ensure_ascii=False)
            }

        # Route 3: POST /chat (Default Strands Agent conversational interface)
        message = body.get("message", "").strip()
        lang = body.get("language", body.get("lang", "en")).strip()
        profile = body.get("profile", {})

        if not message and profile:
            message = "Check my eligibility based on my profile."

        if not message:
            return {
                "statusCode": 400,
                "headers": CORS_HEADERS,
                "body": json.dumps({"error": "Message parameter is required."}, ensure_ascii=False)
            }

        agent_result = agent.run(message=message, lang=lang, profile=profile)

        return {
            "statusCode": 200,
            "headers": CORS_HEADERS,
            "body": json.dumps(agent_result, ensure_ascii=False)
        }

    except Exception as e:
        logger.error(f"Error handling request: {e}", exc_info=True)
        return {
            "statusCode": 500,
            "headers": CORS_HEADERS,
            "body": json.dumps({"error": str(e)}, ensure_ascii=False)
        }
