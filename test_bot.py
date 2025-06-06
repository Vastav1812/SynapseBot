# test_bot.py

import asyncio
import logging
from config import Config
from llm.gemini_client import GeminiClient
from orchestrator.communication import AgentOrchestrator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_components():
    """Test individual components"""
    try:
        # Validate configuration
        Config.validate()
        logger.info("✅ Configuration validated")
        
        # Test Gemini client
        logger.info("Testing Gemini client...")
        gemini_client = GeminiClient(Config.GEMINI_API_KEY)
        response = await gemini_client.generate("Hello, this is a test. Respond with 'Test successful!'")
        logger.info(f"Gemini response: {response[:100]}...")
        logger.info("✅ Gemini client working")
        
        # Test Orchestrator
        logger.info("Testing Orchestrator...")
        orchestrator = AgentOrchestrator(gemini_client)
        
        # Test routing to CEO
        ceo_response = await orchestrator.route_to_agent('ceo', {
            'type': 'test',
            'content': 'This is a test message',
            'brief': True
        })
        logger.info(f"CEO response: {ceo_response}")
        logger.info("✅ Orchestrator working")
        
        # Test team consensus
        logger.info("Testing team consensus...")
        consensus = await orchestrator.get_team_consensus({
            'type': 'test',
            'content': 'Should we proceed with testing?',
            'brief': True
        })
        logger.info(f"Team consensus received: {len(consensus.get('responses', {}))} responses")
        logger.info("✅ Team consensus working")
        
        logger.info("\n🎉 All components tested successfully!")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(test_components())