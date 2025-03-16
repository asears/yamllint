# Upgrading to pyproject.toml Configuration

This document explains how to migrate your yamllint configuration from the traditional YAML files
(e.g. `default.yaml` or `relaxed.yaml`) to the `pyproject.toml` file using the `[tool.yamllint]` key.

## What’s New?

- You can now configure yamllint using `pyproject.toml`.
- The configuration should be placed under the `[tool.yamllint]` section.
- The format is similar to the existing YAML setup.

## Example

Below is an example configuration in `pyproject.toml`:

````toml
# pyproject.toml

[tool.yamllint]
extends = "default"

[rules.braces]
level = "warning"
max-spaces-inside = 1

[rules.brackets]
level = "warning"
max-spaces-inside = 1

[rules.colons]
level = "warning"

[rules.commas]
level = "warning"

[rules.comments]
# Set the rule to "disable" to turn comments linting off.
level = "disable"

# ... additional rules ...
````

## Details for Maintainers

- The TOML configuration leverages the standard [TOML format](https://toml.io/en/) and adheres to
  [PEP 518](https://www.python.org/dev/peps/pep-0518/) and [PEP 621](https://www.python.org/dev/peps/pep-0621/).
- When a `pyproject.toml` file exists with a `[tool.yamllint]` section, its configuration will be used
  instead of the legacy YAML files.
- The migration is straightforward: simply convert your existing YAML configuration into valid TOML using tables.

## Migration Steps

1. Create or update `pyproject.toml` at the root of your project.
2. Add your yamllint configuration under the `[tool.yamllint]` section.
3. Optionally, archive or remove the old configuration files (`default.yaml` and `relaxed.yaml`).
4. Run yamllint to verify that the new configuration loads correctly.

For further information on the TOML format and related PEP standards, refer to the links provided above.
