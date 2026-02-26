import argparse
import json
import os
import sys
import threading

import keyring
import pyperclip

# Configuration
SERVICE_NAME = "keyholder"
INDEX_PATH = os.path.expanduser("~/.keyholder_index")
LEGACY_CONFIG_PATH = os.path.expanduser("~/.keyholder.json")


# ── Index helpers ──────────────────────────────────────────────────────────

def _load_index():
    """Return the set of key names tracked in the index file."""
    if not os.path.exists(INDEX_PATH):
        return set()
    with open(INDEX_PATH, "r") as f:
        return {line.strip() for line in f if line.strip()}


def _save_index(names):
    """Persist the set of key names to the index file."""
    existed = os.path.exists(INDEX_PATH)
    with open(INDEX_PATH, "w") as f:
        for name in sorted(names):
            f.write(name + "\n")
    if not existed:
        os.chmod(INDEX_PATH, 0o600)


# ── Migration ──────────────────────────────────────────────────────────────

def _maybe_migrate():
    """If ~/.keyholder.json exists, offer to import keys into the keyring."""
    if not os.path.exists(LEGACY_CONFIG_PATH):
        return

    print("Found legacy key file ~/.keyholder.json.")
    answer = input("Migrate keys to the system keyring and delete the file? [Y/n] ").strip().lower()
    if answer not in ("", "y", "yes"):
        return

    try:
        with open(LEGACY_CONFIG_PATH, "r") as f:
            keys = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error reading legacy file: {e}", file=sys.stderr)
        return

    index = _load_index()
    migrated = 0
    for name, value in keys.items():
        keyring.set_password(SERVICE_NAME, name, value)
        index.add(name)
        migrated += 1

    _save_index(index)
    os.remove(LEGACY_CONFIG_PATH)
    print(f"Migrated {migrated} key(s) to the system keyring. Legacy file deleted.")


# ── Clipboard auto-clear ──────────────────────────────────────────────────

def _schedule_clipboard_clear(timeout):
    """Overwrite the clipboard with an empty string after *timeout* seconds."""
    if timeout <= 0:
        return

    def _clear():
        try:
            pyperclip.copy("")
        except Exception:
            pass  # silently ignore if display server is gone

    timer = threading.Timer(timeout, _clear)
    timer.daemon = True
    timer.start()


# ── Commands ───────────────────────────────────────────────────────────────

def set_key(name, key):
    keyring.set_password(SERVICE_NAME, name, key)
    index = _load_index()
    index.add(name)
    _save_index(index)
    print(f"Key for '{name}' saved successfully.")


def get_key(name, timeout=30):
    key = keyring.get_password(SERVICE_NAME, name)
    if key is None:
        print(f"Error: Key for '{name}' not found.", file=sys.stderr)
        sys.exit(1)

    try:
        pyperclip.copy(key)
        print(f"Key for '{name}' has been copied to your clipboard.")
        if timeout > 0:
            print(f"Clipboard will be cleared in {timeout} seconds.")
            _schedule_clipboard_clear(timeout)
    except Exception as e:
        print(f"Failed to copy to clipboard (is a display server running?): {e}", file=sys.stderr)
        print(f"Key: {key}")


def list_keys():
    names = _load_index()
    if not names:
        print("No keys saved currently.")
        return
    print("Saved service keys:")
    for name in sorted(names):
        print(f"  - {name}")


def remove_key(name):
    index = _load_index()
    if name not in index:
        print(f"Error: Key for '{name}' not found.", file=sys.stderr)
        sys.exit(1)

    keyring.delete_password(SERVICE_NAME, name)
    index.discard(name)
    _save_index(index)
    print(f"Key for '{name}' removed successfully.")


# ── CLI ────────────────────────────────────────────────────────────────────

def main():
    _maybe_migrate()

    parser = argparse.ArgumentParser(description="Keyholder: A simple CLI to manage and retrieve API keys.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Set command
    parser_set = subparsers.add_parser("set", help="Save an API key for a service.")
    parser_set.add_argument("name", type=str, help="Name of the service (e.g., 'elevenlabs', 'openai')")
    parser_set.add_argument("key", type=str, help="The API key itself")

    # Get command
    parser_get = subparsers.add_parser("get", help="Retrieve an API key and copy it to the clipboard.")
    parser_get.add_argument("name", type=str, help="Name of the service")
    parser_get.add_argument("--timeout", type=int, default=30,
                            help="Seconds before clipboard is cleared (default: 30, 0 to disable)")

    # List command
    subparsers.add_parser("list", help="List all saved service names.")

    # Remove command
    parser_remove = subparsers.add_parser("remove", help="Remove an API key from storage.")
    parser_remove.add_argument("name", type=str, help="Name of the service")

    args = parser.parse_args()

    if args.command == "set":
        set_key(args.name, args.key)
    elif args.command == "get":
        get_key(args.name, timeout=args.timeout)
    elif args.command == "list":
        list_keys()
    elif args.command == "remove":
        remove_key(args.name)


if __name__ == "__main__":
    main()
