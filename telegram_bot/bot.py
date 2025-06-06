# telegram_bot/bot.py

import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, 
    CallbackQueryHandler, ContextTypes, filters,
    Defaults
)
import logging
from typing import Dict, List, Optional, Union
from datetime import datetime
import time
import pytz
from telegram import error as telegram_error
import traceback

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
                ceo_message,
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
        
        if data == "new_project":
            await query.edit_message_text(
                "Please use `/newproject [project name]` to start a new project.",
                parse_mode='Markdown'
            )
            
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
                message,
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
                message,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            
        except Exception as e:
            self.logger.error(f"Error in project planning: {e}")
            await query.edit_message_text(
                "⚠️ Error creating project plan. Please try again.",
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
            
            for agent, response in team_responses.items():
                agent_emoji = {
                    'ceo': '👔',
                    'developer': '💻',
                    'project_manager': '📊',
                    'designer': '🎨'
                }.get(agent, '👤')
                
                message += f"{agent_emoji} **{agent.title()}:**\n{response.get('content', 'No response')}\n\n"
            
            keyboard = [
                [InlineKeyboardButton("✅ Approve Project", callback_data=f"approve:{project_name}")],
                [InlineKeyboardButton("🔄 Refine Concept", callback_data=f"refine:{project_name}")],
                [InlineKeyboardButton("❌ Cancel", callback_data="cancel_project")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                message[:4000],  # Telegram message limit
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            
        except Exception as e:
            self.logger.error(f"Error in team discussion: {e}")
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
        
        # Route message based on session state
        if session['state'] == 'project_planning':
            await self._handle_project_message(update, context, message)
        else:
            await self._handle_general_message(update, context, message)
    
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
            
            if response:
                formatted_response = self._format_agent_response(response)
                
                # Add follow-up options
                keyboard = self._create_follow_up_keyboard(response)
                reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
                
                await update.message.reply_text(
                    formatted_response,
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
            else:
                await update.message.reply_text(
                    "I'm not sure how to help with that. Try /help for available commands.",
                    parse_mode='Markdown'
                )
                
        except Exception as e:
            self.logger.error(f"Error handling message: {e}")
            await update.message.reply_text(
                "⚠️ Sorry, I encountered an error. Please try again.",
                parse_mode='Markdown'
            )
    
    def _format_agent_response(self, response: Dict) -> str:
        """Format agent response for Telegram"""
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
        if confidence:
            confidence_bar = '🟢' if confidence > 0.8 else '🟡' if confidence > 0.5 else '🔴'
            formatted += f"\n\n{confidence_bar} Confidence: {confidence:.0%}"
        
        return formatted[:4000]  # Telegram limit
    
    def _create_follow_up_keyboard(self, response: Dict) -> List[List[InlineKeyboardButton]]:
        """Create follow-up action buttons based on response"""
        keyboard = []
        
        # Check for suggested next agents
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
        
        if session.get('context', {}).get('project_name'):
            project_name = session['context']['project_name']
            status_message += f"🚀 **Active Project:** {project_name}\n"
            status_message += f"📍 **Stage:** {session.get('state', 'Unknown')}\n\n"
            
            # Get project status from orchestrator
            try:
                status_task = {
                    'type': 'project_status',
                    'content': f"Status update for {project_name}",
                    'brief': True
                }
                
                status_response = await self.orchestrator.get_project_status(status_task)
                status_message += status_response.get('content', 'No status available')
                
            except Exception as e:
                self.logger.error(f"Error getting status: {e}")
                status_message += "Status information temporarily unavailable."
        else:
            status_message += "No active project. Use /newproject to start!"
        
        keyboard = [
            [InlineKeyboardButton("🚀 New Project", callback_data="new_project")],
            [InlineKeyboardButton("📈 Full Report", callback_data="full_report")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            status_message,
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
• `/tasks` - View and manage tasks

**Team Interaction:**
• `/team` - Meet your AI team members
• `/meeting` - Start a team meeting
• `/ask [question]` - Ask the team anything

**Quick Actions:**
• `/idea [description]` - Quick brainstorm
• `/review [topic]` - Get team review
• `/decide [options]` - Help with decisions

**Other Commands:**
• `/help` - Show this help message
• `/settings` - Configure preferences
• `/cancel` - Cancel current operation

💡 **Tip:** You can also just type naturally, and I'll route your message to the right team member!"""
        
        keyboard = [
            [InlineKeyboardButton("🚀 Start Project", callback_data="new_project")],
            [InlineKeyboardButton("👥 Meet Team", callback_data="team_intro")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            help_message,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    def setup_handlers(self, application):
        """Setup all command and message handlers"""
        # Command handlers
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CommandHandler("newproject", self.new_project))
        application.add_handler(CommandHandler("status", self.status_command))
        application.add_handler(CommandHandler("team", self.team_command))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("meeting", self.meeting))
        application.add_handler(CommandHandler("sprint", self.sprint_planning))
        
        # Callback query handler
        application.add_handler(CallbackQueryHandler(self.handle_callback_query))
        
        # Message handler
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
    
    async def initialize(self):
        """Initialize the bot application"""
        try:
            # Create defaults with proper pytz timezone
            defaults = Defaults(tzinfo=pytz.UTC)  # Use UTC as the default timezone
            
            # Initialize application with defaults
            self.application = (
                Application.builder()
                .token(self.token)
                .defaults(defaults)
                .build()
            )
            self.setup_handlers(self.application)
            
            # Add error handler
            self.application.add_error_handler(self.error_handler)
            
        except Exception as e:
            self.logger.error(f"Error initializing bot: {e}")
            raise
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle errors in the bot"""
        error = context.error
        self.logger.error(f"Update {update} caused error: {error}")
        
        try:
            if update and update.effective_message:
                error_message = "⚠️ Sorry, I encountered an error. "
                
                if isinstance(error, telegram_error.NetworkError):
                    error_message += "Network connection issue. Please try again in a moment."
                elif isinstance(error, telegram_error.Unauthorized):
                    error_message += "Bot token is invalid or expired."
                elif isinstance(error, telegram_error.BadRequest):
                    error_message += "Invalid request. Please check your input."
                elif isinstance(error, telegram_error.TimedOut):
                    error_message += "Request timed out. Please try again."
                elif isinstance(error, telegram_error.Conflict):
                    error_message += "Another request is in progress. Please wait."
                else:
                    error_message += "Please try again or use /help for available commands."
                
                await update.effective_message.reply_text(
                    error_message,
                    parse_mode='Markdown'
                )
                
                # Log detailed error for debugging
                self.logger.error(f"Detailed error: {traceback.format_exc()}")
                
        except Exception as e:
            self.logger.error(f"Error in error handler: {e}")
            self.logger.error(f"Original error: {traceback.format_exc()}")
    
    async def run(self):
        """Run the bot"""
        try:
            self.logger.info("Starting Synapse Bot...")
            await self.initialize()
            
            # Start polling
            await self.application.run_polling(
                allowed_updates=Update.ALL_TYPES,
                drop_pending_updates=True
            )
            
        except Exception as e:
            self.logger.error(f"Error running bot: {e}")
            raise

    async def meeting(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /meeting command"""
        user_id = update.effective_user.id
        
        # Get meeting topic from command args or default
        topic = ' '.join(context.args) if context.args else "General team meeting"
        
        # Send typing action
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action="typing"
        )
        
        # Start meeting message
        await update.message.reply_text(
            f"👥 **Starting Team Meeting**\n\nTopic: {topic}\n\nGathering team responses...",
            parse_mode='Markdown'
        )
        
        try:
            # Get responses from all agents
            meeting_task = {
                'type': 'team_meeting',
                'topic': topic,
                'context': 'Team meeting discussion'
            }
            
            responses = await self.orchestrator.get_team_consensus(meeting_task)
            
            # Send each response with a delay
            for agent, response in responses.items():
                await asyncio.sleep(1.5)  # Delay between responses
                await self.format_and_send_response(update, response)
                
        except Exception as e:
            self.logger.error(f"Error in meeting: {e}")
            await update.message.reply_text(
                "⚠️ Error during team meeting. Please try again.",
                parse_mode='Markdown'
            )

    async def sprint_planning(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /sprint command"""
        user_id = update.effective_user.id
        
        # Get sprint goal from command args or default
        sprint_goal = ' '.join(context.args) if context.args else "Next development cycle"
        
        # Send typing action
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action="typing"
        )
        
        # Start sprint planning message
        await update.message.reply_text(
            f"📋 **Starting Sprint Planning**\n\nGoal: {sprint_goal}\n\nProject Manager is preparing...",
            parse_mode='Markdown'
        )
        
        try:
            # Get sprint planning responses
            planning_task = {
                'type': 'sprint_planning',
                'goal': sprint_goal,
                'context': 'Sprint planning session'
            }
            
            responses = await self.orchestrator.handle_planning_task(planning_task)
            
            # Send each response with a delay
            for response in responses:
                await asyncio.sleep(1.5)  # Delay between responses
                await self.format_and_send_response(update, response)
                
        except Exception as e:
            self.logger.error(f"Error in sprint planning: {e}")
            await update.message.reply_text(
                "⚠️ Error during sprint planning. Please try again.",
                parse_mode='Markdown'
            )

    async def format_and_send_response(self, update: Update, response: Dict) -> None:
        """Format and send agent response"""
        try:
            # Format the response
            formatted = self._format_agent_response(response)
            
            # Escape special characters for Markdown
            formatted = formatted.replace('_', '\\_').replace('*', '\\*').replace('[', '\\[').replace(']', '\\]')
            
            # Send the message
            if update.callback_query:
                await update.callback_query.message.reply_text(
                    formatted,
                    parse_mode='Markdown',
                    disable_web_page_preview=True
                )
            else:
                await update.message.reply_text(
                    formatted,
                    parse_mode='Markdown',
                    disable_web_page_preview=True
                )
                
        except Exception as e:
            self.logger.error(f"Error formatting response: {e}")
            # Fallback to plain text if Markdown fails
            try:
                plain_text = response.get('content', 'No response available')
                if update.callback_query:
                    await update.callback_query.message.reply_text(plain_text)
                else:
                    await update.message.reply_text(plain_text)
            except Exception as e2:
                self.logger.error(f"Error sending fallback response: {e2}")