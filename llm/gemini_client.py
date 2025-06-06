import google.generativeai as genai
from typing import Dict, List, Optional
import asyncio
import logging
from datetime import datetime
import json

class GeminiClient:
    """Client for Google's Gemini AI"""
    
    def __init__(self, api_key: str, model_name: str = "gemini-1.5-flash"):
        self.api_key = api_key
        self.model_name = model_name
        self.logger = logging.getLogger(__name__)
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        
        # Initialize chat session
        self.chat = self.model.start_chat(history=[])
        
        # Configuration
        self.generation_config = genai.GenerationConfig(
            temperature=0.7,
            top_p=0.95,
            top_k=40,
            max_output_tokens=2048,
        )
        
        self.safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            }
        ]
    
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate response from Gemini"""
        try:
            # Override generation config if provided
            generation_config = kwargs.get('generation_config', self.generation_config)
            
            # Generate response
            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt,
                generation_config=generation_config,
                safety_settings=self.safety_settings
            )
            
            # Extract text from response
            if response.text:
                return response.text
            else:
                self.logger.warning("Empty response from Gemini")
                return "I couldn't generate a response. Please try again."
                
        except Exception as e:
            self.logger.error(f"Error generating response: {e}")
            return f"Error: {str(e)}"
    
    async def generate_with_context(self, prompt: str, context: Dict) -> str:
        """Generate response with additional context"""
        # Build context string
        context_str = "Context:\n"
        for key, value in context.items():
            context_str += f"- {key}: {value}\n"
        
        full_prompt = f"{context_str}\n{prompt}"
        return await self.generate(full_prompt)
    
    async def chat_response(self, message: str) -> str:
        """Generate chat response maintaining conversation history"""
        try:
            response = await asyncio.to_thread(
                self.chat.send_message,
                message,
                generation_config=self.generation_config,
                safety_settings=self.safety_settings
            )
            
            return response.text if response.text else "No response generated."
            
        except Exception as e:
            self.logger.error(f"Chat error: {e}")
            return f"Chat error: {str(e)}"
    
    def reset_chat(self):
        """Reset chat history"""
        self.chat = self.model.start_chat(history=[])
    
    async def generate_structured(self, prompt: str, structure: Dict) -> Dict:
        """Generate structured response"""
        structured_prompt = f"""{prompt}

Please provide your response in the following JSON structure:
{json.dumps(structure, indent=2)}

Ensure the response is valid JSON."""
        
        response = await self.generate(structured_prompt)
        
        # Try to parse JSON response
        try:
            # Extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return {"error": "No JSON found in response", "raw_response": response}
        except json.JSONDecodeError:
            return {"error": "Invalid JSON in response", "raw_response": response}
    
    async def analyze_sentiment(self, text: str) -> Dict:
        """Analyze sentiment of text"""
        prompt = f"""Analyze the sentiment of the following text:

"{text}"

Provide response as JSON with:
- sentiment: positive/negative/neutral
- confidence: 0-1
- key_phrases: list of important phrases
- emotion: primary emotion detected"""

        return await self.generate_structured(prompt, {
            "sentiment": "string",
            "confidence": "number",
            "key_phrases": ["string"],
            "emotion": "string"
        })
    
    async def summarize(self, text: str, max_length: int = 100) -> str:
        """Summarize text"""
        prompt = f"""Summarize the following text in no more than {max_length} words:

{text}

Be concise and capture the key points."""
        
        return await self.generate(prompt)
    
    async def translate(self, text: str, target_language: str) -> str:
        """Translate text to target language"""
        prompt = f"""Translate the following text to {target_language}:

{text}

Provide only the translation."""
        
        return await self.generate(prompt)
    
    def update_generation_config(self, **kwargs):
        """Update generation configuration"""
        for key, value in kwargs.items():
            if hasattr(self.generation_config, key):
                setattr(self.generation_config, key, value)
    
    def get_model_info(self) -> Dict:
        """Get model information"""
        return {
            "model_name": self.model_name,
            "temperature": self.generation_config.temperature,
            "max_tokens": self.generation_config.max_output_tokens,
            "top_p": self.generation_config.top_p,
            "top_k": self.generation_config.top_k
        }