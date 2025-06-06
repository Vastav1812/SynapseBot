# Development Setup

This document provides instructions for setting up the development environment for SynapseBot.

## Prerequisites

- Python 3.11 or higher
- Git
- Docker (optional, for containerized development)

## Setup Steps

1. Clone the repository:
```bash
git clone https://github.com/yourusername/SynapseBot.git
cd SynapseBot
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install development dependencies:
```bash
pip install -r requirements.txt
```

4. Copy the example environment file:
```bash
cp .env.example .env
```

5. Update the `.env` file with your credentials:
- Get a Telegram Bot Token from [@BotFather](https://t.me/BotFather)
- Get a Gemini API Key from [Google AI Studio](https://makersuite.google.com/app/apikey)

## Development Workflow

1. Create a new branch for your feature:
```bash
git checkout -b feature/your-feature-name
```

2. Make your changes and commit them:
```bash
git add .
git commit -m "feat: your feature description"
```

3. Push your changes:
```bash
git push origin feature/your-feature-name
```

4. Create a Pull Request on GitHub

## Testing

Run the environment check:
```bash
python check_env.py
```

Run the requirements check:
```bash
python check_requirements.py
```

## Docker Development

Build the Docker image:
```bash
docker build -t synapsebot .
```

Run with Docker Compose:
```bash
docker-compose up
```

## Code Style

- Follow PEP 8 guidelines
- Use type hints
- Write docstrings for all functions and classes
- Keep functions small and focused
- Use meaningful variable names

## Logging

- Use the built-in logging module
- Log levels:
  - DEBUG: Detailed information for debugging
  - INFO: General information about program execution
  - WARNING: Warning messages for potentially problematic situations
  - ERROR: Error messages for serious problems
  - CRITICAL: Critical errors that may lead to program termination

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 