# stool

Modern Python project task management with automatic command discovery.

## Overview

`stool` is a task management framework built with modern Python practices. It provides:

- **Zero-config task discovery**: Install the package and bootstrap with one command
- **Automatic merging**: Builtin commands + your custom commands unified
- **Minimal footprint**: Only `tasks.py` (2 lines) and `_stool/` directory needed
- **Modern Python**: Uses `pyproject.toml`, src layout, pathlib, and Python 3.13+

## Installation

```bash
pip install stool
```

For PDF commands:

```bash
pip install "stool[all]"
brew install ghostscript  # for image recompression
```

## Quick Start

### Method 1: Using stool-init (Recommended)

```bash
# Navigate to your project
cd my-project

# Bootstrap stool (creates tasks.py)
stool-init

# Complete setup (creates _stool/ directory)
inv init.project

# Or with gitignore: 
# (in case you don't want to commit stool related files in your project)
inv init.project --add-to-gitignore
inv init.project --global-gitignore
```

### Method 2: Manual Setup

1. Create `tasks.py` in your project root:
    ```python
    from stool.tasks import init as namespace
    namespace = namespace(__file__)
    ```

2. Complete setup:
    ```bash
    inv init.project
    ```

### Verify Installation

```bash
# List all available tasks
inv -l

# Run the hello world example
inv hello

# Get help for a specific task
inv hello --help
```

## Project Structure

After initialization, your project will have:

```
my-project/
├── tasks.py              # Bootstrap (2 lines)
├── _stool/               # Your custom tasks
│   ├── __init__.py
│   ├── _settings.py      # Configuration
│   └── mycommand.py      # Your tasks
└── ... your project files
```

## Creating Custom Tasks

Add Python files in the `_stool/` directory:

```python
# _stool/deploy.py

import invoke

@invoke.task(default=True)
def production(ctx):
    """Deploy to production."""
    print("Deploying to production...")
    ctx.run("./deploy.sh production")

@invoke.task()
def staging(ctx):
    """Deploy to staging."""
    print("Deploying to staging...")
    ctx.run("./deploy.sh staging")
```

Your tasks are immediately available:

```bash
inv deploy              # Runs deploy.production (default)
inv deploy.staging      # Runs deploy.staging
```

## Configuration

Edit `_stool/_settings.py` to configure stool for your project:

```python
from stool.settings import create_env

env = create_env(
    # Disable specific base commands
    disabled_tasks=[
        'hello.*',           # Disable all hello tasks
        'hello.world',       # Or disable specific task
    ],

    # Add custom settings
    deployment_env='production',
    api_endpoint='https://api.example.com',
)
```

Access settings in your tasks:

```python
@invoke.task()
def deploy(ctx):
    env = ctx.config.deployment_env
    print(f"Deploying to {env}")
```

## Built-in Commands

### stool-init

Standalone command to bootstrap stool (creates `tasks.py`):

```bash
stool-init              # Creates tasks.py
```

### hello - Example commands

```bash
inv hello              # Hello current user (default)
inv hello.user         # Greet current user
```

### init - Project initialization

```bash
inv init.project       # Initialize stool in current project
inv init.clean         # Remove stool from project
```

### pdf - PDF utilities

```bash
inv pdf.compress --source input.pdf --output output.pdf
inv pdf.compress --source input.pdf --quality screen     # Smaller, lower quality
inv pdf.compress --source input.pdf --lossless           # No image recompression
inv pdf.compres --source input.pdf --output output.pdf   # Alias
```

## How It Works

### The Bootstrap Problem

Without `tasks.py`, you can't run `inv` commands. The `stool-init` command solves this:

```bash
pip install stool       # Install stool
cd my-project
stool-init             # Creates tasks.py (doesn't need inv)
inv init.project       # Now inv works! Creates _stool/
```

### Task Discovery

When you run `inv`, the system:

1. Scans `stool/` (installed package) for builtin commands
2. Scans your project's `_stool/` for local commands
3. Merges them into a unified namespace
4. Respects `disabled_tasks` configuration

### Bootstrap Pattern

Your `tasks.py` contains just:

```python
from stool.tasks import init as namespace
namespace = namespace(__file__)
```

This:
- Sets the project root
- Discovers all tasks
- Returns a merged collection
- Makes everything available to `invoke`

## Gitignore Support

The `inv init.project` command can automatically add stool files to gitignore.

### Interactive Prompt

When you run `inv init.project` (after `stool-init`), it will ask:

```
Do you want to add stool files to gitignore?
  1. No - commit tasks.py and _stool/ to version control
  2. Local gitignore - add to .gitignore in this project
  3. Global gitignore - add to ~/.gitignore_global
```

### Command Line Flags

Or use flags to skip the prompt:

```bash
# Add to local .gitignore
inv init.project --add-to-gitignore

# Add to global ~/.gitignore_global
inv init.project --global-gitignore
```

## Advanced Usage

### Custom Namespace

Override the default namespace in your task file:

```python
# _stool/mycommand.py

NAMESPACE = 'deploy'  # Use 'deploy' instead of 'mycommand'

import invoke

@invoke.task()
def prod(ctx):
    """Deploy to production."""
    pass
```

Now available as: `inv deploy.prod`

### Task Dependencies

```python
@invoke.task()
def build(ctx):
    """Build the project."""
    ctx.run("python -m build")

@invoke.task(pre=[build])
def deploy(ctx):
    """Deploy (builds first)."""
    ctx.run("./deploy.sh")
```

### Accessing Other Tasks

```python
from stool.tasks import exists, context

@invoke.task()
def check(ctx):
    """Check if a task exists."""
    if exists('hello.world'):
        print("hello.world exists")
```
