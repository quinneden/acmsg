# Git AI Commit Message Generator

A Python tool that automatically generates meaningful git commit messages using AI models through the OpenRouter API.

## Features

- Analyzes staged changes in your git repository
- Generates contextual commit messages using AI
- Supports multiple AI models via OpenRouter
- Automatically commits changes with generated message

## Installation

```bash
pip install git-ai-commit
```

## Prerequisites
- [OpenRouter](https://openrouter.ai/) API Key

## Usage

```bash
# Stage your changes first
git add <files>

# Generate commit message and commit
acmsg

# Or just generate a message without committing
git-commit-ai --preview
```

## Configuration

You can configure default settings in `~/.config/git-commit-ai/config.yaml`:

```yaml
model: 'anthropic/claude-3-haiku:beta' # Default AI model
max_tokens: 100            # Maximum length of commit message
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Submit a Pull Request

## License

MIT License - See LICENSE file for details
