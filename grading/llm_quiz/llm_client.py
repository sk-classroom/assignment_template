"""
LLM client for API interactions in the LLM Quiz Challenge.

This module provides a clean interface for interacting with various LLM APIs
including OpenRouter, OpenAI, Ollama, and other OpenAI-compatible services.
"""

import json
import logging
import urllib.request
import urllib.error
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class LLMProvider(Enum):
    """Supported LLM providers."""
    OPENROUTER = "openrouter"
    OPENAI = "openai"
    OLLAMA = "ollama"
    CUSTOM = "custom"


@dataclass
class LLMMessage:
    """Represents a single message in a conversation."""
    role: str  # "system", "user", or "assistant"
    content: str


@dataclass
class LLMRequest:
    """Represents a request to an LLM API."""
    messages: List[LLMMessage]
    model: str
    temperature: float = 0.1
    max_tokens: int = 500
    stream: bool = False
    extra_params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LLMResponse:
    """Represents a response from an LLM API."""
    content: str
    success: bool
    error: Optional[str] = None
    raw_response: Optional[Dict[str, Any]] = None
    model_used: Optional[str] = None


class LLMClientError(Exception):
    """Base exception for LLM client errors."""
    pass


class LLMAuthenticationError(LLMClientError):
    """Raised when authentication fails."""
    pass


class LLMModelNotFoundError(LLMClientError):
    """Raised when the specified model is not found."""
    pass


class LLMRateLimitError(LLMClientError):
    """Raised when rate limits are exceeded."""
    pass


class LLMClient:
    """Client for interacting with LLM APIs."""
    
    def __init__(self, base_url: str, api_key: str, timeout: int = 30, context_window_size: int = 32768):
        """Initialize the LLM client.
        
        Args:
            base_url: Base URL for the LLM API endpoint
            api_key: API key for authentication
            timeout: Request timeout in seconds
            context_window_size: Context window size for models (default: 32768)
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        self.context_window_size = context_window_size
        self.provider = self._detect_provider()
        
        logger.info(f"Initialized LLM client for {self.provider.value} at {self.base_url}")
        logger.info(f"Context window size: {self.context_window_size}")
    
    def _detect_provider(self) -> LLMProvider:
        """Detect the LLM provider based on the base URL."""
        url_lower = self.base_url.lower()
        
        if "openrouter.ai" in url_lower:
            return LLMProvider.OPENROUTER
        elif "api.openai.com" in url_lower:
            return LLMProvider.OPENAI
        elif ":11434" in url_lower or "ollama" in url_lower:
            return LLMProvider.OLLAMA
        else:
            return LLMProvider.CUSTOM
    
    def chat(self, request: LLMRequest) -> LLMResponse:
        """Send a chat completion request to the LLM API.
        
        Args:
            request: The LLM request to send
            
        Returns:
            LLM response with content and metadata
        """
        try:
            # Build the request payload
            payload = self._build_payload(request)
            
            logger.debug(f"Sending request to {self.base_url}/chat/completions")
            logger.debug(f"Model: {request.model}, Temperature: {request.temperature}, Max tokens: {request.max_tokens}")
            
            # Make the API request
            url = f"{self.base_url}/chat/completions"
            data = json.dumps(payload).encode('utf-8')
            
            req = urllib.request.Request(
                url,
                data=data,
                headers=self._build_headers()
            )
            
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                result = json.loads(response.read().decode('utf-8'))
                return self._parse_response(result, request.model)
                
        except urllib.error.HTTPError as e:
            return self._handle_http_error(e, request.model)
        except urllib.error.URLError as e:
            return LLMResponse(
                content="",
                success=False,
                error=f"Connection error: {e.reason}",
                model_used=request.model
            )
        except json.JSONDecodeError as e:
            return LLMResponse(
                content="",
                success=False,
                error=f"Invalid JSON response: {e}",
                model_used=request.model
            )
        except Exception as e:
            return LLMResponse(
                content="",
                success=False,
                error=f"Unexpected error: {e}",
                model_used=request.model
            )
    
    def simple_chat(self, prompt: str, model: str, system_message: Optional[str] = None, 
                   temperature: float = 0.1, max_tokens: int = 500, 
                   response_format: Optional[Dict[str, Any]] = None) -> LLMResponse:
        """Simplified interface for single-prompt chat requests.
        
        Args:
            prompt: The user prompt/question
            model: Model name to use
            system_message: Optional system message
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            response_format: Optional structured output format (for JSON schema)
            
        Returns:
            LLM response
        """
        messages = []
        
        if system_message:
            messages.append(LLMMessage(role="system", content=system_message))
        
        messages.append(LLMMessage(role="user", content=prompt))
        
        extra_params = {}
        if response_format:
            extra_params["response_format"] = response_format
            
        request = LLMRequest(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            extra_params=extra_params
        )
        
        return self.chat(request)
    
    def _build_payload(self, request: LLMRequest) -> Dict[str, Any]:
        """Build the API request payload."""
        # Convert messages to dict format
        messages = [
            {"role": msg.role, "content": msg.content} 
            for msg in request.messages
        ]
        
        payload = {
            "model": request.model,
            "messages": messages,
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
            "stream": request.stream
        }
        
        # Add provider-specific parameters
        if self.provider == LLMProvider.OLLAMA:
            # Ollama supports additional options
            payload["options"] = {"num_ctx": self.context_window_size}
        
        # Add any extra parameters
        payload.update(request.extra_params)
        
        return payload
    
    def _build_headers(self) -> Dict[str, str]:
        """Build HTTP headers for the request."""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        # Add provider-specific headers
        if self.provider == LLMProvider.OPENROUTER:
            headers["HTTP-Referer"] = "https://github.com/your-repo/llm-quiz-challenge"
            headers["X-Title"] = "LLM Quiz Challenge"
        
        return headers
    
    def _parse_response(self, result: Dict[str, Any], model: str) -> LLMResponse:
        """Parse the API response into an LLMResponse object."""
        if "choices" not in result or not result["choices"]:
            return LLMResponse(
                content="",
                success=False,
                error="No choices in API response",
                raw_response=result,
                model_used=model
            )
        
        choice = result["choices"][0]
        if "message" not in choice or "content" not in choice["message"]:
            return LLMResponse(
                content="",
                success=False,
                error="Invalid response format",
                raw_response=result,
                model_used=model
            )
        
        content = choice["message"]["content"].strip()
        
        return LLMResponse(
            content=content,
            success=True,
            raw_response=result,
            model_used=model
        )
    
    def _handle_http_error(self, error: urllib.error.HTTPError, model: str) -> LLMResponse:
        """Handle HTTP errors and convert to appropriate exceptions or responses."""
        error_msg = f"HTTP {error.code}: {error.reason}"
        
        # Try to read error response for more details
        try:
            error_body = error.read().decode('utf-8')
            error_data = json.loads(error_body)
            if "error" in error_data:
                if isinstance(error_data["error"], dict):
                    error_msg = error_data["error"].get("message", error_msg)
                else:
                    error_msg = str(error_data["error"])
        except:
            pass  # Use the basic error message if we can't parse the response
        
        # Map HTTP status codes to specific error types
        if error.code == 401:
            error_msg = "Authentication failed. Please check your API key."
        elif error.code == 404:
            error_msg = f"Model '{model}' not found or endpoint not available."
        elif error.code == 429:
            error_msg = "Rate limit exceeded. Please try again later."
        elif error.code >= 500:
            error_msg = f"Server error ({error.code}). The API service may be temporarily unavailable."
        
        return LLMResponse(
            content="",
            success=False,
            error=error_msg,
            model_used=model
        )
    
    def test_connection(self, test_model: str = None) -> bool:
        """Test the connection to the LLM API.
        
        Args:
            test_model: Model to use for testing (optional)
            
        Returns:
            True if connection successful, False otherwise
        """
        if not test_model:
            # Use default test models based on provider
            test_models = {
                LLMProvider.OPENROUTER: "gpt-3.5-turbo",
                LLMProvider.OPENAI: "gpt-3.5-turbo", 
                LLMProvider.OLLAMA: "llama2",
                LLMProvider.CUSTOM: "default"
            }
            test_model = test_models.get(self.provider, "gpt-3.5-turbo")
        
        response = self.simple_chat(
            prompt="Hello, this is a connection test.",
            model=test_model,
            max_tokens=10
        )
        
        if response.success:
            logger.info(f"Connection test successful with model {test_model}")
            return True
        else:
            logger.error(f"Connection test failed: {response.error}")
            return False