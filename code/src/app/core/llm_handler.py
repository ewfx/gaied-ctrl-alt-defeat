import json
import os
import logging
from typing import Dict, List

from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

# Import LLM providers
from langchain_anthropic import ChatAnthropic
from langchain_openai import AzureChatOpenAI, ChatOpenAI

from app.core.api_manager import ApiManager

logger = logging.getLogger(__name__)

class LLMHandler:
    """
    Handles interactions with various LLM providers using LangChain.
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
            "AzureChatOpenAI": AzureChatOpenAI,
            "ChatOpenAI": ChatOpenAI,
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
            raise ValueError(f"Unknown LLM class: {llm_class_name}")
        
        # Get API key
        api_key = self.api_manager.get_key(config["api_key_name"])
        
        # Create LLM instance based on class
        if llm_class_name == "AzureChatOpenAI":
            return llm_class(
                openai_api_version=config["openai_api_version"],
                openai_api_key=api_key,
                temperature=config["temperature"],
                azure_endpoint=config["openai_api_base"],
                openai_api_type=config["openai_api_type"],
                deployment_name=config["deployment_name"],
            )
        else:
            # Handle other LLM types with common parameters
            api_key_param = {f"{config['api_key_name'].lower()}": api_key}
            
            # Add streaming if specified
            callbacks = None
            if config.get("streaming", False):
                callbacks = CallbackManager([StreamingStdOutCallbackHandler()])
            
            return llm_class(
                model=config["model"],
                temperature=config["temperature"],
                callbacks=callbacks,
                **api_key_param,
            )
    
    def format_message_history(self, 
                              system_prompt: str, 
                              messages: List[Dict[str, str]] = None) -> List[Dict[str, str]]:
        """
        Format message history for LLM conversation
        
        Args:
            system_prompt: System prompt to use
            messages: List of previous messages (optional)
            
        Returns:
            Formatted message history
        """
        history = [{"role": "system", "content": system_prompt}]
        
        if messages:
            for msg in messages:
                if msg["role"] not in ["user", "assistant", "system"]:
                    continue
                history.append({"role": msg["role"], "content": msg["content"]})
        
        return history
    
    def structured_output_parser(self, schema_fields: List[ResponseSchema]):
        """
        Create a structured output parser for LLM responses
        
        Args:
            schema_fields: List of response schema fields
            
        Returns:
            StructuredOutputParser instance
        """
        return StructuredOutputParser.from_response_schemas(schema_fields)