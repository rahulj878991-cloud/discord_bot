import os
import random
import time
from openai import AsyncOpenAI
from typing import List, Dict, Optional
import asyncio

class APIManager:
    def __init__(self):
        self.api_keys = self._load_api_keys()
        self.current_index = 0
        self.failed_keys = {}  # Track failed keys temporarily
        self.key_stats = {}    # Track usage stats
        
        print(f"✅ Loaded {len(self.api_keys)} API keys")
        
    def _load_api_keys(self) -> List[str]:
        """Load all API keys from environment variables"""
        keys = []
        i = 1
        
        while True:
            key_name = f"LLM_API_KEY_{i}"
            key_value = os.getenv(key_name)
            
            if not key_value:
                # Also check without number for backward compatibility
                if i == 1:
                    single_key = os.getenv('LLM_API_KEY')
                    if single_key:
                        keys.append(single_key)
                        print(f"✅ Loaded single API key")
                break
            
            # Check if key is not empty or placeholder
            if key_value.strip() and "your_openrouter_api_key" not in key_value:
                keys.append(key_value.strip())
                print(f"✅ Loaded API key {i}")
                self.key_stats[key_name] = {"success": 0, "fail": 0, "last_used": None}
            
            i += 1
        
        if not keys:
            print("❌ No valid API keys found! Add LLM_API_KEY_1, LLM_API_KEY_2, etc. in .env")
        
        return keys
    
    def get_next_key(self, exclude_key: Optional[str] = None) -> Optional[str]:
        """Get next available API key (round-robin with exclusion)"""
        if not self.api_keys:
            return None
        
        # Remove temporarily failed keys from consideration
        available_keys = [
            key for key in self.api_keys 
            if key not in self.failed_keys or 
            (time.time() - self.failed_keys.get(key, 0) > 60)  # 60 second cooldown
        ]
        
        if not available_keys:
            # All keys are in cooldown, use the one with oldest failure
            if self.failed_keys:
                oldest_key = min(self.failed_keys.items(), key=lambda x: x[1])[0]
                print(f"⚠️ All keys in cooldown, trying oldest failed key: {oldest_key[:15]}...")
                return oldest_key
            return None
        
        # Get next key (round-robin)
        key = available_keys[self.current_index % len(available_keys)]
        self.current_index += 1
        
        # If we need to exclude a specific key
        if exclude_key and key == exclude_key and len(available_keys) > 1:
            key = available_keys[(self.current_index + 1) % len(available_keys)]
        
        return key
    
    def mark_success(self, api_key: str):
        """Mark an API key as successful"""
        # Remove from failed keys if present
        if api_key in self.failed_keys:
            del self.failed_keys[api_key]
        
        # Update stats
        for key_name, key_value in os.environ.items():
            if key_value == api_key:
                if key_name not in self.key_stats:
                    self.key_stats[key_name] = {"success": 0, "fail": 0, "last_used": None}
                self.key_stats[key_name]["success"] += 1
                self.key_stats[key_name]["last_used"] = time.time()
                break
    
    def mark_failed(self, api_key: str, error_message: str = ""):
        """Mark an API key as failed (temporarily)"""
        self.failed_keys[api_key] = time.time()
        
        # Update stats
        for key_name, key_value in os.environ.items():
            if key_value == api_key:
                if key_name not in self.key_stats:
                    self.key_stats[key_name] = {"success": 0, "fail": 0, "last_used": None}
                self.key_stats[key_name]["fail"] += 1
                break
        
        # Print error info
        key_prefix = api_key[:15] + "..." if len(api_key) > 15 else api_key
        print(f"❌ API key failed: {key_prefix} | Error: {error_message[:100]}")
    
    def get_stats(self) -> Dict:
        """Get statistics about API key usage"""
        return {
            "total_keys": len(self.api_keys),
            "available_keys": len(self.api_keys) - len(self.failed_keys),
            "failed_keys": len(self.failed_keys),
            "key_stats": self.key_stats.copy()
        }
    
    def get_client(self, api_key: Optional[str] = None) -> Optional[AsyncOpenAI]:
        """Get OpenAI client with an API key"""
        if not api_key:
            api_key = self.get_next_key()
        
        if not api_key:
            return None
        
        return AsyncOpenAI(
            base_url=os.getenv('LLM_BASE_URL', 'https://openrouter.ai/api/v1'),
            api_key=api_key
        )

# Global instance
api_manager = APIManager()
