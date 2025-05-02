# acmsg (automated commit message generator)

A cli tool written in Python that generates git commit messages using AI models
through the OpenRouter API.

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

### with nix:
using flakes, i.e. nixos/nix-darwin/home-manager:
```bash
# Add `acmsg` to your flake inputs
inputs.acmsg.url = "github:quinneden/acmsg";

# Add the nixpkgs overlay & include the package in your configuration
nixpkgs.overlays = [ inputs.acmsg.overlays.default ];
environment.systemPackages = [ pkgs.acmsg ];
# or home.packages = [ pkgs.acmsg ];

# Or include the package directly from inputs
environment.systemPackages = [ inputs.acmsg.packages.${pkgs.system}.acmsg ];
```
using a standalone profile:
```bash
$ nix profile install "github:quinneden/acmsg"
# or run the command directly, without installation
$ nix run "github:quinneden/acmsg" -- commit
```

## Configuration

You can also configure default settings directly in `~/.config/acmsg/config.yaml`:

```yaml
api_token: <OPENROUTER_API_TOKEN>
model: thudm/glm-4-32b:free # Default model
```

## Usage

```bash
# Set api_token in config
$ acmsg config set api_token <token_value>

# Optionally, configure a different default model
$ acmsg config set model <model>

# Stage your changes
$ git add <files>

# Review message & commit
$ acmsg commit
# output:
  Commit message:

    fix(docs): fix typo in `README.md`

  Commit with this message? (y/n/e[dit]):
```

## License

acmsg is licenced under the MIT License, as included in the [LICENSE](LICENSE) file.
