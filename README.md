# AI Commit Message Generator (acmsg)

A Python tool that automatically generates meaningful git commit messages using AI models through the OpenRouter API.

## Features

- Analyzes staged changes in your git repository
- Generates contextual commit messages using AI
- Supports multiple AI models via [OpenRouter](https://openrouter.ai)
- Automatically commits changes with generated message

## Prerequisites
- [OpenRouter](https://openrouter.ai/) API Key

## Installation

### With Nix Flakes:
```bash
# Add this flake as an input
inputs.acmsg.url = "github:quinneden/acmsg";

# Add the overlay & include the package in your configuration
nixpkgs.overlays = [ inputs.acmsg.overlays.default ];
environment.systemPackages = [ pkgs.acmsg ];

# Or just add the package directly
environment.systemPackages = [ inputs.acmsg.packages.${pkgs.system}.acmsg ];
```

## Usage

```bash
# Save api_token configuration value
$ acmsg config set api_token <token_value>

# Optional: Change AI model
acmsg config set model <model>

# Stage your changes first
git add <files>

# Review message & commit
$ acmsg commit
Commit message:

feat(content): add portfolio site content


Do you want to commit? (y/n):
```

## Configuration

You can also configure default settings in `~/.config/git-commit-ai/config.yaml`:

```yaml
api_token: **-**-**-****************************************************************
model: deepseek/deepseek-r1:free # Default model
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Submit a Pull Request

## License

MIT License - See LICENSE file for details
