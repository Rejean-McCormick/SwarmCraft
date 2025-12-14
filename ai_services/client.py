import os
import json
import logging
import asyncio
import aiohttp
from typing import List, Dict, Any, Optional, Union
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log
)
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- Configuration ---
LLM_API_KEY = os.getenv("LLM_API_KEY")
REQUESTY_API_KEY = os.getenv("REQUESTY_API_KEY")
API_KEY = LLM_API_KEY or REQUESTY_API_KEY

_raw_base_url = os.getenv("LLM_API_BASE_URL")
if REQUESTY_API_KEY and not LLM_API_KEY and _raw_base_url == "https://api.openai.com/v1/chat/completions":
    _raw_base_url = None

BASE_URL_PREFIX = os.getenv("REQUESTY_BASE_URL") or _raw_base_url
if not BASE_URL_PREFIX:
    if REQUESTY_API_KEY and not LLM_API_KEY:
        BASE_URL_PREFIX = "https://router.requesty.ai/v1"
    else:
        BASE_URL_PREFIX = "https://api.openai.com/v1/chat/completions"

if BASE_URL_PREFIX.rstrip("/").endswith("/chat/completions"):
    BASE_URL = BASE_URL_PREFIX
else:
    BASE_URL = f"{BASE_URL_PREFIX.rstrip('/')}/chat/completions"

REQUESTY_HTTP_REFERER = os.getenv("REQUESTY_HTTP_REFERER")
REQUESTY_X_TITLE = os.getenv("REQUESTY_X_TITLE")
ROUTER_DEFAULT_PROVIDER = os.getenv("ROUTER_DEFAULT_PROVIDER", "openai")
MODEL_OVERRIDE = os.getenv("MODEL_OVERRIDE")
REASONING_EFFORT = os.getenv("REQUESTY_REASONING_EFFORT") or os.getenv("REASONING_EFFORT")
GPT5_MIN_MAX_TOKENS = int(os.getenv("GPT5_MIN_MAX_TOKENS", "2000"))
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-4-turbo")
TIMEOUT_SECONDS = int(os.getenv("AI_TIMEOUT", "60"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))

# Setup Logging
logger = logging.getLogger(__name__)

class AIError(Exception):
    """Custom exception for AI Service failures."""
    pass

# --- Response Normalization ---

def _normalize_response(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Converts provider-specific JSON into the standard TextCraft Response Object.
    Ensures the Logic layer always receives a consistent structure.
    """
    try:
        if raw_data.get("error"):
            raise AIError(str(raw_data.get("error")))

        choices = raw_data.get("choices")
        if not choices:
            raise AIError(f"Empty choices in response: {raw_data}")

        choice = choices[0]
        message = choice.get("message", {})
        usage = raw_data.get("usage", {})
        finish_reason = choice.get("finish_reason")

        # Extract content
        content = message.get("content")
        if isinstance(content, list):
            parts = []
            for part in content:
                if isinstance(part, str):
                    parts.append(part)
                elif isinstance(part, dict):
                    if isinstance(part.get("text"), str):
                        parts.append(part["text"])
                    elif isinstance(part.get("content"), str):
                        parts.append(part["content"])
            content = "".join(parts) if parts else None
        elif content is not None and not isinstance(content, str):
            content = str(content)
        
        # Extract tool calls (OpenAI format)
        tool_calls = []
        if message.get("tool_calls"):
            for tc in message["tool_calls"]:
                tool_calls.append({
                    "id": tc.get("id"),
                    "name": tc["function"]["name"],
                    "arguments": json.loads(tc["function"]["arguments"])
                })

        if (content is None or content == "") and not tool_calls:
            choice_text = choice.get("text")
            if isinstance(choice_text, str) and choice_text.strip():
                content = choice_text
            else:
                raw_summary = {
                    "id": raw_data.get("id"),
                    "model": raw_data.get("model"),
                    "finish_reason": finish_reason,
                    "usage": raw_data.get("usage"),
                }
                if finish_reason == "length":
                    raise AIError(
                        "Empty message content with finish_reason='length' (output likely truncated). "
                        f"Response summary: {raw_summary}"
                    )
                raise AIError(f"Empty message content in response. Response summary: {raw_summary}")

        return {
            "status": "success",
            "data": {
                "content": content,
                "tool_calls": tool_calls,
                "finish_reason": finish_reason
            },
            "usage": {
                "prompt_tokens": usage.get("prompt_tokens", 0),
                "completion_tokens": usage.get("completion_tokens", 0),
                "total_tokens": usage.get("total_tokens", 0)
            }
        }

    except Exception as e:
        logger.error(f"Failed to normalize response: {e} | Raw Data: {raw_data}")
        raise AIError(f"Response normalization failed: {str(e)}")

# --- The Brain Gateway ---

@retry(
    stop=stop_after_attempt(MAX_RETRIES),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((aiohttp.ClientError, asyncio.TimeoutError, AIError)),
    before_sleep=before_sleep_log(logger, logging.WARNING)
)
async def generate(
    messages: List[Dict[str, str]],
    model: str = DEFAULT_MODEL,
    tools: Optional[List[Dict]] = None,
    temperature: float = 0.7,
    max_tokens: int = 2000
) -> Dict[str, Any]:
    """
    The primary entry point for AI generation.
    
    Args:
        messages: List of {"role": "...", "content": "..."} dicts.
        model: Target model ID.
        tools: List of JSON Schema tool definitions.
        temperature: Creativity parameter (0.0 to 1.0).
        max_tokens: Output length limit.

    Returns:
        Standardized Response Object (Dict).
    """
    if not API_KEY:
        logger.critical("No API key found (LLM_API_KEY or REQUESTY_API_KEY).")
        return {"status": "error", "message": "Missing API Key configuration."}

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    if REQUESTY_HTTP_REFERER:
        headers["HTTP-Referer"] = REQUESTY_HTTP_REFERER
    if REQUESTY_X_TITLE:
        headers["X-Title"] = REQUESTY_X_TITLE

    effective_model = MODEL_OVERRIDE or model
    base_prefix_lc = (BASE_URL_PREFIX or "").lower()
    if "/" not in effective_model and ("router.requesty.ai" in base_prefix_lc or "openrouter.ai" in base_prefix_lc):
        effective_model = f"{ROUTER_DEFAULT_PROVIDER}/{effective_model}"

    effective_max_tokens = max_tokens
    effective_model_lc = (effective_model or "").lower()
    is_requesty_router = "router.requesty.ai" in base_prefix_lc
    is_gpt5 = "gpt-5" in effective_model_lc
    if is_gpt5 and effective_max_tokens < GPT5_MIN_MAX_TOKENS:
        effective_max_tokens = GPT5_MIN_MAX_TOKENS

    payload = {
        "model": effective_model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": effective_max_tokens
    }

    if is_requesty_router and is_gpt5 and not REASONING_EFFORT:
        payload["reasoning_effort"] = "low"
    elif is_requesty_router and REASONING_EFFORT:
        payload["reasoning_effort"] = REASONING_EFFORT

    if tools:
        payload["tools"] = tools
        payload["tool_choice"] = "auto"

    # Use aiohttp for async, non-blocking I/O
    async with aiohttp.ClientSession() as session:
        try:
            logger.info(f"Sending request to Brain: {effective_model} (Tools: {len(tools) if tools else 0}) - Effective Model: {payload['model']}")
            
            async with session.post(
                BASE_URL, 
                headers=headers, 
                json=payload, 
                timeout=aiohttp.ClientTimeout(total=TIMEOUT_SECONDS)
            ) as response:
                
                # Handle HTTP Errors
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"AI API Error {response.status}: {error_text}")
                    
                    # Raise for retry if it's a server error or rate limit
                    if response.status in [429, 500, 502, 503, 504]:
                        raise AIError(f"Upstream Error {response.status}")
                    
                    return {"status": "error", "message": f"Provider Error: {error_text}"}

                # Success
                raw_data = await response.json()
                return _normalize_response(raw_data)

        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            logger.warning(f"Network error interacting with AI: {e}")
            raise # Trigger Tenacity retry
        except AIError as e:
            logger.warning(f"AI response error: {e}")
            raise
        except Exception as e:
            logger.exception(f"Unexpected error in AI Client: {e}")
            return {"status": "error", "message": str(e)}