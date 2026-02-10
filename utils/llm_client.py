import os
import logging
from typing import Optional, Dict, Any, List
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
import yaml

logger = logging.getLogger(__name__)

class LLMClient:
    """Wrapper for LLM interactions (Anthropic/OpenAI)."""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config = self._load_config(config_path)
        self.provider = self.config.get("llm", {}).get("provider", "anthropic")
        self.model_name = self.config.get("llm", {}).get("model", "claude-3-5-sonnet-20240620")
        self.temperature = self.config.get("llm", {}).get("temperature", 0.7)
        self.llm = self._initialize_llm()

    def _load_config(self, path: str) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            with open(path, "r") as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.warning(f"Config file not found at {path}, using defaults.")
            return {}

    def _initialize_llm(self):
        """Initialize the LangChain LLM object based on provider."""
        api_key = None
        
        if self.provider == "anthropic":
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                logger.error("ANTHROPIC_API_KEY not found in environment variables.")
                raise ValueError("ANTHROPIC_API_KEY is required for Anthropic provider.")
            
            return ChatAnthropic(
                model=self.model_name,
                temperature=self.temperature,
                anthropic_api_key=api_key
            )
            
        elif self.provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                logger.error("OPENAI_API_KEY not found in environment variables.")
                raise ValueError("OPENAI_API_KEY is required for OpenAI provider.")
                
            return ChatOpenAI(
                model=self.model_name,
                temperature=self.temperature,
                openai_api_key=api_key
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Generate a response from the LLM."""
        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            response = self.llm.invoke(messages)
            return response.content
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            raise

    def generate_structured(self, system_prompt: str, user_prompt: str, output_schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a structured JSON response.
        Note: This is a simplified implementation. For production, use LangChain's structured output parsers.
        """
        # Append instruction to output JSON
        json_instruction = f"\n\nPlease output the result as a valid JSON object matching this schema: {output_schema}"
        full_user_prompt = user_prompt + json_instruction
        
        response_text = self.generate(system_prompt, full_user_prompt)
        
        # Basic JSON parsing (robust parsing would use a parser)
        import json
        import re
        
        try:
            # Try to find JSON block
            match = re.search(r"\{.*\}", response_text, re.DOTALL)
            if match:
                json_str = match.group(0)
                return json.loads(json_str)
            else:
                # Try parsing the whole text
                return json.loads(response_text)
        except json.JSONDecodeError:
            logger.error(f"Failed to parse JSON response: {response_text}")
            raise ValueError("LLM did not return valid JSON.")
