from .base_agent import BaseAgent
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from enum import Enum
import json
import re
import pytz

class TechStack(Enum):
    FRONTEND = "frontend"
    BACKEND = "backend"
    DATABASE = "database"
    DEVOPS = "devops"
    MOBILE = "mobile"
    AI_ML = "ai_ml"

class DeveloperAgent(BaseAgent):
    def __init__(self, llm_client=None):
        super().__init__(
            name="Sarah Kim",
            role="Lead Developer",
            personality="Technical expert, pragmatic problem-solver, detail-oriented, innovative",
            llm_client=llm_client
        )
        
        self.skills = [
            "Full-stack development",
            "System architecture",
            "Code review",
            "Performance optimization",
            "Security best practices",
            "API design",
            "Database optimization",
            "DevOps practices",
            "AI/ML implementation"
        ]
        
        # Developer-specific attributes
        self.tech_stack_expertise = {
            TechStack.FRONTEND: ["React", "Vue", "TypeScript", "Next.js"],
            TechStack.BACKEND: ["Python", "Node.js", "Go", "FastAPI"],
            TechStack.DATABASE: ["PostgreSQL", "MongoDB", "Redis", "Elasticsearch"],
            TechStack.DEVOPS: ["Docker", "Kubernetes", "CI/CD", "AWS", "Terraform"],
            TechStack.AI_ML: ["TensorFlow", "PyTorch", "Scikit-learn", "LangChain"]
        }
        self.code_quality_standards = {
            "test_coverage": 0.8,
            "code_review_required": True,
            "documentation_standard": "comprehensive"
        }
        
    def _define_capabilities(self):
        from .base_agent import AgentCapability
        return [
            AgentCapability.TECHNICAL,
            AgentCapability.ANALYSIS,
            AgentCapability.CREATIVE,
            AgentCapability.PLANNING
        ]
    
    def _define_response_style(self):
        return {
            "brief_format": "Technical assessment with implementation path",
            "focus_areas": ["feasibility", "performance", "scalability", "security"],
            "communication_style": "clear, precise, solution-oriented",
            "code_examples": True
        }
    
    async def process_task(self, task: Dict) -> Dict:
        """Process technical tasks with specialized handlers"""
        task_type = task.get("type")
        
        if "brief" in task_type or task.get("brief", False):
            return await self.process_brief_task(task)
        
        task_handlers = {
            "code_review": self._handle_code_review,
            "architecture_design": self._handle_architecture_design,
            "bug_fix": self._handle_bug_fix,
            "feature_implementation": self._handle_feature_implementation,
            "technical_assessment": self._handle_technical_assessment,
            "performance_optimization": self._handle_performance_optimization,
            "security_audit": self._handle_security_audit,
            "tech_stack_recommendation": self._handle_tech_stack_recommendation
        }
        
        handler = task_handlers.get(task_type, self._handle_general_technical)
        return await handler(task)
    
    async def process_brief_task(self, task: Dict) -> Dict:
        """Developer's brief, technical responses"""
        content = task.get('content', '')
        
        # Create focused technical prompt
        if 'implement' in content.lower() or 'build' in content.lower():
            prompt = f"""As Lead Developer, provide implementation approach for: {content}

Format:
🔧 Tech Approach: [1 line - key technology/method]
⚡ Complexity: [Simple/Medium/Complex - time estimate]
🔒 Key Risk: [Main technical challenge]
✅ Next Step: [Immediate action to start]"""

        elif 'bug' in content.lower() or 'fix' in content.lower():
            prompt = f"""As Lead Developer, diagnose issue: {content}

Format:
🐛 Likely Cause: [1 line diagnosis]
�� Debug Approach: [1 line - how to investigate]
⚡ Quick Fix: [Temporary solution if applicable]
✅ Permanent Fix: [Proper solution approach]"""

        elif 'performance' in content.lower() or 'optimize' in content.lower():
            prompt = f"""As Lead Developer, optimize performance for: {content}

Format:
📊 Bottleneck: [Likely performance issue]
⚡ Quick Win: [Immediate optimization]
🚀 Full Solution: [Comprehensive approach]
📈 Expected Improvement: [Estimated gain]"""

        else:
            prompt = f"""As Lead Developer, provide technical guidance on: {content}

Format:
🔧 Technical Assessment: [1 line summary]
💡 Best Practice: [Recommended approach]
⚠️ Watch Out: [Common pitfall to avoid]
✅ Implementation: [First step to take]"""

        response = await self.llm_client.generate(prompt)
        
        return {
            "sender": self.name,
            "role": self.role,
            "content": response,
            "response_type": "brief_technical",
            "technical_confidence": self._calculate_technical_confidence(task),
            "requires_code_sample": self._needs_code_sample(content),
            "timestamp": datetime.now(pytz.UTC).isoformat()
        }
    
    async def _handle_tech_stack_recommendation(self, task: Dict) -> Dict:
        """Handle technology stack recommendations"""
        project_type = task.get('project_type', '')
        requirements = task.get('requirements', [])
        team_expertise = task.get('team_expertise', [])
        budget = task.get('budget', 'moderate')
        
        prompt = f"""As Lead Developer, recommend technology stack:

Project Type: {project_type}
Requirements: {json.dumps(requirements, indent=2)}
Team Expertise: {', '.join(team_expertise) if team_expertise else 'Full-stack team'}
Budget: {budget}

Technology Recommendations:

1. Frontend Stack
   - Framework: [Choice with reasoning]
   - State Management: [If applicable]
   - UI Library: [Component library]
   - Build Tools: [Webpack/Vite/etc]

2. Backend Stack
   - Language: [Choice with reasoning]
   - Framework: [Specific framework]
   - API Type: [REST/GraphQL/gRPC]
   - Authentication: [Strategy]

3. Database Layer
   - Primary DB: [SQL/NoSQL choice]
   - Caching: [Redis/Memcached]
   - Search: [If needed]

4. DevOps & Infrastructure
   - Cloud Provider: [AWS/GCP/Azure]
   - Container Strategy: [Docker/K8s]
   - CI/CD: [Tools and pipeline]
   - Monitoring: [Tools]

5. Development Tools
   - Version Control: [Git workflow]
   - Project Management: [Tools]
   - Communication: [Slack/Teams]

6. Cost Analysis
   - Initial setup cost
   - Monthly running cost
   - Scaling cost projection

Justify each choice based on requirements and constraints."""

        response = await self.llm_client.generate(prompt)
        
        return {
            "sender": self.name,
            "role": self.role,
            "content": response,
            "recommendation_type": "tech_stack",
            "stack_summary": self._extract_tech_stack(response),
            "learning_curve": self._assess_learning_curve(team_expertise, response),
            "estimated_costs": self._estimate_stack_costs(response, budget),
            "implementation_roadmap": self._create_tech_roadmap(response),
            "timestamp": datetime.now(pytz.UTC).isoformat()
        }

    async def _handle_general_technical(self, task: Dict) -> Dict:
        """Handle general technical questions"""
        content = task.get('content', '')
        
        prompt = f"""As Lead Developer, provide technical expertise on: {content}

Consider:
- Technical feasibility
- Best practices
- Implementation complexity
- Performance implications
- Security considerations
- Maintenance requirements

Provide clear technical guidance with examples where helpful."""

        response = await self.llm_client.generate(prompt)
        
        return {
            "sender": self.name,
            "role": self.role,
            "content": response,
            "technical_complexity": self._assess_complexity(content),
            "requires_poc": self._needs_proof_of_concept(content),
            "related_skills": self._identify_required_skills(content),
            "timestamp": datetime.now(pytz.UTC).isoformat()
        }

    def _calculate_technical_confidence(self, task: Dict) -> float:
        """Calculate confidence in technical assessment"""
        content = task.get('content', '').lower()
        confidence = 0.5  # Base confidence
        
        # Check for expertise match
        for tech_area, techs in self.tech_stack_expertise.items():
            for tech in techs:
                if tech.lower() in content:
                    confidence += 0.1
        
        # Check for skill match
        for skill in self.skills:
            if skill.lower() in content:
                confidence += 0.05
        
        return min(confidence, 1.0)

    def _needs_code_sample(self, content: str) -> bool:
        """Determine if response needs code sample"""
        code_indicators = ['implement', 'code', 'function', 'class', 'api', 
                          'example', 'how to', 'syntax', 'algorithm']
        return any(indicator in content.lower() for indicator in code_indicators)

    def _extract_quality_score(self, review: str) -> float:
        """Extract quality score from code review"""
        import re
        match = re.search(r'Rate:\s*(\d+(?:\.\d+)?)/10', review)
        if match:
            return float(match.group(1))
        
        # Fallback: analyze sentiment
        if 'excellent' in review.lower():
            return 9.0
        elif 'good' in review.lower():
            return 7.5
        elif 'needs improvement' in review.lower():
            return 5.0
        return 6.0

    def _extract_issues(self, review: str) -> Dict[str, List[str]]:
        """Extract issues from code review"""
        issues = {
            'critical': [],
            'improvements': []
        }
        
        lines = review.split('\n')
        current_section = None
        
        for line in lines:
            line_lower = line.lower()
            if 'critical' in line_lower or 'bug' in line_lower or 'security' in line_lower:
                current_section = 'critical'
            elif 'improvement' in line_lower or 'suggestion' in line_lower:
                current_section = 'improvements'
            elif current_section and line.strip().startswith('-'):
                issues[current_section].append(line.strip())
        
        return issues

    def _assess_scalability(self, scale: str) -> str:
        """Assess scalability requirements"""
        scale_ratings = {
            'small': 'basic',
            'medium': 'moderate',
            'large': 'high',
            'enterprise': 'extreme'
        }
        return scale_ratings.get(scale.lower(), 'moderate')

    def _define_implementation_phases(self, requirements: List[str]) -> List[Dict]:
        """Define implementation phases based on requirements"""
        phases = []
        
        # Phase 1: Core functionality
        phases.append({
            "phase": 1,
            "name": "Core Implementation",
            "duration": "2-3 weeks",
            "deliverables": ["Basic functionality", "API structure", "Database schema"]
        })
        
        # Phase 2: Enhanced features
        if len(requirements) > 3:
            phases.append({
                "phase": 2,
                "name": "Feature Enhancement",
                "duration": "3-4 weeks",
                "deliverables": ["Advanced features", "Integration points", "Performance optimization"]
            })
        
        # Phase 3: Production readiness
        phases.append({
            "phase": 3,
            "name": "Production Preparation",
            "duration": "1-2 weeks",
            "deliverables": ["Security hardening", "Monitoring setup", "Documentation"]
        })
        
        return phases

    def _extract_tech_stack(self, response: str) -> Dict[str, List[str]]:
        """Extract technology stack from response"""
        tech_stack = {
            'frontend': [],
            'backend': [],
            'database': [],
            'devops': []
        }
        
        lines = response.split('\n')
        current_category = None
        
        for line in lines:
            line_lower = line.lower()
            if 'frontend' in line_lower:
                current_category = 'frontend'
            elif 'backend' in line_lower:
                current_category = 'backend'
            elif 'database' in line_lower:
                current_category = 'database'
            elif 'devops' in line_lower or 'infrastructure' in line_lower:
                current_category = 'devops'
            elif current_category and ':' in line:
                tech = line.split(':')[1].strip().split('[')[0].strip()
                if tech:
                    tech_stack[current_category].append(tech)
        
        return tech_stack

    def _extract_effort_estimate(self, response: str) -> Dict[str, str]:
        """Extract effort estimates from response"""
        import re
        effort = {
            'development': 'unknown',
            'testing': 'unknown',
            'total': 'unknown'
        }
        
        # Look for time patterns
        dev_match = re.search(r'Development:\s*(\d+\s*(?:hours?|days?|weeks?))', response)
        test_match = re.search(r'Testing:\s*(\d+\s*(?:hours?|days?|weeks?))', response)
        total_match = re.search(r'Total:\s*(\d+\s*(?:hours?|days?|weeks?))', response)
        
        if dev_match:
            effort['development'] = dev_match.group(1)
        if test_match:
            effort['testing'] = test_match.group(1)
        if total_match:
            effort['total'] = total_match.group(1)
        
        return effort

    def _identify_technical_risks(self, response: str) -> List[str]:
        """Identify technical risks from response"""
        risks = []
        risk_keywords = ['risk', 'challenge', 'concern', 'issue', 'problem', 'difficult']
        
        lines = response.split('\n')
        for line in lines:
            if any(keyword in line.lower() for keyword in risk_keywords):
                risks.append(line.strip())
        
        return risks[:5]  # Top 5 risks

    def _extract_dependencies(self, response: str) -> List[str]:
        """Extract dependencies from response"""
        dependencies = []
        dep_keywords = ['dependency', 'depends on', 'requires', 'needs']
        
        lines = response.split('\n')
        for line in lines:
            if any(keyword in line.lower() for keyword in dep_keywords):
                dependencies.append(line.strip())
        
        return dependencies

    def _assess_bug_severity(self, description: str, error_logs: str) -> str:
        """Assess bug severity"""
        critical_indicators = ['crash', 'data loss', 'security', 'production down', '500 error']
        high_indicators = ['performance', 'memory leak', 'incorrect data', 'authentication']
        
        combined_text = (description + ' ' + error_logs).lower()
        
        if any(indicator in combined_text for indicator in critical_indicators):
            return 'critical'
        elif any(indicator in combined_text for indicator in high_indicators):
            return 'high'
        return 'medium'

    def _determine_testing_requirements(self, severity: str) -> Dict[str, bool]:
        """Determine testing requirements based on severity"""
        return {
            'unit_tests': True,
            'integration_tests': severity in ['critical', 'high'],
            'regression_tests': severity == 'critical',
            'performance_tests': 'performance' in severity.lower(),
            'manual_qa': severity == 'critical'
        }

    def _suggest_monitoring(self, bug_description: str) -> List[str]:
        """Suggest monitoring improvements"""
        monitoring = []
        
        if 'performance' in bug_description.lower():
            monitoring.append("Add performance metrics tracking")
        if 'error' in bug_description.lower():
            monitoring.append("Enhance error logging and alerting")
        if 'memory' in bug_description.lower():
            monitoring.append("Add memory usage monitoring")
        
        monitoring.append("Add specific metric for this component")
        return monitoring

    def _calculate_expected_improvement(self, current: Dict, target: Dict) -> Dict[str, float]:
        """Calculate expected performance improvement"""
        improvements = {}
        
        for metric, current_value in current.items():
            if metric in target and isinstance(current_value, (int, float)):
                target_value = target[metric]
                if isinstance(target_value, (int, float)) and current_value > 0:
                    improvement = ((target_value - current_value) / current_value) * 100
                    improvements[metric] = round(improvement, 2)
        
        return improvements

    def _prioritize_optimizations(self, response: str) -> List[Dict[str, str]]:
        """Prioritize optimization recommendations"""
        priorities = []
        
        sections = response.split('\n\n')
        for section in sections:
            if 'quick win' in section.lower():
                priorities.append({
                    "priority": "immediate",
                    "type": "quick_win",
                    "description": section.strip()
                })
            elif 'medium-term' in section.lower():
                priorities.append({
                    "priority": "medium",
                    "type": "refactoring",
                    "description": section.strip()
                })
            elif 'long-term' in section.lower():
                priorities.append({
                    "priority": "low",
                    "type": "architecture",
                    "description": section.strip()
                })
        
        return sorted(priorities, key=lambda x: {'immediate': 0, 'medium': 1, 'low': 2}[x['priority']])

    def _create_performance_monitoring_plan(self, component: str) -> Dict[str, Any]:
        """Create performance monitoring plan"""
        return {
            "metrics": {
                "response_time": "p50, p95, p99 latencies",
                "throughput": "requests per second",
                "error_rate": "4xx and 5xx errors percentage",
                "resource_usage": "CPU, memory, disk I/O"
            },
            "tools": {
                "apm": "DataDog or New Relic",
                "logging": "ELK stack or CloudWatch",
                "custom_metrics": "Prometheus + Grafana"
            },
            "alerts": {
                "response_time": "Alert if p95 > 500ms",
                "error_rate": "Alert if error rate > 1%",
                "resource_usage": "Alert if CPU > 80% for 5 min"
            },
            "review_frequency": "weekly" if component == "critical" else "monthly"
        }

    def _extract_vulnerabilities(self, response: str) -> Dict[str, int]:
        """Extract vulnerability counts from security audit"""
        vulnerabilities = {
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 0,
            'total': 0
        }
        
        lines = response.split('\n')
        for line in lines:
            line_lower = line.lower()
            if 'critical' in line_lower and any(char.isdigit() for char in line):
                vulnerabilities['critical'] += 1
            elif 'high' in line_lower and any(char.isdigit() for char in line):
                vulnerabilities['high'] += 1
            elif 'medium' in line_lower and any(char.isdigit() for char in line):
                vulnerabilities['medium'] += 1
            elif 'low' in line_lower and any(char.isdigit() for char in line):
                vulnerabilities['low'] += 1
        
        vulnerabilities['total'] = sum(vulnerabilities.values()) - vulnerabilities['total']
        return vulnerabilities

    def _assess_compliance(self, requirements: List[str], response: str) -> Dict[str, bool]:
        """Assess compliance with requirements"""
        compliance = {}
        response_lower = response.lower()
        
        for req in requirements:
            req_lower = req.lower()
            # Simple check - can be enhanced
            compliance[req] = req_lower in response_lower or 'compliant' in response_lower
        
        return compliance

    def _create_remediation_timeline(self, vulnerabilities: Dict[str, int]) -> Dict[str, str]:
        """Create remediation timeline based on vulnerabilities"""
        timeline = {}
        
        if vulnerabilities['critical'] > 0:
            timeline['critical'] = "Immediate - within 24 hours"
        if vulnerabilities['high'] > 0:
            timeline['high'] = "Within 1 week"
        if vulnerabilities['medium'] > 0:
            timeline['medium'] = "Within 1 month"
        if vulnerabilities['low'] > 0:
            timeline['low'] = "Next quarter"
        
        timeline['review'] = "Security review after all critical/high fixed"
        return timeline

    def _assess_learning_curve(self, team_expertise: List[str], response: str) -> str:
        """Assess learning curve for recommended stack"""
        recommended_tech = self._extract_tech_stack(response)
        all_tech = []
        for techs in recommended_tech.values():
            all_tech.extend(techs)
        
        # Calculate overlap
        team_expertise_lower = [tech.lower() for tech in team_expertise]
        known_tech = sum(1 for tech in all_tech if tech.lower() in team_expertise_lower)
        
        overlap_percentage = (known_tech / len(all_tech)) * 100 if all_tech else 0
        
        if overlap_percentage > 70:
            return "minimal"
        elif overlap_percentage > 40:
            return "moderate"
        else:
            return "steep"

    def _estimate_stack_costs(self, response: str, budget: str) -> Dict[str, str]:
        """Estimate costs for recommended tech stack"""
        # Simple estimation - can be enhanced with actual pricing data
        base_costs = {
            'low': {'monthly': '$100-500', 'annual': '$1,200-6,000'},
            'moderate': {'monthly': '$500-2,000', 'annual': '$6,000-24,000'},
            'high': {'monthly': '$2,000-10,000', 'annual': '$24,000-120,000'}
        }
        
        return base_costs.get(budget.lower(), base_costs['moderate'])

    def _create_tech_roadmap(self, response: str) -> List[Dict[str, str]]:
        """Create technology implementation roadmap"""
        return [
            {
                "phase": "Foundation",
                "duration": "Week 1-2",
                "tasks": ["Set up development environment", "Initialize repositories", "Configure CI/CD"]
            },
            {
                "phase": "Core Development",
                "duration": "Week 3-8",
                "tasks": ["Implement backend API", "Build frontend framework", "Set up database"]
            },
            {
                "phase": "Integration",
                "duration": "Week 9-10",
                "tasks": ["Connect all components", "Implement authentication", "Add monitoring"]
            },
            {
                "phase": "Production Ready",
                "duration": "Week 11-12",
                "tasks": ["Security hardening", "Performance optimization", "Documentation"]
            }
        ]

    def _assess_complexity(self, content: str) -> str:
        """Assess technical complexity"""
        complex_indicators = ['distributed', 'microservices', 'real-time', 'machine learning', 
                             'blockchain', 'scale', 'concurrent']
        simple_indicators = ['crud', 'basic', 'simple', 'straightforward']
        
        content_lower = content.lower()
        
        complex_count = sum(1 for indicator in complex_indicators if indicator in content_lower)
        simple_count = sum(1 for indicator in simple_indicators if indicator in content_lower)
        
        if complex_count > simple_count:
            return "high"
        elif simple_count > complex_count:
            return "low"
        return "medium"

    def _needs_proof_of_concept(self, content: str) -> bool:
        """Determine if POC is needed"""
        poc_indicators = ['new technology', 'untested', 'experimental', 'innovative', 
                         'risky', 'complex integration', 'performance critical']
        return any(indicator in content.lower() for indicator in poc_indicators)

    def _identify_required_skills(self, content: str) -> List[str]:
        """Identify required skills for the task"""
        skills = []
        content_lower = content.lower()
        
        # Map keywords to skills
        skill_mapping = {
            'frontend': ['JavaScript', 'React/Vue/Angular', 'CSS', 'UI/UX'],
            'backend': ['API design', 'Database', 'Server architecture'],
            'mobile': ['iOS/Android', 'React Native', 'Mobile UX'],
            'devops': ['Docker', 'CI/CD', 'Cloud platforms'],
            'security': ['Security best practices', 'Encryption', 'Authentication'],
            'performance': ['Optimization', 'Caching', 'Load testing']
        }
        
        for category, category_skills in skill_mapping.items():
            if category in content_lower:
                skills.extend(category_skills)
        
        return list(set(skills))[:5]  # Top 5 unique skills

    async def provide_code_example(self, language: str, task: str) -> str:
        """Provide specific code example"""
        prompt = f"""Provide a clean, well-commented {language} code example for: {task}

Requirements:
- Production-ready code
- Error handling included
- Best practices followed
- Comments explaining key parts
- Keep it concise but complete"""

        return await self.llm_client.generate(prompt)

    def generate_technical_report(self) -> Dict[str, Any]:
        """Generate technical status report"""
        return {
            "developer": self.name,
            "active_tasks": len([t for t in self.context.conversation_history if t.get('status') == 'active']),
            "code_reviews_completed": len([t for t in self.context.conversation_history if t.get('type') == 'code_review']),
            "tech_stack_expertise": {
                category.value: techs 
                for category, techs in self.tech_stack_expertise.items()
            },
            "quality_standards": self.code_quality_standards,
            "recent_decisions": self.context.conversation_history[-3:] if self.context.conversation_history else [],
            "skills_utilized": self._get_utilized_skills()
        }

    def _get_utilized_skills(self) -> List[str]:
        """Get recently utilized skills"""
        utilized = set()
        for interaction in self.context.conversation_history[-10:]:
            content = interaction.get('content', '')
            for skill in self.skills:
                if skill.lower() in content.lower():
                    utilized.add(skill)
        return list(utilized)

    async def collaborate_on_technical_design(self, project: Dict, other_agents: List['BaseAgent']) -> Dict:
        """Collaborate on technical design with other agents"""
        tech_prompt = f"""As Lead Developer, provide technical design for project: {project.get('name')}

Focus on:
1. Technical Architecture
2. Implementation Approach  
3. Technology Choices
4. Development Timeline
5. Technical Risks

Be specific and practical."""

        tech_design = await self.llm_client.generate(tech_prompt)
        
        return {
            "sender": self.name,
            "role": self.role,
            "technical_design": tech_design,
            "requires_input_from": [agent.role for agent in other_agents],
            "next_steps": ["Review with team", "Create detailed specs", "Set up development environment"],
            "estimated_effort": self._estimate_project_effort(project),
            "timestamp": datetime.now().isoformat()
        }

    def _estimate_project_effort(self, project: Dict) -> str:
        """Estimate project effort"""
        complexity = project.get('complexity', 'medium')
        effort_mapping = {
            'simple': '1-2 weeks',
            'medium': '4-8 weeks',
            'complex': '12-24 weeks'
        }
        return effort_mapping.get(complexity, '6-12 weeks')
