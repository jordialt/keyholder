# 🔑 Keyholder

A simple, lightweight CLI tool to securely store and retrieve your API keys. Never go hunting through files again — just ask for a key and it's on your clipboard, ready to paste.

## Features

- **Store** API keys locally with strict file permissions (`600`)
- **Retrieve & copy** keys directly to your clipboard
- **List** all your configured services
- **Remove** keys you no longer need

## Installation

```bash
git clone https://github.com/yourusername/keyholder.git
cd keyholder
chmod +x install.sh
./install.sh
```

> [!NOTE]
> The installer creates a Python virtual environment in the project folder and links the `keyholder` command to `~/.local/bin/`. Make sure this directory is in your `$PATH`.
>
> You can check by running `echo $PATH`. If it's missing, add this to your `~/.bashrc` or `~/.zshrc`:
> ```bash
> export PATH="$HOME/.local/bin:$PATH"
> ```

## Usage

```bash
# Save an API key
keyholder set <service> <key>

# Get a key (copies to clipboard automatically)
keyholder get <service>

# List all saved services
keyholder list

# Remove a key
keyholder remove <service>
```

### Example

```bash
keyholder set elevenlabs sk-my-elevenlabs-key
keyholder set openai sk-my-openai-key

keyholder list
# Saved service keys:
#   - elevenlabs
#   - openai

keyholder get elevenlabs
# Key for 'elevenlabs' has been copied to your clipboard.
```

## Storage

Keys are saved in `~/.keyholder.json` with `600` permissions (readable only by your user). This file is excluded from the repo via `.gitignore`.

## Running Tests

```bash
venv/bin/python -m unittest test_main.py
```

## Requirements

- Python 3.8+
- `pyperclip` (installed automatically by `install.sh`)
