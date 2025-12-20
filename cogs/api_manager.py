import os
import time
from openai import AsyncOpenAI
import aiohttp

class APIManager:
    def __init__(self):
        self.api_keys = []
        self.current_index = 0
        self.failed_keys = {}
        self.load_keys()
        
    def load_keys(self):
        """Load API keys"""
        keys = []
        
        # Check multiple keys
        for i in range(1, 10):
            key = os.getenv(f'LLM_API_KEY_{i}')
            if key and key.strip() and 'your_openrouter_api_key' not in key:
                keys.append(key.strip())
                print(f'   🔑 Loaded LLM_API_KEY_{i}')
        
        # Check single key
        single_key = os.getenv('LLM_API_KEY')
        if single_key and single_key not in keys and 'your_openrouter_api_key' not in single_key:
            keys.append(single_key.strip())
            print(f'   🔑 Loaded LLM_API_KEY')
        
        self.api_keys = keys
        print(f'📦 TOTAL API KEYS: {len(self.api_keys)}')
    
    def get_next_key(self):
        """Get working key"""
        if not self.api_keys:
            return None
        
        # Clean old failures
        current = time.time()
        self.failed_keys = {k: v for k, v in self.failed_keys.items() if current - v < 60}
        
        # Find working key
        for _ in range(len(self.api_keys)):
            key = self.api_keys[self.current_index % len(self.api_keys)]
            self.current_index += 1
            
            if key not in self.failed_keys:
                return key
        
        return None
    
    def mark_success(self, key):
        """Mark key as good"""
        if key in self.failed_keys:
            del self.failed_keys[key]
    
    def mark_failed(self, key, error=""):
        """Mark key as bad"""
        self.failed_keys[key] = time.time()
        print(f'❌ KEY FAILED: {error[:80]}')
    
    def get_client(self):
        """Get OpenAI client"""
        key = self.get_next_key()
        if not key:
            return None
        
        return AsyncOpenAI(
            base_url=os.getenv('LLM_BASE_URL', 'https://openrouter.ai/api/v1'),
            api_key=key,
            http_client=aiohttp.ClientSession()  # Use aiohttp instead of httpx
        )

api_manager = APIManager()
