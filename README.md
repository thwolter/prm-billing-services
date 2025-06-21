# Billing Services

This repository contains the billing services for the project.

## Development

### Prerequisites

- Python 3.8+
- Poetry

### Installation

```bash
poetry install
```

### Testing

#### Local OpenMeter Instance

Some tests require a local OpenMeter instance. To set up a local OpenMeter instance:

1. Clone the OpenMeter repository:
   ```bash
   git clone git@github.com:openmeterio/openmeter.git
   cd openmeter/quickstart
   ```

2. Launch OpenMeter and its dependencies:
   ```bash
   docker compose up -d
   ```

3. The local OpenMeter instance will be available at `http://localhost:8888`. This URL is already configured in the `.env` file.

4. No bearer token is required for the local instance.

#### Running Tests

```bash
poetry run pytest
```

To run only the integration tests:

```bash
poetry run pytest -m integration
```

## Commands

### Using manage.py

The project includes a `manage.py` script at the root directory that provides a convenient way to run commands without having to type the full module path.

```bash
# General usage
python manage.py <command> [options]
# or (since the script is executable)
./manage.py <command> [options]

# List available commands
python manage.py --help
# or
./manage.py --help
```

### Ensure Entitlement Features

The `ensure_entitlement_features` command ensures that entitlement features exist in the system. It checks if the feature specified in the settings exists, and if not, creates it.

This command addresses the issue where the EntitlementService throws a 404 Not Found when a feature (e.g., "metered") does not exist. Instead of checking and creating the feature every time the service is called, this command allows you to run the check/create once when:
- The parameter in Settings is changed (i.e., feature might now be necessary), or
- Manually triggered (e.g., admin action, migration script).

#### Usage

```bash
# Using the module path
# Ensure the feature from settings exists
python -m billing_services.commands.ensure_entitlement_features

# Ensure specific features exist
python -m billing_services.commands.ensure_entitlement_features --features feature1 feature2

# Using the manage.py script (shorter and more convenient)
# Ensure the feature from settings exists
python manage.py ensure_entitlement_features
# or
./manage.py ensure_entitlement_features

# Ensure specific features exist
python manage.py ensure_entitlement_features --features feature1 feature2
# or
./manage.py ensure_entitlement_features --features feature1 feature2
```

For more details, see the [commands README](src/billing_services/commands/README.md).
