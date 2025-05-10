# acmsg (automated commit message generator)

A cli tool written in Python that generates git commit messages using AI models
through the OpenRouter API.

[![Create Release and Publish to PyPI](https://github.com/quinneden/acmsg/actions/workflows/publish-and-release.yaml/badge.svg)](https://github.com/quinneden/acmsg/actions/workflows/publish-and-release.yaml)
[![Run Tests](https://github.com/quinneden/acmsg/actions/workflows/test.yaml/badge.svg?branch=main)](https://github.com/quinneden/acmsg/actions/workflows/test.yaml)

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
using flakes (i.e. nixos/nix-darwin/home-manager):
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
```

## Configuration

The configuration file is located at `~/.config/acmsg/config.yaml`.

To setup acmsg, you'll need to configure your OpenRouter API token by running
the following command:
```bash
$ acmsg config set api_token <your_api_token>
```

## Usage

```
usage: acmsg [-h] [--version] {commit,config} ...

Automated commit message generator

positional arguments:
  {commit,config}  Commands
    commit         generate a commit message
    config         manage configuration settings

options:
  -h, --help       show this help message and exit
  --version        display the program version and exit
```

## License

acmsg is licenced under the MIT License, as included in the [LICENSE](LICENSE) file.
