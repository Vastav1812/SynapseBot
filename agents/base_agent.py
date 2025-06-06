from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Tuple
import json
from datetime import datetime
from dataclasses import dataclass, field
import asyncio
from enum import Enum
import pytz

class AgentCapability(Enum):
    """Define agent capabilities for better routing"""
    ANALYSIS = "analysis"
    DECISION_MAKING = "decision_making"
    CREATIVE = "creative"
    TECHNICAL = "technical"
    PLANNING = "planning"
    COMMUNICATION = "communication"

@dataclass
class AgentContext:
    """Enhanced context tracking for each agent"""
    conversation_history: List[Dict] = field(default_factory=list)
    current_task: Optional[Dict] = None
    active_project: Optional[str] = None
    user_preferences: Dict = field(default_factory=dict)
    collaboration_requests: List[Dict] = field(default_factory=list)
    expertise_confidence: Dict[str, float] = field(default_factory=dict)

class BaseAgent(ABC):
    """Enhanced base agent with advanced capabilities"""
    
    def __init__(self, name: str, role: str, personality: str, llm_client=None):
        self.name = name
        self.role = role
        self.personality = personality
        self.memory = []
        self.skills = []
        self.llm_client = llm_client
        self.context = AgentContext()
        self.capabilities = self._define_capabilities()
        self.response_style = self._define_response_style()
        self.collaboration_mode = False
        self.brief_mode = False
        
    @abstractmethod
    def _define_capabilities(self) -> List[AgentCapability]:
        """Define specific capabilities for each agent type"""
        pass
    
    @abstractmethod
    def _define_response_style(self) -> Dict[str, Any]:
        """Define how this agent should format responses"""
        pass
    
    def analyze_task_relevance(self, task: Dict) -> float:
        """Determine how relevant this task is to the agent's expertise"""
        task_keywords = self._extract_keywords(task.get('content', ''))
        relevance_score = 0.0
        
        for keyword in task_keywords:
            for capability in self.capabilities:
                if self._matches_capability(keyword, capability):
                    relevance_score += 0.2
                    
        return min(relevance_score, 1.0)
    
    def should_participate(self, task: Dict) -> bool:
        """Decide if this agent should participate in the task"""
        relevance = self.analyze_task_relevance(task)
        threshold = 0.3  # Configurable threshold
        return relevance >= threshold
    
    async def process_brief_task(self, task: Dict) -> Dict:
        """Enhanced brief task processing with structured output"""
        prompt = self._create_brief_prompt(task)
        response = await self._generate_brief_response(prompt, task.get('context'))
        
        return {
            "sender": self.name,
            "role": self.role,
            "content": response,
            "response_type": "brief",
            "confidence": self.analyze_task_relevance(task),
            "suggestions": self._extract_actionable_items(response),
            "timestamp": datetime.now(pytz.UTC).isoformat()
        }
    
    def _create_brief_prompt(self, task: Dict) -> str:
        """Create an enhanced brief prompt"""
        task_type = task.get('type', 'general')
        content = task.get('content', '')
        
        style_guide = self.response_style.get('brief_format', '')
        
        return f"""As {self.role}, provide a brief, actionable response.
        
Task Type: {task_type}
Question: {content}

Response Style: {style_guide}
Focus on: {', '.join(self.response_style.get('focus_areas', []))}

Provide:
1. One key insight (1-2 lines)
2. One specific recommendation (1-2 lines)
3. One next step (1 line)

Be {self.personality}."""

    async def collaborate_with_agent(self, other_agent: 'BaseAgent', task: Dict) -> Dict:
        """Enable agent-to-agent collaboration"""
        collaboration_prompt = f"""
I am {self.name} ({self.role}), collaborating with {other_agent.name} ({other_agent.role}).
Task: {task.get('content')}

My perspective based on my {self.role} expertise:
"""
        
        my_response = await self._generate_brief_response(
            collaboration_prompt, 
            task.get('context')
        )
        
        return {
            "collaboration": True,
            "agents": [self.name, other_agent.name],
            "perspectives": {
                self.name: my_response
            },
            "synthesis_needed": True
        }
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords for capability matching"""
        # Simple implementation - can be enhanced with NLP
        keywords = text.lower().split()
        return [word for word in keywords if len(word) > 3]
    
    def _matches_capability(self, keyword: str, capability: AgentCapability) -> bool:
        """Check if keyword matches a capability"""
        capability_keywords = {
            AgentCapability.ANALYSIS: ['analyze', 'data', 'metrics', 'insights'],
            AgentCapability.DECISION_MAKING: ['decide', 'choice', 'strategy', 'direction'],
            AgentCapability.CREATIVE: ['design', 'create', 'innovate', 'idea'],
            AgentCapability.TECHNICAL: ['code', 'develop', 'implement', 'technical'],
            AgentCapability.PLANNING: ['plan', 'schedule', 'timeline', 'milestone'],
            AgentCapability.COMMUNICATION: ['communicate', 'present', 'explain', 'clarify']
        }
        
        return keyword in capability_keywords.get(capability, [])
    
    def _extract_actionable_items(self, response: str) -> List[str]:
        """Extract actionable items from response"""
        # Simple implementation - looks for action verbs
        action_verbs = ['create', 'develop', 'implement', 'review', 'analyze', 
                       'design', 'build', 'test', 'deploy', 'plan']
        
        sentences = response.split('.')
        actionable = []
        
        for sentence in sentences:
            if any(verb in sentence.lower() for verb in action_verbs):
                actionable.append(sentence.strip())
                
        return actionable[:3]  # Return top 3 actionable items
    
    async def _generate_brief_response(self, prompt: str, context: Optional[str]) -> str:
        """Generate a brief response using LLM"""
        if not self.llm_client:
            return "LLM client not configured"
            
        try:
            # Add context management
            full_prompt = prompt
            if context:
                full_prompt = f"Context: {context}\n\n{prompt}"
            
            # Add response constraints
            full_prompt += "\n\nKeep response under 100 words. Be specific and actionable."
            
            response = await self.llm_client.generate(full_prompt)
            return response
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    def update_context(self, interaction: Dict):
        """Update agent's context with new interaction"""
        self.context.conversation_history.append(interaction)
        
        # Keep only last 10 interactions for memory efficiency
        if len(self.context.conversation_history) > 10:
            self.context.conversation_history = self.context.conversation_history[-10:]
    
    def get_status_summary(self) -> Dict:
        """Get agent's current status and activity summary"""
        return {
            "agent": self.name,
            "role": self.role,
            "active": self.context.current_task is not None,
            "recent_interactions": len(self.context.conversation_history),
            "confidence_areas": {
                k: v for k, v in self.context.expertise_confidence.items() 
                if v > 0.7
            },
            "collaboration_mode": self.collaboration_mode
        }
    
    def suggest_next_agent(self, task: Dict) -> Optional[str]:
        """Suggest which agent should handle the task next"""
        # This can be overridden by specific agents
        task_type = task.get('type', '')
        
        suggestions = {
            'technical': 'developer',
            'design': 'designer',
            'planning': 'manager',
            'strategic': 'ceo'
        }
        
        for key, agent in suggestions.items():
            if key in task_type.lower():
                return agent
                
        return None