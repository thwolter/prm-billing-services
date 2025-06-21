#!/usr/bin/env python
"""
Manage script for billing services.

This script provides a convenient way to run commands without having to type the full module path.

Example usage:
    python manage.py ensure_entitlement_features
    python manage.py ensure_entitlement_features --features feature1 feature2
"""

import sys
import importlib
import argparse

# Map of command names to their module paths
COMMANDS = {
    "ensure_entitlement_features": "billing_services.commands.ensure_entitlement_features",
    "meter_tokens": "billing_services.commands.meter_tokens",
}

def main():
    """
    Main entry point for the manage script.
    """
    parser = argparse.ArgumentParser(description="Billing services management script")
    parser.add_argument(
        "command",
        choices=COMMANDS.keys(),
        help="Command to run",
    )

    # Parse just the command argument
    args, remaining_args = parser.parse_known_args()

    # Get the module path for the command
    module_path = COMMANDS.get(args.command)
    if not module_path:
        print(f"Unknown command: {args.command}")
        sys.exit(1)

    # Import the module
    try:
        module = importlib.import_module(module_path)
    except ImportError as e:
        print(f"Error importing module {module_path}: {e}")
        sys.exit(1)

    # Replace sys.argv with the remaining args for the command
    sys.argv = [module_path] + remaining_args

    # Run the command's main function
    try:
        module.main()
    except Exception as e:
        print(f"Error running command {args.command}: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
