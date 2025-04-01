# ACMSG (automated commit message generator)

A Python tool that generates meaningful git commit messages by calling AI models using the OpenRouter API.

## Features

- Analyzes staged changes in your git repository
- Generates contextual commit messages using AI
- Supports multiple AI models via [OpenRouter](https://openrouter.ai)
- Optionally edit generated commit message
- Automatically commits changes with generated message, if confirmed

## Prerequisites
- OpenRouter API Key

## Installation

### with pipx:
```bash
pipx install acmsg
```

### with Nix flakes:
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

  chore: update README.md and poetry.lock

  README.md:
  - Change project title
  - Update project description to clarify tool functionality
  - Improve formatting and consistency

  poetry.lock:
  - Update dependencies to latest versions

Commit with this message? (y/n/e[dit]):
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
