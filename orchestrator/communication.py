import asyncio
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime, timedelta
import json
import pytz

# Define UTC timezone as a constant
UTC = pytz.UTC

class AgentOrchestrator:
    """Orchestrates communication between different AI agents"""
    
    def __init__(self, llm_client):
        self.llm_client = llm_client
        self.agents = self._initialize_agents()
        self.conversation_history = []
        self.active_projects = {}
        self.logger = logging.getLogger(__name__)
        
    def _initialize_agents(self) -> Dict[str, Any]:
        """Initialize all agents with the LLM client"""
        from agents.ceo_agent import CEOAgent
        from agents.developer_agent import DeveloperAgent
        from agents.manager_agent import ProjectManagerAgent
        from agents.designer_agent import DesignerAgent
        
        return {
            'ceo': CEOAgent(self.llm_client),
            'developer': DeveloperAgent(self.llm_client),
            'project_manager': ProjectManagerAgent(self.llm_client),
            'designer': DesignerAgent(self.llm_client)
        }
    
    async def route_to_agent(self, agent_name: str, task: Dict) -> Dict:
        """Route task to specific agent"""
        agent = self.agents.get(agent_name)
        if not agent:
            return {
                "error": f"Agent {agent_name} not found",
                "available_agents": list(self.agents.keys())
            }
        
        try:
            response = await agent.process_task(task)
            self._log_interaction(agent_name, task, response)
            return response
        except Exception as e:
            self.logger.error(f"Error processing task with {agent_name}: {e}")
            return {
                "error": f"Error processing task: {str(e)}",
                "agent": agent_name
            }
    
    async def analyze_and_route(self, task: Dict) -> Dict:
        """Analyze task and route to most appropriate agent"""
        content = task.get('content', '').lower()
        
        # Keyword-based routing
        routing_rules = {
            'ceo': ['strategy', 'business', 'vision', 'market', 'growth', 'revenue'],
            'developer': ['code', 'technical', 'implement', 'bug', 'api', 'database'],
            'designer': ['design', 'ui', 'ux', 'user', 'interface', 'wireframe'],
            'project_manager': ['timeline', 'project', 'deadline', 'resource', 'sprint']
        }
        
        # Score each agent based on keyword matches
        agent_scores = {}
        for agent, keywords in routing_rules.items():
            score = sum(1 for keyword in keywords if keyword in content)
            if score > 0:
                agent_scores[agent] = score
        
        # Route to highest scoring agent, or CEO if no clear match
        if agent_scores:
            best_agent = max(agent_scores, key=agent_scores.get)
        else:
            best_agent = 'ceo'  # Default to CEO for general queries
        
        return await self.route_to_agent(best_agent, task)
    
    async def get_team_consensus(self, task: Dict) -> Dict[str, Dict]:
        """Get input from all team members on a task"""
        consensus = {
            "timestamp": self._format_datetime(self._get_current_time()),
            "responses": {}
        }
        
        # Get responses from all agents in parallel
        agent_tasks = []
        for agent_name, agent in self.agents.items():
            agent_task = agent.process_brief_task(task)
            agent_tasks.append((agent_name, agent_task))
        
        # Gather all responses
        for agent_name, agent_task in agent_tasks:
            try:
                response = await agent_task
                consensus["responses"][agent_name] = response
            except Exception as e:
                self.logger.error(f"Error getting response from {agent_name}: {e}")
                consensus["responses"][agent_name] = {
                    "error": str(e),
                    "content": "Unable to provide input at this time."
                }
        
        return consensus
    
    async def facilitate_collaboration(self, primary_agent: str, 
                                     supporting_agents: List[str], 
                                     task: Dict) -> Dict:
        """Facilitate collaboration between agents"""
        collaboration_result = {
            "primary_agent": primary_agent,
            "supporting_agents": supporting_agents,
            "task": task,
            "responses": {},
            "synthesis": ""
        }
        
        # Get primary agent response
        primary_response = await self.route_to_agent(primary_agent, task)
        collaboration_result["responses"][primary_agent] = primary_response
        
        # Get supporting agent inputs
        for agent in supporting_agents:
            support_task = {
                **task,
                "context": f"Supporting {primary_agent} with: {task.get('content', '')}",
                "primary_response": primary_response.get('content', '')
            }
            response = await self.route_to_agent(agent, support_task)
            collaboration_result["responses"][agent] = response
        
        # Synthesize responses
        synthesis = await self._synthesize_responses(collaboration_result["responses"])
        collaboration_result["synthesis"] = synthesis
        
        return collaboration_result
    
    async def _synthesize_responses(self, responses: Dict[str, Dict]) -> str:
        """Synthesize multiple agent responses into cohesive output"""
        synthesis_prompt = "Synthesize these team responses into a cohesive plan:\n\n"
        
        for agent, response in responses.items():
            content = response.get('content', 'No response')
            synthesis_prompt += f"{agent.upper()}:\n{content}\n\n"
        
        synthesis_prompt += """Create a unified response that:
1. Combines key insights from all team members
2. Resolves any conflicting recommendations
3. Provides clear, actionable next steps
4. Maintains each agent's expertise perspective"""
        
        synthesis = await self.llm_client.generate(synthesis_prompt)
        return synthesis
    
    async def run_project_workflow(self, project: Dict) -> Dict:
        """Run complete project workflow with all agents"""
        workflow_result = {
            "project": project,
            "phases": {},
            "timeline": "",
            "status": "initiated"
        }
        
        # Phase 1: CEO Strategic Approval
        ceo_task = {
            "type": "project_approval",
            "content": f"New project proposal: {project.get('name', 'Unnamed')}",
            "project_details": project
        }
        workflow_result["phases"]["strategic_approval"] = await self.route_to_agent("ceo", ceo_task)
        
        # Phase 2: Technical Feasibility
        dev_task = {
            "type": "technical_assessment",
            "content": f"Assess technical feasibility for {project.get('name', 'Unnamed')}",
            "requirements": project.get('requirements', [])
        }
        workflow_result["phases"]["technical_feasibility"] = await self.route_to_agent("developer", dev_task)
        
        # Phase 3: Design Concept
        design_task = {
            "type": "design_concept",
            "project_name": project.get('name', 'Unnamed'),
            "project_type": project.get('type', 'web'),
            "target_audience": project.get('target_audience', 'general users')
        }
        workflow_result["phases"]["design_concept"] = await self.route_to_agent("designer", design_task)
        
        # Phase 4: Project Planning
        pm_task = {
            "type": "project_planning",
            "project_name": project.get('name', 'Unnamed'),
            "requirements": project.get('requirements', []),
            "constraints": project.get('constraints', {})
        }
        workflow_result["phases"]["project_planning"] = await self.route_to_agent("project_manager", pm_task)
        
        # Generate summary
        workflow_result["summary"] = await self._generate_workflow_summary(workflow_result)
        workflow_result["status"] = "completed"
        
        return workflow_result
    
    async def _generate_workflow_summary(self, workflow_result: Dict) -> str:
        """Generate summary of workflow results"""
        summary_parts = ["Project Workflow Summary:\n"]
        
        for phase, result in workflow_result["phases"].items():
            phase_title = phase.replace('_', ' ').title()
            content = result.get('content', 'No content')[:200] + "..."
            summary_parts.append(f"\n{phase_title}:\n{content}")
        
        return "\n".join(summary_parts)
    
    def _get_current_time(self) -> datetime:
        """Get current time in UTC"""
        return datetime.now(UTC)
    
    def _format_datetime(self, dt: datetime) -> str:
        """Format datetime to ISO format string"""
        return dt.isoformat()
    
    def _log_interaction(self, agent: str, task: Dict, response: Dict):
        """Log interaction with timestamp"""
        interaction = {
            "timestamp": self._format_datetime(self._get_current_time()),
            "agent": agent,
            "task": task,
            "response": response
        }
        self.conversation_history.append(interaction)
        
        # Keep only last 100 interactions
        if len(self.conversation_history) > 100:
            self.conversation_history = self.conversation_history[-100:]
    
    async def get_project_status(self, status_task: Dict) -> Dict:
        """Get comprehensive project status from all agents"""
        project_name = status_task.get('content', '').replace('Status update for ', '')
        
        # Get status from each agent
        status_responses = {}
        
        # PM provides overall status
        pm_status = await self.route_to_agent("project_manager", {
            "type": "progress_update",
            "content": f"Provide status for {project_name}"
        })
        status_responses["project_overview"] = pm_status
        
        # Developer provides technical status
        dev_status = await self.route_to_agent("developer", {
            "type": "brief",
            "content": f"Technical progress on {project_name}"
        })
        status_responses["technical_status"] = dev_status
        
        # Designer provides design status
        design_status = await self.route_to_agent("designer", {
            "type": "brief",
            "content": f"Design progress on {project_name}"
        })
        status_responses["design_status"] = design_status
        
        # Compile comprehensive status
        return self._compile_status_report(status_responses)
    
    def _compile_status_report(self, responses: Dict) -> Dict:
        """Compile status responses into unified report"""
        compiled_status = "📊 **Project Status Report**\n\n"
        
        if "project_overview" in responses:
            compiled_status += "**Overall Status:**\n"
            compiled_status += responses["project_overview"].get("content", "No update")[:300] + "\n\n"
        
        if "technical_status" in responses:
            compiled_status += "**Technical Progress:**\n"
            compiled_status += responses["technical_status"].get("content", "No update")[:200] + "\n\n"
        
        if "design_status" in responses:
            compiled_status += "**Design Progress:**\n"
            compiled_status += responses["design_status"].get("content", "No update")[:200] + "\n"
        
        return {
            "content": compiled_status,
            "detailed_responses": responses,
            "timestamp": self._format_datetime(self._get_current_time())
        }
    
    def get_conversation_history(self, limit: int = 10) -> List[Dict]:
        """Get recent conversation history"""
        return self.conversation_history[-limit:]
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
    
    async def generate_team_report(self) -> Dict:
        """Generate a report of team activity"""
        report = {
            "timestamp": self._format_datetime(self._get_current_time()),
            "active_projects": len(self.active_projects),
            "recent_activity": self._analyze_recent_activity(),
            "agent_status": {}
        }
        
        # Get status from each agent
        for agent_name, agent in self.agents.items():
            report["agent_status"][agent_name] = {
                "recent_tasks": self._get_agent_recent_tasks(agent_name),
                "active_tasks": len([t for t in self.conversation_history 
                                   if t.get("agent") == agent_name 
                                   and t.get("timestamp", "") > self._format_datetime(
                                       self._get_current_time() - timedelta(hours=24)
                                   )])
            }
        
        return report
    
    def _analyze_recent_activity(self) -> Dict:
        """Analyze recent team activity"""
        activity = {
            "total_interactions": len(self.conversation_history),
            "most_active_agent": "",
            "common_task_types": {},
            "peak_activity_time": ""
        }
        
        if not self.conversation_history:
            return activity
        
        # Count agent interactions
        agent_counts = {}
        task_types = {}
        
        for interaction in self.conversation_history:
            agent = interaction.get("agent", "unknown")
            agent_counts[agent] = agent_counts.get(agent, 0) + 1
            
            task_type = interaction.get("task", {}).get("type", "general")
            task_types[task_type] = task_types.get(task_type, 0) + 1
        
        if agent_counts:
            activity["most_active_agent"] = max(agent_counts, key=agent_counts.get)
        
        activity["common_task_types"] = dict(sorted(
            task_types.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:5])
        
        return activity
    
    def _get_agent_recent_tasks(self, agent_name: str) -> List[str]:
        """Get recent tasks for specific agent"""
        recent_tasks = []
        
        for interaction in self.conversation_history[-10:]:
            if interaction.get("agent") == agent_name:
                task_type = interaction.get("task", {}).get("type", "unknown")
                timestamp = interaction.get("timestamp", "")
                recent_tasks.append(f"{task_type} - {timestamp}")
        
        return recent_tasks[-5:]  # Last 5 tasks