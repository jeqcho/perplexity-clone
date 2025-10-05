"""OpenAI API client wrapper for LLM access via OpenRouter."""

from openai import OpenAI
from src.config import Config


class OpenAIClient:
    """Wrapper for OpenAI-compatible API calls via OpenRouter."""

    def __init__(self, api_key: str = None, model: str = None):
        """Initialize OpenRouter client.

        Args:
            api_key: OpenRouter API key. If not provided, uses Config.OPENROUTER_API_KEY
            model: Model name. If not provided, uses Config.OPENROUTER_MODEL
        """
        self.api_key = api_key or Config.OPENROUTER_API_KEY
        if not self.api_key:
            raise ValueError("OpenRouter API key is required")

        self.model = model or Config.OPENROUTER_MODEL
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://openrouter.ai/api/v1"
        )

    def generate(
        self,
        prompt: str,
        max_tokens: int = 2000,
        temperature: float = 0.7,
        system_prompt: str = None
    ) -> str:
        """Generate a completion using OpenRouter.

        Args:
            prompt: The user prompt
            max_tokens: Maximum tokens in the response
            temperature: Sampling temperature (0-2)
            system_prompt: Optional system prompt to guide behavior

        Returns:
            The generated text response

        Raises:
            Exception: If the API call fails
        """
        try:
            messages = []

            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})

            messages.append({"role": "user", "content": prompt})

            # Ensure max_tokens meets minimum requirement for OpenRouter models
            safe_max_tokens = max(max_tokens, Config.MIN_MAX_TOKENS)

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=safe_max_tokens,
                temperature=temperature,
            )

            content = response.choices[0].message.content
            # Handle None response
            if content is None:
                return ""
            return content

        except Exception as e:
            # Fail fast on API errors as per requirements
            raise Exception(f"OpenRouter API request failed: {str(e)}") from e
