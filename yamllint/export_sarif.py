"""Export sarif format."""

import json
from pathlib import Path


def export_sarif(report: dict, output_file: str) -> None:
    """
    Export linting report in SARIF format.

    :param report: Dictionary containing linting results.
    :param output_file: Path to the SARIF output file.
    """
    # Aggregate unique rule IDs from results
    rules = {}
    for result in report.get("results", []):
        rule_id = result.get("rule")
        if rule_id:
            rules[rule_id] = {"id": rule_id, "shortDescription": {"text": rule_id}}
    
    sarif = {
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "yamllint",
                        "informationUri": "https://example.com/yamllint",
                        "rules": list(rules.values())
                    }
                },
                "results": report.get("results", [])
            }
        ]
    }
    output_path = Path(output_file)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(sarif, f, indent=2)
