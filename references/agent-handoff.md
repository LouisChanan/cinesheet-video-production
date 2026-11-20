# Downstream agent handoff (optional extension)

Canonical handoff file: `production.json`. The interactive HTML is a human-facing view, not a parsable execution contract. The schema is the interface contract.

## Gates

Follow the [approval gates](../SKILL.md#approval-gates) for the written plan, draft visuals, full storyboard set, and separate production permission. Before executing an authorized handoff, check the current files, tool availability, recorded permissions, cost or spend cap, and rights. In a legacy manifest with absent storyboard fields, treat the image authorization as unrecorded.

## Agent contract

- Storyboard Image Agent reads `storyboard_panels` in scene and panel order, including linked location references where relevant. For drafts, use the preview authorization, which can be recorded before plan approval. For full stills, check the approved plan, approved contact sheet, and separate set authorization together. Record actual output files when they exist; a location reference does not satisfy a panel still.
- Video Agent reads scenes in numerical order and uses each scene's `video.reference_asset_ids`, including its shared `kind=location` reference, to create clips. It reports per-scene job IDs and status (outside this v1 schema or via a subsequent versioned schema).
- Audio Agent reads dialogue/ambience/SFX/BGM; never reuse copyrighted voices or music without rights.
- Editing Agent reads scene timing and layout, creates composite and QA report; inspect original product label during finishing.

## Compatibility

Stable schema `schema_version: 1.0.0`; preserve IDs between revisions; when adding breaking fields create a new schema version. Avoid machine-local absolute paths in shared projects. Do not put API keys, passwords, or account tokens in production JSON.

If a downstream agent cannot validate the schema, stop and return a structured error; no silent default to a different model/duration. Missing asset, model capability or approval status => stop at draft/handoff state.
