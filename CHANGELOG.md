## v0.2.3 (2025-05-09)

### Feat

- add release workflow and update version script
- **create-release**: replace shell script with Nix package

### Fix

- **ci**: remove --locked flag from uv sync command
- **ci**: add forgotten checkout step
- **deps**: fix python version in flake.nix
- **script/create-release.nix**: use branch variable and fix flag handling
- **create-release**: fix version variable
- **acmsg**: Fix semicolon to colon in error message

### Refactor

- fix ci workflow for hopefully the last time
- **ci**: move changelog generation to first job
- **flake**: rename create-release -> bump-version
- reorganize prompts and config setup

## v0.2.2 (2025-05-04)

### Feat

- Refactor configuration management and CLI interface

### Fix

- **config**: enhance CLI parameter management and error handling
- **__main__.py, system.md, user.md**: improve code readability and structure

## v0.2.1 (2025-05-02)

### Feat

- **model**: change default model from 'deepseek/deepseek-r1:free' to 'thudm/glm-4-32b:free'

### Fix

- **docs**: fix typos and reorganize layout in `README.md`
- Fix bug where manually editing commit message doesn't update the actual message used for the commit.
- **git_utils,config**: fix bugs in GitUtils.is_git_repo() and cli arg parsing
- update gitignore
- **flake**: add uv to dev-shell packages

### Refactor

- **open_router**: remove system prompt containing conventional commits spec
- **prompts**: change prompts to markdown format

## v0.2.0 (2025-04-16)

### Feat

- **release**: add release script
- **cli**: add loading spinner during message generation
- **prompts**: add system and user prompt templates
- add tests and dev dependencies
- add Python development environment to flake.nix
- **git_utils**: improve git status handling
- **package**: update dependencies

### Fix

- **open_router**: update OpenRouter to fetch Conventional Commits specification
- **open_router**: update system message content
- **api**: handle newline in commit message response

## v0.1.0 (2025-03-31)

### Feat

- add Git AI Commit Message Generator
