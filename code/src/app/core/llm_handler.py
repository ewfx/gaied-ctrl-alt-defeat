import json
import os
import logging
from typing import Dict, Optional

from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

# Import LLM providers
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain.chat_models.openai import ChatOpenAI as BaseChatOpenAI

from app.core.api_manager import ApiManager

logger = logging.getLogger(__name__)

class OpenRouterLLM(BaseChatOpenAI):
    """
    Custom LLM class for OpenRouter integration (DeepSeek R1, etc).
    """
    openrouter_headers: Optional[Dict[str, str]] = None
    
    def __init__(
        self,
        model: str = "deepseek/deepseek-r1:free",
        openai_api_key: str = None,
        temperature: float = 0.7,
        openrouter_headers: Optional[Dict[str, str]] = None,
        callbacks = None,
        **kwargs
    ):
        super().__init__(
            model=model,
            openai_api_key=openai_api_key,
            openai_api_base="https://openrouter.ai/api/v1",
            temperature=temperature,
            callbacks=callbacks,
            **kwargs
        )
        self.openrouter_headers = openrouter_headers or {}
        
    def _create_params(self, **kwargs):
        params = super()._create_params(**kwargs)
        if self.openrouter_headers:
            # Add OpenRouter specific headers
            params["extra_headers"] = self.openrouter_headers
        return params

class LLMHandler:
    """
    Handles interactions with Anthropic, OpenAI and DeepSeek LLM providers using LangChain.
    """
    
    def __init__(self, api_manager: ApiManager, config_filename: str = "llm-config.json"):
        """
        Initialize the LLM handler
        
        Args:
            api_manager: ApiManager instance for key management
            config_filename: Path to LLM configuration file
        """
        self.api_manager = api_manager
        
        # Load LLM configuration
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        config_path = os.path.join(base_path, config_filename)
        
        try:
            with open(config_path, "r") as config_file:
                self.llm_config = json.load(config_file)
                logger.info(f"Loaded LLM configuration from {config_path}")
        except Exception as e:
            logger.error(f"Error loading LLM configuration: {str(e)}")
            self.llm_config = {}
        
        # Map LLM class names to actual classes
        self.llm_class_mapping = {
            "ChatAnthropic": ChatAnthropic,
            "ChatOpenAI": ChatOpenAI,
            "OpenRouterLLM": OpenRouterLLM,
        }

    def get_llm(self, task_type: str):
        """
        Get an LLM instance for the specified task type
        
        Args:
            task_type: Type of task to get LLM for (must match config)
            
        Returns:
            LangChain LLM instance
            
        Raises:
            ValueError: If no configuration found for task type
        """
        # Get configuration for the task
        config = self.llm_config.get(task_type)
        if not config:
            logger.error(f"No LLM configuration found for task type: {task_type}")
            # Try fallback configuration
            config = self.llm_config.get("fallback")
            if not config:
                raise ValueError(f"No LLM configuration found for task type: {task_type}")
            logger.info(f"Using fallback LLM for task type: {task_type}")
        
        # Get LLM class
        llm_class_name = config["llm"]
        llm_class = self.llm_class_mapping.get(llm_class_name)
        if not llm_class:
            logger.error(f"Unknown LLM class: {llm_class_name}")
            raise ValueError(f"Unknown or unsupported LLM class: {llm_class_name}")
        
        # Get API key
        api_key = self.api_manager.get_key(config["api_key_name"])
        
        # Add streaming if specified
        callbacks = None
        if config.get("streaming", False):
            callbacks = CallbackManager([StreamingStdOutCallbackHandler()])
        
        # Special handling for OpenRouter models (DeepSeek R1)
        if llm_class_name == "OpenRouterLLM":
            # Get optional OpenRouter headers
            openrouter_headers = {}
            if config.get("http_referer"):
                openrouter_headers["HTTP-Referer"] = config["http_referer"]
            if config.get("x_title"):
                openrouter_headers["X-Title"] = config["x_title"]
                
            return llm_class(
                model=config["model"],
                openai_api_key=api_key,
                temperature=config["temperature"],
                callbacks=callbacks,
                openrouter_headers=openrouter_headers,
            )
        else:
            # Handle other LLM types with common parameters
            api_key_param = {f"{config['api_key_name'].lower()}": api_key}
            
            return llm_class(
                model=config["model"],
                temperature=config["temperature"],
                callbacks=callbacks,
                **api_key_param,
            )