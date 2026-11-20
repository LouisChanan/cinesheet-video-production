"""Shared rules for production assets and storyboard approval."""

from dataclasses import dataclass
from pathlib import Path


STORYBOARD_KEYS = {
    "storyboard_preview_authorized",
    "storyboard_preview_status",
    "storyboard_preview_asset_id",
    "storyboard_images_authorized",
    "storyboard_images_status",
}
IMAGE_SUFFIXES = {".avif", ".gif", ".jpeg", ".jpg", ".png", ".svg", ".webp"}
SOURCE_REFERENCES = {"user", "licensed"}


def asset_path(asset, project_dir):
    path = asset.get("path")
    return Path(project_dir) / path if path else None


def asset_status(asset, project_dir):
    """Return the effective file status, including files that have disappeared."""
    status = asset.get("status", "planned")
    if status == "present":
        path = asset_path(asset, project_dir)
        try:
            if path is None or not path.is_file():
                return "missing"
        except (OSError, ValueError):
            return "missing"
    return status


def present_image_path(asset, project_dir):
    path = asset_path(asset, project_dir)
    if path and path.suffix.lower() in IMAGE_SUFFIXES and asset_status(asset, project_dir) == "present":
        return path
    return None


def is_character_sheet(character_id, asset_id):
    prefix = f"character_sheet_{character_id}_v"
    version = asset_id.removeprefix(prefix)
    return asset_id.startswith(prefix) and version.isascii() and version.isdecimal() and version[0] != "0"


def scene_panel_records(scene, assets_by_id):
    visual = scene["visual"]
    if visual.get("storyboard_panels"):
        return visual["storyboard_panels"]
    return [
        {
            "id": aid,
            "description": assets_by_id.get(aid, {}).get("description", aid),
            "image_asset_id": aid,
        }
        for aid in visual.get("storyboard_asset_ids", [])
    ]


@dataclass
class StoryboardReview:
    preview_id: str | None
    preview_visible: bool
    full_image_ids: frozenset[str]
    errors: list[str]
    warnings: list[str]

    def allows_asset(self, asset):
        if asset.get("kind") != "storyboard":
            return True
        if asset["id"] == self.preview_id:
            return self.preview_visible
        return asset.get("source") in SOURCE_REFERENCES or asset["id"] in self.full_image_ids


def assess_storyboard(production, assets_by_id, project_dir):
    """Validate the recorded gates and decide which images can appear in a sheet."""
    workflow = production["workflow"]
    staged = bool(STORYBOARD_KEYS.intersection(workflow))
    sheet_approved = workflow["approval_status"] == "approved"
    preview_status = workflow.get("storyboard_preview_status", "not_started")
    preview_authorized = workflow.get("storyboard_preview_authorized", False)
    preview_id = workflow.get("storyboard_preview_asset_id")
    images_status = workflow.get("storyboard_images_status", "not_started")
    images_authorized = workflow.get("storyboard_images_authorized", False)
    errors, warnings = [], []

    preview = assets_by_id.get(preview_id, {})
    preview_path = None
    if preview_id is not None:
        if not preview:
            errors.append(f"Unknown storyboard preview asset: {preview_id}")
        elif preview["kind"] != "storyboard":
            errors.append(f"Storyboard preview asset is not kind=storyboard: {preview_id}")
        else:
            preview_path = present_image_path(preview, project_dir)
    if preview_status in {"awaiting_review", "approved"}:
        if preview_id is None:
            errors.append(f"Storyboard preview status={preview_status} requires storyboard_preview_asset_id")
        elif preview and preview_path is None:
            errors.append(f"Storyboard preview must be a present image file when status={preview_status}: {preview_id}")
    preview_can_be_seen = preview_status in {"awaiting_review", "approved", "changes_requested"}
    if preview_can_be_seen and not preview_authorized:
        errors.append(f"Storyboard preview status={preview_status} requires preview authorization")
    if preview_status == "approved" and not sheet_approved:
        errors.append("Storyboard preview cannot be approved before the production sheet")
    preview_visible = bool(
        preview_path
        and preview_authorized
        and preview_can_be_seen
        and (preview_status != "approved" or sheet_approved)
    )
    if images_authorized and not (preview_visible and preview_status == "approved" and sheet_approved):
        errors.append("Full storyboard images require an approved storyboard preview and production sheet")
    if images_status == "declined" and images_authorized:
        errors.append("Declined storyboard image set cannot be authorized")
    if images_status == "generated" and not images_authorized:
        errors.append("Generated storyboard images require explicit storyboard_images_authorized=true")

    full_ids, full_paths = [], []
    held_legacy_ids = set()
    panel_ids = set()
    for scene in production["scenes"]:
        sid = scene["id"]
        visual = scene["visual"]
        panels = visual.get("storyboard_panels", [])
        panel_image_ids = [panel["image_asset_id"] for panel in panels]
        scene_image_ids = visual.get("storyboard_asset_ids", [])
        linked_ids = set(scene_image_ids) | (set(panel_image_ids) - {None})
        for panel in panels:
            pid = panel["id"]
            if pid in panel_ids:
                errors.append(f"Duplicate storyboard panel ID: {pid}")
            panel_ids.add(pid)
            aid = panel["image_asset_id"]
            references = panel.get("reference_asset_ids", [])
            image_path = present_image_path(assets_by_id.get(aid, {}), project_dir)
            if aid in references or (image_path and any(
                reference_path is not None and reference_path.resolve() == image_path.resolve()
                for reference_path in (
                    present_image_path(assets_by_id.get(ref_id, {}), project_dir) for ref_id in references
                )
            )):
                errors.append(f"{sid} panel {pid} cannot use its own image as a source reference")
        for aid in sorted(linked_ids):
            asset = assets_by_id.get(aid)
            if not asset or asset["kind"] != "storyboard":
                errors.append(f"{sid} references unknown or non-storyboard image asset: {aid}")
                continue
            if aid == preview_id:
                errors.append(f"{sid} cannot use the contact sheet as a full storyboard still: {aid}")
            if images_status != "generated" and asset["status"] == "present" and asset["source"] not in SOURCE_REFERENCES:
                if staged:
                    errors.append(f"{sid} links full storyboard image {aid} before an authorized set is complete")
                else:
                    held_legacy_ids.add(aid)

        if images_status != "generated":
            continue
        if None in panel_image_ids:
            errors.append(f"{sid} is missing a full image for one or more storyboard panels")
        if scene_image_ids != panel_image_ids:
            errors.append(f"{sid} storyboard_asset_ids must match panel image assets in order")
        for aid in panel_image_ids:
            if aid is None:
                continue
            full_ids.append(aid)
            asset = assets_by_id.get(aid, {})
            path = present_image_path(asset, project_dir)
            if path is None:
                errors.append(f"{sid} full storyboard image must be a present image file: {aid}")
            else:
                full_paths.append(path.resolve())
    if images_status == "generated":
        if not panel_ids:
            errors.append("Generated storyboard images require storyboard_panels")
        if len(full_ids) != len(set(full_ids)) or len(full_paths) != len(set(full_paths)):
            errors.append("Each storyboard panel must map to its own full image asset and file")
        if preview_path and preview_path.resolve() in full_paths:
            errors.append("The contact-sheet file cannot also serve as a full storyboard still")
    if held_legacy_ids:
        warnings.append(
            "Full storyboard approval is unrecorded in this older manifest. Images are withheld: "
            + ", ".join(sorted(held_legacy_ids))
        )
    return StoryboardReview(
        preview_id, preview_visible, frozenset(full_ids if not errors else ()), errors, warnings
    )
