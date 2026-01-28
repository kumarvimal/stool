# Example Third-Party Project

This directory demonstrates how a third-party project would use `stool`.

## Structure

```
my-project/
├── tasks.py              # Bootstrap file (2 lines)
├── _stool/               # Custom tasks directory
│   ├── __init__.py
│   ├── _settings.py      # Project configuration
│   └── deploy.py         # Example custom tasks
└── src/                  # Your actual project code
    └── myapp/
        └── __init__.py
```

## Usage

1. Install stool in your environment:
   ```bash
   pip install stool
   ```

2. Initialize (two options):
   ```bash
   # Option 1: Use standalone command
   stool-init            # Creates tasks.py
   inv init.project      # Creates _stool/ directory

   # Option 2: Manual
   # Create tasks.py with 2 lines, then:
   inv init.project      # Creates _stool/ directory
   ```

3. Use commands:
   ```bash
   inv -l                # List all tasks
   inv hello             # Run builtin command
   inv deploy            # Run custom command
   ```

## Key Points

- Only `tasks.py` and `_stool/` are needed
- `tasks.py` is just 2 lines
- Custom tasks in `_stool/*.py` are auto-discovered
- All builtin commands from `stool` are available
- Configuration in `_stool/_settings.py`
