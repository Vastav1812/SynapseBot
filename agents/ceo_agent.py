from .base_agent import BaseAgent
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import json
import asyncio
from enum import Enum
import pytz

class DecisionPriority(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class CEOAgent(BaseAgent):
    def __init__(self, llm_client=None):
        super().__init__(
            name="Alex Chen",
            role="Chief Executive Officer",
            personality="Visionary, strategic thinker, decisive, growth-oriented",
            llm_client=llm_client
        )
        
        self.skills = [
            "Strategic planning",
            "Decision making",
            "Team leadership",
            "Business development",
            "Stakeholder management",
            "Risk assessment",
            "Market analysis",
            "Vision setting"
        ]
        
        # CEO-specific attributes
        self.decision_history = []
        self.strategic_priorities = []
        self.risk_tolerance = "moderate"
        self.leadership_style = "transformational"
        
    def _define_capabilities(self):
        from .base_agent import AgentCapability
        return [
            AgentCapability.DECISION_MAKING,
            AgentCapability.ANALYSIS,
            AgentCapability.PLANNING,
            AgentCapability.COMMUNICATION
        ]
    
    def _define_response_style(self):
        return {
            "brief_format": "Executive summary with clear action items",
            "focus_areas": ["strategic impact", "ROI", "risk/reward", "market position"],
            "communication_style": "direct, inspiring, data-informed",
            "decision_framework": "SWOT + financial impact"
        }
    
    async def process_task(self, task: Dict) -> Dict:
        """Enhanced task processing with CEO-specific logic"""
        task_type = task.get("type")
        
        # Route to specialized handlers
        if "brief" in task_type or task.get("brief", False):
            return await self.process_brief_task(task)
        
        task_handlers = {
            "project_approval": self._handle_project_approval,
            "strategy_meeting": self._handle_strategy_meeting,
            "resource_allocation": self._handle_resource_allocation,
            "team_review": self._handle_team_review,
            "crisis_management": self._handle_crisis,
            "market_analysis": self._handle_market_analysis,
            "vision_setting": self._handle_vision_setting
        }
        
        handler = task_handlers.get(task_type, self._handle_general_strategic)
        return await handler(task)
    
    async def _handle_project_approval(self, task: Dict) -> Dict:
        """Handle project approval with enhanced decision framework"""
        content = task.get('content', '')
        context = task.get('context', {})
        
        prompt = f"""As CEO, evaluate this project proposal:

{content}

Consider:
1. Strategic Alignment: How does this fit our vision?
2. ROI Potential: Expected returns vs. investment
3. Resource Requirements: Team, time, budget
4. Risk Assessment: What could go wrong?
5. Market Impact: Competitive advantage gained

Provide:
- Decision: Approve/Reject/Modify
- Key Rationale (2-3 points)
- Conditions/Requirements
- Success Metrics
- Next Steps

Be decisive and strategic."""

        response = await self.llm_client.generate(prompt)
        
        # Extract decision
        decision = self._extract_decision(response)
        
        # Log decision
        self.decision_history.append({
            "timestamp": datetime.now(pytz.UTC).isoformat(),
            "type": "project_approval",
            "decision": decision,
            "rationale": response
        })
        
        return {
            "sender": self.name,
            "role": self.role,
            "content": response,
            "decision": decision,
            "priority": self._assess_priority(task),
            "follow_up_required": decision != "reject",
            "timestamp": datetime.now(pytz.UTC).isoformat()
        }
    
    async def _handle_strategy_meeting(self, task: Dict) -> Dict:
        """Handle strategy meeting preparation"""
        topics = task.get('topics', [])
        participants = task.get('participants', [])
        
        prompt = f"""Prepare strategic meeting agenda:

Topics: {', '.join(topics) if topics else 'General strategy review'}
Participants: {', '.join(participants) if participants else 'Leadership team'}

Structure:
1. Current State Analysis (5 min)
2. Key Opportunities/Challenges (10 min)
3. Strategic Options (15 min)
4. Decision Points (10 min)
5. Action Items & Ownership (10 min)

For each topic, provide:
- Executive insight
- Data needed
- Decision required
- Success metric"""

        response = await self.llm_client.generate(prompt)
        
        return {
            "sender": self.name,
            "role": self.role,
            "content": response,
            "meeting_type": "strategy",
            "estimated_duration": "50 minutes",
            "preparation_required": True,
            "timestamp": datetime.now(pytz.UTC).isoformat()
        }
    
    async def _handle_crisis(self, task: Dict) -> Dict:
        """Handle crisis management with rapid response"""
        crisis_details = task.get('content', '')
        severity = task.get('severity', 'high')
        
        prompt = f"""URGENT: Crisis Management Required

Situation: {crisis_details}
Severity: {severity}

Immediate CEO Response Needed:

1. Immediate Actions (First 24 hours):
   - Containment steps
   - Communication plan
   - Resource mobilization

2. Stakeholder Management:
   - Internal communication
   - External messaging
   - Key stakeholder outreach

3. Recovery Strategy:
   - Short-term fixes
   - Long-term solutions
   - Prevention measures

Be calm, decisive, and action-oriented."""

        response = await self.llm_client.generate(prompt)
        
        return {
            "sender": self.name,
            "role": self.role,
            "content": response,
            "response_type": "crisis_management",
            "priority": DecisionPriority.CRITICAL.value,
            "requires_immediate_action": True,
            "escalation_plan": self._generate_escalation_plan(severity),
            "timestamp": datetime.now(pytz.UTC).isoformat()
        }
    
    async def process_brief_task(self, task: Dict) -> Dict:
        """CEO's brief, strategic responses"""
        content = task.get('content', '')
        
        # Create focused prompt
        if 'project' in content.lower():
            prompt = f"""As CEO, provide strategic assessment of: {content}

Format:
💡 Opportunity: [1 line]
⚡ Strategic Fit: [1 line]
✅ Key Risk: [1 line]
🎯 Decision: [Clear yes/no/investigate further]"""

        elif 'market' in content.lower() or 'competitor' in content.lower():
            prompt = f"""As CEO, assess market situation: {content}

Format:
📊 Market Impact: [1 line]
🎯 Our Position: [1 line]
⚡ Strategic Response: [1 line]
✅ Next Step: [Specific action]"""

        else:
            prompt = f"""As CEO, provide executive guidance on: {content}

Format:
🎯 Strategic Priority: [High/Medium/Low]
💡 Key Insight: [1 line]
⚡ Business Impact: [1 line]
✅ Executive Decision: [Clear direction]"""

        response = await self.llm_client.generate(prompt)
        
        return {
            "sender": self.name,
            "role": self.role,
            "content": response,
            "response_type": "brief_strategic",
            "decision_confidence": self._calculate_confidence(task),
            "requires_follow_up": self._needs_follow_up(response),
            "timestamp": datetime.now(pytz.UTC).isoformat()
        }
    
    def _extract_decision(self, response: str) -> str:
        """Extract decision from response"""
        response_lower = response.lower()
        if "approve" in response_lower:
            return "approved"
        elif "reject" in response_lower:
            return "rejected"
        elif "modify" in response_lower or "conditional" in response_lower:
            return "conditional"
        return "review_required"
    
    def _assess_priority(self, task: Dict) -> str:
        """Assess task priority based on content and context"""
        content = task.get('content', '').lower()
        context = task.get('context', {})
        
        # Priority keywords
        critical_keywords = ['urgent', 'crisis', 'critical', 'immediate', 'emergency']
        high_keywords = ['important', 'strategic', 'major', 'significant']
        
        if any(keyword in content for keyword in critical_keywords):
            return DecisionPriority.CRITICAL.value
        elif any(keyword in content for keyword in high_keywords):
            return DecisionPriority.HIGH.value
        elif context.get('budget', 0) > 1000000:  # High budget items
            return DecisionPriority.HIGH.value
        
        return DecisionPriority.MEDIUM.value
    
    def _calculate_confidence(self, task: Dict) -> float:
        """Calculate confidence level for decision"""
        # Factors affecting confidence
        factors = {
            'data_available': 0.3,
            'expertise_match': 0.3,
            'risk_assessment': 0.2,
            'strategic_alignment': 0.2
        }
        
        confidence = 0.0
        content = task.get('content', '').lower()
        
        # Check data availability
        if any(word in content for word in ['data', 'metrics', 'analysis', 'report']):
            confidence += factors['data_available']
        
        # Check expertise match
        if any(skill.lower() in content for skill in self.skills):
            confidence += factors['expertise_match']
        
        # Risk assessment clarity
        if 'risk' in content or 'safe' in content:
            confidence += factors['risk_assessment']
        
        # Strategic alignment
        if any(word in content for word in ['strategy', 'vision', 'goal', 'objective']):
            confidence += factors['strategic_alignment']
        
        return min(confidence, 1.0)
    
    def _needs_follow_up(self, response: str) -> bool:
        """Determine if response requires follow-up"""
        follow_up_indicators = [
            'investigate', 'review', 'analyze further', 
            'need more', 'discuss', 'meeting', 'follow up'
        ]
        return any(indicator in response.lower() for indicator in follow_up_indicators)
    
    def _generate_escalation_plan(self, severity: str) -> Dict:
        """Generate escalation plan for crisis"""
        plans = {
            "critical": {
                "response_time": "immediate",
                "team": ["COO", "Legal", "PR", "Security"],
                "communication": "All hands meeting within 1 hour",
                "external": "Prepare stakeholder communication"
            },
            "high": {
                "response_time": "within 2 hours",
                "team": ["COO", "Relevant Department Heads"],
                "communication": "Leadership brief within 4 hours",
                "external": "Monitor and prepare if needed"
            },
            "medium": {
                "response_time": "within 24 hours",
                "team": ["Relevant Department Head"],
                "communication": "Email update to leadership",
                "external": "Standard protocols"
            }
        }
        return plans.get(severity, plans["medium"])
    
    async def _handle_resource_allocation(self, task: Dict) -> Dict:
        """Handle resource allocation decisions"""
        resources = task.get('resources', {})
        projects = task.get('projects', [])
        
        prompt = f"""As CEO, optimize resource allocation:

Available Resources:
{json.dumps(resources, indent=2) if resources else 'To be determined'}

Projects Requesting Resources:
{json.dumps(projects, indent=2) if projects else 'Multiple projects'}

Provide allocation strategy considering:
1. Strategic priorities alignment
2. ROI maximization
3. Risk distribution
4. Team capacity
5. Timeline constraints

Format:
- Priority 1 Project: [allocation]
- Priority 2 Project: [allocation]
- Reserve/Buffer: [amount]
- Rationale: [brief explanation]"""

        response = await self.llm_client.generate(prompt)
        
        return {
            "sender": self.name,
            "role": self.role,
            "content": response,
            "decision_type": "resource_allocation",
            "requires_approval": False,
            "implementation_timeline": "immediate",
            "review_cycle": "monthly",
            "timestamp": datetime.now(pytz.UTC).isoformat()
        }
    
    async def _handle_market_analysis(self, task: Dict) -> Dict:
        """Handle market analysis and competitive intelligence"""
        market_data = task.get('market_data', {})
        competitors = task.get('competitors', [])
        
        prompt = f"""As CEO, provide strategic market analysis:

Market Conditions: {json.dumps(market_data, indent=2) if market_data else 'Current market'}
Key Competitors: {', '.join(competitors) if competitors else 'Main competitors'}

Executive Analysis:
1. Market Position Assessment
   - Our strengths vs. competition
   - Market share trajectory
   
2. Strategic Opportunities
   - Untapped segments
   - Innovation gaps
   
3. Threats & Mitigation
   - Competitive threats
   - Market risks
   
4. Strategic Recommendation
   - 3-6 month focus
   - Resource allocation
   - Success metrics"""

        response = await self.llm_client.generate(prompt)
        
        return {
            "sender": self.name,
            "role": self.role,
            "content": response,
            "analysis_type": "market_strategic",
            "actionable_insights": self._extract_actionable_items(response),
            "competitor_response_needed": bool(competitors),
            "timestamp": datetime.now(pytz.UTC).isoformat()
        }
    
    async def _handle_vision_setting(self, task: Dict) -> Dict:
        """Handle vision and long-term strategy setting"""
        timeframe = task.get('timeframe', '3 years')
        focus_areas = task.get('focus_areas', [])
        
        prompt = f"""As CEO, articulate company vision:

Timeframe: {timeframe}
Focus Areas: {', '.join(focus_areas) if focus_areas else 'All business areas'}

Create inspiring vision addressing:

1. Where We're Going
   - Market position
   - Product/service evolution
   - Geographic expansion
   
2. How We'll Get There
   - Key strategies
   - Cultural principles
   - Innovation approach
   
3. Why It Matters
   - Customer impact
   - Team motivation
   - Market differentiation
   
4. Success Metrics
   - Quantifiable goals
   - Milestone markers

Be visionary yet actionable, inspiring yet realistic."""

        response = await self.llm_client.generate(prompt)
        
        # Update strategic priorities
        self.strategic_priorities = self._extract_priorities(response)
        
        return {
            "sender": self.name,
            "role": self.role,
            "content": response,
            "vision_type": "strategic",
            "timeframe": timeframe,
            "communication_plan": self._create_vision_rollout_plan(),
            "timestamp": datetime.now(pytz.UTC).isoformat()
        }
    
    async def _handle_team_review(self, task: Dict) -> Dict:
        """Handle team performance and organizational reviews"""
        team_data = task.get('team_data', {})
        review_type = task.get('review_type', 'quarterly')
        
        prompt = f"""As CEO, conduct {review_type} team review:

Team Performance Data: {json.dumps(team_data, indent=2) if team_data else 'Overall team'}

Executive Assessment:

1. Team Strengths
   - What's working well
   - Star performers/teams
   
2. Areas for Improvement
   - Performance gaps
   - Skill deficiencies
   
3. Organizational Health
   - Culture indicators
   - Engagement levels
   
4. Strategic Alignment
   - Team goals vs. company vision
   - Resource optimization
   
5. Action Items
   - Immediate changes
   - Long-term development
   - Recognition needed"""

        response = await self.llm_client.generate(prompt)
        
        return {
            "sender": self.name,
            "role": self.role,
            "content": response,
            "review_type": review_type,
            "follow_up_meetings": self._identify_follow_up_meetings(response),
            "hr_actions_required": self._identify_hr_actions(response),
            "timestamp": datetime.now(pytz.UTC).isoformat()
        }
    
    async def _handle_general_strategic(self, task: Dict) -> Dict:
        """Handle general strategic questions"""
        content = task.get('content', '')
        
        prompt = f"""As CEO, provide strategic guidance on: {content}

Consider:
- Business impact
- Strategic alignment
- Resource implications
- Risk/opportunity balance
- Stakeholder effects

Provide executive perspective with clear direction."""

        response = await self.llm_client.generate(prompt)
        
        return {
            "sender": self.name,
            "role": self.role,
            "content": response,
            "requires_team_input": self._requires_team_input(content),
            "strategic_importance": self._assess_strategic_importance(content),
            "timestamp": datetime.now(pytz.UTC).isoformat()
        }
    
    def _extract_priorities(self, vision_response: str) -> List[str]:
        """Extract strategic priorities from vision statement"""
        # Simple extraction - can be enhanced with NLP
        priorities = []
        lines = vision_response.split('\n')
        
        for line in lines:
            if any(word in line.lower() for word in ['priority', 'focus', 'key', 'strategic']):
                priorities.append(line.strip())
        
        return priorities[:5]  # Top 5 priorities
    
    def _create_vision_rollout_plan(self) -> Dict:
        """Create plan for rolling out vision to organization"""
        return {
            "week_1": "Leadership team alignment session",
            "week_2": "Department head cascading meetings",
            "week_3": "All-hands presentation",
            "week_4": "Team-level integration workshops",
            "ongoing": "Quarterly progress reviews and adjustments"
        }
    
    def _identify_follow_up_meetings(self, review: str) -> List[Dict]:
        """Identify needed follow-up meetings from review"""
        meetings = []
        
        if "performance" in review.lower():
            meetings.append({
                "type": "performance_improvement",
                "participants": ["HR", "Department Heads"],
                "timeline": "within 1 week"
            })
        
        if "recognition" in review.lower():
            meetings.append({
                "type": "recognition_planning",
                "participants": ["HR", "Finance"],
                "timeline": "within 2 weeks"
            })
        
        return meetings
    
    def _identify_hr_actions(self, review: str) -> List[str]:
        """Identify HR actions from review"""
        actions = []
        review_lower = review.lower()
        
        if "training" in review_lower or "skill" in review_lower:
            actions.append("Develop training program")
        if "hire" in review_lower or "recruit" in review_lower:
            actions.append("Initiate recruitment process")
        if "culture" in review_lower:
            actions.append("Conduct culture assessment")
        
        return actions
    
    def _requires_team_input(self, content: str) -> List[str]:
        """Determine which team members should provide input"""
        content_lower = content.lower()
        team_input = []
        
        if any(word in content_lower for word in ['technical', 'development', 'code']):
            team_input.append("CTO/Developer")
        if any(word in content_lower for word in ['design', 'user', 'experience']):
            team_input.append("Designer")
        if any(word in content_lower for word in ['timeline', 'project', 'delivery']):
            team_input.append("Project Manager")
        
        return team_input
    
    def _assess_strategic_importance(self, content: str) -> str:
        """Assess strategic importance of the issue"""
        content_lower = content.lower()
        
        high_importance_keywords = [
            'revenue', 'growth', 'competitive', 'market share',
            'strategic', 'vision', 'culture', 'major'
        ]
        
        if any(keyword in content_lower for keyword in high_importance_keywords):
            return "high"
        
        return "medium"
    
    def _analyze_decision_pattern(self) -> Dict:
        """Analyze patterns in decision making"""
        if not self.decision_history:
            return {"pattern": "No decisions yet"}
        
        patterns = {
            "approval_rate": 0,
            "common_considerations": [],
            "average_response_time": "immediate",
            "risk_preference": self.risk_tolerance
        }
        
        approved = sum(1 for d in self.decision_history if d.get('decision') == 'approved')
        patterns['approval_rate'] = approved / len(self.decision_history) if self.decision_history else 0
        
        return patterns
    
    async def collaborate_on_strategic_initiative(self, initiative: Dict, team_members: List['BaseAgent']) -> Dict:
        """Lead strategic initiative with team collaboration"""
        initiative_name = initiative.get('name', 'Strategic Initiative')
        
        # CEO sets the vision and framework
        ceo_prompt = f"""As CEO, establish framework for strategic initiative: {initiative_name}

Define:
1. Vision & Success Criteria
2. Key Milestones
3. Resource Allocation
4. Risk Tolerance
5. Decision Rights

Be clear and inspiring."""

        ceo_framework = await self.llm_client.generate(ceo_prompt)
        
        # Prepare collaboration request for team
        collaboration_request = {
            "initiative": initiative_name,
            "ceo_framework": ceo_framework,
            "required_inputs": {
                "developer": "Technical feasibility and architecture",
                "designer": "User experience and market appeal",
                "pm": "Timeline and resource planning"
            }
        }
        
        return {
            "sender": self.name,
            "role": self.role,
            "initiative_framework": ceo_framework,
            "collaboration_request": collaboration_request,
            "next_step": "Await team input for comprehensive strategy",
            "decision_timeline": "48 hours",
            "timestamp": datetime.now(pytz.UTC).isoformat()
        }
    
    def generate_executive_dashboard(self) -> Dict:
        """Generate executive dashboard data"""
        return {
            "strategic_health": {
                "vision_alignment": self._calculate_vision_alignment(),
                "execution_speed": "on-track",
                "team_morale": "high",
                "market_position": "growing"
            },
            "recent_decisions": self.get_decision_summary(),
            "key_metrics": {
                "decision_velocity": f"{len(self.decision_history)} decisions this period",
                "strategic_initiatives": len(self.strategic_priorities),
                "risk_level": self.risk_tolerance
            },
            "attention_required": self._identify_attention_areas()
        }
    
    def _calculate_vision_alignment(self) -> float:
        """Calculate how well current activities align with vision"""
        # Simplified calculation - can be enhanced
        if not self.strategic_priorities:
            return 0.5
        
        # Check recent decisions against priorities
        alignment_score = 0.7  # Base score
        
        if len(self.decision_history) > 3:
            alignment_score = 0.85
        
        return alignment_score
    
    def _identify_attention_areas(self) -> List[Dict]:
        """Identify areas requiring CEO attention"""
        attention_areas = []
        
        # Check decision history for patterns
        if self.decision_history:
            recent_rejections = sum(1 for d in self.decision_history[-5:] 
                                   if d.get('decision') == 'rejected')
            if recent_rejections > 2:
                attention_areas.append({
                    "area": "Project Quality",
                    "concern": "High rejection rate",
                    "action": "Review project submission criteria"
                })
        
        # Always include strategic review
        attention_areas.append({
            "area": "Strategic Review",
            "concern": "Quarterly assessment due",
            "action": "Schedule leadership strategy session"
        })
        
        return attention_areas