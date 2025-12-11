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
API_KEY = os.getenv("LLM_API_KEY")
BASE_URL = os.getenv("LLM_API_BASE_URL", "https://api.openai.com/v1/chat/completions")
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
        choice = raw_data.get("choices", [{}])[0]
        message = choice.get("message", {})
        usage = raw_data.get("usage", {})

        # Extract content
        content = message.get("content")
        
        # Extract tool calls (OpenAI format)
        tool_calls = []
        if message.get("tool_calls"):
            for tc in message["tool_calls"]:
                tool_calls.append({
                    "id": tc.get("id"),
                    "name": tc["function"]["name"],
                    "arguments": json.loads(tc["function"]["arguments"])
                })

        return {
            "status": "success",
            "data": {
                "content": content,
                "tool_calls": tool_calls,
                "finish_reason": choice.get("finish_reason")
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
        logger.critical("LLM_API_KEY not found in environment variables.")
        return {"status": "error", "message": "Missing API Key configuration."}

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens
    }

    if tools:
        payload["tools"] = tools
        payload["tool_choice"] = "auto"

    # Use aiohttp for async, non-blocking I/O
    async with aiohttp.ClientSession() as session:
        try:
            logger.info(f"Sending request to Brain: {model} (Tools: {len(tools) if tools else 0})")
            
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
        except Exception as e:
            logger.exception(f"Unexpected error in AI Client: {e}")
            return {"status": "error", "message": str(e)}