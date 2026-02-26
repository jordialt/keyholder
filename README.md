# 🔐 Keyholder

A minimal CLI to store and retrieve API keys using your operating system's secure keyring (GNOME Keyring, KWallet, macOS Keychain).

## Installation

```bash
cd keyholder
./install.sh
```

This creates a virtual environment, installs dependencies (`keyring`, `pyperclip`), and symlinks the `keyholder` command to `~/.local/bin`.

## Usage

```bash
# Save a key
keyholder set openai sk-abc123

# Retrieve a key (copies to clipboard, auto-clears after 30s)
keyholder get openai

# Retrieve with custom clipboard timeout (in seconds, 0 = no auto-clear)
keyholder get openai --timeout 10

# List stored key names
keyholder list

# Remove a key
keyholder remove openai
```

## How it works

| Concern | Mechanism |
|---------|-----------|
| Secret storage | OS keyring via the `keyring` Python library (service name: `keyholder`) |
| Key listing | Lightweight index file at `~/.keyholder_index` (names only, no secrets) |
| Clipboard safety | After `get`, clipboard is overwritten with `""` after a configurable timeout |
| Migration | If `~/.keyholder.json` is found on first run, keys are imported into the keyring and the file is deleted |

## Requirements

- Python 3.8+
- A supported keyring backend (GNOME Keyring, KWallet, macOS Keychain)
- `xclip` / `xsel` / `pbcopy` for clipboard support

## Running Tests

```bash
source venv/bin/activate
python -m pytest test_main.py -v
```
