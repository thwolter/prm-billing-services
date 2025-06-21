# Entitlement Features Management

This directory contains commands for managing entitlement features in the system.

## ensure_entitlement_features

This command ensures that entitlement features exist in the system. It checks if the feature specified in the settings exists, and if not, creates it.

### When to run

This command should be run when:
- The parameter in Settings is changed (i.e., feature might now be necessary), or
- Manually triggered (e.g., admin action, migration script).

### Usage

```bash
# Ensure the feature from settings exists
python manage.py ensure_entitlement_features
# or
./manage.py ensure_entitlement_features

# Ensure specific features exist
python manage.py ensure_entitlement_features --features feature1 feature2
# or
./manage.py ensure_entitlement_features --features feature1 feature2
```

### Implementation Details

The command:
1. Checks if a feature exists by listing all entitlements and checking if any has the specified feature_key
2. Creates a feature by creating a dummy entitlement with the specified feature_key
3. Provides a main function that can be run from the command line, with an option to specify a list of feature keys to ensure

The EntitlementService has been modified to provide a more informative error message when a feature doesn't exist, suggesting to run this command.
