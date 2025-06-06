# main.py
import asyncio
import logging
from datetime import timezone
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, Defaults
from telegram_bot.bot import SynapseBot
from orchestrator.communication import AgentOrchestrator
from llm.gemini_client import GeminiClient
from config import Config
import os
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class SynapseBotApp:
    def __init__(self):
        self.application = None
        self.bot = None
        self.is_running = False
    
    async def initialize(self):
        """Initialize all components"""
        try:
            load_dotenv()
            
            # Validate configuration
            if not Config.validate():
                logger.error("Configuration validation failed")
                return False
            
            # Initialize components
            logger.info("Initializing Gemini LLM client...")
            gemini_client = GeminiClient(
                api_key=Config.GEMINI_API_KEY,
                model_name=Config.GEMINI_MODEL,
                **Config.get_model_config()
            )
            
            logger.info("Initializing Agent Orchestrator...")
            orchestrator = AgentOrchestrator(
                llm_client=gemini_client,
                **Config.get_agent_config()
            )
            
            logger.info("Initializing Synapse Bot...")
            self.bot = SynapseBot(
                token=Config.TELEGRAM_BOT_TOKEN,
                gemini_client=gemini_client,
                orchestrator=orchestrator
            )
            
            # Create application with fixed timezone (no more pytz deprecation warning)
            defaults = Defaults(tzinfo=timezone.utc)
            self.application = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).defaults(defaults).build()
            
            # Add handlers
            self.application.add_handler(CommandHandler("start", self.bot.start))
            self.application.add_handler(CommandHandler("newproject", self.bot.new_project))
            self.application.add_handler(CommandHandler("status", self.bot.status_command))
            self.application.add_handler(CommandHandler("team", self.bot.team_command))
            self.application.add_handler(CommandHandler("help", self.bot.help_command))
            self.application.add_handler(CallbackQueryHandler(self.bot.handle_callback_query))
            self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.bot.handle_message))
            
            logger.info("Bot initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error during initialization: {e}")
            return False
    
    async def start_polling(self):
        """Start the bot polling"""
        try:
            if not self.application:
                raise RuntimeError("Application not initialized")
            
            logger.info("Starting bot polling...")
            self.is_running = True
            
            # Initialize the application
            await self.application.initialize()
            await self.application.start()
            await self.application.updater.start_polling(
                allowed_updates=Update.ALL_TYPES,
                drop_pending_updates=True
            )
            
            # Keep the bot running
            logger.info("Bot is now running. Press Ctrl+C to stop.")
            try:
                # Use a simple wait loop instead of complex event handling
                while self.is_running:
                    await asyncio.sleep(1)
            except asyncio.CancelledError:
                logger.info("Polling cancelled")
            
        except Exception as e:
            logger.error(f"Error during polling: {e}")
            raise
        finally:
            await self.cleanup()
    
    async def cleanup(self):
        """Clean up resources properly"""
        try:
            self.is_running = False
            logger.info("Shutting down application...")
            
            if self.application:
                # Stop updater first
                if self.application.updater and self.application.updater.running:
                    await self.application.updater.stop()
                
                # Then stop and shutdown the application
                if self.application.running:
                    await self.application.stop()
                
                await self.application.shutdown()
                
            logger.info("Cleanup completed successfully")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def stop(self):
        """Stop the bot"""
        self.is_running = False

async def main():
    """Main async function"""
    app = SynapseBotApp()
    
    try:
        # Initialize the app
        if not await app.initialize():
            logger.error("Failed to initialize application")
            return
        
        # Start polling
        await app.start_polling()
        
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
        app.stop()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        app.stop()
        raise

def run_bot():
    """Run the bot with proper event loop handling"""
    try:
        # Check if we're already in an event loop
        try:
            loop = asyncio.get_running_loop()
            logger.error("Cannot run bot inside an existing event loop")
            logger.info("Please run this script in a new terminal or restart your Python environment")
            return False
        except RuntimeError:
            # No existing loop, we can proceed
            pass
        
        # Run the bot
        asyncio.run(main())
        return True
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
        return True
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        return False

if __name__ == "__main__":
    success = run_bot()
    if not success:
        exit(1)
