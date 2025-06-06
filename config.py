import os
from dotenv import load_dotenv
from typing import Dict, Any

# Load environment variables
load_dotenv()

class Config:
    """Application configuration"""
    
    # Bot Configuration
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    BOT_USERNAME = os.getenv('BOT_USERNAME', 'SynapseBot')
    
    # Gemini Configuration
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-1.5-flash')
    
    # Model Parameters
    MODEL_TEMPERATURE = float(os.getenv('MODEL_TEMPERATURE', '0.7'))
    MODEL_TOP_P = float(os.getenv('MODEL_TOP_P', '0.95'))
    MODEL_TOP_K = int(os.getenv('MODEL_TOP_K', '40'))
    MODEL_MAX_TOKENS = int(os.getenv('MODEL_MAX_TOKENS', '2048'))
    
    # Application Settings
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # Database Configuration (if needed)
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///synapse_bot.db')
    
    # Rate Limiting
    RATE_LIMIT_MESSAGES = int(os.getenv('RATE_LIMIT_MESSAGES', '30'))
    RATE_LIMIT_WINDOW = int(os.getenv('RATE_LIMIT_WINDOW', '60'))  # seconds
    
    # Agent Configuration
    AGENT_RESPONSE_TIMEOUT = int(os.getenv('AGENT_RESPONSE_TIMEOUT', '30'))  # seconds
    MAX_CONVERSATION_HISTORY = int(os.getenv('MAX_CONVERSATION_HISTORY', '100'))
    
    # Feature Flags
    ENABLE_VOICE_MESSAGES = os.getenv('ENABLE_VOICE_MESSAGES', 'False').lower() == 'true'
    ENABLE_FILE_UPLOAD = os.getenv('ENABLE_FILE_UPLOAD', 'True').lower() == 'true'
    ENABLE_INLINE_MODE = os.getenv('ENABLE_INLINE_MODE', 'False').lower() == 'true'
    
    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration"""
        required = ['TELEGRAM_BOT_TOKEN', 'GEMINI_API_KEY']
        missing = []
        
        for field in required:
            if not getattr(cls, field):
                missing.append(field)
        
        if missing:
            print(f"Missing required configuration: {', '.join(missing)}")
            return False
        
        return True
    
    @classmethod
    def get_model_config(cls) -> Dict[str, Any]:
        """Get model configuration"""
        return {
            'temperature': cls.MODEL_TEMPERATURE,
            'top_p': cls.MODEL_TOP_P,
            'top_k': cls.MODEL_TOP_K,
            'max_output_tokens': cls.MODEL_MAX_TOKENS
        }
    
    @classmethod
    def get_agent_config(cls) -> Dict[str, Any]:
        """Get agent configuration"""
        return {
            'timeout': cls.AGENT_RESPONSE_TIMEOUT,
            'max_history': cls.MAX_CONVERSATION_HISTORY
        }