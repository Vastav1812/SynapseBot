# 🚀 SynapseBot - AI-Powered Team Assistant

<div align="center">
  <img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/telegram--bot-20.7+-green.svg" alt="python-telegram-bot">
  <img src="https://img.shields.io/badge/gemini-1.5--flash-orange.svg" alt="Gemini AI">
  <img src="https://img.shields.io/badge/license-MIT-purple.svg" alt="MIT License">
</div>

## 🤖 Overview

SynapseBot is an innovative Telegram bot that simulates an entire AI development team, powered by Google's Gemini AI. It features four specialized AI agents that work together to help you plan, design, and execute projects.

### 👥 Meet Your AI Team

- **👔 Alex Chen (CEO)** - Strategic vision, business decisions, and market analysis
- **💻 Sarah Kim (Lead Developer)** - Technical architecture, coding solutions, and optimization
- **📊 Mike Johnson (Project Manager)** - Project planning, timelines, and resource allocation
- **🎨 Emma Davis (UX/UI Designer)** - User experience, visual design, and creative solutions

## ✨ Features

- **🎯 Intelligent Task Routing** - Automatically routes your questions to the most qualified agent
- **👥 Team Collaboration** - Get perspectives from multiple agents on complex topics
- **📋 Project Management** - Full project lifecycle support from ideation to execution
- **💬 Natural Conversations** - Chat naturally with any team member
- **🔄 Context Awareness** - Maintains conversation history and project context
- **⚡ Real-time Responses** - Quick, thoughtful responses from each agent
- **📊 Status Tracking** - Monitor project progress and team activity

## 🛠️ Tech Stack

- **Language**: Python 3.8+
- **Bot Framework**: python-telegram-bot 20.7+
- **AI Engine**: Google Gemini 1.5 Flash
- **Architecture**: Modular agent-based system
- **Async Support**: Full asyncio implementation

## 📋 Prerequisites

Before you begin, ensure you have:

- Python 3.8 or higher installed
- A Telegram Bot Token (from [@BotFather](https://t.me/botfather))
- A Google Gemini API Key (from [Google AI Studio](https://makersuite.google.com/app/apikey))

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/synapse-bot.git
cd synapse-bot
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the root directory:

```env
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
BOT_USERNAME=YourBotUsername

# Google Gemini Configuration
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-1.5-flash

# Model Parameters (Optional)
MODEL_TEMPERATURE=0.7
MODEL_TOP_P=0.95
MODEL_TOP_K=40
MODEL_MAX_TOKENS=2048

# Application Settings
DEBUG=False
LOG_LEVEL=INFO
```

### 4. Run the Bot

```bash
python main.py
```

## 📱 Usage

### Basic Commands

- `/start` - Initialize the bot and see the main menu
- `/newproject [name]` - Start a new project with your AI team
- `/team` - Meet your AI team members
- `/status` - Check current project status
- `/help` - Show available commands

### Example Interactions

1. **Starting a New Project**
   ```
   /newproject AI Shopping Assistant
   ```
   The CEO will provide initial assessment, then you can get input from other team members.

2. **Direct Agent Conversation**
   ```
   You: "What's the best database for a real-time chat app?"
   Bot: *Routes to Developer who provides technical recommendation*
   ```

3. **Team Meeting**
   ```
   Click "Team Meeting" button to get perspectives from all agents
   ```

## 🏗️ Project Structure

```
synapse-bot/
├── agents/                 # AI Agent implementations
│   ├── __init__.py
│   ├── base_agent.py      # Base agent class
│   ├── ceo_agent.py       # CEO agent
│   ├── developer_agent.py # Developer agent
│   ├── designer_agent.py  # Designer agent
│   └── manager_agent.py   # Project Manager agent
├── llm/                   # Language Model integration
│   ├── __init__.py
│   └── gemini_client.py   # Gemini AI client
├── orchestrator/          # Communication orchestration
│   ├── __init__.py
│   ├── communication.py   # Agent orchestrator
│   └── task_manager.py    # Task management
├── telegram_bot/          # Telegram bot implementation
│   ├── __init__.py
│   └── bot.py            # Main bot logic
├── data/                  # Data storage
│   ├── conversations/     # Conversation history
│   └── projects/         # Project data
├── .env                   # Environment variables
├── config.py             # Configuration management
├── main.py               # Application entry point
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `TELEGRAM_BOT_TOKEN` | Your Telegram bot token | Required |
| `GEMINI_API_KEY` | Google Gemini API key | Required |
| `GEMINI_MODEL` | Gemini model to use | gemini-1.5-flash |
| `MODEL_TEMPERATURE` | Response creativity (0-1) | 0.7 |
| `MODEL_TOP_P` | Nucleus sampling | 0.95 |
| `MODEL_TOP_K` | Top-k sampling | 40 |
| `MODEL_MAX_TOKENS` | Max response length | 2048 |
| `DEBUG` | Enable debug mode | False |
| `LOG_LEVEL` | Logging level | INFO |

### Agent Customization

You can customize agent personalities and capabilities by modifying the agent files in the `agents/` directory. Each agent has:

- Defined skills and expertise
- Response style and personality
- Specialized task handlers
- Decision-making frameworks

## 🧪 Testing

Run the test script to verify all components are working:

```bash
python test_bot.py
```

This will test:
- ✅ Configuration validation
- ✅ Gemini AI connection
- ✅ Agent orchestration
- ✅ Team consensus functionality

## 🛠️ Development

### Adding New Agents

1. Create a new agent class in `agents/` inheriting from `BaseAgent`
2. Define agent capabilities and response style
3. Implement specialized task handlers
4. Register the agent in the orchestrator

### Extending Functionality

- **New Commands**: Add handlers in `telegram_bot/bot.py`
- **New Task Types**: Extend task handlers in agent classes
- **Custom Workflows**: Modify orchestrator in `orchestrator/communication.py`

## 🐛 Troubleshooting

### Common Issues

1. **Bot not responding**
   - Check your bot token is correct
   - Ensure the bot is running (`python main.py`)
   - Verify internet connection

2. **Gemini API errors**
   - Verify your API key is valid
   - Check API quotas and limits
   - Ensure proper internet connectivity

3. **Agent response errors**
   - Check logs for detailed error messages
   - Verify Gemini model is accessible
   - Review agent task handling logic

### Debug Mode

Enable debug logging by setting in `.env`:
```env
DEBUG=True
LOG_LEVEL=DEBUG
```

## 📊 Performance Optimization

- **Response Caching**: Implement Redis caching for frequent queries
- **Async Operations**: All operations are async for better performance
- **Rate Limiting**: Built-in rate limiting to prevent API abuse
- **Context Management**: Efficient conversation history management

## 🔒 Security Considerations

- Store API keys securely in environment variables
- Never commit `.env` file to version control
- Implement user authentication for sensitive operations
- Regular security audits of dependencies

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Google Gemini AI for powering the intelligence
- python-telegram-bot community for the excellent framework
- All contributors and users of SynapseBot


---

<div align="center">
  Made with ❤️ by the SynapseBot Team
</div>