import os
import time
from openai import AsyncOpenAI

class APIManager:
    def __init__(self):
        self.api_keys = []
        self.current_index = 0
        self.failed_keys = {}  # key: failure_time
        self.load_keys()
        
    def load_keys(self):
        """Load all API keys from environment"""
        keys = []
        
        # Load keys: LLM_API_KEY_1, LLM_API_KEY_2, etc.
        i = 1
        while True:
            key_name = f"LLM_API_KEY_{i}"
            key_value = os.getenv(key_name)
            
            if not key_value:
                break
            
            if key_value.strip() and "your_openrouter_api_key" not in key_value:
                keys.append(key_value.strip())
                print(f'   ✅ Loaded {key_name}')
            
            i += 1
        
        # Also check single key
        single_key = os.getenv('LLM_API_KEY')
        if single_key and single_key.strip() and "your_openrouter_api_key" not in single_key:
            if single_key not in keys:
                keys.append(single_key.strip())
                print('   ✅ Loaded LLM_API_KEY')
        
        self.api_keys = keys
        print(f'📦 Total API keys loaded: {len(self.api_keys)}')
        
        if not self.api_keys:
            print('⚠️  WARNING: No API keys found! Add LLM_API_KEY_1 to .env')
    
    def get_next_key(self):
        """Get next working API key with round-robin"""
        if not self.api_keys:
            return None
        
        # Clean old failures (older than 60 seconds)
        current_time = time.time()
        expired_keys = [
            key for key, fail_time in self.failed_keys.items()
            if current_time - fail_time > 60
        ]
        for key in expired_keys:
            del self.failed_keys[key]
        
        # Try each key once
        for _ in range(len(self.api_keys)):
            key = self.api_keys[self.current_index % len(self.api_keys)]
            self.current_index += 1
            
            if key not in self.failed_keys:
                return key
        
        # All keys are in cooldown
        if self.failed_keys:
            # Return the one that failed longest ago
            oldest_key = min(self.failed_keys.items(), key=lambda x: x[1])[0]
            print(f'⚠️  All keys in cooldown, trying: {oldest_key[:20]}...')
            return oldest_key
        
        return None
    
    def mark_success(self, api_key):
        """Mark API key as successful"""
        if api_key in self.failed_keys:
            del self.failed_keys[api_key]
    
    def mark_failed(self, api_key, error_message=""):
        """Mark API key as failed"""
        self.failed_keys[api_key] = time.time()
        error_short = error_message[:100] if error_message else "Unknown error"
        print(f'❌ API key failed: {error_short}')
    
    def get_client(self):
        """Get OpenAI client with working key"""
        api_key = self.get_next_key()
        if not api_key:
            return None
        
        return AsyncOpenAI(
            base_url=os.getenv('LLM_BASE_URL', 'https://openrouter.ai/api/v1'),
            api_key=api_key
        )

# Create global instance
api_manager = APIManager()
