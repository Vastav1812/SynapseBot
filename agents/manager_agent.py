from .base_agent import BaseAgent
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
from enum import Enum
import pytz

class ProjectPhase(Enum):
    INITIATION = "initiation"
    PLANNING = "planning"
    EXECUTION = "execution"
    MONITORING = "monitoring"
    CLOSING = "closing"

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ProjectManagerAgent(BaseAgent):
    def __init__(self, llm_client=None):
        super().__init__(
            name="Mike Johnson",
            role="Project Manager",
            personality="Organized, methodical, risk-aware, collaborative, deadline-focused",
            llm_client=llm_client
        )
        
        self.skills = [
            "Project Planning",
            "Risk Management",
            "Resource Allocation",
            "Timeline Management",
            "Stakeholder Communication",
            "Agile Methodologies",
            "Scrum Master",
            "Budget Management",
            "Team Coordination",
            "Progress Tracking",
            "Quality Assurance",
            "Change Management"
        ]
        
        # PM-specific attributes
        self.methodologies = ["Agile", "Scrum", "Kanban", "Waterfall", "Hybrid"]
        self.project_tools = ["Jira", "Trello", "Asana", "Monday.com", "MS Project"]
        self.risk_register = []
        self.project_phases = ProjectPhase
        self.current_projects = {}
        
    def _define_capabilities(self):
        from .base_agent import AgentCapability
        return [
            AgentCapability.PLANNING,
            AgentCapability.ANALYSIS,
            AgentCapability.COMMUNICATION,
            AgentCapability.DECISION_MAKING
        ]
    
    def _define_response_style(self):
        return {
            "brief_format": "Structured timeline with key milestones",
            "focus_areas": ["timeline", "resources", "risks", "deliverables"],
            "communication_style": "clear, structured, action-oriented",
            "include_metrics": True
        }
    
    async def process_task(self, task: Dict) -> Dict:
        """Process project management tasks"""
        task_type = task.get("type")
        
        if "brief" in task_type or task.get("brief", False):
            return await self.process_brief_task(task)
        
        task_handlers = {
            "project_planning": self._handle_project_planning,
            "timeline_creation": self._handle_timeline_creation,
            "resource_allocation": self._handle_resource_allocation,
            "risk_assessment": self._handle_risk_assessment,
            "sprint_planning": self._handle_sprint_planning,
            "progress_update": self._handle_progress_update,
            "team_coordination": self._handle_team_coordination,
            "budget_planning": self._handle_budget_planning,
            "milestone_review": self._handle_milestone_review,
            "retrospective": self._handle_retrospective
        }
        
        handler = task_handlers.get(task_type, self._handle_general_pm)
        return await handler(task)
    
    async def process_brief_task(self, task: Dict) -> Dict:
        """PM's brief, structured responses"""
        content = task.get('content', '')
        
        if 'timeline' in content.lower() or 'schedule' in content.lower():
            prompt = f"""As Project Manager, provide timeline for: {content}

Format:
📅 Duration: [Total time estimate]
🎯 Key Milestone: [Most important deliverable - when]
⚠️ Critical Path: [What could delay project]
✅ First Week: [Immediate actions]"""

        elif 'risk' in content.lower():
            prompt = f"""As Project Manager, assess risk for: {content}

Format:
⚠️ Main Risk: [Biggest concern]
📊 Impact: [High/Medium/Low - why]
🛡️ Mitigation: [How to prevent/handle]
✅ Action: [Immediate step to take]"""

        elif 'team' in content.lower() or 'resource' in content.lower():
            prompt = f"""As Project Manager, plan resources for: {content}

Format:
👥 Team Needs: [Key roles required]
⏱️ Effort: [Person-days/weeks estimate]
🔄 Dependencies: [What blocks progress]
✅ Next Step: [How to proceed]"""

        else:
            prompt = f"""As Project Manager, provide project guidance on: {content}

Format:
📊 Assessment: [Project viability/complexity]
📅 Timeline: [Rough estimate]
👥 Resources: [Team size needed]
✅ Recommendation: [Clear next action]"""

        response = await self.llm_client.generate(prompt)
        
        return {
            "sender": self.name,
            "role": self.role,
            "content": response,
            "response_type": "brief_project",
            "urgency_level": self._assess_urgency(task),
            "requires_planning_session": self._needs_detailed_planning(content),
            "timestamp": datetime.now(pytz.UTC).isoformat()
        }
    
    async def _handle_project_planning(self, task: Dict) -> Dict:
        """Handle comprehensive project planning"""
        project_name = task.get('project_name', '')
        requirements = task.get('requirements', [])
        constraints = task.get('constraints', {})
        stakeholders = task.get('stakeholders', [])
        
        prompt = f"""As Project Manager, create comprehensive project plan for: {project_name}

Requirements: {json.dumps(requirements, indent=2)}
Constraints: {json.dumps(constraints, indent=2)}
Stakeholders: {', '.join(stakeholders) if stakeholders else 'Standard stakeholders'}

Project Plan:

1. Project Charter
   - Project Vision & Objectives
   - Success Criteria
   - Key Deliverables
   - Assumptions & Constraints

2. Scope Definition
   - In Scope: [What's included]
   - Out of Scope: [What's excluded]
   - Scope Management Process

3. Work Breakdown Structure (WBS)
   - Phase 1: [Major deliverables]
   - Phase 2: [Major deliverables]
   - Phase 3: [Major deliverables]

4. Project Timeline
   - Start Date: [Date]
   - Major Milestones:
     * Milestone 1: [Description - Date]
     * Milestone 2: [Description - Date]
     * Milestone 3: [Description - Date]
   - End Date: [Date]

5. Resource Plan
   - Core Team:
     * Role 1: [Responsibilities - % allocation]
     * Role 2: [Responsibilities - % allocation]
   - Extended Team: [Support roles]

6. Risk Management Plan
   - Top 5 Risks:
     * Risk 1: [Description - Mitigation]
     * Risk 2: [Description - Mitigation]

7. Communication Plan
   - Daily: [Standups, channels]
   - Weekly: [Reviews, reports]
   - Monthly: [Stakeholder updates]

8. Quality Assurance
   - Quality Standards
   - Review Process
   - Acceptance Criteria

9. Budget Estimate
   - Development: [Cost]
   - Resources: [Cost]
   - Contingency: [20% recommended]
   - Total: [Sum]"""

        response = await self.llm_client.generate(prompt)
        
        # Create project record
        project_id = f"proj_{datetime.now(pytz.UTC).strftime('%Y%m%d%H%M%S')}"
        self.current_projects[project_id] = {
            "name": project_name,
            "status": "planning",
            "created": datetime.now(pytz.UTC).isoformat()
        }
        
        return {
            "sender": self.name,
            "role": self.role,
            "content": response,
            "project_id": project_id,
            "methodology": self._recommend_methodology(requirements),
            "estimated_duration": self._estimate_duration(requirements),
            "team_size": self._estimate_team_size(requirements),
            "next_actions": self._define_next_actions("planning"),
            "timestamp": datetime.now(pytz.UTC).isoformat()
        }
    
    async def _handle_timeline_creation(self, task: Dict) -> Dict:
        """Create detailed project timeline"""
        project_details = task.get('project_details', {})
        deliverables = task.get('deliverables', [])
        dependencies = task.get('dependencies', [])
        
        prompt = f"""As Project Manager, create detailed timeline:

Project: {json.dumps(project_details, indent=2)}
Deliverables: {json.dumps(deliverables, indent=2)}
Dependencies: {json.dumps(dependencies, indent=2)}

Detailed Timeline:

1. Project Phases
   Phase 1: Initiation (Week 1)
   - [ ] Project kickoff
   - [ ] Stakeholder alignment
   - [ ] Team onboarding

   Phase 2: Planning (Week 2-3)
   - [ ] Requirements finalization
   - [ ] Technical design
   - [ ] Resource allocation

   Phase 3: Execution (Week 4-10)
   - [ ] Sprint 1: [Goals]
   - [ ] Sprint 2: [Goals]
   - [ ] Sprint 3: [Goals]
   - [ ] Sprint 4: [Goals]

   Phase 4: Testing (Week 11-12)
   - [ ] QA testing
   - [ ] User acceptance testing
   - [ ] Bug fixes

   Phase 5: Deployment (Week 13)
   - [ ] Production deployment
   - [ ] Documentation
   - [ ] Handover

2. Critical Path Analysis
   - Critical tasks: [List]
   - Float available: [Where flexibility exists]
   - Dependencies: [Key blockers]

3. Milestone Schedule
   - M1: [Description] - End of Week 3
   - M2: [Description] - End of Week 7
   - M3: [Description] - End of Week 10
   - M4: [Description] - End of Week 13

4. Resource Loading
   - Peak periods: [When most resources needed]
   - Resource conflicts: [Potential issues]
   - Mitigation strategies

Gantt Chart ASCII:
Week: 1 2 3 4 5 6 7 8 9 10 11 12 13
Plan: ███
Dev:     ████████████████
Test:                   ████
Deploy:                     █"""

        response = await self.llm_client.generate(prompt)
        
        return {
            "sender": self.name,
            "role": self.role,
            "content": response,
            "timeline_type": "detailed",
            "critical_path": self._identify_critical_path(deliverables, dependencies),
            "buffer_time": "20%",
            "tracking_method": "Weekly progress reviews",
            "visualization_available": True,
            "timestamp": datetime.now(pytz.UTC).isoformat()
        }
    
    async def _handle_resource_allocation(self, task: Dict) -> Dict:
        """Handle resource allocation planning"""
        available_resources = task.get('available_resources', {})
        project_needs = task.get('project_needs', {})
        timeline = task.get('timeline', {})
        
        prompt = f"""As Project Manager, optimize resource allocation:

Available Resources: {json.dumps(available_resources, indent=2)}
Project Needs: {json.dumps(project_needs, indent=2)}
Timeline: {json.dumps(timeline, indent=2)}

Resource Allocation Plan:

1. Team Composition
   - Core Team (100% allocated):
     * Lead Developer: [Name/TBD] - Full stack ownership
     * UI/UX Designer: [Name/TBD] - Design system
     * QA Engineer: [Name/TBD] - Test automation
   
   - Part-time Support (50% or less):
     * DevOps: 25% - Infrastructure setup
     * Data Analyst: 20% - Analytics implementation

2. Allocation Timeline
   Week 1-2: Designer (100%), PM (100%)
   Week 3-8: Developer (100%), Designer (50%), PM (75%)
   Week 9-10: Developer (100%), QA (100%), PM (100%)
   Week 11-12: All hands - deployment prep

3. Skill Gap Analysis
   - Required skills: [List]
   - Available skills: [List]
   - Gaps: [What's missing]
   - Solutions: [Training/hiring/outsourcing]

4. Resource Optimization
   - Parallel work streams
   - Cross-training opportunities
   - Efficiency improvements

5. Contingency Planning
   - Backup resources identified
   - Overtime budget allocated
   - External vendor options

6. Resource Costs
   - Internal: [Cost breakdown]
   - External: [If needed]
   - Total monthly burn rate: [Amount]"""

        response = await self.llm_client.generate(prompt)
        
        return {
            "sender": self.name,
            "role": self.role,
            "content": response,
            "allocation_type": "optimized",
            "utilization_rate": self._calculate_utilization(available_resources, project_needs),
            "bottlenecks": self._identify_resource_bottlenecks(available_resources, project_needs),
            "recommendations": self._resource_recommendations(available_resources, project_needs),
            "timestamp": datetime.now(pytz.UTC).isoformat()
        }
    
    async def _handle_risk_assessment(self, task: Dict) -> Dict:
        """Conduct comprehensive risk assessment"""
        project_scope = task.get('scope', {})
        complexity = task.get('complexity', 'medium')
        external_factors = task.get('external_factors', [])
        
        prompt = f"""As Project Manager, conduct risk assessment:

Project Scope: {json.dumps(project_scope, indent=2)}
Complexity: {complexity}
External Factors: {json.dumps(external_factors, indent=2)}

Risk Assessment:

1. Risk Identification
   Technical Risks:
   - R1: [Description] | Probability: H/M/L | Impact: H/M/L
   - R2: [Description] | Probability: H/M/L | Impact: H/M/L
   
   Resource Risks:
   - R3: [Description] | Probability: H/M/L | Impact: H/M/L
   
   Schedule Risks:
   - R4: [Description] | Probability: H/M/L | Impact: H/M/L
   
   External Risks:
   - R5: [Description] | Probability: H/M/L | Impact: H/M/L

2. Risk Matrix
   High Impact:    [R1] [R3]     []
   Medium Impact:  []   [R4]     [R2]
   Low Impact:     []   []       [R5]
                   High Med      Low
                   Probability

3. Mitigation Strategies
   For each high-priority risk:
   - Risk: [Description]
   - Mitigation: [Preventive actions]
   - Contingency: [If risk occurs]
   - Owner: [Responsible person]
   - Trigger: [Warning signs]

4. Risk Monitoring Plan
   - Weekly risk reviews
   - Risk register updates
   - Escalation procedures
   - Early warning indicators

5. Contingency Budget
   - Recommended: 20% of project budget
   - Allocation per risk category
   - Approval process

6. Risk Response Strategies
   - Accept: [Low impact risks]
   - Mitigate: [High probability risks]
   - Transfer: [Insurable risks]
   - Avoid: [Scope adjustments]"""

        response = await self.llm_client.generate(prompt)
        
        # Update risk register
        risks = self._extract_risks(response)
        self.risk_register.extend(risks)
        
        return {
            "sender": self.name,
            "role": self.role,
            "content": response,
            "risk_assessment_type": "comprehensive",
            "high_priority_risks": [r for r in risks if r['level'] == RiskLevel.HIGH],
            "total_risk_score": self._calculate_risk_score(risks),
            "mitigation_budget": self._estimate_mitigation_budget(project_scope),
            "review_frequency": "weekly",
            "timestamp": datetime.now(pytz.UTC).isoformat()
        }
    
    async def _handle_sprint_planning(self, task: Dict) -> Dict:
        """Handle agile sprint planning"""
        backlog_items = task.get('backlog', [])
        team_velocity = task.get('velocity', 30)
        sprint_length = task.get('sprint_length', 2)
        
        prompt = f"""As Project Manager, plan sprint:

Backlog Items: {json.dumps(backlog_items, indent=2)}
Team Velocity: {team_velocity} story points
Sprint Length: {sprint_length} weeks

Sprint Plan:

1. Sprint Goal
   - Primary objective: [Clear, achievable goal]
   - Success criteria: [Measurable outcomes]

2. Selected User Stories
   Story 1: [Title]
   - Points: [#]
   - Acceptance Criteria: [List]
   - Assigned to: [Team member]
   
   Story 2: [Title]
   - Points: [#]
   - Acceptance Criteria: [List]
   - Assigned to: [Team member]
   
   [Continue for all stories fitting velocity]

3. Sprint Capacity
   - Total capacity: {team_velocity} points
   - Committed: [Sum of selected stories]
   - Buffer: [Remaining capacity]

4. Daily Schedule
   - Standup: 9:00 AM daily
   - Core hours: 10 AM - 4 PM
   - Sprint events:
     * Planning: Day 1 (2 hours)
     * Review: Last day (1 hour)
     * Retrospective: Last day (1 hour)

5. Dependencies & Blockers
   - External dependencies: [List]
   - Potential blockers: [List]
   - Mitigation plan: [Actions]

6. Definition of Done
   - Code complete & reviewed
   - Tests written & passing
   - Documentation updated
   - Deployed to staging

7. Sprint Risks
   - [Risk 1: Mitigation]
   - [Risk 2: Mitigation]"""

        response = await self.llm_client.generate(prompt)
        
        return {
            "sender": self.name,
            "role": self.role,
            "content": response,
            "sprint_type": "scrum",
            "estimated_completion": f"{self._calculate_sprint_completion(backlog_items, team_velocity)}%",
            "recommended_stories": self._select_sprint_stories(backlog_items, team_velocity),
            "sprint_ceremonies": self._define_ceremonies(sprint_length),
            "tracking_metrics": ["velocity", "burndown", "cycle_time"],
            "timestamp": datetime.now(pytz.UTC).isoformat()
        }
    
    async def _handle_progress_update(self, task: Dict) -> Dict:
        """Generate project progress update"""
        project_id = task.get('project_id', '')
        current_status = task.get('status', {})
        metrics = task.get('metrics', {})
        
        prompt = f"""As Project Manager, provide progress update:

Project ID: {project_id}
Current Status: {json.dumps(current_status, indent=2)}
Metrics: {json.dumps(metrics, indent=2)}

Progress Update:

1. Executive Summary
   - Overall Status: [Green/Yellow/Red]
   - % Complete: [Overall progress]
   - On Track: [Yes/No - why]

2. Milestone Status
   ✅ Completed:
   - [Milestone 1] - [Date completed]
   
   🔄 In Progress:
   - [Milestone 2] - [% complete] - ETA: [Date]
   
   ⏳ Upcoming:
   - [Milestone 3] - Start: [Date]

3. Key Metrics
   - Budget: [% used] of [total]
   - Schedule: [Days ahead/behind]
   - Scope: [Changes since baseline]
   - Quality: [Defect rate/metrics]

4. Accomplishments This Period
   - [Achievement 1]
   - [Achievement 2]
   - [Achievement 3]

5. Issues & Risks
   🔴 Critical Issues:
   - [Issue]: [Impact] - [Action plan]
   
   🟡 Risks to Watch:
   - [Risk]: [Mitigation status]

6. Resource Status
   - Team utilization: [%]
   - Burnout risk: [Low/Medium/High]
   - Skills gaps: [Any identified]

7. Next Period Focus
   - Priority 1: [Task/milestone]
   - Priority 2: [Task/milestone]
   - Priority 3: [Task/milestone]

8. Stakeholder Actions Needed
   - [Decision needed from: Person]
   - [Approval needed for: Item]"""

        response = await self.llm_client.generate(prompt)
        
        return {
            "sender": self.name,
            "role": self.role,
            "content": response,
            "update_type": "comprehensive",
            "health_status": self._assess_project_health(current_status, metrics),
            "trend": self._analyze_trend(metrics),
            "forecast_completion": self._forecast_completion(current_status),
            "escalations_needed": self._identify_escalations(current_status),
            "timestamp": datetime.now(pytz.UTC).isoformat()
        }
    
    async def _handle_general_pm(self, task: Dict) -> Dict:
        """Handle general project management queries"""
        content = task.get('content', '')
        
        prompt = f"""As Project Manager, provide guidance on: {content}

Consider:
- Project best practices
- Risk management
- Team dynamics
- Timeline optimization
- Stakeholder management
- Quality assurance

Provide structured, actionable advice."""

        response = await self.llm_client.generate(prompt)
        
        return {
            "sender": self.name,
            "role": self.role,
            "content": response,
            "pm_area": self._identify_pm_area(content),
            "methodology_relevant": self._suggest_methodology(content),
            "tools_recommended": self._recommend_tools(content),
            "timestamp": datetime.now(pytz.UTC).isoformat()
        }
    
    # Helper methods
    def _assess_urgency(self, task: Dict) -> str:
        """Assess task urgency"""
        content = task.get('content', '').lower()
        urgent_keywords = ['urgent', 'asap', 'immediately', 'critical', 'emergency']
        
        if any(keyword in content for keyword in urgent_keywords):
            return "high"
        return "normal"
    
    def _needs_detailed_planning(self, content: str) -> bool:
        """Determine if detailed planning session is needed"""
        planning_indicators = ['complex', 'large', 'enterprise', 'multiple teams', 
                              'long-term', 'strategic']
        return any(indicator in content.lower() for indicator in planning_indicators)
    
    def _recommend_methodology(self, requirements: List[str]) -> str:
        """Recommend project methodology"""
        req_text = ' '.join(requirements).lower()
        
        if 'iterative' in req_text or 'changing' in req_text:
            return "Agile/Scrum"
        elif 'fixed' in req_text or 'regulatory' in req_text:
            return "Waterfall"
        elif 'continuous' in req_text:
            return "Kanban"
        return "Hybrid Agile"
    
    def _estimate_duration(self, requirements: List[str]) -> str:
        """Estimate project duration"""
        complexity = len(requirements)
        
        if complexity < 5:
            return "4-6 weeks"
        elif complexity < 10:
            return "2-3 months"
        elif complexity < 20:
            return "3-6 months"
        return "6-12 months"
    
    def _estimate_team_size(self, requirements: List[str]) -> int:
        """Estimate team size needed"""
        complexity = len(requirements)
        
        if complexity < 5:
            return 3
        elif complexity < 10:
            return 5
        elif complexity < 20:
            return 8
        return 12
    
    def _define_next_actions(self, phase: str) -> List[str]:
        """Define next actions based on phase"""
        actions = {
            "planning": [
                "Finalize requirements with stakeholders",
                "Conduct technical feasibility review",
                "Create detailed WBS",
                "Set up project infrastructure"
            ],
            "execution": [
                "Daily standups",
                "Weekly progress reviews",
                "Risk monitoring",
                "Quality checks"
            ],
            "closing": [
                "Final testing",
                "Documentation completion",
                "Lessons learned session",
                "Handover preparation"
            ]
        }
        return actions.get(phase, ["Review project status"])
    
    def _extract_risks(self, response: str) -> List[Dict]:
        """Extract risks from response"""
        risks = []
        risk_levels = {
            'critical': RiskLevel.CRITICAL,
            'high': RiskLevel.HIGH,
            'medium': RiskLevel.MEDIUM,
            'low': RiskLevel.LOW
        }
        
        lines = response.split('\n')
        for line in lines:
            for level_text, level_enum in risk_levels.items():
                if level_text in line.lower() and 'risk' in line.lower():
                    risks.append({
                        'description': line.strip(),
                        'level': level_enum,
                        'identified_date': datetime.now(pytz.UTC).isoformat()
                    })
        
        return risks
    
    def _calculate_risk_score(self, risks: List[Dict]) -> float:
        """Calculate overall risk score"""
        if not risks:
            return 0.0
        
        risk_weights = {
            RiskLevel.CRITICAL: 10,
            RiskLevel.HIGH: 5,
            RiskLevel.MEDIUM: 2,
            RiskLevel.LOW: 1
        }
        
        total_score = sum(risk_weights.get(r['level'], 0) for r in risks)
        max_possible = len(risks) * 10
        
        return (total_score / max_possible) if max_possible > 0 else 0.0
    
    def _estimate_mitigation_budget(self, project_scope: Dict) -> str:
        """Estimate risk mitigation budget"""
        base_budget = project_scope.get('budget', 100000)
        recommended_percentage = 0.2  # 20% for contingency
        
        mitigation_budget = base_budget * recommended_percentage
        return f"${mitigation_budget:,.0f} (20% of project budget)"
    
    def _identify_critical_path(self, deliverables: List, dependencies: List) -> List[str]:
        """Identify critical path tasks"""
        # Simplified critical path identification
        critical_tasks = []
        
        for deliverable in deliverables:
            if any(dep.get('critical', False) for dep in dependencies 
                   if dep.get('task') == deliverable):
                critical_tasks.append(deliverable)
        
        return critical_tasks if critical_tasks else ["Requirements", "Development", "Testing"]
    
    def _calculate_utilization(self, available: Dict, needed: Dict) -> float:
        """Calculate resource utilization"""
        if not available or not needed:
            return 0.0
        
        total_available = sum(available.values()) if isinstance(available, dict) else 0
        total_needed = sum(needed.values()) if isinstance(needed, dict) else 0
        
        if total_available == 0:
            return 1.0  # Over-utilized
        
        return min(1.0, total_needed / total_available)
    
    def _identify_resource_bottlenecks(self, available: Dict, needed: Dict) -> List[str]:
        """Identify resource bottlenecks"""
        bottlenecks = []
        
        for resource, need in needed.items():
            if resource in available:
                if need > available[resource]:
                    bottlenecks.append(f"{resource}: need {need}, have {available[resource]}")
            else:
                bottlenecks.append(f"{resource}: not available")
        
        return bottlenecks
    
    def _resource_recommendations(self, available: Dict, needed: Dict) -> List[str]:
        """Generate resource recommendations"""
        recommendations = []
        utilization = self._calculate_utilization(available, needed)
        
        if utilization > 0.9:
            recommendations.append("Consider hiring additional resources")
        if utilization > 0.8:
            recommendations.append("Plan for overtime budget")
        if len(self._identify_resource_bottlenecks(available, needed)) > 0:
            recommendations.append("Address bottlenecks through cross-training")
        
        recommendations.append("Maintain 10-15% buffer for unexpected needs")
        return recommendations
    
    def _calculate_sprint_completion(self, backlog: List, velocity: int) -> float:
        """Calculate expected sprint completion percentage"""
        if not backlog:
            return 100.0
        
        total_points = sum(item.get('points', 0) for item in backlog)
        if total_points == 0:
            return 100.0
        
        return min(100.0, (velocity / total_points) * 100)
    
    def _select_sprint_stories(self, backlog: List, velocity: int) -> List[Dict]:
        """Select stories for sprint based on velocity"""
        selected = []
        remaining_velocity = velocity
        
        # Sort by priority
        sorted_backlog = sorted(backlog, 
                               key=lambda x: x.get('priority', 999))
        
        for story in sorted_backlog:
            story_points = story.get('points', 0)
            if story_points <= remaining_velocity:
                selected.append(story)
                remaining_velocity -= story_points
        
        return selected
    
    def _define_ceremonies(self, sprint_length: int) -> Dict[str, str]:
        """Define sprint ceremonies schedule"""
        ceremonies = {
            "sprint_planning": f"Day 1 - {2 * sprint_length} hours",
            "daily_standup": "Every day - 15 minutes",
            "sprint_review": f"Day {sprint_length * 5} - 1 hour",
            "retrospective": f"Day {sprint_length * 5} - 1 hour"
        }
        
        if sprint_length > 2:
            ceremonies["mid_sprint_check"] = f"Day {sprint_length * 5 // 2} - 30 minutes"
        
        return ceremonies
    
    def _assess_project_health(self, status: Dict, metrics: Dict) -> str:
        """Assess overall project health"""
        # Simple health assessment
        budget_used = metrics.get('budget_used_percentage', 0)
        schedule_variance = metrics.get('schedule_variance_days', 0)
        scope_creep = metrics.get('scope_change_percentage', 0)
        
        issues = 0
        if budget_used > 80:
            issues += 1
        if schedule_variance < -5:
            issues += 1
        if scope_creep > 20:
            issues += 1
        
        if issues == 0:
            return "Green - Healthy"
        elif issues == 1:
            return "Yellow - Needs Attention"
        else:
            return "Red - Critical Issues"
    
    def _analyze_trend(self, metrics: Dict) -> str:
        """Analyze project trend"""
        velocity_trend = metrics.get('velocity_trend', 'stable')
        defect_trend = metrics.get('defect_trend', 'stable')
        
        if velocity_trend == 'increasing' and defect_trend == 'decreasing':
            return "Positive - Improving"
        elif velocity_trend == 'decreasing' or defect_trend == 'increasing':
            return "Negative - Declining"
        else:
            return "Stable - No significant change"
    
    def _forecast_completion(self, status: Dict) -> str:
        """Forecast project completion"""
        progress = status.get('progress_percentage', 0)
        days_elapsed = status.get('days_elapsed', 0)
        total_days = status.get('total_planned_days', 100)
        
        if progress == 0 or days_elapsed == 0:
            return "Unable to forecast"
        
        # Simple linear forecast
        days_per_percent = days_elapsed / progress
        estimated_total_days = days_per_percent * 100
        
        variance = estimated_total_days - total_days
        
        if variance > 10:
            return f"Delayed - Expected {int(variance)} days late"
        elif variance < -10:
            return f"Ahead - Expected {int(abs(variance))} days early"
        else:
            return "On track - Expected on time"
    
    def _identify_escalations(self, status: Dict) -> List[str]:
        """Identify issues needing escalation"""
        escalations = []
        
        if status.get('blocked_tasks', 0) > 0:
            escalations.append("Blocked tasks need executive intervention")
        if status.get('budget_variance', 0) > 0.1:
            escalations.append("Budget overrun requires approval")
        if status.get('key_resource_unavailable', False):
            escalations.append("Critical resource gap needs resolution")
        
        return escalations
    
    def _identify_pm_area(self, content: str) -> str:
        """Identify PM area from content"""
        content_lower = content.lower()
        
        areas = {
            'schedule': ['timeline', 'schedule', 'deadline', 'milestone'],
            'resource': ['team', 'resource', 'allocation', 'capacity'],
            'risk': ['risk', 'issue', 'problem', 'blocker'],
            'quality': ['quality', 'testing', 'defect', 'bug'],
            'communication': ['stakeholder', 'report', 'update', 'meeting'],
            'scope': ['scope', 'requirement', 'change', 'feature']
        }
        
        for area, keywords in areas.items():
            if any(keyword in content_lower for keyword in keywords):
                return area
        
        return "general"
    
    def _suggest_methodology(self, content: str) -> str:
        """Suggest methodology based on content"""
        content_lower = content.lower()
        
        if 'startup' in content_lower or 'mvp' in content_lower:
            return "Lean/Agile"
        elif 'enterprise' in content_lower or 'compliance' in content_lower:
            return "Waterfall/PRINCE2"
        elif 'continuous' in content_lower or 'devops' in content_lower:
            return "Kanban/DevOps"
        
        return "Agile/Scrum"
    
    def _recommend_tools(self, content: str) -> List[str]:
        """Recommend PM tools based on content"""
        content_lower = content.lower()
        tools = []
        
        if 'agile' in content_lower or 'scrum' in content_lower:
            tools.extend(["Jira", "Azure DevOps"])
        if 'simple' in content_lower or 'small' in content_lower:
            tools.extend(["Trello", "Asana"])
        if 'enterprise' in content_lower:
            tools.extend(["MS Project", "Smartsheet"])
        
        return list(set(tools))[:3]  # Top 3 unique tools
    
    async def collaborate_on_project_plan(self, project: Dict, team_members: List['BaseAgent']) -> Dict:
        """Collaborate on project planning with team"""
        pm_prompt = f"""As Project Manager, create initial project structure for: {project.get('name')}

Focus on:
1. Timeline and Milestones
2. Resource Requirements
3. Risk Identification
4. Success Metrics
5. Communication Plan

Be specific about deliverables and deadlines."""

        pm_plan = await self.llm_client.generate(pm_prompt)
        
        return {
            "sender": self.name,
            "role": self.role,
            "project_plan": pm_plan,
            "methodology": self._suggest_methodology(project.get('description', '')),
            "estimated_timeline": self._estimate_duration([]),
            "team_structure": self._define_team_structure(team_members),
            "first_sprint_plan": self._create_initial_sprint(),
            "timestamp": datetime.now(pytz.UTC).isoformat()
        }
    
    def _define_team_structure(self, team_members: List['BaseAgent']) -> Dict[str, str]:
        """Define team structure and responsibilities"""
        structure = {}
        for member in team_members:
            structure[member.role] = f"Responsible for {', '.join(member.skills[:3])}"
        return structure
    
    def _create_initial_sprint(self) -> Dict[str, Any]:
        """Create initial sprint plan"""
        return {
            "sprint_goal": "Setup and initial planning",
            "duration": "1 week",
                        "tasks": [
                "Project setup and infrastructure",
                "Requirements gathering",
                "Initial design concepts",
                "Technical architecture planning"
            ],
            "deliverables": [
                "Project charter",
                "Technical design document",
                "UI/UX wireframes",
                "Sprint backlog"
            ]
        }
    
    def generate_project_report(self) -> Dict[str, Any]:
        """Generate comprehensive project status report"""
        active_projects = [p for p in self.current_projects.values() 
                          if p.get('status') != 'completed']
        
        return {
            "project_manager": self.name,
            "active_projects": len(active_projects),
            "methodologies_used": self.methodologies[:3],
            "total_risks_tracked": len(self.risk_register),
            "high_priority_risks": len([r for r in self.risk_register 
                                       if r.get('level') == RiskLevel.HIGH]),
            "project_health_summary": self._summarize_project_health(),
            "resource_utilization": self._calculate_overall_utilization(),
            "upcoming_milestones": self._get_upcoming_milestones()
        }
    
    def _summarize_project_health(self) -> Dict[str, int]:
        """Summarize health of all projects"""
        health_summary = {
            "green": 0,
            "yellow": 0,
            "red": 0
        }
        
        # This would normally check actual project statuses
        # For now, return sample data
        health_summary["green"] = len(self.current_projects) * 0.6
        health_summary["yellow"] = len(self.current_projects) * 0.3
        health_summary["red"] = len(self.current_projects) * 0.1
        
        return health_summary
    
    def _calculate_overall_utilization(self) -> float:
        """Calculate overall resource utilization across projects"""
        # Simplified calculation
        # In real implementation, would aggregate from all projects
        return 0.75  # 75% utilization
    
    def _get_upcoming_milestones(self) -> List[Dict[str, str]]:
        """Get upcoming milestones across all projects"""
        # Sample milestones
        milestones = []
        for project_id, project in list(self.current_projects.items())[:3]:
            milestones.append({
                "project": project['name'],
                "milestone": "Phase completion",
                "due_date": (datetime.now(pytz.UTC) + timedelta(days=14)).strftime("%Y-%m-%d")
            })
        
        return milestones
    
    async def handle_team_coordination(self, team_members: List['BaseAgent'], task: Dict) -> Dict:
        """Coordinate team members for a task"""
        coordination_plan = f"""Team Coordination Plan for: {task.get('description', 'Task')}

Team Members Involved:
{chr(10).join([f"- {member.name} ({member.role})" for member in team_members])}

Coordination Strategy:
1. Daily sync meetings at 9 AM
2. Shared project board for visibility
3. Weekly progress reviews
4. Clear ownership matrix

Communication Channels:
- Immediate: Team chat
- Daily: Standup meetings  
- Weekly: Progress reports
- Ad-hoc: Video calls for blockers"""
        
        return {
            "sender": self.name,
            "role": self.role,
            "coordination_plan": coordination_plan,
            "meeting_schedule": self._create_meeting_schedule(),
            "collaboration_tools": ["Slack", "Jira", "Confluence"],
            "escalation_path": self._define_escalation_path(),
            "timestamp": datetime.now(pytz.UTC).isoformat()
        }
    
    def _create_meeting_schedule(self) -> Dict[str, str]:
        """Create standard meeting schedule"""
        return {
            "daily_standup": "9:00 AM - 15 min",
            "weekly_planning": "Monday 10:00 AM - 1 hour",
            "bi_weekly_review": "Every other Friday 2:00 PM - 1 hour",
            "monthly_retrospective": "Last Friday 3:00 PM - 1.5 hours"
        }
    
    def _define_escalation_path(self) -> List[str]:
        """Define escalation path for issues"""
        return [
            "Level 1: Team Lead - Immediate response",
            "Level 2: Project Manager - Within 2 hours",
            "Level 3: Program Manager - Within 4 hours",
            "Level 4: Executive Sponsor - Within 24 hours"
        ]
    
    async def _handle_budget_planning(self, task: Dict) -> Dict:
        """Handle budget planning requests"""
        project_scope = task.get('scope', {})
        duration = task.get('duration', '3 months')
        team_size = task.get('team_size', 5)
        
        prompt = f"""As Project Manager, create budget plan:

Project Scope: {json.dumps(project_scope, indent=2)}
Duration: {duration}
Team Size: {team_size}

Budget Plan:

1. Labor Costs
   - Development: ${team_size * 150 * 8 * 20}/month
   - Design: $[Amount]
   - QA: $[Amount]
   - PM: $[Amount]
   - Total Monthly Labor: $[Sum]

2. Infrastructure & Tools
   - Cloud hosting: $[Monthly]
   - Development tools: $[One-time + Monthly]
   - Monitoring tools: $[Monthly]
   - Security tools: $[Monthly]

3. External Services
   - Contractors: $[If needed]
   - Consultants: $[If needed]
   - Training: $[Budget]

4. Operational Costs
   - Meetings & Travel: $[Amount]
   - Equipment: $[Amount]
   - Software licenses: $[Amount]

5. Contingency
   - Risk mitigation: 15% of total
   - Scope changes: 10% of total
   - Total contingency: 25%

6. Total Budget
   - Monthly burn rate: $[Amount]
   - Total project cost: $[Amount]
   - Cost per deliverable: $[Breakdown]

7. Budget Tracking
   - Weekly reviews
   - Monthly reports
   - Variance thresholds
   - Approval levels"""

        response = await self.llm_client.generate(prompt)
        
        return {
            "sender": self.name,
            "role": self.role,
            "content": response,
            "budget_type": "comprehensive",
            "total_estimate": self._calculate_budget_estimate(team_size, duration),
            "cost_breakdown": self._create_cost_breakdown(team_size),
            "payment_schedule": self._define_payment_schedule(duration),
            "timestamp": datetime.now(pytz.UTC).isoformat()
        }
    
    def _calculate_budget_estimate(self, team_size: int, duration: str) -> str:
        """Calculate rough budget estimate"""
        # Parse duration
        months = 3  # default
        if 'month' in duration:
            months = int(duration.split()[0])
        elif 'week' in duration:
            months = int(duration.split()[0]) / 4
        
        # Rough calculation: $150/hour * 8 hours * 20 days * team_size
        monthly_cost = team_size * 150 * 8 * 20
        total_cost = monthly_cost * months
        
        # Add 30% for overhead and contingency
        total_with_overhead = total_cost * 1.3
        
        return f"${total_with_overhead:,.0f}"
    
    def _create_cost_breakdown(self, team_size: int) -> Dict[str, str]:
        """Create cost breakdown by category"""
        monthly_labor = team_size * 150 * 8 * 20
        
        return {
            "labor": f"${monthly_labor:,.0f} (70%)",
            "infrastructure": f"${monthly_labor * 0.15:,.0f} (10%)",
            "tools": f"${monthly_labor * 0.1:,.0f} (7%)",
            "contingency": f"${monthly_labor * 0.2:,.0f} (13%)"
        }
    
    def _define_payment_schedule(self, duration: str) -> List[str]:
        """Define payment milestones"""
        return [
            "20% - Project kickoff and planning complete",
            "30% - Design phase complete",
            "30% - Development phase complete",
            "15% - Testing and deployment complete",
            "5% - Project closure and handover"
        ]
    
    async def _handle_milestone_review(self, task: Dict) -> Dict:
        """Handle milestone review"""
        milestone = task.get('milestone', {})
        deliverables = task.get('deliverables', [])
        
        prompt = f"""As Project Manager, conduct milestone review:

Milestone: {json.dumps(milestone, indent=2)}
Deliverables: {json.dumps(deliverables, indent=2)}

Milestone Review:

1. Completion Status
   - Planned completion: [Date]
   - Actual completion: [Date]
   - Variance: [Days ahead/behind]

2. Deliverables Assessment
   ✅ Completed:
   - [Deliverable 1] - Quality: [Score]
   - [Deliverable 2] - Quality: [Score]
   
   ⏳ Pending:
   - [Deliverable 3] - Expected: [Date]

3. Success Criteria Evaluation
   - Criterion 1: [Met/Not Met] - [Evidence]
   - Criterion 2: [Met/Not Met] - [Evidence]

4. Lessons Learned
   What went well:
   - [Success 1]
   - [Success 2]
   
   What could improve:
   - [Improvement 1]
   - [Improvement 2]

5. Resource Performance
   - Team efficiency: [%]
   - Budget utilization: [%]
   - Time utilization: [%]

6. Stakeholder Feedback
   - Satisfaction score: [1-10]
   - Key feedback points
   - Action items

7. Next Milestone Preparation
   - Key dependencies
   - Risk mitigation needed
   - Resource adjustments"""

        response = await self.llm_client.generate(prompt)
        
        return {
            "sender": self.name,
            "role": self.role,
            "content": response,
            "review_type": "milestone",
            "milestone_health": self._assess_milestone_health(milestone, deliverables),
            "recommendations": self._milestone_recommendations(milestone),
            "next_milestone_risks": self._identify_next_milestone_risks(),
            "timestamp": datetime.now(pytz.UTC).isoformat()
        }
    
    def _assess_milestone_health(self, milestone: Dict, deliverables: List) -> str:
        """Assess milestone health"""
        completed = sum(1 for d in deliverables if d.get('status') == 'completed')
        total = len(deliverables)
        
        if total == 0:
            return "No deliverables defined"
        
        completion_rate = completed / total
        if completion_rate >= 0.9:
            return "Green - On track"
        elif completion_rate >= 0.7:
            return "Yellow - Minor delays"
        else:
            return "Red - Significant issues"
    
    def _milestone_recommendations(self, milestone: Dict) -> List[str]:
        """Generate milestone-based recommendations"""
        recommendations = []
        
        if milestone.get('delayed', False):
            recommendations.append("Accelerate critical path activities")
            recommendations.append("Consider parallel processing where possible")
        
        if milestone.get('budget_overrun', False):
            recommendations.append("Review and optimize resource allocation")
            recommendations.append("Identify cost-saving opportunities")
        
        recommendations.append("Conduct thorough quality checks before proceeding")
        recommendations.append("Update risk register based on learnings")
        
        return recommendations
    
    def _identify_next_milestone_risks(self) -> List[Dict[str, str]]:
        """Identify risks for next milestone"""
        return [
            {
                "risk": "Resource availability",
                "mitigation": "Confirm team allocation in advance"
            },
            {
                "risk": "Dependency delays",
                "mitigation": "Create buffer time for critical dependencies"
            },
            {
                "risk": "Scope creep",
                "mitigation": "Lock requirements before starting"
            }
        ]
    
    async def _handle_retrospective(self, task: Dict) -> Dict:
        """Handle retrospective facilitation"""
        sprint_data = task.get('sprint_data', {})
        team_feedback = task.get('feedback', [])
        
        prompt = f"""As Project Manager, facilitate retrospective:

Sprint Data: {json.dumps(sprint_data, indent=2)}
Team Feedback: {json.dumps(team_feedback, indent=2)}

Retrospective Summary:

1. Sprint Overview
   - Sprint goal achievement: [Yes/Partial/No]
   - Velocity achieved: [Points] vs planned: [Points]
   - Sprint satisfaction: [1-10 team average]

2. What Went Well 🎉
   - [Success 1]: [Why it worked]
   - [Success 2]: [Why it worked]
   - [Success 3]: [Why it worked]

3. What Didn't Go Well 😟
   - [Issue 1]: [Root cause]
   - [Issue 2]: [Root cause]
   - [Issue 3]: [Root cause]

4. Action Items 🎯
   - [Action 1]: Owner: [Name] - Due: [Date]
   - [Action 2]: Owner: [Name] - Due: [Date]
   - [Action 3]: Owner: [Name] - Due: [Date]

5. Team Mood & Dynamics
   - Overall mood: [Description]
   - Collaboration level: [High/Medium/Low]
   - Communication effectiveness: [Score]

6. Process Improvements
   - To start doing: [Practice]
   - To stop doing: [Practice]
   - To continue doing: [Practice]

7. Metrics & Trends
   - Velocity trend: [Increasing/Stable/Decreasing]
   - Quality metrics: [Defect rate, etc.]
   - Team happiness: [Trend]

8. Next Sprint Focus
   - Key improvement to implement
   - Team commitment
   - Success metrics"""

        response = await self.llm_client.generate(prompt)
        
        return {
            "sender": self.name,
            "role": self.role,
            "content": response,
            "retrospective_type": "sprint",
            "action_items": self._extract_action_items(response),
            "team_health": self._assess_team_health(team_feedback),
            "improvement_priorities": self._prioritize_improvements(response),
            "follow_up_date": (datetime.now(pytz.UTC) + timedelta(days=7)).isoformat(),
            "timestamp": datetime.now(pytz.UTC).isoformat()
        }
    
    def _extract_action_items(self, response: str) -> List[Dict[str, str]]:
        """Extract action items from retrospective"""
        action_items = []
        lines = response.split('\n')
        
        for line in lines:
            if 'action' in line.lower() and ':' in line:
                action_items.append({
                    "action": line.split(':')[0].strip(),
                    "details": line.split(':')[1].strip() if len(line.split(':')) > 1 else "",
                    "status": "pending"
                })
        
        return action_items[:5]  # Top 5 actions
    
    def _assess_team_health(self, feedback: List) -> str:
        """Assess team health from feedback"""
        if not feedback:
            return "No feedback available"
        
        # Simple sentiment analysis
        positive_words = ['good', 'great', 'excellent', 'happy', 'productive']
        negative_words = ['bad', 'difficult', 'frustrated', 'blocked', 'stress']
        
        feedback_text = ' '.join(str(f) for f in feedback).lower()
        positive_count = sum(1 for word in positive_words if word in feedback_text)
        negative_count = sum(1 for word in negative_words if word in feedback_text)
        
        if positive_count > negative_count * 2:
            return "Excellent - Team is thriving"
        elif positive_count > negative_count:
            return "Good - Generally positive"
        elif negative_count > positive_count:
            return "Concerning - Needs attention"
        else:
            return "Neutral - Room for improvement"
    
    def _prioritize_improvements(self, response: str) -> List[str]:
        """Prioritize improvements from retrospective"""
        improvements = []
        
        # Extract improvements from response
        if "to start doing" in response.lower():
            improvements.append("Implement new suggested practices")
        if "to stop doing" in response.lower():
            improvements.append("Eliminate identified inefficiencies")
        if "communication" in response.lower():
            improvements.append("Enhance team communication")
        
        return improvements[:3]
    
    async def handle_crisis_management(self, crisis: Dict) -> Dict:
        """Handle project crisis situations"""
        crisis_prompt = f"""As Project Manager, manage crisis situation:

Crisis: {crisis.get('description', 'Unknown crisis')}
Severity: {crisis.get('severity', 'high')}
Impact: {crisis.get('impact', 'Project timeline at risk')}

Crisis Management Plan:

1. Immediate Actions (Next 2 hours)
   - Assess full impact
   - Communicate to stakeholders
   - Mobilize crisis team
   - Stop affected work

2. Mitigation Strategy
   - Short-term fixes
   - Resource reallocation
   - Timeline adjustments
   - Quality trade-offs

3. Communication Plan
   - Stakeholder notifications
   - Team instructions
   - Status updates frequency
   - Escalation triggers

4. Recovery Plan
   - Recovery timeline
   - Additional resources needed
   - Risk mitigation steps
   - Success metrics"""

        response = await self.llm_client.generate(crisis_prompt)
        
        return {
            "sender": self.name,
            "role": self.role,
            "crisis_response": response,
            "response_time": "immediate",
            "escalation_level": self._determine_escalation_level(crisis),
            "recovery_timeline": self._estimate_recovery_time(crisis),
            "timestamp": datetime.now(pytz.UTC).isoformat()
        }
    
    def _determine_escalation_level(self, crisis: Dict) -> str:
        """Determine crisis escalation level"""
        severity = crisis.get('severity', 'medium')
        
        if severity == 'critical' or 'data loss' in crisis.get('description', '').lower():
            return "Executive - Immediate escalation required"
        elif severity == 'high':
            return "Senior Management - Within 1 hour"
        else:
            return "Project Level - Handle internally"
    
    def _estimate_recovery_time(self, crisis: Dict) -> str:
        """Estimate recovery time from crisis"""
        severity = crisis.get('severity', 'medium')
        
        recovery_times = {
            'critical': '1-2 weeks with all hands on deck',
            'high': '3-5 days with focused effort',
            'medium': '1-2 days with normal resources',
            'low': 'Within 24 hours'
        }
        
        return recovery_times.get(severity, '1 week')
    
    def calculate_project_velocity(self, completed_items: List[Dict]) -> float:
        """Calculate team velocity"""
        if not completed_items:
            return 0.0
        
        total_points = sum(item.get('story_points', 0) for item in completed_items)
        return total_points
    
    def forecast_project_completion(self, remaining_work: int, velocity: float) -> str:
        """Forecast project completion based on velocity"""
        if velocity <= 0:
            return "Unable to forecast - no velocity data"
        
        sprints_remaining = remaining_work / velocity
        weeks_remaining = sprints_remaining * 2  # Assuming 2-week sprints
        
        completion_date = datetime.now(pytz.UTC) + timedelta(weeks=weeks_remaining)
        return completion_date.strftime("%Y-%m-%d")
    
    def generate_burndown_data(self, sprint_data: Dict) -> Dict[str, List]:
        """Generate burndown chart data"""
        total_points = sprint_data.get('total_points', 0)
        completed_points = sprint_data.get('completed_points', [])
        
        ideal_burndown = []
        actual_burndown = []
        
        days = len(completed_points)
        daily_ideal = total_points / days if days > 0 else 0
        
        for day in range(days):
            ideal_burndown.append(total_points - (daily_ideal * (day + 1)))
            actual_burndown.append(total_points - sum(completed_points[:day+1]))
        
        return {
            "ideal": ideal_burndown,
            "actual": actual_burndown,
            "remaining": actual_burndown[-1] if actual_burndown else total_points
        }