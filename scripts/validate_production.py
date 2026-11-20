#!/usr/bin/env python3
"""Validate the shape and internal consistency of a CineSheet manifest."""

import argparse
import json
import sys
from pathlib import Path

from production_state import assess_storyboard, asset_status, is_character_sheet


DEFAULT_SCHEMA = Path(__file__).resolve().parents[1] / "schemas/production.schema.json"


def schema_errors(data, schema_path):
    try:
        from jsonschema import Draft202012Validator
        from jsonschema.exceptions import SchemaError
    except ImportError:
        return ["jsonschema is required. Run python -m pip install -r requirements.txt from the Skill folder."]

    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        validator = Draft202012Validator(schema)
        errors = sorted(validator.iter_errors(data), key=lambda error: list(map(str, error.path)))
    except (OSError, UnicodeError, json.JSONDecodeError, SchemaError) as exc:
        return [f"Schema unavailable or invalid: {exc}"]
    return ["Schema /" + "/".join(map(str, error.path)) + ": " + error.message for error in errors]


def indexed_by_id(records, label, errors):
    index = {}
    for record in records:
        identifier = record["id"]
        if identifier in index:
            errors.append(f"Duplicate {label} ID: {identifier}")
        index[identifier] = record
    return index


def check_production(data, project_dir):
    """Check relationships after schema validation has succeeded."""
    errors, warnings = [], []
    assets = indexed_by_id(data["assets"], "asset", errors)
    characters = indexed_by_id(data["characters"], "character", errors)
    indexed_by_id(data["scenes"], "scene", errors)
    indexed_by_id(data["product_claims"], "claim", errors)

    for asset in assets.values():
        aid = asset["id"]
        status = asset["status"]
        if status == "present" and asset_status(asset, project_dir) != "present":
            if not asset["path"]:
                errors.append(f"Asset {aid} marked present but path absent")
            else:
                errors.append(f"Asset {aid} marked present but file does not exist: {asset['path']}")
        elif status in {"missing", "planned"}:
            warnings.append(f"Asset {aid} is {status} and unavailable for attachment")

    for cid, character in characters.items():
        references = character.get("reference_asset_ids", [])
        if sum(is_character_sheet(cid, aid) for aid in references) > 1:
            errors.append(f"Character {cid} must link at most one current character sheet")
        for aid in references:
            if aid not in assets:
                errors.append(f"Character {cid} references unknown asset {aid}")
            elif assets[aid]["kind"] != "character":
                errors.append(f"Character {cid} reference asset must have kind=character: {aid}")

    elapsed = 0
    for sequence, scene in enumerate(data["scenes"], start=1):
        sid = scene["id"]
        if scene["sequence"] != sequence:
            errors.append(f"{sid} sequence must be {sequence}")
        if scene["start_seconds"] != elapsed:
            errors.append(f"{sid} starts at {scene['start_seconds']} but must start at {elapsed}")
        elapsed += scene["duration_seconds"]

        for cid in scene["continuity"]["character_ids"]:
            if cid not in characters:
                errors.append(f"{sid} references unknown character {cid}")
        for line in scene["audio"]["dialogue"]:
            if line["speaker_id"] not in characters:
                errors.append(f"{sid} speaker ID unknown: {line['speaker_id']}")

        video = scene["video"]
        for aid in video["reference_asset_ids"]:
            if aid not in assets:
                errors.append(f"{sid} references unknown video asset: {aid}")
        if video["generation_status"] == "completed":
            warnings.append(f"{sid}: generation_status=completed. Verify the actual video file separately.")

        for panel in scene["visual"].get("storyboard_panels", []):
            for aid in panel.get("reference_asset_ids", []):
                if aid not in assets:
                    errors.append(f"{sid} panel {panel['id']} references unknown source asset: {aid}")

    duration = data["project"]["duration_seconds"]
    if elapsed != duration:
        errors.append(f"All scenes total {elapsed}s, project duration {duration}s")

    for claim in data["product_claims"]:
        if claim["verification"] != "verified":
            if claim["permitted_copy"]:
                errors.append(f"Unverified claim cannot be permitted in advertising copy: {claim['id']}")
            warnings.append(f"Claim {claim['id']} is {claim['verification']}. Exclude from copy until substantiated.")

    review = assess_storyboard(data, assets, project_dir)
    errors.extend(review.errors)
    warnings.extend(review.warnings)
    if data["workflow"]["production_authorized"] and data["workflow"]["approval_status"] != "approved":
        errors.append("Production authorization requires an approved production sheet")
    return errors, warnings


def load_and_check_file(path: Path, schema_path: Path = DEFAULT_SCHEMA):
    """Return the same JSON object that passed validation for use by consumers."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return None, [f"Cannot read production JSON: {exc}"], []

    errors = schema_errors(data, schema_path)
    if errors:
        return data, errors, []
    errors, warnings = check_production(data, path.parent)
    return data, errors, warnings


def check_file(path: Path, schema_path: Path = DEFAULT_SCHEMA):
    _, errors, warnings = load_and_check_file(path, schema_path)
    return errors, warnings


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("production", type=Path)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    args = parser.parse_args()

    errors, warnings = check_file(args.production.resolve(), args.schema.resolve())
    for warning in warnings:
        print("WARNING:", warning)
    for error in errors:
        print("ERROR:", error)
    if errors:
        print(f"FAILED ({len(errors)} error(s), {len(warnings)} warning(s))")
        return 1
    print(f"PASS: production JSON validated ({len(warnings)} warning(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
