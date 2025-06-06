# main.py

import asyncio
import logging
import os
from dotenv import load_dotenv

# Import components
from llm.gemini_client import GeminiClient
from orchestrator.communication import AgentOrchestrator
from telegram_bot.bot import SynapseBot

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    """Main function to run the Synapse Bot"""
    try:
        # Get configuration from environment
        telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
        gemini_api_key = os.getenv('GEMINI_API_KEY')
        
        if not telegram_token:
            raise ValueError("TELEGRAM_BOT_TOKEN not found in environment variables")
        
        if not gemini_api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        # Initialize Gemini client
        logger.info("Initializing Gemini client...")
        gemini_client = GeminiClient(
            api_key=gemini_api_key,
            model_name=os.getenv('GEMINI_MODEL', 'gemini-1.5-flash')
        )
        
        # Initialize orchestrator
        logger.info("Initializing agent orchestrator...")
        orchestrator = AgentOrchestrator(gemini_client)
        
        # Initialize and run bot
        logger.info("Initializing Telegram bot...")
        bot = SynapseBot(
            token=telegram_token,
            gemini_client=gemini_client,
            orchestrator=orchestrator
        )
        
        # Run the bot
        logger.info("Starting bot...")
        bot.run()
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise

if __name__ == "__main__":
    main()