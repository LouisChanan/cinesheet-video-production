---
name: cinesheet-video-production
description: Create or revise an AI Video Production Sheet from a creative brief, product image, script or story idea. Deliver a coherent storyboard, shot/audio plan, model-specific AI video prompts, reviewable sheet and validated production JSON for downstream agents. Use for commercials, UGC, reels, series and films at pre-production stage; not for directly generating or publishing finished video.
---

# CineSheet — AI Video Production Sheet (v1.0)

A **single modular pre-production skill**. Turn a simple Thai or English brief into (1) a reviewable sheet, (2) a canonical `production.json` and (3) an asset manifest. Do not pretend to have rendered storyboards, videos, audio, DOCX or PDF unless those files were actually created.

## Operating boundaries

- This skill plans production. Follow the [approval gates](#approval-gates) for drafting visuals and recording permission. Obtain separate express permission before publishing media or sending it to external agents.
- Preserve user-supplied character/product identity and chosen aspect ratio. Don't invent licensing, medical, pet-safety, eco-certification, performance or other brand claims. Keep claims with evidence and approval status.
- Treat attached images as references, not as permission to preserve them for future projects or to publish them. Reuse only in the requested project; seek consent for real-person likeness use as appropriate.
- Distinguish actual image files from **proposed storyboard frames**. If image generation is unavailable, write shot descriptions and mark frames `planned`, not `generated`.
- Verify duration, audio, reference inputs, resolution and camera features for the selected model and provider. Record unresolved requirements in `scenes[].video.unverified_capabilities`.
- Handle uncertain source evidence explicitly. A product label stating 'plant based' does not by itself prove 'safe for pets'.

## Trigger / invocation

User examples:
- `$cinesheet-video-production สร้าง UGC Naturgenic 30 วินาที แนวโรแมนติกคอมเมดี้ ใช้ Seedance`
- `Use CineSheet to turn this brief into an approved, agent-ready production plan.`
- `Revise Scene 3 only and synchronize the production JSON and preview.`

Don't trigger for requests solely to generate a single picture, produce/render a video file, or transcribe finished footage; those need different workflows.

## Procedure

1. **Read input**: capture user objective, audience, platform, duration, aspect ratio, model, CTA, cast, visual references, product facts, limitations, and authorization. Use known input first; ask only for a truly blocking detail. Default to `9:16`, `30s`, Thai, 3 scenes of 10s, `model: unspecified` only if user provided no stronger preference; label assumptions.
2. **Register sources**. Inspect supplied files where possible. Record every reference in `assets` with a stable ID, `source`, `status`, and a local file path when known. Prefer paths relative to `production.json`. Put source URLs and ownership notes in `description` or `workflow.qc_notes`. Separate observations, user claims, and marketing ideas. Mark absent files `missing`.
3. **Creative design**: apply [brief analysis](modules/brief-analyzer.md), [concept](modules/creative-director.md) and [script](modules/scriptwriter.md). Choose a hook, situation, payoff, CTA. For short UGC, keep dialogue realistic for its allocated seconds.
4. **Visual continuity and draft boards**. Use [character and asset planning](modules/character-asset-planner.md), [storyboard planning](modules/storyboard-planner.md), and the [filmmaking reference](references/filmmaking-standard.md). Choose shots for a story reason and keep geography, cast, wardrobe, props, lighting, and timing consistent. Describe the key frames in the ordered `scenes[].visual.storyboard_panels`. Prepare draft visuals according to the [approval gates](#approval-gates).
5. **Model prompt**: use [prompt engineer](modules/prompt-engineer.md). Write all model-facing image and video prompts, including negative prompts, in English by default regardless of brief language. Preserve dialogue, exact on-screen copy, and brand/product names verbatim in their source language; do not translate them unless the user asks. Keep the human-facing script and sheet in the project's language. An explicit user choice of another prompt language overrides the default. Consult exactly the applicable file in `adapters/` to adjust prompt style. Adapters are qualitative **not** capability guarantees. Each scene prompt includes style, assets/identity locks, action timeline, framing, sound/dialogue intent, negatives, and finish condition where meaningful.
6. **Sound and edit plan**: apply [sound/edit](modules/audio-editing-planner.md): Dialogue, Ambience, SFX, BGM; prioritize intelligibility. Optional elements may be omitted intentionally, not automatically injected.
7. **Create one canonical JSON** conforming to `schemas/production.schema.json`. Start from `templates/production.template.json`. Preserve stable scene and panel IDs across revisions and give each replacement image asset its own versioned ID. Use `present` only for real files. Use the [approval gates](#approval-gates) to record current visual links and approval status.
8. **Validate**: run `python scripts/validate_production.py <path/to/production.json>`; fix schema, continuity/timing and storyboard authorization errors. Apply [QC](modules/quality-controller.md); if mandatory assets are missing or claims unverified, use truthful flags rather than fabricate completion.
9. **Render**: run `python scripts/render_sheet.py <path/to/production.json> --out <path/to/production-sheet.html>` to create portable clickable HTML with scene video prompts, per-panel image prompts and Ref IDs, the draft contact sheet, linked character sheets, and any separately authorized full stills inside their scene cards. `--format markdown` creates a shareable review document with the same prompts, references and previews. Before approval, label generated contact and character sheets as drafts pending approval. Missing or planned images remain labeled as such. Offer PDF via browser Print → Save as PDF if requested; offer DOCX only when a real DOCX tool is available. Store all exports beside JSON; never maintain contradictory separate text sources.
   - Use the Editorial Storyboard layout as the standard for every HTML sheet: a scene timeline with first-frame thumbnails or planned placeholders near the top; storyboard panels before each scene's action and production details; image/video/negative prompts inside collapsed disclosures with copy buttons; and a compact Project assets section grouped by asset kind. Show a summary count and friendly display name, source and status badges, and a thumbnail for each existing visual asset. Link assets to the scenes that use them; show open-file and copy-path actions only when the file exists. Keep asset IDs and long paths inside collapsed file details. Planned, missing, or unavailable files must have a clear placeholder and must not produce a broken image or file link. Generate friendly labels from the asset description, falling back to a readable form of the ID; never hardcode project- or character-specific IDs in the renderer. Keep this section self-contained and responsive.
   - Keep the HTML self-contained and usable offline. Preserve visible keyboard focus, accessible copy feedback, and responsive layouts at the renderer's 800px and 560px breakpoints. The default palette is cream/green/orange/blue. When supplied references show clear brand colors, use verified six-digit hex values with `--brand-accent` and optionally `--brand-secondary`; otherwise leave both unset. The HTML renderer rejects colors below 4.5:1 contrast on the text backgrounds. This changes accents only; the renderer layout and Markdown output stay the same.
   - Before delivery, inspect the rendered page at 360, 768, 1280 and 1600 CSS pixels. Check for horizontal overflow, readable timeline and scene hierarchy, working prompt disclosures/copy buttons, collapsed asset paths, and visible keyboard focus. Report any viewport that could not be visually checked; do not claim it was tested.
10. **Review and revise**. Present the exported sheet and explain the current state using the [approval gates](#approval-gates).

## Approval gates

1. **Prepare draft visuals.** Before plan approval, make one contact sheet ordered by scene and key beat and one character sheet per planned character. Create drafts automatically when the tool has verified zero cost. For paid or unknown cost, state the tool, number of images, and known or unknown cost, and obtain explicit permission before calling it. Set `storyboard_preview_authorized=true` when the draft preview can be created. If the tool is unavailable or permission is pending, leave the preview `not_started` and show planned assets. On a failed attempt use `failed` and record the reason in `workflow.qc_notes`. A failed attempt does not authorize a retry or a different tool.
2. **Link the current drafts.** Link the present `storyboard` contact sheet via `workflow.storyboard_preview_asset_id` and set its status to `awaiting_review`. Each character sheet shows the locked face, wardrobe, and views needed for continuity. Give it a `character_sheet_<character_id>_v1` asset ID with `kind=character` and link it under that character's `reference_asset_ids`. Reserve the same versioned ID with status `planned` and a null path while its file is pending. Keep one current sheet link per character. A preview or character sheet can guide review without being a full panel still.
3. **Review the written plan and available drafts.** State which files the user is reviewing. Explicit signoff on the displayed pack sets `approval_status=approved` and marks an included, present contact sheet `approved`. If the user approves text only, set just the plan to `approved`. A contact sheet added to the same plan can be reviewed later as `awaiting_review`, then marked `approved` when the user sees and approves it. Reopen plan review when adding or replacing a character sheet after signoff so that the user can review the current character imagery. Reuse an accepted preview.
4. **Authorize the full storyboard set.** After plan and contact approval, write the panel `image_prompt` and `reference_asset_ids` in the JSON and export them for review. Ask separately for an explicit yes with the tool, exact panel count, and known or unknown cost. A yes sets `storyboard_images_authorized=true`. A no sets `storyboard_images_authorized=false` and `storyboard_images_status=declined`. Use one distinct present image file per panel. When the entire set is ready, set each panel's `image_asset_id`, match each scene's `storyboard_asset_ids` to those IDs in panel order, and set `storyboard_images_status=generated`. Keep partial or failed output files in `assets` with their true file status, leave the set unlinked from panels and scene still lists, and use `failed` if the attempt failed.
5. **Handle revisions.** When a change affects the approved creative plan, panel content, character imagery, or active references, set `approval_status=review`, `storyboard_images_authorized=false`, `storyboard_images_status=not_started`, and `production_authorized=false`. Detach the previously linked set from `image_asset_id` and `storyboard_asset_ids` and set the affected scene `storyboard_status` to `planned`. Remove obsolete input references from panel and video prompts. Keep existing files in the manifest and reuse unaffected files if appropriate once the revised set is approved. If the contact sheet still represents the new plan, keep its file and return it to `awaiting_review`. If affected, unlink it, clear preview authorization, and set its status to `not_started`. Give replacement assets a new version ID and show them again for approval.
6. **Record video or audio production permission separately.** Keep `workflow.production_authorized=false` until the plan is approved and the user explicitly authorizes the scope and provider after seeing the known cost or spend cap. The skill prepares the handoff. It never purchases credits or starts video or audio production.

## Output contract

- Master: `production.json` (machine-readable and canonical).
- Human review: `production-sheet.html` (works offline in a browser, copy buttons), optionally `.md`.
- Draft visuals: the ordered contact sheet and one character sheet per planned character appear in the review sheet before production approval when generation is authorized and available; full-size storyboard stills appear in scene previews only after separate image-set authorization.
- Assets: `asset-manifest` within JSON (actual files vs missing/planned are explicitly marked); in HTML, show a grouped, responsive Project assets section with friendly labels, source/status, available visual previews, scene-use links, and collapsed file details. Do not render broken previews or file links for planned, missing, or unavailable files.
- State: clear `draft` / `review` / `approved`; storyboard image generation follows its separate approval states; video/audio production generation remains out of scope here.

## Tool commands

```bash
# Start a blank project template (creates folder only; doesn't write creative prose)
python scripts/new_project.py --id my-ad-001 --title "My video" --out output/my-ad-001
# After filling out production.json using this skill:
python scripts/validate_production.py output/my-ad-001/production.json
python scripts/render_sheet.py output/my-ad-001/production.json --out output/my-ad-001/production-sheet.html
python scripts/render_sheet.py output/my-ad-001/production.json --out output/my-ad-001/production-sheet.md --format markdown
```

Python 3.10+ and `jsonschema` are required for validation and export. Install with `python -m pip install -r requirements.txt` from the Skill folder.

Read [workflow + handoff](references/agent-handoff.md) only when a downstream agent integration is requested. `examples/naturgenic-ugc.json` is a **fictional instructional sample**, with deliberately unverified pet-safety claim; do not treat it as verified manufacturer evidence.
