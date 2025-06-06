from .base_agent import BaseAgent
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
from enum import Enum
import pytz

class DesignPrinciple(Enum):
    SIMPLICITY = "simplicity"
    ACCESSIBILITY = "accessibility"
    CONSISTENCY = "consistency"
    USABILITY = "usability"
    AESTHETICS = "aesthetics"
    RESPONSIVENESS = "responsiveness"

class DesignerAgent(BaseAgent):
    def __init__(self, llm_client=None):
        super().__init__(
            name="Emma Davis",
            role="UX/UI Designer",
            personality="Creative, user-focused, detail-oriented, innovative, empathetic",
            llm_client=llm_client
        )
        
        self.skills = [
            "User Experience Design",
            "User Interface Design",
            "Visual Design",
            "Prototyping",
            "User Research",
            "Information Architecture",
            "Interaction Design",
            "Design Systems",
            "Accessibility Design",
            "Mobile Design",
            "Web Design",
            "Branding"
        ]
        
        # Designer-specific attributes
        self.design_principles = {
            DesignPrinciple.SIMPLICITY: "Less is more - focus on essential elements",
            DesignPrinciple.ACCESSIBILITY: "Design for all users, including those with disabilities",
            DesignPrinciple.CONSISTENCY: "Maintain visual and behavioral consistency",
            DesignPrinciple.USABILITY: "Make it intuitive and easy to use",
            DesignPrinciple.AESTHETICS: "Create visually appealing experiences",
            DesignPrinciple.RESPONSIVENESS: "Design for all screen sizes and devices"
        }
        
        self.design_tools = [
            "Figma", "Sketch", "Adobe XD", "Framer",
            "Principle", "InVision", "Zeplin", "Abstract"
        ]
        
        self.color_psychology = {
            "blue": "trust, stability, professionalism",
            "green": "growth, nature, success",
            "red": "energy, urgency, passion",
            "purple": "luxury, creativity, wisdom",
            "orange": "friendliness, enthusiasm, creativity",
            "yellow": "optimism, happiness, attention",
            "black": "sophistication, luxury, power",
            "white": "simplicity, cleanliness, space"
        }
    
    def _define_capabilities(self):
        from .base_agent import AgentCapability
        return [
            AgentCapability.CREATIVE,
            AgentCapability.ANALYSIS,
            AgentCapability.COMMUNICATION,
            AgentCapability.PLANNING
        ]
    
    def _define_response_style(self):
        return {
            "brief_format": "Visual concept with user impact focus",
            "focus_areas": ["user experience", "visual hierarchy", "accessibility", "brand alignment"],
            "communication_style": "creative, empathetic, user-centric",
            "include_visuals": True
        }
    
    async def process_task(self, task: Dict) -> Dict:
        """Process design-related tasks"""
        task_type = task.get("type")
        
        if "brief" in task_type or task.get("brief", False):
            return await self.process_brief_task(task)
        
        task_handlers = {
            "design_concept": self._handle_design_concept,
            "ui_review": self._handle_ui_review,
            "ux_assessment": self._handle_ux_assessment,
            "wireframe": self._handle_wireframe_request,
            "design_system": self._handle_design_system,
            "user_research": self._handle_user_research,
            "accessibility_audit": self._handle_accessibility_audit,
            "branding": self._handle_branding,
            "prototype": self._handle_prototype_request
        }
        
        handler = task_handlers.get(task_type, self._handle_general_design)
        return await handler(task)
    
    async def process_brief_task(self, task: Dict) -> Dict:
        """Designer's brief, user-focused responses"""
        content = task.get('content', '')
        
        if 'design' in content.lower() or 'ui' in content.lower() or 'ux' in content.lower():
            prompt = f"""As UX/UI Designer, provide design guidance for: {content}

Format:
🎨 Design Approach: [Key design direction]
👤 User Impact: [How this helps users]
🎯 Visual Focus: [Main visual element/principle]
✅ Quick Win: [One immediate improvement]"""

        elif 'user' in content.lower() or 'experience' in content.lower():
            prompt = f"""As UX/UI Designer, analyze user experience for: {content}

Format:
👤 User Need: [Primary user requirement]
🔄 User Journey: [Key interaction point]
💡 UX Solution: [Design recommendation]
📱 Implementation: [Quick design tip]"""

        elif 'color' in content.lower() or 'brand' in content.lower():
            prompt = f"""As UX/UI Designer, provide branding guidance for: {content}

Format:
🎨 Color Strategy: [Color recommendation + meaning]
📐 Visual Style: [Design direction]
🎯 Brand Impact: [How it affects perception]
✅ Application: [Where to use it]"""

        else:
            prompt = f"""As UX/UI Designer, provide creative input on: {content}

Format:
🎨 Design Insight: [Visual/UX perspective]
👤 User Benefit: [How users gain value]
💡 Creative Solution: [Design approach]
✅ Next Step: [Immediate action]"""

        response = await self.llm_client.generate(prompt)
        
        return {
            "sender": self.name,
            "role": self.role,
            "content": response,
            "response_type": "brief_design",
            "design_confidence": self._calculate_design_confidence(task),
            "requires_mockup": self._needs_visual_mockup(content),
            "timestamp": datetime.now(pytz.UTC).isoformat()
        }
    
    async def _handle_design_concept(self, task: Dict) -> Dict:
        """Handle design concept creation"""
        project_name = task.get('project_name', '')
        project_type = task.get('project_type', '')
        target_audience = task.get('target_audience', '')
        brand_guidelines = task.get('brand_guidelines', {})
        
        prompt = f"""As UX/UI Designer, create design concept for: {project_name}

Project Type: {project_type}
Target Audience: {target_audience}
Brand Guidelines: {json.dumps(brand_guidelines, indent=2) if brand_guidelines else 'To be defined'}

Design Concept:

1. Visual Direction
   - Overall aesthetic and mood
   - Design principles to follow
   - Inspiration and references

2. Color Palette
   - Primary colors: [HEX codes with usage]
   - Secondary colors: [HEX codes with usage]
   - Accent colors: [HEX codes with usage]
   - Color psychology rationale

3. Typography System
   - Heading font: [Font family and weights]
   - Body font: [Font family and weights]
   - Font scale and hierarchy

4. Layout & Grid System
   - Grid structure (columns, gutters)
   - Spacing system (8px base unit recommended)
   - Responsive breakpoints

5. Component Design
   - Button styles (primary, secondary, ghost)
   - Form elements (inputs, selects, checkboxes)
   - Card layouts
   - Navigation patterns

6. Interaction Design
   - Micro-interactions
   - Animation principles
   - User feedback patterns

7. Accessibility Considerations
   - WCAG compliance level
   - Color contrast ratios
   - Focus states
   - Screen reader support

Include ASCII mockup for key screen if helpful."""

        response = await self.llm_client.generate(prompt)
        
        return {
            "sender": self.name,
            "role": self.role,
            "content": response,
            "design_type": "concept",
            "design_deliverables": self._identify_deliverables(project_type),
            "tools_recommended": self._recommend_design_tools(project_type),
            "timeline_estimate": self._estimate_design_timeline(project_type),
            "timestamp": datetime.now(pytz.UTC).isoformat()
        }
    
    async def _handle_ui_review(self, task: Dict) -> Dict:
        """Handle UI review requests"""
        ui_description = task.get('ui_description', '')
        screenshots = task.get('screenshots', [])
        review_focus = task.get('focus', 'general')
        
        prompt = f"""As UX/UI Designer, review this UI:

UI Description: {ui_description}
Review Focus: {review_focus}

UI Review:

1. Visual Hierarchy Assessment
   - Is the information hierarchy clear?
   - Are CTAs prominent and accessible?
   - Is visual flow intuitive?

2. Consistency Check
   - Design pattern consistency
   - Spacing and alignment
   - Color and typography usage

3. Usability Analysis
   - Ease of navigation
   - Touch target sizes (mobile)
   - Error prevention and handling

4. Accessibility Review
   - Color contrast ratios
   - Text readability
   - Keyboard navigation
   - Screen reader compatibility

5. Visual Design Quality
   - Aesthetic appeal
   - Brand alignment
   - Modern design trends
   - Polish and attention to detail

6. Improvement Recommendations
   - Quick fixes (immediate)
   - Medium-term improvements
   - Long-term enhancements

Rate the UI: [1-10] with justification"""

        response = await self.llm_client.generate(prompt)
        
        ui_score = self._extract_ui_score(response)
        issues = self._extract_ui_issues(response)
        
        return {
            "sender": self.name,
            "role": self.role,
            "content": response,
            "review_type": "ui_review",
            "ui_score": ui_score,
            "critical_issues": issues['critical'],
            "improvements": issues['improvements'],
            "requires_redesign": ui_score < 6,
            "timestamp": datetime.now(pytz.UTC).isoformat()
        }
    
    async def _handle_ux_assessment(self, task: Dict) -> Dict:
        """Handle UX assessment requests"""
        product_description = task.get('product_description', '')
        user_flows = task.get('user_flows', [])
        pain_points = task.get('pain_points', [])
        
        prompt = f"""As UX/UI Designer, assess user experience:

Product: {product_description}
User Flows: {json.dumps(user_flows, indent=2) if user_flows else 'To be analyzed'}
Known Pain Points: {json.dumps(pain_points, indent=2) if pain_points else 'To be discovered'}

UX Assessment:

1. User Journey Analysis
   - Entry points and onboarding
   - Key user tasks and flows
   - Exit points and retention

2. Usability Heuristics Evaluation
   - Visibility of system status
   - Match with real world
   - User control and freedom
   - Consistency and standards
   - Error prevention
   - Recognition over recall
   - Flexibility and efficiency
   - Aesthetic and minimalist design
   - Error recovery
   - Help and documentation

3. Pain Point Identification
   - Current friction points
   - User frustrations
   - Abandonment triggers

4. Information Architecture
   - Content organization
   - Navigation structure
   - Search and findability

5. Emotional Design
   - User delight moments
   - Trust building elements
   - Engagement factors

6. UX Recommendations
   - Priority 1: Critical fixes
   - Priority 2: Important improvements
   - Priority 3: Nice-to-have enhancements

Include user flow diagram if helpful."""

        response = await self.llm_client.generate(prompt)
        
        return {
            "sender": self.name,
            "role": self.role,
            "content": response,
            "assessment_type": "ux_comprehensive",
            "usability_score": self._calculate_usability_score(response),
            "priority_fixes": self._extract_priority_fixes(response),
            "user_satisfaction_estimate": self._estimate_user_satisfaction(response),
            "timestamp": datetime.now(pytz.UTC).isoformat()
        }
    
    async def _handle_wireframe_request(self, task: Dict) -> Dict:
        """Handle wireframe creation requests"""
        screen_name = task.get('screen_name', '')
        requirements = task.get('requirements', [])
        platform = task.get('platform', 'web')
        
        prompt = f"""As UX/UI Designer, create wireframe for: {screen_name}

Platform: {platform}
Requirements: {json.dumps(requirements, indent=2)}

Wireframe Design:

1. Layout Structure
[Create ASCII wireframe here]

2. Component Breakdown
- Header: [Components and purpose]
- Main Content: [Sections and hierarchy]
- Sidebar/Navigation: [If applicable]
- Footer: [Components and links]

3. Interactive Elements
- Buttons: [List with actions]
- Forms: [Fields and validation]
- Links: [Navigation paths]

4. Content Hierarchy
- Primary content
- Secondary content
- Supporting elements

5. Responsive Behavior
- Desktop layout
- Tablet adaptations
- Mobile reorganization

6. Accessibility Notes
- Focus order
- ARIA labels needed
- Semantic HTML structure"""

        response = await self.llm_client.generate(prompt)
     
        return {
         "sender": self.name,
         "role": self.role,
         "content": response,
         "wireframe_type": platform,
         "fidelity": "low",
         "next_steps": ["Create high-fidelity mockup", "Prototype interactions", "User testing"],
         "timestamp": datetime.now(pytz.UTC).isoformat()
     }
 
    async def _handle_design_system(self, task: Dict) -> Dict:
        """Handle design system creation"""
        brand_name = task.get('brand_name', '')
        existing_assets = task.get('existing_assets', {})
        scale = task.get('scale', 'medium')
        
        prompt = f"""As UX/UI Designer, create design system for: {brand_name}

Scale: {scale}
Existing Assets: {json.dumps(existing_assets, indent=2) if existing_assets else 'Starting fresh'}

Design System:

1. Foundation
- Design Principles: [5-7 core principles]
- Brand Personality: [Attributes and tone]
- Design Language: [Visual vocabulary]

2. Color System
- Brand Colors
  * Primary: #[HEX] - [Usage]
  * Secondary: #[HEX] - [Usage]
- Functional Colors
  * Success: #[HEX]
  * Warning: #[HEX]
  * Error: #[HEX]
  * Info: #[HEX]
- Neutral Palette
  * Grays: [Scale from light to dark]

3. Typography
- Type Scale: [Sizes and line heights]
- Font Families: [Primary and secondary]
- Font Weights: [Available weights]
- Usage Guidelines: [When to use what]

4. Spacing & Grid
- Base Unit: [8px recommended]
- Spacing Scale: [4, 8, 16, 24, 32, 48, 64]
- Grid System: [Columns and gutters]
- Container Widths: [Breakpoints]

5. Components Library
- Atoms: [Buttons, inputs, labels]
- Molecules: [Cards, forms, navigation items]
- Organisms: [Headers, footers, sidebars]
- Templates: [Page layouts]

6. Motion & Animation
- Timing Functions: [Easing curves]
- Duration Scale: [Fast, normal, slow]
- Animation Principles: [Guidelines]

7. Documentation
- Usage Guidelines
- Do's and Don'ts
- Implementation Notes"""

        response = await self.llm_client.generate(prompt)
        
        return {
            "sender": self.name,
            "role": self.role,
            "content": response,
            "system_type": "comprehensive",
            "components_count": self._estimate_components_count(scale),
            "implementation_format": ["Figma library", "CSS framework", "React components"],
            "maintenance_plan": self._create_maintenance_plan(scale),
            "timestamp": datetime.now(pytz.UTC).isoformat()
        }
 
    async def _handle_user_research(self, task: Dict) -> Dict:
        """Handle user research planning"""
        research_goal = task.get('goal', '')
        target_users = task.get('target_users', '')
        timeline = task.get('timeline', 'flexible')
        
        prompt = f"""As UX/UI Designer, plan user research:

Research Goal: {research_goal}
Target Users: {target_users}
Timeline: {timeline}

User Research Plan:

1. Research Objectives
- Primary questions to answer
- Success metrics
- Hypotheses to validate

2. Research Methods
- User Interviews: [Sample size and format]
- Surveys: [Distribution and questions]
- Usability Testing: [Tasks and scenarios]
- Analytics Review: [Metrics to analyze]
- Competitive Analysis: [Competitors to study]

3. Participant Recruitment
- Screening criteria
- Sample size needed
- Recruitment channels
- Incentive structure

4. Research Protocol
- Interview guide
- Testing scenarios
- Data collection methods
- Ethics and consent

5. Analysis Framework
- Synthesis approach
- Affinity mapping
- Persona development
- Journey mapping

6. Deliverables
- Research report
- Key findings presentation
- Design recommendations
- Prototype updates

Timeline: [Week-by-week breakdown]"""

        response = await self.llm_client.generate(prompt)
        
        return {
            "sender": self.name,
            "role": self.role,
            "content": response,
            "research_type": "comprehensive",
            "estimated_duration": self._estimate_research_duration(timeline),
            "budget_estimate": self._estimate_research_budget(task),
            "key_deliverables": self._extract_research_deliverables(response),
            "timestamp": datetime.now().isoformat()
        }
 
    async def _handle_accessibility_audit(self, task: Dict) -> Dict:
        """Handle accessibility audit requests"""
        product_url = task.get('url', '')
        wcag_level = task.get('wcag_level', 'AA')
        focus_areas = task.get('focus_areas', [])
        
        prompt = f"""As UX/UI Designer, conduct accessibility audit:

Product: {product_url}
WCAG Level Target: {wcag_level}
Focus Areas: {json.dumps(focus_areas, indent=2) if focus_areas else 'Comprehensive audit'}

Accessibility Audit:

1. Visual Accessibility
- Color contrast ratios
- Text size and readability
- Focus indicators
- Visual hierarchy

2. Keyboard Navigation
- Tab order logic
- Keyboard shortcuts
- Skip links
- Focus trapping

3. Screen Reader Support
- Semantic HTML usage
- ARIA labels and roles
- Alt text for images
- Form labels and instructions

4. Interactive Elements
- Touch target sizes (48x48px minimum)
- Hover and focus states
- Error messages clarity
- Loading states communication

5. Content Accessibility
- Heading hierarchy
- Link text clarity
- Language declaration
- Reading level

6. Media Accessibility
- Video captions
- Audio transcripts
- Animation controls
- Reduced motion support

7. Compliance Issues
- Critical: [Must fix immediately]
- High: [Fix soon]
- Medium: [Plan to fix]
- Low: [Nice to fix]

8. Remediation Recommendations
- Quick wins
- Development updates needed
   - Design pattern changes
   - Testing requirements

9. Testing Tools Used
   - Automated tools: [WAVE, axe, Lighthouse]
   - Manual testing: [Keyboard, screen reader]
   - Browser extensions: [Accessibility insights]"""

        response = await self.llm_client.generate(prompt)
        
        accessibility_score = self._calculate_accessibility_score(response)
        issues = self._extract_accessibility_issues(response)
        
        return {
            "sender": self.name,
            "role": self.role,
            "content": response,
            "audit_type": "accessibility",
            "wcag_compliance": accessibility_score >= 0.9,
            "accessibility_score": accessibility_score,
            "critical_issues": issues['critical'],
            "total_issues": issues['total'],
            "remediation_effort": self._estimate_remediation_effort(issues),
            "timestamp": datetime.now().isoformat()
        }

    async def _handle_branding(self, task: Dict) -> Dict:
        """Handle branding requests"""
        company_info = task.get('company_info', {})
        brand_values = task.get('values', [])
        target_market = task.get('target_market', '')
        competitors = task.get('competitors', [])
        
        prompt = f"""As UX/UI Designer, develop brand identity:

Company: {json.dumps(company_info, indent=2)}
Brand Values: {', '.join(brand_values) if brand_values else 'To be defined'}
Target Market: {target_market}
Competitors: {', '.join(competitors) if competitors else 'Various'}

Brand Identity:

1. Brand Strategy
   - Brand Promise: [One clear statement]
   - Brand Personality: [5-6 traits]
   - Brand Voice: [Tone and style]
   - Unique Value Proposition

2. Visual Identity
   - Logo Concept: [Description and style]
   - Color Palette:
     * Primary: [Color + meaning]
     * Secondary: [Colors + usage]
   - Typography:
     * Display: [Font for headlines]
     * Body: [Font for content]
   - Visual Style: [Photography, illustration, icons]

3. Brand Applications
   - Digital: [Website, app, social media]
   - Print: [Business cards, brochures]
   - Environmental: [Signage, packaging]

4. Brand Guidelines
   - Logo usage rules
   - Color specifications
   - Typography hierarchy
   - Spacing and layout
   - Do's and don'ts

5. Emotional Connection
   - How users should feel
   - Brand story elements
   - Key messages
   - Brand differentiators

6. Implementation Roadmap
   - Phase 1: Core identity
   - Phase 2: Digital presence
   - Phase 3: Marketing materials
   - Phase 4: Full rollout"""

        response = await self.llm_client.generate(prompt)
        
        return {
            "sender": self.name,
            "role": self.role,
            "content": response,
            "branding_type": "comprehensive",
            "deliverables": self._list_branding_deliverables(),
            "timeline": self._estimate_branding_timeline(task),
            "brand_consistency_score": self._evaluate_brand_fit(response, brand_values),
            "timestamp": datetime.now().isoformat()
        }
    
    async def _handle_prototype_request(self, task: Dict) -> Dict:
        """Handle prototype creation requests"""
        prototype_type = task.get('type', 'interactive')
        screens = task.get('screens', [])
        interactions = task.get('interactions', [])
        fidelity = task.get('fidelity', 'high')
        
        prompt = f"""As UX/UI Designer, plan prototype:

Prototype Type: {prototype_type}
Fidelity: {fidelity}
Screens: {json.dumps(screens, indent=2) if screens else 'Key user flows'}
Interactions: {json.dumps(interactions, indent=2) if interactions else 'Standard interactions'}

Prototype Plan:

1. Prototype Scope
   - User flows to demonstrate
   - Key interactions to prototype
   - Device/platform targets

2. Screen Designs
   - Screen 1: [Purpose and key elements]
   - Screen 2: [Purpose and key elements]
   - [Additional screens as needed]

3. Interaction Design
   - Transitions: [Between screens]
   - Micro-interactions: [Buttons, forms]
   - Gestures: [Swipe, tap, etc.]
   - Feedback: [Loading, success, error]

4. Prototype Features
   - Click/tap areas
   - Form interactions
   - Navigation flow
   - State changes
   - Animations

5. Testing Scenarios
   - Task 1: [User goal and steps]
   - Task 2: [User goal and steps]
   - Task 3: [User goal and steps]

6. Technical Specifications
   - Tool: [Figma/Framer/Principle]
   - Sharing method: [Link/app]
   - Device requirements
   - Testing setup

7. Success Metrics
   - Task completion rate
   - Time to complete
   - Error frequency
   - User satisfaction"""

        response = await self.llm_client.generate(prompt)
        
        return {
            "sender": self.name,
            "role": self.role,
            "content": response,
            "prototype_details": {
                "type": prototype_type,
                "fidelity": fidelity,
                "screens_count": len(screens) if screens else "TBD"
            },
            "estimated_effort": self._estimate_prototype_effort(fidelity, screens),
            "testing_ready": fidelity == "high",
            "next_steps": self._define_prototype_next_steps(fidelity),
            "timestamp": datetime.now().isoformat()
        }
    
    async def _handle_general_design(self, task: Dict) -> Dict:
        """Handle general design questions"""
        content = task.get('content', '')
        
        prompt = f"""As UX/UI Designer, provide design expertise on: {content}

Consider:
- User needs and goals
- Visual design best practices
- Accessibility requirements
- Brand alignment
- Technical feasibility
- Current design trends

Provide creative and user-centered guidance."""

        response = await self.llm_client.generate(prompt)
        
        return {
            "sender": self.name,
            "role": self.role,
            "content": response,
            "design_area": self._identify_design_area(content),
            "requires_mockup": self._needs_visual_mockup(content),
            "collaboration_needed": self._identify_collaboration_needs(content),
            "timestamp": datetime.now().isoformat()
        }
    
    # Helper methods
    def _calculate_design_confidence(self, task: Dict) -> float:
        """Calculate confidence in design recommendation"""
        content = task.get('content', '').lower()
        confidence = 0.5
        
        # Check for design-specific keywords
        design_keywords = ['design', 'ui', 'ux', 'visual', 'user', 'interface', 
                          'experience', 'wireframe', 'mockup', 'prototype']
        
        for keyword in design_keywords:
            if keyword in content:
                confidence += 0.05
        
        # Check for skill match
        for skill in self.skills:
            if skill.lower() in content:
                confidence += 0.03
        
        return min(confidence, 1.0)
    
    def _needs_visual_mockup(self, content: str) -> bool:
        """Determine if visual mockup is needed"""
        mockup_indicators = ['layout', 'design', 'interface', 'screen', 
                            'mockup', 'wireframe', 'visual', 'ui']
        return any(indicator in content.lower() for indicator in mockup_indicators)
    
    def _extract_ui_score(self, response: str) -> float:
        """Extract UI score from review"""
        import re
        match = re.search(r'Rate.*?:\s*(\d+(?:\.\d+)?)/10', response)
        if match:
            return float(match.group(1))
        return 5.0  # Default middle score
    
    def _extract_ui_issues(self, response: str) -> Dict[str, List[str]]:
        """Extract UI issues from review"""
        issues = {
            'critical': [],
            'improvements': []
        }
        
        lines = response.split('\n')
        current_section = None
        
        for line in lines:
            line_lower = line.lower()
            if 'critical' in line_lower or 'major' in line_lower:
                current_section = 'critical'
            elif 'improvement' in line_lower or 'recommendation' in line_lower:
                current_section = 'improvements'
            elif current_section and line.strip().startswith('-'):
                issues[current_section].append(line.strip())
        
        return issues
    
    def _identify_deliverables(self, project_type: str) -> List[str]:
        """Identify design deliverables for project type"""
        deliverables = ["Style guide", "Component library"]
        
        project_deliverables = {
            'web': ["Responsive mockups", "Desktop designs", "Mobile designs"],
            'mobile': ["iOS designs", "Android designs", "App icon"],
            'dashboard': ["Dashboard layouts", "Data visualization", "Empty states"],
            'ecommerce': ["Product pages", "Checkout flow", "Cart design"]
        }
        
        deliverables.extend(project_deliverables.get(project_type.lower(), ["Mockups"]))
        return deliverables
    
    def _recommend_design_tools(self, project_type: str) -> List[str]:
        """Recommend design tools based on project"""
        base_tools = ["Figma"]
        
        if 'prototype' in project_type.lower():
            base_tools.extend(["Framer", "Principle"])
        if 'mobile' in project_type.lower():
            base_tools.append("Sketch")
        if 'web' in project_type.lower():
            base_tools.append("Webflow")
        
        return base_tools[:3]  # Top 3 tools
    
    def _estimate_design_timeline(self, project_type: str) -> str:
        """Estimate design timeline"""
        timelines = {
            'simple': "1-2 weeks",
            'medium': "3-4 weeks",
            'complex': "6-8 weeks",
            'enterprise': "8-12 weeks"
        }
        
        # Determine complexity based on project type
        if any(word in project_type.lower() for word in ['mvp', 'prototype', 'simple']):
            return timelines['simple']
        elif any(word in project_type.lower() for word in ['enterprise', 'platform', 'system']):
            return timelines['enterprise']
        elif any(word in project_type.lower() for word in ['app', 'dashboard', 'portal']):
            return timelines['complex']
        
        return timelines['medium']
    
    def _calculate_usability_score(self, response: str) -> float:
        """Calculate usability score from UX assessment"""
        positive_indicators = ['intuitive', 'easy', 'clear', 'simple', 'efficient']
        negative_indicators = ['confusing', 'difficult', 'complex', 'frustrating', 'unclear']
        
        response_lower = response.lower()
        positive_count = sum(1 for indicator in positive_indicators if indicator in response_lower)
        negative_count = sum(1 for indicator in negative_indicators if indicator in response_lower)
        
        # Calculate score (0-1)
        base_score = 0.7
        score = base_score + (positive_count * 0.05) - (negative_count * 0.1)
        return max(0, min(1, score))
    
    def _extract_priority_fixes(self, response: str) -> List[Dict[str, str]]:
        """Extract priority fixes from UX assessment"""
        fixes = []
        lines = response.split('\n')
        
        priority_keywords = {
            'critical': 1,
            'high': 2,
            'medium': 3,
            'low': 4
        }
        
        for line in lines:
            for priority, level in priority_keywords.items():
                if priority in line.lower():
                    fixes.append({
                        'priority': priority,
                        'level': level,
                        'description': line.strip()
                    })
        
        return sorted(fixes, key=lambda x: x['level'])[:5]
    
    def _estimate_user_satisfaction(self, response: str) -> str:
        """Estimate user satisfaction from UX assessment"""
        score = self._calculate_usability_score(response)
        
        if score >= 0.8:
            return "High - Users will love it"
        elif score >= 0.6:
            return "Medium - Good but room for improvement"
        elif score >= 0.4:
            return "Low - Significant improvements needed"
        else:
            return "Very Low - Major redesign recommended"
    
    def _estimate_components_count(self, scale: str) -> int:
        """Estimate number of components in design system"""
        component_counts = {
            'small': 20,
            'medium': 50,
            'large': 100,
            'enterprise': 200
        }
        return component_counts.get(scale.lower(), 50)
    
    def _create_maintenance_plan(self, scale: str) -> Dict[str, str]:
        """Create design system maintenance plan"""
        return {
            'review_frequency': 'quarterly' if scale == 'enterprise' else 'bi-annually',
            'update_process': 'Version control with approval workflow',
            'documentation': 'Living documentation site',
            'training': 'Onboarding materials and workshops',
            'governance': 'Design system team ownership'
        }
    
    def _estimate_research_duration(self, timeline: str) -> str:
        """Estimate user research duration"""
        durations = {
            'urgent': '1 week',
            'fast': '2 weeks',
            'normal': '3-4 weeks',
            'flexible': '4-6 weeks',
            'comprehensive': '8-12 weeks'
        }
        return durations.get(timeline.lower(), '3-4 weeks')
    
    def _estimate_research_budget(self, task: Dict) -> str:
        """Estimate research budget"""
        participants = task.get('participants', 10)
        incentive = task.get('incentive', 50)
        
        budget = participants * incentive
        tools = 500  # Research tools estimate
        
        total = budget + tools
        
        if total < 1000:
            return f"${total} (Low budget)"
        elif total < 5000:
            return f"${total} (Moderate budget)"
        else:
            return f"${total} (High budget)"
    
    def _extract_research_deliverables(self, response: str) -> List[str]:
        """Extract research deliverables"""
        deliverables = []
        deliverable_keywords = ['report', 'presentation', 'findings', 'recommendations', 
                               'personas', 'journey map', 'insights']
        
        lines = response.split('\n')
        for line in lines:
            if any(keyword in line.lower() for keyword in deliverable_keywords):
                deliverables.append(line.strip())
        
        return deliverables[:5]
    
    def _calculate_accessibility_score(self, response: str) -> float:
        """Calculate accessibility score"""
        # Simple scoring based on issues found
        critical_count = response.lower().count('critical')
        high_count = response.lower().count('high priority')
        
        if critical_count > 0:
            return 0.5 - (critical_count * 0.1)
        elif high_count > 0:
            return 0.7 - (high_count * 0.05)
        else:
            return 0.9
    
    def _extract_accessibility_issues(self, response: str) -> Dict[str, int]:
        """Extract accessibility issues count"""
        issues = {
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 0,
            'total': 0
        }
        
        # Count occurrences
        response_lower = response.lower()
        issues['critical'] = response_lower.count('critical')
        issues['high'] = response_lower.count('high priority')
        issues['medium'] = response_lower.count('medium priority')
        issues['low'] = response_lower.count('low priority')
        issues['total'] = sum(issues.values())
        
        return issues
    
    def _estimate_remediation_effort(self, issues: Dict[str, int]) -> str:
        """Estimate effort to fix accessibility issues"""
        total_days = (issues['critical'] * 2) + (issues['high'] * 1) + (issues['medium'] * 0.5)
        
        if total_days < 5:
            return "Low - Less than 1 week"
        elif total_days < 15:
            return "Medium - 2-3 weeks"
        else:
            return "High - 1+ months"
    
    def _list_branding_deliverables(self) -> List[str]:
        """List branding deliverables"""
        return [
            "Brand strategy document",
            "Visual identity system",
            "Logo files (all formats)",
            "Brand guidelines PDF",
            "Color palette (digital & print)",
            "Typography specifications",
            "Template library",
            "Brand assets kit"
        ]
    
    def _estimate_branding_timeline(self, task: Dict) -> str:
        """Estimate branding project timeline"""
        scope = task.get('scope', 'medium')
        
        timelines = {
            'refresh': '2-3 weeks',
            'rebrand': '6-8 weeks',
            'new_brand': '8-12 weeks',
            'medium': '4-6 weeks'
        }
        
        return timelines.get(scope, '4-6 weeks')
    
    def _evaluate_brand_fit(self, response: str, brand_values: List[str]) -> float:
        """Evaluate how well design fits brand values"""
        if not brand_values:
            return 0.8
        
        response_lower = response.lower()
        matches = sum(1 for value in brand_values if value.lower() in response_lower)
        
        return min(1.0, 0.5 + (matches / len(brand_values)) * 0.5)
    
    def _estimate_prototype_effort(self, fidelity: str, screens: List) -> str:
        """Estimate prototype creation effort"""
        screen_count = len(screens) if screens else 5  # Default estimate
        
        effort_per_screen = {
            'low': 2,  # hours
            'medium': 4,
            'high': 8
        }
        
        hours = screen_count * effort_per_screen.get(fidelity, 4)
        
        if hours < 20:
            return f"{hours} hours"
        else:
            days = hours / 8
            return f"{days:.1f} days"
    
    def _define_prototype_next_steps(self, fidelity: str) -> List[str]:
        """Define next steps after prototype"""
        if fidelity == 'low':
            return ["Create high-fidelity designs", "Define interactions", "Gather feedback"]
        elif fidelity == 'medium':
            return ["Add micro-interactions", "Conduct user testing", "Refine based on feedback"]
        else:  # high
            return ["User testing sessions", "Developer handoff", "Create documentation"]
    
    def _identify_design_area(self, content: str) -> str:
        """Identify design area from content"""
        content_lower = content.lower()
        
        if any(word in content_lower for word in ['ux', 'user experience', 'usability']):
            return "UX Design"
        elif any(word in content_lower for word in ['ui', 'interface', 'visual']):
            return "UI Design"
        elif any(word in content_lower for word in ['brand', 'logo', 'identity']):
            return "Branding"
        elif any(word in content_lower for word in ['research', 'user study', 'testing']):
            return "User Research"
        else:
            return "General Design"
    
    def _identify_collaboration_needs(self, content: str) -> List[str]:
        """Identify which team members should collaborate"""
        collaborators = []
        content_lower = content.lower()
        
        if any(word in content_lower for word in ['implement', 'develop', 'code']):
            collaborators.append("Developer")
        if any(word in content_lower for word in ['timeline', 'project', 'planning']):
            collaborators.append("Project Manager")
        if any(word in content_lower for word in ['business', 'strategy', 'market']):
            collaborators.append("CEO")
        
        return collaborators
    
    async def collaborate_on_design(self, project: Dict, team_members: List['BaseAgent']) -> Dict:
        """Collaborate on design with team"""
        design_prompt = f"""As UX/UI Designer, provide design vision for project: {project.get('name')}

Focus on:
1. User Experience Goals
2. Visual Design Direction
3. Key User Flows
4. Design Principles
5. Success Metrics

Be creative yet practical."""

        design_vision = await self.llm_client.generate(design_prompt)
        
        return {
            "sender": self.name,
            "role": self.role,
            "design_vision": design_vision,
            "requires_input_from": [agent.name for agent in team_members],
            "timestamp": datetime.now().isoformat()
        }
    
    def generate_design_report(self) -> Dict[str, Any]:
        """Generate design status report"""
        return {
            "designer": self.name,
            "active_projects": len([h for h in self.context.conversation_history if h.get('status') == 'active']),
            "designs_completed": self._count_completed_designs(),
            "design_principles": list(self.design_principles.keys()),
            "tools_in_use": self.design_tools[:3],
            "recent_work": self._get_recent_design_work(),
            "user_satisfaction_average": self._calculate_average_satisfaction()
        }
    
    def _count_completed_designs(self) -> int:
        """Count completed design tasks"""
        return len([h for h in self.context.conversation_history 
                   if h.get('type') in ['design_concept', 'wireframe', 'prototype'] 
                   and h.get('status') == 'completed'])
    
    def _get_recent_design_work(self) -> List[str]:
        """Get recent design work"""
        recent = []
        for item in self.context.conversation_history[-5:]:
            if item.get('type') in ['design_concept', 'ui_review', 'ux_assessment']:
                recent.append(f"{item.get('type', 'Unknown')} - {item.get('timestamp', 'N/A')}")
        return recent
    
    def _calculate_average_satisfaction(self) -> float:
        """Calculate average user satisfaction from assessments"""
        scores = []
        for item in self.context.conversation_history:
            if 'usability_score' in item:
                scores.append(item['usability_score'])
        
        return sum(scores) / len(scores) if scores else 0.75