# llm/deepseek_client.py
import requests
import json
from typing import Dict, List, Optional
import logging

class DeepSeekClient:
    """Client for DeepSeek local LLM"""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "deepseek-coder:6.7b"):
        self.base_url = base_url
        self.model = model  # Can be deepseek-coder:6.7b, deepseek-coder:33b, etc.
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    def generate(self, prompt: str, system: Optional[str] = None, 
                context: Optional[List[Dict]] = None, temperature: float = 0.7) -> str:
        """Generate response from DeepSeek via Ollama"""
        
        # DeepSeek specific prompt formatting
        messages = []
        
        # Add system message
        if system:
            messages.append({
                "role": "system",
                "content": system
            })
        
        # Add context messages
        if context:
            for msg in context[-5:]:  # Last 5 messages for context
                role = "assistant" if msg.get("sender") == msg.get("current_agent") else "user"
                messages.append({
                    "role": role,
                    "content": f"{msg.get('sender', 'User')}: {msg.get('content', '')}"
                })
        
        # Add current prompt
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        # Convert to DeepSeek format
        formatted_prompt = self._format_deepseek_prompt(messages)
        
        payload = {
            "model": self.model,
            "prompt": formatted_prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "top_p": 0.95,
                "top_k": 40,
                "repeat_penalty": 1.1,
                "num_predict": 1024
            }
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()["response"]
                self.logger.info(f"Generated response: {result[:100]}...")
                return result
            else:
                error_msg = f"Error: {response.status_code} - {response.text}"
                self.logger.error(error_msg)
                return error_msg
                
        except Exception as e:
            error_msg = f"Error connecting to DeepSeek: {str(e)}"
            self.logger.error(error_msg)
            return error_msg
    
    def _format_deepseek_prompt(self, messages: List[Dict]) -> str:
        """Format messages for DeepSeek model"""
        formatted = ""
        
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            
            if role == "system":
                formatted += f"<|system|>\n{content}\n"
            elif role == "user":
                formatted += f"<|user|>\n{content}\n"
            elif role == "assistant":
                formatted += f"<|assistant|>\n{content}\n"
        
        formatted += "<|assistant|>\n"
        return formatted