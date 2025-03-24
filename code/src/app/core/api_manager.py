import logging
import os
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class ApiManager:
    """
    Manages API keys with rate limiting capabilities.
    Handles multiple keys for the same service with rotation based on usage limits.
    """
    
    def __init__(self):
        self.api_keys: Dict[str, List[Tuple[str, int, int]]] = {}
        self.api_usage: Dict[str, Dict[str, Dict[str, any]]] = {}
        
        
        
        # Load API keys from environment variables
        # Get the absolute path of the app directory
        APP_DIR = Path(__file__).resolve().parent.parent

        # Load .env from app directory
        dotenv_path = APP_DIR / ".env"
        load_dotenv(dotenv_path=dotenv_path)
        
        for key, value in os.environ.items():
            if "_API_KEY_" in key:
                parts = key.split('_')
                if len(parts) >= 5:
                    # Format: SERVICE_API_KEY_LIMIT_PERIOD_INDEX
                    service_parts = parts[:-3]  # All parts before LIMIT_PERIOD_INDEX
                    service = "_".join(service_parts)
                    limit = int(parts[-3])
                    period = int(parts[-2])
                    
                    if service not in self.api_keys:
                        self.api_keys[service] = []
                        self.api_usage[service] = {}
                    
                    self.api_keys[service].append((value, limit, period))
                    self.api_usage[service][value] = {
                        'count': 0, 
                        'expiry': None, 
                        'limit': limit, 
                        'period': period
                    }
                    logger.info(f"Loaded API key for service: {service}")
    
    def _reset_key(self, service: str, key: str) -> None:
        """Reset usage counters for a specific API key"""
        usage = self.api_usage[service][key]
        self.api_usage[service][key] = {
            'count': 0, 
            'expiry': None, 
            'limit': usage['limit'], 
            'period': usage['period']
        }
        logger.debug(f"Reset usage for {service} API key")
    
    def _is_key_expired(self, service: str, key: str) -> bool:
        """Check if the key's current usage period has expired"""
        expiry = self.api_usage[service][key]['expiry']
        return expiry is not None and time.time() > expiry
    
    def get_key(self, service: str) -> str:
        """
        Get an available API key for the specified service.
        Handles rate limiting and key rotation.
        
        Args:
            service: Service name to get API key for
            
        Returns:
            A valid API key
            
        Raises:
            Exception: If no valid API keys are available
        """
        if service not in self.api_keys:
            logger.error(f"No API keys available for service: {service}")
            raise Exception(f"No API keys available for service: {service}")
        
        for key, limit, period in self.api_keys[service]:
            usage = self.api_usage[service][key]
            
            # Reset if period has expired
            if self._is_key_expired(service, key):
                self._reset_key(service, key)
            
            # Use key if under limit
            if usage['count'] < limit:
                if usage['expiry'] is None:
                    usage['expiry'] = time.time() + (period * 60)
                usage['count'] += 1
                logger.debug(f"Using {service} API key: {key[:5]}... ({usage['count']}/{limit})")
                return key
        
        logger.error(f"No valid API keys available for service: {service}")
        raise Exception(f"Rate limit exceeded for all {service} API keys")
    
    def get_usage_info(self) -> Dict[str, Dict[str, Dict[str, any]]]:
        """Get current API key usage information"""
        # Create a copy to avoid exposing the full keys
        usage_info = {}
        for service, keys in self.api_usage.items():
            usage_info[service] = {}
            for key, data in keys.items():
                masked_key = key[:5] + "..." + key[-3:] if len(key) > 10 else key
                usage_info[service][masked_key] = data.copy()
        
        return usage_info
    
    def reset(self) -> None:
        """Reset usage for all API keys"""
        for service in self.api_usage:
            for key in self.api_usage[service]:
                self._reset_key(service, key)
        logger.info("Reset all API key usage counters")