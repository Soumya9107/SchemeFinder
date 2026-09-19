import re
import logging
from typing import Dict, Any, List
from src.agent.tools import check_eligibility, get_scheme_details, search_schemes, load_schemes

logger = logging.getLogger("scheme_finder.local_engine")

class LocalRuleAgentEngine:
    """
    Built-in deterministic NLP & reasoning engine for SchemeFinder.
    Executes tool calling and constructs multilingual responses without external LLM dependencies.
    """

    def process_message(self, user_message: str, lang: str = "en", profile: Dict[str, Any] = None) -> Dict[str, Any]:
        user_message_clean = user_message.strip()
        lang = lang.lower() if lang in ["en", "hi", "bn"] else "en"
        user_profile = profile or {}

        # Extract demographic parameters from user message if available
        extracted_params = self._extract_parameters(user_message_clean)
        merged_profile = {**user_profile, **extracted_params}

        # Intent detection logic
        intent = self._detect_intent(user_message_clean)

        if intent == "check_eligibility" or merged_profile.get("age") or merged_profile.get("income"):
            res = check_eligibility(merged_profile)
            text_reply = self._format_eligibility_response(res, lang, merged_profile)
            return {
                "response": text_reply,
                "intent": "check_eligibility",
                "tool_used": "check_eligibility",
                "data": res,
                "language": lang
            }

        elif intent == "get_details":
            scheme_id = self._extract_scheme_id(user_message_clean)
            if scheme_id:
                details = get_scheme_details(scheme_id)
                text_reply = self._format_details_response(details, lang)
                return {
                    "response": text_reply,
                    "intent": "get_scheme_details",
                    "tool_used": "get_scheme_details",
                    "data": details,
                    "language": lang
                }

        # Default: Free-text Search across schemes
        matched_schemes = search_schemes(user_message_clean)
        text_reply = self._format_search_response(matched_schemes, user_message_clean, lang)
        return {
            "response": text_reply,
            "intent": "search_schemes",
            "tool_used": "search_schemes",
            "data": {"results": matched_schemes},
            "language": lang
        }

    def _extract_parameters(self, text: str) -> Dict[str, Any]:
        extracted = {}
        text_lower = text.lower()

        # Extract Age (e.g., "25 years old", "age 30", "30 saal", "25 বছর")
        age_match = re.search(r'\b(age\s*is\s*|age\s*|i am\s*|im\s*)?(\d{1,2})\s*(years|yr|yrs|saal|sal|বছর)?\b', text_lower)
        if age_match:
            try:
                val = int(age_match.group(2))
                if 5 <= val <= 100:
                    extracted["age"] = val
            except ValueError:
                pass

        # Extract Income (e.g. "income 200000", "2 lakh", "1.5 lakhs", "200000 rs", "২০ হাজার")
        lakh_match = re.search(r'(\d+(?:\.\d+)?)\s*(lakh|lakhs|lac|lacs|लाख|লক্ষ)', text_lower)
        if lakh_match:
            try:
                extracted["income"] = float(lakh_match.group(1)) * 100000
            except ValueError:
                pass
        else:
            inc_match = re.search(r'(income|salary|earning|कमाई|आय)\s*(?:is|of|=|:)?\s*₹?\s*(\d{4,8})', text_lower)
            if inc_match:
                try:
                    extracted["income"] = float(inc_match.group(2))
                except ValueError:
                    pass

        # Extract Gender
        if any(w in text_lower for w in ["female", "woman", "girl", "महिला", "लड़की", "নারী", "মহিলা"]):
            extracted["gender"] = "female"
        elif any(w in text_lower for w in ["male", "man", "boy", "पुरुष", "पुरुष", "পুরুষ"]):
            extracted["gender"] = "male"

        # Extract Occupation
        if any(w in text_lower for w in ["farmer", "kisan", "agriculture", "किसान", "কৃষক"]):
            extracted["occupation"] = "farmer"
        elif any(w in text_lower for w in ["student", "study", "college", "school", "छात्र", "छात्रवृत्ति", "ছাত্র", "ছাত্রী"]):
            extracted["occupation"] = "student"
        elif any(w in text_lower for w in ["vendor", "shopkeeper", "hawker", "रेहड़ी", "दुकानदार", "হকার", "দোকানদার"]):
            extracted["occupation"] = "vendor"

        # Extract State
        if any(w in text_lower for w in ["west bengal", "wb", "bengal", "पश्चिम बंगाल", "পশ্চিমবঙ্গ"]):
            extracted["state"] = "West Bengal"

        return extracted

    def _detect_intent(self, text: str) -> str:
        text_lower = text.lower()

        if any(w in text_lower for w in ["eligible", "eligibility", "check my", "am i eligible", "पात्रता", "योग्य", "যোগ্যता", "যোগ্য"]):
            return "check_eligibility"

        if any(w in text_lower for w in ["how to apply", "apply link", "documents required", "details", "दस्तावेज़", "आवेदन", "আবেদন", "নথি पत्र"]):
            return "get_details"

        return "search"

    def _extract_scheme_id(self, text: str) -> str:
        all_schemes = load_schemes()
        text_lower = text.lower()
        for scheme in all_schemes:
            if scheme["id"] in text_lower:
                return scheme["id"]
            for lang, name in scheme["name"].items():
                if name.lower() in text_lower or any(word in text_lower for word in name.lower().split() if len(word) > 3):
                    return scheme["id"]
        return ""

    def _format_eligibility_response(self, res: Dict[str, Any], lang: str, profile: Dict[str, Any]) -> str:
        eligible = res.get("eligible_schemes", [])
        ineligible = res.get("ineligible_schemes", [])

        if lang == "hi":
            msg = f"🔍 **आपकी प्रोफाइल के आधार पर पात्रता परिणाम:**\n\n"
            if eligible:
                msg += f"✅ **आप {len(eligible)} योजनाओं के लिए पात्र हैं:**\n"
                for s in eligible:
                    name = s['name'].get('hi', s['name']['en'])
                    msg += f"• **{name}**: {s['objective'].get('hi', s['objective']['en'])}\n  🔗 **आवेदन लिंक:** [{s['apply_link']}]({s['apply_link']})\n\n"
            else:
                msg += "❌ आपके द्वारा दर्ज मानदंडों से कोई योजना सीधे मेल नहीं खाती।\n\n"
            if ineligible:
                msg += f"ℹ️ **अन्य योजनाएं जिन्हें आप देख सकते हैं ({len(ineligible)}):**\n"
                for s in ineligible[:3]:
                    name = s['name'].get('hi', s['name']['en'])
                    reasons = "; ".join(s.get('reasons', []))
                    msg += f"• {name} (कारण: {reasons})\n"
            return msg

        elif lang == "bn":
            msg = f"🔍 **আপনার প্রোফাইলের ওপর ভিত্তি করে যোগ্যতার ফলাফল:**\n\n"
            if eligible:
                msg += f"✅ **আপনি {len(eligible)}টি প্রকল্পের জন্য যোগ্য:**\n"
                for s in eligible:
                    name = s['name'].get('bn', s['name']['en'])
                    msg += f"• **{name}**: {s['objective'].get('bn', s['objective']['en'])}\n  🔗 **আবেদনের লিঙ্ক:** [{s['apply_link']}]({s['apply_link']})\n\n"
            else:
                msg += "❌ আপনার প্রদান করা তথ্যের সাথে সরাসরি কোনো প্রকল্প মিলছে না।\n\n"
            if ineligible:
                msg += f"ℹ️ **অন্যান্য প্রকল্পগুলি পরীক্ষা করে দেখুন ({len(ineligible)}টি):**\n"
                for s in ineligible[:3]:
                    name = s['name'].get('bn', s['name']['en'])
                    reasons = "; ".join(s.get('reasons', []))
                    msg += f"• {name} (কারণ: {reasons})\n"
            return msg

        else: # English
            msg = f"🔍 **Eligibility Check Results based on your profile:**\n\n"
            if eligible:
                msg += f"✅ **You qualify for {len(eligible)} scheme(s):**\n"
                for s in eligible:
                    name = s['name'].get('en')
                    msg += f"• **{name}**: {s['objective'].get('en')}\n  🔗 **Apply Here:** [{s['apply_link']}]({s['apply_link']})\n\n"
            else:
                msg += "❌ No schemes directly matched the profile entered.\n\n"
            if ineligible:
                msg += f"ℹ️ **Other available schemes ({len(ineligible)} evaluated):**\n"
                for s in ineligible[:3]:
                    name = s['name'].get('en')
                    reasons = "; ".join(s.get('reasons', []))
                    msg += f"• {name} (Note: {reasons})\n"
            return msg

    def _format_details_response(self, details: Dict[str, Any], lang: str) -> str:
        if details.get("status") != "success":
            return f"❌ {details.get('message', 'Scheme details not found.')}"

        s = details["scheme"]
        name = s["name"].get(lang, s["name"]["en"])
        obj = s["objective"].get(lang, s["objective"]["en"])
        ben = s["benefits"].get(lang, s["benefits"]["en"])
        docs = s.get("documents", [])
        link = s.get("apply_link", "#")

        if lang == "hi":
            return (
                f"📋 **योजना विवरण: {name}**\n\n"
                f"🎯 **उद्देश्य:** {obj}\n\n"
                f"💰 **लाभ:** {ben}\n\n"
                f"📄 **आवश्यक दस्तावेज़:**\n" + "\n".join([f"  • {d}" for d in docs]) + "\n\n"
                f"🌐 **आधिकारिक आवेदन पोर्टल:** [{link}]({link})"
            )
        elif lang == "bn":
            return (
                f"📋 **প্রকল্পের বিবরণ: {name}**\n\n"
                f"🎯 **উদ্দেশ্য:** {obj}\n\n"
                f"💰 **সুবিধা:** {ben}\n\n"
                f"📄 **প্রয়োজনীয় কাগজপত্র:**\n" + "\n".join([f"  • {d}" for d in docs]) + "\n\n"
                f"🌐 **অফিসিয়াল আবেদনের পোর্টাল:** [{link}]({link})"
            )
        else:
            return (
                f"📋 **Scheme Details: {name}**\n\n"
                f"🎯 **Objective:** {obj}\n\n"
                f"💰 **Key Benefits:** {ben}\n\n"
                f"📄 **Required Documents:**\n" + "\n".join([f"  • {d}" for d in docs]) + "\n\n"
                f"🌐 **Official Application Portal:** [{link}]({link})"
            )

    def _format_search_response(self, results: List[Dict[str, Any]], query: str, lang: str) -> str:
        if not results:
            if lang == "hi":
                return f"❌ '{query}' से संबंधित कोई योजना नहीं मिली। कृपया कोई अन्य खोज शब्द आज़माएं।"
            elif lang == "bn":
                return f"❌ '{query}' সংক্রান্ত কোনো প্রকল্প পাওয়া যায়নি। অনুগ্রহ করে অন্য কোনো কিওয়ার্ড চেষ্টা করুন।"
            else:
                return f"❌ No schemes matching '{query}' were found. Try searching for terms like 'farmer', 'health', 'student', or 'loan'."

        if lang == "hi":
            msg = f"🔎 **'{query}' के लिए पाए गए परिणाम ({len(results)} योजनाएं):**\n\n"
            for s in results[:4]:
                name = s["name"].get("hi", s["name"]["en"])
                obj = s["objective"].get("hi", s["objective"]["en"])
                msg += f"• **{name}** ({s['category']})\n  {obj}\n  🔗 **आवेदन करें:** [{s['apply_link']}]({s['apply_link']})\n\n"
            return msg
        elif lang == "bn":
            msg = f"🔎 **'{query}' সংক্রান্ত অনুসন্ধানের ফলাফল ({len(results)}টি প্রকল্প):**\n\n"
            for s in results[:4]:
                name = s["name"].get("bn", s["name"]["en"])
                obj = s["objective"].get("bn", s["objective"]["en"])
                msg += f"• **{name}** ({s['category']})\n  {obj}\n  🔗 **আবেদন করুন:** [{s['apply_link']}]({s['apply_link']})\n\n"
            return msg
        else:
            msg = f"🔎 **Found {len(results)} scheme(s) matching '{query}':**\n\n"
            for s in results[:4]:
                name = s["name"].get("en")
                obj = s["objective"].get("en")
                msg += f"• **{name}** ({s['category']})\n  {obj}\n  🔗 **Apply Here:** [{s['apply_link']}]({s['apply_link']})\n\n"
            return msg
