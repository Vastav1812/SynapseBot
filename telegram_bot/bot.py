# telegram_bot/bot.py

import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, 
    CallbackQueryHandler, ContextTypes, filters
)
import logging
from typing import Dict, List, Optional, Union
from datetime import datetime
import traceback
import pytz

class SynapseBot:
    def __init__(self, token: str, gemini_client, orchestrator):
        self.token = token
        self.gemini_client = gemini_client
        self.orchestrator = orchestrator
        self.logger = logging.getLogger(__name__)
        self.application = None
        self.user_sessions = {}
        
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user_id = update.effective_user.id
        self.user_sessions[user_id] = {
            'state': 'idle',
            'context': {},
            'history': []
        }
        
        welcome_message = """🚀 **Welcome to SynapseBot!**

I'm your AI-powered team assistant with multiple specialized agents:

👔 **CEO** - Strategic decisions & vision
💻 **Developer** - Technical solutions & code
📊 **PM** - Project planning & coordination  
🎨 **Designer** - UI/UX & creative solutions

**Commands:**
/newproject - Start a new project
/team - Consult the team
/status - Check project status
/help - Show all commands

How can I help you today?"""
        
        keyboard = [
            [InlineKeyboardButton("🚀 New Project", callback_data="new_project")],
            [InlineKeyboardButton("👥 Team Meeting", callback_data="team_meeting"),
             InlineKeyboardButton("📈 Status", callback_data="status")],
            [InlineKeyboardButton("💡 Quick Idea", callback_data="quick_idea")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            welcome_message,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def new_project(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /newproject command"""
        user_id = update.effective_user.id
        
        # Extract project name from command
        if context.args:
            project_name = ' '.join(context.args)
        else:
            await update.message.reply_text(
                "Please provide a project name:\n`/newproject [project name]`",
                parse_mode='Markdown'
            )
            return
        
        # Update user session
        self.user_sessions[user_id] = {
            'state': 'project_planning',
            'context': {'project_name': project_name},
            'history': []
        }
        
        # Send initial response
        await update.message.reply_text(
            f"🚀 Starting new project: **{project_name}**\n\nGathering the team for initial planning...",
            parse_mode='Markdown'
        )
        
        # Send typing action
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action="typing"
        )
        
        # Get CEO's initial assessment
        try:
            ceo_task = {
                'type': 'project_approval',
                'content': f"New project proposal: {project_name}",
                'brief': True
            }
            
            ceo_response = await self.orchestrator.route_to_agent('ceo', ceo_task)
            
            # Format and send CEO response
            ceo_message = f"👔 **CEO Assessment:**\n\n{ceo_response.get('content', 'Processing...')}"
            
            # Create action buttons
            keyboard = [
                [InlineKeyboardButton("💻 Technical Feasibility", callback_data=f"tech_assessment:{project_name}")],
                [InlineKeyboardButton("📊 Project Planning", callback_data=f"project_planning:{project_name}")],
                [InlineKeyboardButton("🎨 Design Concept", callback_data=f"design_concept:{project_name}")],
                [InlineKeyboardButton("👥 Full Team Discussion", callback_data=f"team_discussion:{project_name}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                ceo_message[:4000],  # Respect Telegram limit
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            
        except Exception as e:
            self.logger.error(f"Error in new_project: {e}")
            await update.message.reply_text(
                "⚠️ Sorry, I encountered an error. Please try again.",
                parse_mode='Markdown'
            )
    
    async def handle_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle inline keyboard callbacks"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        user_id = update.effective_user.id
        
        try:
            if data == "new_project":
                await query.edit_message_text(
                    "Please use `/newproject [project name]` to start a new project.",
                    parse_mode='Markdown'
                )
                
            elif data == "team_meeting":
                await self._handle_quick_team_meeting(query)
                
            elif data == "status":
                await self._handle_quick_status(query)
                
            elif data == "quick_idea":
                await self._handle_quick_idea(query)
                
            elif data.startswith("tech_assessment:"):
                project_name = data.split(":", 1)[1]
                await self._handle_tech_assessment(query, project_name)
                
            elif data.startswith("project_planning:"):
                project_name = data.split(":", 1)[1]
                await self._handle_project_planning(query, project_name)
                
            elif data.startswith("design_concept:"):
                project_name = data.split(":", 1)[1]
                await self._handle_design_concept(query, project_name)
                
            elif data.startswith("team_discussion:"):
                project_name = data.split(":", 1)[1]
                await self._handle_team_discussion(query, project_name)
                
            elif data.startswith("talk_"):
                agent = data.replace("talk_", "")
                await self._handle_talk_to_agent(query, agent)
                
        except Exception as e:
            self.logger.error(f"Error in callback handler: {e}")
            await query.edit_message_text(
                "⚠️ An error occurred. Please try again.",
                parse_mode='Markdown'
            )
    
    async def _handle_quick_team_meeting(self, query):
        """Handle quick team meeting"""
        await query.edit_message_text(
            "👥 **Quick Team Meeting**\n\nWhat would you like to discuss?",
            parse_mode='Markdown'
        )
        
        keyboard = [
            [InlineKeyboardButton("📊 Project Updates", callback_data="meeting_updates")],
            [InlineKeyboardButton("💡 Brainstorming", callback_data="meeting_brainstorm")],
            [InlineKeyboardButton("⚠️ Problem Solving", callback_data="meeting_problems")],
            [InlineKeyboardButton("🔙 Back", callback_data="start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.message.edit_reply_markup(reply_markup=reply_markup)
    
    async def _handle_quick_status(self, query):
        """Handle quick status check"""
        try:
            status_message = "📊 **System Status**\n\n"
            
            # Get team report
            team_report = await self.orchestrator.generate_team_report()
            
            status_message += f"✅ **Active Projects:** {team_report.get('active_projects', 0)}\n"
            status_message += f"👥 **Team Activity:** {team_report.get('recent_activity', {}).get('total_interactions', 0)} interactions\n"
            status_message += f"🔥 **Most Active:** {team_report.get('recent_activity', {}).get('most_active_agent', 'N/A')}\n\n"
            
            status_message += "**Agent Status:**\n"
            for agent, status in team_report.get('agent_status', {}).items():
                emoji = {'ceo': '👔', 'developer': '💻', 'project_manager': '📊', 'designer': '🎨'}.get(agent, '👤')
                status_message += f"{emoji} {agent.title()}: {status.get('active_tasks', 0)} active tasks\n"
            
            await query.edit_message_text(
                status_message,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Error in quick status: {e}")
            await query.edit_message_text(
                "⚠️ Unable to fetch status. Please try again.",
                parse_mode='Markdown'
            )
    
    async def _handle_quick_idea(self, query):
        """Handle quick idea submission"""
        await query.edit_message_text(
            "💡 **Quick Idea Session**\n\nPlease type your idea and I'll have the team evaluate it!",
            parse_mode='Markdown'
        )
        
        # Set user state to expect idea input
        user_id = query.from_user.id
        if user_id in self.user_sessions:
            self.user_sessions[user_id]['state'] = 'awaiting_idea'
    
    async def _handle_talk_to_agent(self, query, agent: str):
        """Handle direct conversation with specific agent"""
        agent_map = {
            'ceo': ('ceo', '👔 CEO - Alex Chen'),
            'dev': ('developer', '💻 Developer - Sarah Kim'),
            'pm': ('project_manager', '📊 PM - Mike Johnson'),
            'designer': ('designer', '🎨 Designer - Emma Davis')
        }
        
        if agent in agent_map:
            agent_key, agent_name = agent_map[agent]
            
            await query.edit_message_text(
                f"Connected to {agent_name}\n\nHow can I help you today?",
                parse_mode='Markdown'
            )
            
            # Set user state to talk to specific agent
            user_id = query.from_user.id
            if user_id in self.user_sessions:
                self.user_sessions[user_id]['state'] = f'talking_to_{agent_key}'
    
    async def _handle_tech_assessment(self, query, project_name: str):
        """Handle technical assessment request"""
        await query.edit_message_text(
            f"💻 **Technical Assessment for {project_name}**\n\nAnalyzing technical requirements...",
            parse_mode='Markdown'
        )
        
        try:
            tech_task = {
                'type': 'technical_assessment',
                'content': f"Assess technical feasibility for {project_name}",
                'brief': True
            }
            
            dev_response = await self.orchestrator.route_to_agent('developer', tech_task)
            
            message = f"💻 **Developer Analysis:**\n\n{dev_response.get('content', 'Processing...')}"
            
            keyboard = [
                [InlineKeyboardButton("📋 Detailed Specs", callback_data=f"detailed_specs:{project_name}")],
                [InlineKeyboardButton("🔙 Back to Options", callback_data=f"project_options:{project_name}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                message[:4000],
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            
        except Exception as e:
            self.logger.error(f"Error in tech assessment: {e}")
            await query.edit_message_text(
                "⚠️ Error getting technical assessment. Please try again.",
                parse_mode='Markdown'
            )
    
    async def _handle_project_planning(self, query, project_name: str):
        """Handle project planning request"""
        await query.edit_message_text(
            f"📊 **Project Planning for {project_name}**\n\nCreating project roadmap...",
            parse_mode='Markdown'
        )
        
        try:
            pm_task = {
                'type': 'project_planning',
                'content': f"Create project plan for {project_name}",
                'brief': True
            }
            
            pm_response = await self.orchestrator.route_to_agent('project_manager', pm_task)
            
            message = f"📊 **PM's Project Plan:**\n\n{pm_response.get('content', 'Processing...')}"
            
            keyboard = [
                [InlineKeyboardButton("📅 Detailed Timeline", callback_data=f"timeline:{project_name}")],
                [InlineKeyboardButton("🔙 Back to Options", callback_data=f"project_options:{project_name}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                message[:4000],
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            
        except Exception as e:
            self.logger.error(f"Error in project planning: {e}")
            await query.edit_message_text(
                "⚠️ Error creating project plan. Please try again.",
                parse_mode='Markdown'
            )
    
    async def _handle_design_concept(self, query, project_name: str):
        """Handle design concept request"""
        await query.edit_message_text(
            f"🎨 **Design Concept for {project_name}**\n\nCreating design vision...",
            parse_mode='Markdown'
        )
        
        try:
            design_task = {
                'type': 'design_concept',
                'content': f"Create design concept for {project_name}",
                'brief': True
            }
            
            design_response = await self.orchestrator.route_to_agent('designer', design_task)
            
            message = f"🎨 **Designer's Vision:**\n\n{design_response.get('content', 'Processing...')}"
            
            keyboard = [
                [InlineKeyboardButton("🖼️ Wireframes", callback_data=f"wireframes:{project_name}")],
                [InlineKeyboardButton("🔙 Back to Options", callback_data=f"project_options:{project_name}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                message[:4000],
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            
        except Exception as e:
            self.logger.error(f"Error in design concept: {e}")
            await query.edit_message_text(
                "⚠️ Error creating design concept. Please try again.",
                parse_mode='Markdown'
            )
    
    async def _handle_team_discussion(self, query, project_name: str):
        """Handle full team discussion"""
        await query.edit_message_text(
            f"👥 **Team Discussion for {project_name}**\n\nGathering all team members...",
            parse_mode='Markdown'
        )
        
        try:
            # Get brief input from all agents
            discussion_task = {
                'type': 'team_discussion',
                'content': f"Discuss new project: {project_name}",
                'brief': True
            }
            
            team_responses = await self.orchestrator.get_team_consensus(discussion_task)
            
            message = "👥 **Team Discussion Summary:**\n\n"
            
            # Process responses correctly
            responses = team_responses.get('responses', {})
            
            for agent, response in responses.items():
                agent_emoji = {
                    'ceo': '👔',
                    'developer': '💻',
                    'project_manager': '📊',
                    'designer': '🎨'
                }.get(agent, '👤')
                
                content = response.get('content', 'No response') if isinstance(response, dict) else str(response)
                message += f"{agent_emoji} **{agent.title()}:**\n{content[:500]}...\n\n"
            
            keyboard = [
                [InlineKeyboardButton("✅ Approve Project", callback_data=f"approve:{project_name}")],
                [InlineKeyboardButton("🔄 Refine Concept", callback_data=f"refine:{project_name}")],
                [InlineKeyboardButton("❌ Cancel", callback_data="cancel_project")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                message[:4000],
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            
        except Exception as e:
            self.logger.error(f"Error in team discussion: {e}")
            self.logger.error(traceback.format_exc())
            await query.edit_message_text(
                "⚠️ Error during team discussion. Please try again.",
                parse_mode='Markdown'
            )
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular text messages"""
        user_id = update.effective_user.id
        message = update.message.text
        
        # Initialize session if needed
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = {
                'state': 'idle',
                'context': {},
                'history': []
            }
        
        session = self.user_sessions[user_id]
        
        # Send typing action
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action="typing"
        )
        
        try:
            # Route based on session state
            if session['state'] == 'awaiting_idea':
                await self._handle_idea_submission(update, context, message)
            elif session['state'].startswith('talking_to_'):
                agent = session['state'].replace('talking_to_', '')
                await self._handle_agent_conversation(update, context, message, agent)
            elif session['state'] == 'project_planning':
                await self._handle_project_message(update, context, message)
            else:
                await self._handle_general_message(update, context, message)
                
        except Exception as e:
            self.logger.error(f"Error handling message: {e}")
            await update.message.reply_text(
                "⚠️ Sorry, I encountered an error. Please try again.",
                parse_mode='Markdown'
            )
    
    async def _handle_idea_submission(self, update: Update, context: ContextTypes.DEFAULT_TYPE, idea: str):
        """Handle idea submission"""
        user_id = update.effective_user.id
        
        # Reset state
        self.user_sessions[user_id]['state'] = 'idle'
        
        await update.message.reply_text(
            "💡 **Evaluating your idea...**\n\nThe team is reviewing it!",
            parse_mode='Markdown'
        )
        
        try:
            # Get team evaluation
            idea_task = {
                'type': 'idea_evaluation',
                'content': f"Evaluate this idea: {idea}",
                'brief': True
            }
            
            responses = await self.orchestrator.get_team_consensus(idea_task)
            
            # Format response
            message = "💡 **Team Evaluation:**\n\n"
            
            for agent, response in responses.get('responses', {}).items():
                emoji = {'ceo': '👔', 'developer': '💻', 'project_manager': '📊', 'designer': '🎨'}.get(agent, '👤')
                content = response.get('content', 'No response') if isinstance(response, dict) else str(response)
                message += f"{emoji} **{agent.title()}:** {content[:200]}...\n\n"
            
            await update.message.reply_text(
                message[:4000],
                parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Error evaluating idea: {e}")
            await update.message.reply_text(
                "⚠️ Error evaluating idea. Please try again.",
                parse_mode='Markdown'
            )
    
    async def _handle_agent_conversation(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                                       message: str, agent: str):
        """Handle conversation with specific agent"""
        try:
            task = {
                'type': 'conversation',
                'content': message,
                'brief': True
            }
            
            response = await self.orchestrator.route_to_agent(agent, task)
            
            formatted_response = self._format_agent_response(response)
            
            keyboard = [
                [InlineKeyboardButton("👥 Ask Another Agent", callback_data="team")],
                [InlineKeyboardButton("🔙 Main Menu", callback_data="start")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                formatted_response[:4000],
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            
        except Exception as e:
            self.logger.error(f"Error in agent conversation: {e}")
            await update.message.reply_text(
                "⚠️ Error getting response. Please try again.",
                parse_mode='Markdown'
            )
    
    async def _handle_project_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE, message: str):
        """Handle messages during project planning"""
        user_id = update.effective_user.id
        project_name = self.user_sessions[user_id]['context'].get('project_name', 'Unknown')
        
        try:
            # Route to PM for project-related queries
            task = {
                'type': 'project_query',
                'content': f"Regarding project {project_name}: {message}",
                'brief': True
            }
            
            response = await self.orchestrator.route_to_agent('project_manager', task)
            
            formatted_response = self._format_agent_response(response)
            
            await update.message.reply_text(
                formatted_response[:4000],
                parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Error handling project message: {e}")
            await update.message.reply_text(
                "⚠️ Error processing your message. Please try again.",
                parse_mode='Markdown'
            )
    
    async def _handle_general_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE, message: str):
        """Handle general conversation"""
        try:
            # Determine which agent should respond
            task = {
                'type': 'general',
                'content': message,
                'brief': True
            }
            
            response = await self.orchestrator.analyze_and_route(task)
            
            formatted_response = self._format_agent_response(response)
            
            # Add follow-up options
            keyboard = self._create_follow_up_keyboard(response)
            reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
            
            await update.message.reply_text(
                formatted_response[:4000],
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            
        except Exception as e:
            self.logger.error(f"Error handling message: {e}")
            await update.message.reply_text(
                "⚠️ Sorry, I encountered an error. Please try again.",
                parse_mode='Markdown'
            )
    
    def _format_agent_response(self, response: Dict) -> str:
        """Format agent response for Telegram"""
        if not isinstance(response, dict):
            return str(response)
            
        agent = response.get('sender', 'Unknown')
        role = response.get('role', '')
        content = response.get('content', '')
        
        agent_emoji = {
            'Alex Chen': '👔',
            'Sarah Kim': '💻',
            'Mike Johnson': '📊',
            'Emma Davis': '🎨'
        }.get(agent, '👤')
        
        formatted = f"{agent_emoji} **{agent}** ({role}):\n\n{content}"
        
        # Add confidence indicator if available
        confidence = response.get('confidence')
        if confidence and isinstance(confidence, (int, float)):
            confidence_bar = '🟢' if confidence > 0.8 else '🟡' if confidence > 0.5 else '🔴'
            formatted += f"\n\n{confidence_bar} Confidence: {confidence:.0%}"
        
        return formatted
    
    def _create_follow_up_keyboard(self, response: Dict) -> List[List[InlineKeyboardButton]]:
        """Create follow-up action buttons based on response"""
        keyboard = []
        
        # Check for suggested next agents
        if isinstance(response, dict):
            next_agent = response.get('suggest_next_agent')
            if next_agent:
                keyboard.append([
                    InlineKeyboardButton(
                        f"Ask {next_agent.title()}", 
                        callback_data=f"ask_agent:{next_agent}"
                    )
                ])
            
            # Add standard options
            if response.get('requires_follow_up'):
                keyboard.append([
                    InlineKeyboardButton("📝 More Details", callback_data="more_details"),
                    InlineKeyboardButton("👥 Team Input", callback_data="team_input")
                ])
        
        # Always add help option
        keyboard.append([InlineKeyboardButton("❓ Help", callback_data="help")])
        
        return keyboard
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        user_id = update.effective_user.id
        session = self.user_sessions.get(user_id, {})
        
        status_message = "📊 **Current Status**\n\n"
        
        # Send typing action
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action="typing"
        )
        
        try:
            if session.get('context', {}).get('project_name'):
                project_name = session['context']['project_name']
                status_message += f"🚀 **Active Project:** {project_name}\n"
                status_message += f"📍 **Stage:** {session.get('state', 'Unknown')}\n\n"
                
                # Get project status from orchestrator
                status_task = {
                    'type': 'project_status',
                    'content': f"Status update for {project_name}",
                    'brief': True
                }
                
                status_response = await self.orchestrator.get_project_status(status_task)
                status_message += status_response.get('content', 'No status available')
            else:
                status_message += "No active project. Use /newproject to start!"
                
        except Exception as e:
            self.logger.error(f"Error getting status: {e}")
            status_message += "\n\nStatus information temporarily unavailable."
        
        keyboard = [
            [InlineKeyboardButton("🚀 New Project", callback_data="new_project")],
            [InlineKeyboardButton("📈 Full Report", callback_data="full_report")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            status_message[:4000],
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def team_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /team command"""
        team_message = """👥 **Meet Your AI Team**

👔 **Alex Chen** - CEO
_Strategic vision, business decisions, market analysis_

💻 **Sarah Kim** - Lead Developer  
_Technical architecture, coding, performance optimization_

📊 **Mike Johnson** - Project Manager
_Planning, timelines, resource allocation, risk management_

🎨 **Emma Davis** - UX/UI Designer
_User experience, visual design, branding, prototypes_

What would you like to discuss with the team?"""
        
        keyboard = [
            [InlineKeyboardButton("👔 Talk to CEO", callback_data="talk_ceo"),
             InlineKeyboardButton("💻 Talk to Dev", callback_data="talk_dev")],
            [InlineKeyboardButton("📊 Talk to PM", callback_data="talk_pm"),
             InlineKeyboardButton("🎨 Talk to Designer", callback_data="talk_designer")],
            [InlineKeyboardButton("👥 Team Meeting", callback_data="team_meeting")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            team_message,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_message = """❓ **SynapseBot Commands**

**Project Management:**
• `/newproject [name]` - Start a new project
• `/status` - Check current project status

**Team Interaction:**
• `/team` - Meet your AI team members
• `/help` - Show this help message

**Quick Actions:**
• Just type naturally, and I'll route your message to the right team member!

💡 **Tip:** Use the inline buttons for quick navigation!"""
        
        keyboard = [
            [InlineKeyboardButton("🚀 Start Project", callback_data="new_project")],
            [InlineKeyboardButton("👥 Meet Team", callback_data="team")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            help_message,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle errors in the bot"""
        self.logger.error(f"Exception while handling an update: {context.error}")
        
        try:
            # Log the error with traceback
            tb_string = ''.join(traceback.format_exception(None, context.error, context.error.__traceback__))
            self.logger.error(tb_string)
            
            # Notify user if possible
            if isinstance(update, Update) and update.effective_message:
                await update.effective_message.reply_text(
                    "⚠️ Sorry, an error occurred while processing your request. Please try again.",
                    parse_mode='Markdown'
                )
                
        except Exception:
            pass
    
    def setup_handlers(self):
        """Setup all command and message handlers"""
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("newproject", self.new_project))
        self.application.add_handler(CommandHandler("status", self.status_command))
        self.application.add_handler(CommandHandler("team", self.team_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        
        # Callback query handler
        self.application.add_handler(CallbackQueryHandler(self.handle_callback_query))
        
        # Message handler
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        # Error handler
        self.application.add_error_handler(self.error_handler)
    
    async def initialize(self):
        """Initialize the bot application"""
        try:
            # Create application
            self.application = Application.builder().token(self.token).build()
            
            # Set up handlers
            self.setup_handlers()
            
            self.logger.info("Bot initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing bot: {e}")
            raise
    
    def run(self):
        """Run the bot (synchronous wrapper)"""
        try:
            # Initialize application
            self.application = Application.builder().token(self.token).build()
            
            # Set up handlers
            self.setup_handlers()
            
            # Start the bot
            self.logger.info("Starting Synapse Bot...")
            self.application.run_polling(allowed_updates=Update.ALL_TYPES)
            
        except Exception as e:
            self.logger.error(f"Error running bot: {e}")
            raise