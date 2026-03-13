#!/usr/bin/python
#
# ShoppingAssistantService - Gemini AI Backend
# Powered by Google Gemini 2.0 Flash (free tier)
#
# ENV VARS:
#   GEMINI_API_KEY   - Your Google AI Studio API key (AIza...)
#   DUMMY_MODE       - "true" to run without Gemini (default: false)
#   PORT             - HTTP port (default: 8080)

import os
import json
import time
import logging
import urllib.request
import urllib.error
from urllib.parse import unquote
from flask import Flask, request, jsonify

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger = logging.getLogger('shoppingassistantservice')

# ─── Configuration ────────────────────────────────────────────────────────────
DUMMY_MODE     = os.environ.get("DUMMY_MODE", "false").lower() == "true"
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL   = "gemini-2.0-flash"

# ─── Compact product catalog (minimizes tokens) ───────────────────────────────
PRODUCTS = "Sunglasses(OLJCESPC7Z,accessories), Tank Top(66VCHSJNUP,clothing), Watch(1YMWWN1N4O,accessories), Loafers(L9ECAV4NIU,footwear), Hairdryer(2ZYFJ3GM2N,hair), Candle Holder(0PUK6V6EV0,home), Salt&Pepper Shakers(LS4PSXUNUM,kitchen), Bamboo Glass Jar(9SIQT8TOJO,kitchen), Mug(6E92ZMYYFZ,kitchen), Vintage Camera(HQTGWGPNH4,electronics)"

# ─── Gemini API Call with retry ───────────────────────────────────────────────

def call_gemini(prompt: str, retries: int = 3) -> str:
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    )
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 300,
        }
    }
    data = json.dumps(payload).encode('utf-8')

    for attempt in range(retries):
        try:
            req = urllib.request.Request(
                url, data=data,
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode('utf-8'))
            candidates = result.get("candidates", [])
            if not candidates:
                raise ValueError("No candidates in response")
            return candidates[0]["content"]["parts"][0]["text"]

        except urllib.error.HTTPError as e:
            body = e.read().decode()
            if e.code == 429:
                # Parse retry delay from response
                wait = 30
                try:
                    err_data = json.loads(body)
                    for detail in err_data.get("error", {}).get("details", []):
                        if "retryDelay" in detail:
                            wait = int(detail["retryDelay"].replace("s", "")) + 2
                            break
                except Exception:
                    pass
                if attempt < retries - 1:
                    logger.warning(f"Rate limited. Waiting {wait}s before retry {attempt+2}/{retries}...")
                    time.sleep(wait)
                    continue
                raise RuntimeError("rate_limited")
            raise

    raise RuntimeError("rate_limited")


def build_prompt(user_message: str) -> str:
    return (
        f"You are a shopping assistant for Online Boutique. "
        f"Products: {PRODUCTS}. "
        f"Customer: {user_message}. "
        f"Reply in 2-3 sentences. Recommend relevant products by name. "
        f"End with: Recommended: [ID1], [ID2]"
    )


# ─── Flask App ────────────────────────────────────────────────────────────────

def create_app():
    app = Flask(__name__)

    @app.route("/", methods=['POST'])
    def talkToAssistant():
        logger.info("Shopping assistant request received")
        body = request.json or {}
        prompt = unquote(body.get('message', ''))

        if DUMMY_MODE:
            return jsonify({'content': f"Demo mode. You asked: '{prompt}'. Set GEMINI_API_KEY to enable AI."})

        if not GEMINI_API_KEY:
            return jsonify({'content': "Shopping assistant not configured. Please set GEMINI_API_KEY."}), 500

        try:
            full_prompt = build_prompt(prompt)
            logger.info(f"Calling Gemini: '{prompt[:50]}'")
            response_text = call_gemini(full_prompt)
            logger.info(f"Gemini responded ({len(response_text)} chars)")
            return jsonify({'content': response_text})

        except RuntimeError as e:
            if "rate_limited" in str(e):
                logger.warning("Rate limit hit after retries")
                return jsonify({'content': "I'm a bit busy right now. Please try again in a moment! 😊"})
            logger.error(f"Error: {e}", exc_info=True)
            return jsonify({'content': "Sorry, I ran into an issue. Please try again!"}), 500

        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            return jsonify({'content': "Sorry, something went wrong. Please try again!"}), 500

    @app.route("/_healthz")
    def health():
        mode = "dummy" if DUMMY_MODE else f"gemini/{GEMINI_MODEL}"
        return jsonify({"status": "ok", "mode": mode}), 200

    return app


if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("PORT", 8080))
    mode = "DUMMY" if DUMMY_MODE else f"GEMINI ({GEMINI_MODEL})"
    logger.info(f"ShoppingAssistantService starting on port {port} | mode={mode}")
    app.run(host='0.0.0.0', port=port)
