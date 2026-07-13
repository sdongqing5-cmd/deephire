"""LLM Client Factory - Support OpenAI and Anthropic"""

from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

from app.core.config import settings


class BaseLLMClient(ABC):
    """Base LLM Client Interface"""

    @abstractmethod
    def chat_completion(
        self,
        messages: list,
        temperature: float = 0,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Generate chat completion

        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Returns:
            Generated text response
        """
        pass


class OpenAIClient(BaseLLMClient):
    """OpenAI Client (supports relay API)"""

    def __init__(self):
        from openai import OpenAI

        self.client = OpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL,
        )
        self.model = settings.OPENAI_MODEL

    def chat_completion(
        self,
        messages: list,
        temperature: float = 0,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Generate chat completion using OpenAI API"""
        try:
            kwargs = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
            }
            if max_tokens:
                kwargs["max_tokens"] = max_tokens

            response = self.client.chat.completions.create(**kwargs)
            return response.choices[0].message.content

        except Exception as e:
            raise ValueError(f"OpenAI API call failed: {str(e)}")


class AnthropicClient(BaseLLMClient):
    """Anthropic Client (supports relay API)"""

    def __init__(self):
        from anthropic import Anthropic

        self.client = Anthropic(
            api_key=settings.ANTHROPIC_API_KEY,
            base_url=settings.ANTHROPIC_BASE_URL,
        )
        self.model = settings.ANTHROPIC_MODEL

    def chat_completion(
        self,
        messages: list,
        temperature: float = 0,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Generate chat completion using Anthropic API"""
        try:
            # Convert OpenAI-style messages to Anthropic format
            system_message = None
            anthropic_messages = []

            for msg in messages:
                if msg["role"] == "system":
                    system_message = msg["content"]
                else:
                    anthropic_messages.append(
                        {"role": msg["role"], "content": msg["content"]}
                    )

            kwargs = {
                "model": self.model,
                "messages": anthropic_messages,
                "temperature": temperature,
                "max_tokens": max_tokens or 4096,
            }

            if system_message:
                kwargs["system"] = system_message

            response = self.client.messages.create(**kwargs)
            return response.content[0].text

        except Exception as e:
            raise ValueError(f"Anthropic API call failed: {str(e)}")


class LLMClientFactory:
    """Factory for creating LLM clients"""

    _instance: Optional[BaseLLMClient] = None

    @classmethod
    def get_client(cls) -> BaseLLMClient:
        """
        Get LLM client based on configuration

        Returns:
            LLM client instance (OpenAI or Anthropic)
        """
        if cls._instance is None:
            provider = settings.LLM_PROVIDER.lower()

            if provider == "openai":
                cls._instance = OpenAIClient()
            elif provider == "anthropic":
                cls._instance = AnthropicClient()
            else:
                raise ValueError(
                    f"Unsupported LLM provider: {provider}. "
                    f"Supported providers: openai, anthropic"
                )

        return cls._instance

    @classmethod
    def reset(cls):
        """Reset client instance (useful for testing)"""
        cls._instance = None


# Global client getter
def get_llm_client() -> BaseLLMClient:
    """Get the configured LLM client"""
    return LLMClientFactory.get_client()
