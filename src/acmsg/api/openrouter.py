"""OpenRouter API client for communication with AI models."""

import json
import re
import time
from typing import Dict, Any, Optional, Tuple

import requests
import colorama
from colorama import Fore, Style

from ..constants import API_ENDPOINT
from ..exceptions import ApiError

colorama.init()


class OpenRouterClient:
    """Client for interacting with the OpenRouter API."""

    # Known context limits for various model families
    MODEL_TOKEN_LIMITS = {
        "default": 4096,
        "gpt-3.5": 16384,
        "gpt-4": 8192,
        "gpt-4-turbo": 128000,
        "gpt-4o": 128000,
        "claude": 100000,
        "claude-3": 200000,
        "gemini": 32768,
        "mistral": 32768,
        "llama": 4096,
        "llama-2": 4096,
        "llama-3": 8192,
        "qwen": 32768,
    }

    def __init__(self, api_token: str):
        """Initialize the OpenRouter API client.

        Args:
            api_token: OpenRouter API token
        """
        self._api_token = api_token
        self._api_endpoint = API_ENDPOINT
        self._models_info_cache: Dict[str, Any] = {}  # Cache for model info
        self._cache_expiry: Dict[str, int] = {}  # Expiry timestamps for cached info
        self._cache_ttl: int = 3600  # Cache TTL (1 hour)

    def _estimate_tokens(self, text: str) -> int:
        """Estimate the number of tokens in a text.

        Uses a simple estimation method of 4 characters per token.

        Args:
            text: The text to estimate tokens for

        Returns:
            Estimated token count
        """
        # Generally 4 chars per token for English text
        # This is an approximation - actual tokenization varies by model
        return len(text) // 4 + 1

    def _fetch_model_info(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Fetch model information from OpenRouter API.

        Args:
            model_id: The model identifier

        Returns:
            Dictionary with model information or None if not found
        """
        try:
            # Check if we have a valid cached response
            current_time = time.time()
            if (
                model_id in self._models_info_cache
                and current_time < self._cache_expiry.get(model_id, 0)
            ):
                return self._models_info_cache[model_id]

            # Make API request to fetch model information
            headers = {"Authorization": f"Bearer {self._api_token}"}
            response = requests.get(
                url="https://openrouter.ai/api/v1/models", headers=headers
            )

            if not response.ok:
                return None

            models_data = response.json().get("data", [])

            # Find the requested model
            model_info = None
            for model_data in models_data:
                if model_data.get("id", "").lower() == model_id.lower():
                    model_info = model_data
                    break

            # If exact match not found, try partial match
            if model_info is None:
                for model_data in models_data:
                    if model_id.lower() in model_data.get("id", "").lower():
                        model_info = model_data
                        break

            # Cache the result with expiry
            if model_info:
                self._models_info_cache[model_id] = model_info
                self._cache_expiry[model_id] = int(current_time + self._cache_ttl)

            return model_info
        except Exception:
            return None

    def _get_model_context_length(self, model: str) -> int:
        """Get the context length for a given model.

        Args:
            model: The model identifier

        Returns:
            Context length in tokens
        """
        # Try to get model context length from API
        model_info = self._fetch_model_info(model)
        if model_info and "context_length" in model_info:
            return int(model_info["context_length"])

        # Fall back to checking known model families
        for model_family, token_limit in self.MODEL_TOKEN_LIMITS.items():
            if model_family.lower() in model.lower():
                return token_limit

        # Default if no specific model is matched
        return self.MODEL_TOKEN_LIMITS["default"]

    def _get_estimated_token_counts(
        self, model: str, system_prompt: str, user_prompt: str
    ) -> Tuple[int, int, int, int]:
        """Get estimated token counts for the prompts.

        Args:
            model: Model ID
            system_prompt: System prompt
            user_prompt: User prompt

        Returns:
            Tuple of (context_length, system_tokens, user_tokens, total_estimated_tokens)
        """
        # Get the context length for this model
        context_length = self._get_model_context_length(model)

        # Estimate tokens
        system_tokens = self._estimate_tokens(system_prompt)
        user_tokens = self._estimate_tokens(user_prompt)

        # Add extra tokens for message formatting (role markers, etc.)
        total_estimated_tokens = system_tokens + user_tokens + 200

        return context_length, system_tokens, user_tokens, total_estimated_tokens

    def _should_use_transforms(
        self, model: str, system_prompt: str, user_prompt: str
    ) -> bool:
        """Determine if we should use transforms for this request.

        Args:
            model: Model ID
            system_prompt: System prompt
            user_prompt: User prompt

        Returns:
            True if transforms should be used, False otherwise
        """
        # Get token counts
        context_length, _, _, total_estimated_tokens = self._get_estimated_token_counts(
            model, system_prompt, user_prompt
        )

        # Return true if we're approaching the context limit
        return total_estimated_tokens > (context_length * 0.9)

    def _trim_content(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int,
        system_max_ratio: float = 0.3,
    ) -> Tuple[str, str, bool]:
        """Trim content to fit within token limits.

        Args:
            system_prompt: System prompt
            user_prompt: User prompt
            max_tokens: Maximum tokens allowed
            system_max_ratio: Maximum ratio of tokens to allocate to system prompt

        Returns:
            Tuple of (trimmed_system_prompt, trimmed_user_prompt, was_trimmed)
        """
        # Reserve tokens for message formatting
        available_tokens = max_tokens - 200

        # Estimate current token counts
        system_tokens = self._estimate_tokens(system_prompt)
        user_tokens = self._estimate_tokens(user_prompt)
        total_tokens = system_tokens + user_tokens

        # If we're within limits, return as is
        if total_tokens <= available_tokens:
            return system_prompt, user_prompt, False

        # Calculate allocation
        max_system_tokens = min(system_tokens, int(available_tokens * system_max_ratio))
        max_user_tokens = available_tokens - max_system_tokens

        trimmed_system = system_prompt
        trimmed_user = user_prompt

        # Trim system prompt if needed, manual middle-out
        if system_tokens > max_system_tokens:
            keep_start = int(max_system_tokens * 0.6)
            keep_end = max_system_tokens - keep_start

            start_chars = keep_start * 4
            end_chars = keep_end * 4

            trimmed_system = (
                system_prompt[:start_chars]
                + "\n\n[...content trimmed due to length constraints...]\n\n"
                + system_prompt[-end_chars:]
            )

        # Trim user prompt if needed
        if user_tokens > max_user_tokens:
            keep_start = int(max_user_tokens * 0.7)
            keep_end = max_user_tokens - keep_start

            start_chars = keep_start * 4
            end_chars = keep_end * 4

            trimmed_user = (
                user_prompt[:start_chars]
                + "\n\n[...content trimmed due to length constraints...]\n\n"
                + user_prompt[-end_chars:]
            )

        return trimmed_system, trimmed_user, True

    def generate_completion(
        self, model: str, system_prompt: str, user_prompt: str, stream: bool = False
    ) -> str:
        """Generate a completion using the OpenRouter API.

        Args:
            model: Model ID to use for generation
            system_prompt: System prompt for the model
            user_prompt: User prompt for the model
            stream: Whether to stream the response

        Returns:
            Generated text

        Raises:
            ApiError: If the API request fails
        """
        # Get token estimates and context length
        context_length, system_tokens, user_tokens, total_tokens = (
            self._get_estimated_token_counts(model, system_prompt, user_prompt)
        )

        # Check if manual trimming is needed (if we're over context length even with transforms)
        trimmed_system_prompt, trimmed_user_prompt, was_trimmed = (
            system_prompt,
            user_prompt,
            False,
        )
        if total_tokens > context_length:
            # Try to trim content to fit within context length
            trimmed_system_prompt, trimmed_user_prompt, was_trimmed = (
                self._trim_content(system_prompt, user_prompt, context_length)
            )

            if was_trimmed:
                print(
                    f"{Fore.YELLOW}Warning: Input content was trimmed to fit within the model's context length.{Style.RESET_ALL}"
                )

        payload = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": "Parse the following messages as markdown.",
                },
                {"role": "system", "content": trimmed_system_prompt},
                {"role": "user", "content": trimmed_user_prompt},
            ],
            "stream": stream,
        }

        # Add middle-out transform in case request exceeds context limit
        if self._should_use_transforms(
            model, trimmed_system_prompt, trimmed_user_prompt
        ):
            payload["transforms"] = ["middle-out"]

        headers = {"Authorization": f"Bearer {self._api_token}"}

        try:
            response = requests.post(
                url=self._api_endpoint,
                headers=headers,
                data=json.dumps(payload),
            )

            response_json = response.json()

            # Check for API & HTTP errors
            if not response.ok or "error" in response_json:
                error_data = response_json
                error_info = error_data.get("error", {})
                error_message = error_info.get("message", response.text)

                # Check for context length error
                if "longer than the model's context length" in error_message:
                    try:
                        # Try to parse token counts from the error message
                        input_tokens_match = re.search(
                            r"input \((\d+) tokens\)", error_message
                        )
                        context_length_match = re.search(
                            r"context length \((\d+) tokens\)", error_message
                        )

                        if input_tokens_match and context_length_match:
                            input_tokens = int(input_tokens_match.group(1))
                            context_length = int(context_length_match.group(1))
                            tokens_exceed = input_tokens - context_length

                            # Notify user if both transforms and trimming were tried
                            transform_note = ""
                            if "transforms" in payload:
                                transform_note = (
                                    " Even with content compression enabled,"
                                )
                                if was_trimmed:
                                    transform_note += (
                                        " and after automatic content trimming,"
                                    )
                                transform_note += (
                                    " the request exceeded the models context limit."
                                )

                            # Remove prefix from model name for display
                            model_display = (
                                model.split("/")[-1] if "/" in model else model
                            )

                            raise ApiError(
                                f"{Fore.RED}Context length exceeded for {model_display}:{Style.RESET_ALL}{transform_note} "
                                f"Input is {input_tokens} tokens, but model only supports {context_length} tokens "
                                f"(exceeding by {tokens_exceed} tokens). "
                                f"Try splitting your staged changes into multiple smaller commits, or use a model "
                                f"with a larger context size."
                            )
                    except (AttributeError, ValueError):
                        pass

                # Generic error fallback
                raise ApiError(
                    f"{Fore.RED}API request failed:{Style.RESET_ALL}\n{error_message}"
                )

            if "choices" not in response_json or not response_json["choices"]:
                raise ApiError(
                    f"{Fore.RED}API returned unexpected response format:{Style.RESET_ALL}\n{response_json}"
                )

            return response_json["choices"][0]["message"]["content"]
        except requests.RequestException as e:
            raise ApiError(f"Failed to connect to OpenRouter API: {e}")
        except (KeyError, ValueError, json.JSONDecodeError) as e:
            raise ApiError(f"Failed to parse API response: {e}")
