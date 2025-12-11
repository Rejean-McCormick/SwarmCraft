# TextCraft AI Client Specification (`ai_services/client.py`)

**Version:** 2.1.0 (Refactored for Specialized Services)
**Status:** Core Definition
**Role:** The Intelligence Gateway (The Brain)

-----

## 1\. Overview

The **AI Client** (`ai_services/client.py`) is the centralized gateway for all Large Language Model (LLM) interactions within TextCraft. It abstracts away provider-specific API details, authentication, rate limiting, and cost tracking.

  * **Invoked By:** Specific `ai_services` modules (e.g., `ai_services/narrator.py`, `ai_services/architect.py`).
  * **Responsibility:** Stateless processing of prompts into text or tool calls.
  * **Design Principle:** The Brain does not know *what* it is writing; it only knows *how* to generate a completion based on the messages provided.

-----

## 2\. Configuration & Environment Variables

The Client initializes by reading specific environment variables defined in `.env`.

| Variable | Description | Default |
| :--- | :--- | :--- |
| `LLM_API_KEY` | The authentication secret for the provider. | **Required** |
| `LLM_API_BASE_URL` | The endpoint URL (e.g., OpenAI, Anthropic, or Local/Ollama). | `https://api.openai.com/v1` |
| `DEFAULT_MODEL` | The fallback model ID if a persona does not specify one. | `gpt-4-turbo` |
| `AI_TIMEOUT` | Max seconds to wait for a response before raising `TimeoutError`. | `60` |
| `MAX_RETRIES` | Number of exponential backoff attempts for 5xx/429 errors. | `3` |

-----

## 3\. Public Interface

The Client exposes a single primary asynchronous method to the rest of the application.

### `generate()`

  * **Signature:**

    ```python
    async def generate(
        messages: List[Dict[str, str]],
        model: str = DEFAULT_MODEL,
        tools: Optional[List[Dict]] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> Dict[str, Any]
    ```

  * **Arguments:**

      * `messages`: A list of message objects (See Section 4).
      * `model`: The specific model identifier (e.g., `claude-3-opus`).
      * `tools`: A list of JSON Schema definitions for available functions.
      * `temperature`: Creativity control (0.0 to 1.0).
      * `max_tokens`: Hard limit on output length.

  * **Returns:** A standardized **Response Object** (See Section 5).

-----

## 4\. Payload Specification (Input Normalization)

The Client enforces a strict schema for input messages to ensure compatibility across the system.

### Message Object Structure

```json
{
  "role": "system|user|assistant",
  "content": "String text content",
  "name": "Optional sender name (e.g., 'Architect')"
}
```

### Tool Schema Structure

If tools are provided, they must adhere to the OpenAI Function Calling format.

```json
{
  "type": "function",
  "function": {
    "name": "write_file",
    "description": "Writes text to a file",
    "parameters": { ... }
  }
}
```

-----

## 5\. Response Specification (Output Normalization)

Regardless of the underlying API provider (OpenAI, Anthropic, etc.), the Client **must** return a standardized dictionary to the Logic layer. This decoupling prevents API changes from breaking the core engine.

### The Response Object

```json
{
  "status": "success",
  "data": {
    "content": "The generated prose...",
    "tool_calls": [
      {
        "id": "call_123",
        "name": "write_file",
        "arguments": { "path": "ch01.md", "content": "..." }
      }
    ],
    "finish_reason": "stop|length|tool_calls"
  },
  "usage": {
    "prompt_tokens": 150,
    "completion_tokens": 200,
    "total_tokens": 350,
    "cost_estimate": 0.012
  }
}
```

### Field Logic

  * `content`: Can be `null` if the AI decided to call a tool instead.
  * `tool_calls`: An array of tool objects. If empty, the AI generated pure text.
  * `usage`: Used by `core/orchestrator.py` to log costs in `data/matrix.json` (optional metric).

-----

## 6\. Internal Logic & Error Handling

### A. Connection Management

The Client uses `aiohttp.ClientSession` for high-concurrency requests. It manages a persistent connection pool to reduce latency during multi-agent swarming.

### B. Retry Logic (Exponential Backoff)

If the API returns specific HTTP status codes, the Client automatically retries.

| HTTP Code | Action | Logic |
| :--- | :--- | :--- |
| `200` | Success | Parse and return JSON. |
| `401` | Auth Error | **Fatal.** Log error and stop Orchestrator. |
| `429` | Rate Limit | **Retry.** Wait $2^n$ seconds (backoff). |
| `5xx` | Server Error | **Retry.** Wait $2^n$ seconds. |
| `Timeout` | Network Error | **Retry.** Up to `MAX_RETRIES`. |

### C. Cost Tracking

Every successful response triggers a calculation based on `usage` fields. While not stored in the Client (which is stateless), this data is returned in the Response Object so the Orchestrator can aggregate it.