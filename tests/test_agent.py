import sys
import os
import json
import pytest

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.agent.tools import check_eligibility, get_scheme_details, search_schemes, load_schemes
from src.agent.strands_agent import StrandsAgent
from src.app import lambda_handler

def test_load_schemes():
    schemes = load_schemes()
    assert len(schemes) >= 5
    assert any(s["id"] == "pm_kisan" for s in schemes)

def test_check_eligibility_farmer():
    profile = {
        "age": 35,
        "income": 150000,
        "gender": "male",
        "occupation": "farmer",
        "state": "Uttar Pradesh",
        "category": "General"
    }
    res = check_eligibility(profile)
    assert res["status"] == "success"
    assert res["eligible_count"] > 0
    eligible_ids = [s["id"] for s in res["eligible_schemes"]]
    assert "pm_kisan" in eligible_ids

def test_get_scheme_details():
    details = get_scheme_details("ayushman_bharat")
    assert details["status"] == "success"
    assert details["scheme"]["id"] == "ayushman_bharat"
    assert "apply_link" in details["scheme"]
    assert len(details["scheme"]["documents"]) > 0

def test_search_schemes_text():
    results = search_schemes("health insurance 5 lakh")
    assert len(results) > 0
    assert results[0]["id"] == "ayushman_bharat"

def test_strands_agent_multilingual():
    agent = StrandsAgent()

    # Test English
    res_en = agent.run("Tell me about PM Kisan scheme", lang="en")
    assert res_en["language"] == "en"
    assert "PM Kisan" in res_en["response"] or "pm_kisan" in str(res_en)

    # Test Hindi
    res_hi = agent.run("किसान योजना की पात्रता जांचें", lang="hi", profile={"age": 40, "income": 100000, "occupation": "farmer"})
    assert res_hi["language"] == "hi"
    assert "पात्रता" in res_hi["response"]

    # Test Bengali
    res_bn = agent.run("স্বাস্থ্য বীমা সম্পর্কিত প্রকল্প দেখান", lang="bn")
    assert res_bn["language"] == "bn"
    assert "আয়ুষ্মান" in res_bn["response"] or "প্রকল্প" in res_bn["response"]

def test_lambda_handler_chat_endpoint():
    event = {
        "httpMethod": "POST",
        "path": "/chat",
        "body": json.dumps({"message": "What is Ayushman Bharat?", "language": "en"})
    }
    response = lambda_handler(event, context=None)
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert "response" in body
    assert "Ayushman Bharat" in body["response"]

def test_lambda_handler_check_endpoint():
    event = {
        "httpMethod": "POST",
        "path": "/check",
        "body": json.dumps({
            "profile": {
                "age": 28,
                "income": 200000,
                "gender": "female",
                "occupation": "student",
                "state": "West Bengal",
                "category": "General"
            }
        })
    }
    response = lambda_handler(event, context=None)
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert "eligible_schemes" in body
