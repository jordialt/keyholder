import argparse
import json
import os
import sys
import pyperclip

# Configuration
CONFIG_PATH = os.path.expanduser("~/.keyholder.json")

def load_keys():
    if not os.path.exists(CONFIG_PATH):
        return {}
    try:
        with open(CONFIG_PATH, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        print("Error: ~/.keyholder.json is corrupted and could not be loaded.", file=sys.stderr)
        return {}

def save_keys(keys):
    # Ensure the file is created with secure permissions if it doesn't exist
    if not os.path.exists(CONFIG_PATH):
        open(CONFIG_PATH, 'w').close()
        os.chmod(CONFIG_PATH, 0o600)
    
    with open(CONFIG_PATH, 'w') as f:
        json.dump(keys, f, indent=4)
    os.chmod(CONFIG_PATH, 0o600)  # Re-apply permissions to be safe

def set_key(name, key):
    keys = load_keys()
    keys[name] = key
    save_keys(keys)
    print(f"Key for '{name}' saved successfully.")

def get_key(name):
    keys = load_keys()
    if name not in keys:
        print(f"Error: Key for '{name}' not found.", file=sys.stderr)
        sys.exit(1)
    
    key = keys[name]
    try:
        pyperclip.copy(key)
        print(f"Key for '{name}' has been copied to your clipboard.")
    except Exception as e:
        print(f"Failed to copy to clipboard (is a display server running?): {e}", file=sys.stderr)
        print(f"Key: {key}")

def list_keys():
    keys = load_keys()
    if not keys:
        print("No keys saved currently.")
        return
    print("Saved service keys:")
    for name in keys:
        print(f"  - {name}")

def remove_key(name):
    keys = load_keys()
    if name not in keys:
        print(f"Error: Key for '{name}' not found.", file=sys.stderr)
        sys.exit(1)
    
    del keys[name]
    save_keys(keys)
    print(f"Key for '{name}' removed successfully.")

def main():
    parser = argparse.ArgumentParser(description="Keyholder: A simple CLI to manage and retrieve API keys.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Set command
    parser_set = subparsers.add_parser("set", help="Save an API key for a service.")
    parser_set.add_argument("name", type=str, help="Name of the service (e.g., 'elevenlabs', 'openai')")
    parser_set.add_argument("key", type=str, help="The API key itself")

    # Get command
    parser_get = subparsers.add_parser("get", help="Retrieve an API key and copy it to the clipboard.")
    parser_get.add_argument("name", type=str, help="Name of the service")

    # List command
    parser_list = subparsers.add_parser("list", help="List all saved service names.")

    # Remove command
    parser_remove = subparsers.add_parser("remove", help="Remove an API key from storage.")
    parser_remove.add_argument("name", type=str, help="Name of the service")

    args = parser.parse_args()

    if args.command == "set":
        set_key(args.name, args.key)
    elif args.command == "get":
        get_key(args.name)
    elif args.command == "list":
        list_keys()
    elif args.command == "remove":
        remove_key(args.name)

if __name__ == "__main__":
    main()
