---
name: cinesheet-video-production
description: Create or revise an AI Video Production Sheet from a creative brief, product image, script or story idea. Deliver a coherent storyboard, shot/audio plan, model-specific AI video prompts, reviewable sheet and validated production JSON for downstream agents. Use for commercials, UGC, reels, series and films at pre-production stage; not for directly generating or publishing finished video.
---

# CineSheet — AI Video Production Sheet (v1.0)

A **single modular pre-production skill**. Turn a simple Thai or English brief into (1) a reviewable sheet, (2) a canonical `production.json` and (3) an asset manifest. Do not pretend to have rendered storyboards, videos, audio, DOCX or PDF unless those files were actually created.

## Operating boundaries

- This skill plans production. **Never** start paid generation, publish media, purchase credits, or send to external agents without separate express permission. Mark the plan `draft` or `review` unless the user explicitly approves it. For the staged storyboard flow, the sheet-approval prompt must say that approval authorizes one contact-sheet preview only; approving that preview does not authorize the full image set or video production.
- Preserve user-supplied character/product identity and chosen aspect ratio. Don't invent licensing, medical, pet-safety, eco-certification, performance or other brand claims. Keep claims with evidence and approval status.
- Treat attached images as references, not as permission to preserve them for future projects or to publish them. Reuse only in the requested project; seek consent for real-person likeness use as appropriate.
- Distinguish actual image files from **proposed storyboard frames**. If image generation is unavailable, write shot descriptions and mark frames `planned`, not `generated`.
- Never claim that a given video model supports a duration, audio feature, multi-image reference, resolution or camera feature unless confirmed from its live capabilities or user-provided documentation. Use `model_requirements`/`unverified_capabilities` in planning.
- Handle uncertain source evidence explicitly. A product label stating 'plant based' does not by itself prove 'safe for pets'.

## Trigger / invocation

User examples:
- `$cinesheet-video-production สร้าง UGC Naturgenic 30 วินาที แนวโรแมนติกคอมเมดี้ ใช้ Seedance`
- `Use CineSheet to turn this brief into an approved, agent-ready production plan.`
- `Revise Scene 3 only and synchronize the production JSON and preview.`

Don't trigger for requests solely to generate a single picture, produce/render a video file, or transcribe finished footage; those need different workflows.

## Procedure

1. **Read input**: capture user objective, audience, platform, duration, aspect ratio, model, CTA, cast, visual references, product facts, limitations, and authorization. Use known input first; ask only for a truly blocking detail. Default to `9:16`, `30s`, Thai, 3 scenes of 10s, `model: unspecified` only if user provided no stronger preference; label assumptions.
2. **Establish source-of-truth**: inspect the original supplied files where possible. Register every reference in `assets` with stable ID, local path or user-supplied URI, ownership/verification. Separate observations, user claims, and marketing ideas. If user files are missing, mark missing; don't invent paths.
3. **Creative design**: apply [brief analysis](modules/brief-analyzer.md), [concept](modules/creative-director.md) and [script](modules/scriptwriter.md). Choose a hook, situation, payoff, CTA. For short UGC, keep dialogue realistic for its allocated seconds.
4. **Visual continuity**: use [character + asset planning](modules/character-asset-planner.md) and [storyboard](modules/storyboard-planner.md). Decide shot size, angle, movement for a story reason. Read [filmmaking standard](references/filmmaking-standard.md) when designing shots or audio. For scripted videos, avoid contradictory left-right geography, wardrobe, seat positions, identity, props, lighting, and timestamps. Create a storyboard contact-sheet preview only after the user approves the production sheet using wording that clearly authorizes that preview. The sheet must be ordered by scene and key beat; keep panel descriptions in `scenes[].visual.storyboard_panels`. Assign each panel's relevant source references in `reference_asset_ids`; do not include the panel's own generated still as a source reference. If the image tool is unavailable, report the blocker and leave the preview planned.
5. **Model prompt**: use [prompt engineer](modules/prompt-engineer.md). Write all model-facing image and video prompts, including negative prompts, in English by default regardless of brief language. Preserve dialogue, exact on-screen copy, and brand/product names verbatim in their source language; do not translate them unless the user asks. Keep the human-facing script and sheet in the project's language. An explicit user choice of another prompt language overrides the default. Consult exactly the applicable file in `adapters/` to adjust prompt style. Adapters are qualitative **not** capability guarantees. Each scene prompt includes style, assets/identity locks, action timeline, framing, sound/dialogue intent, negatives, and finish condition where meaningful.
6. **Sound and edit plan**: apply [sound/edit](modules/audio-editing-planner.md): Dialogue, Ambience, SFX, BGM; prioritize intelligibility. Optional elements may be omitted intentionally, not automatically injected.
7. **Create one canonical JSON** conforming to `schemas/production.schema.json`. Start from `templates/production.template.json`. Preserve stable scene, panel and asset IDs across revisions. Define one ordered `storyboard_panels` item for each planned keyframe; a scene may have multiple panels. Store the contact-sheet preview as a `storyboard` asset referenced by `workflow.storyboard_preview_asset_id`. After the storyboard preview is approved, compose and store an `image_prompt` and its source `reference_asset_ids` for each panel, then render the sheet so the user can review/copy those prompts before separately authorizing the full image set. After authorization, create exactly one full-size still per panel, register each as a present `storyboard` asset, set that panel's `image_asset_id`, and keep `storyboard_asset_ids` synchronized for scene rendering. Prefer paths relative to the production JSON folder. If a frame is only described or planned, do not mark it present. Track preview authorization/status and full-image authorization/status separately from `workflow.production_authorized`.
8. **Validate**: run `python scripts/validate_production.py <path/to/production.json>`; fix schema, continuity/timing and storyboard authorization errors. Apply [QC](modules/quality-controller.md); if mandatory assets are missing or claims unverified, use truthful flags rather than fabricate completion.
9. **Render**: run `python scripts/render_sheet.py <path/to/production.json> --out <path/to/production-sheet.html>` to create portable clickable HTML with scene video prompts, per-panel image prompts and Ref IDs, the contact-sheet preview and linked full stills inside their scene cards. `--format markdown` creates a shareable review document with the same prompts, references and previews. Missing or planned images remain labeled as such. Offer PDF via browser Print → Save as PDF if requested; offer DOCX only when a real DOCX tool is available. Store all exports beside JSON; never maintain contradictory separate text sources.
   - Use the Editorial Storyboard layout as the standard for every HTML sheet: a scene timeline with first-frame thumbnails or planned placeholders near the top; storyboard panels before each scene's action and production details; image/video/negative prompts inside collapsed disclosures with copy buttons; and a compact Project assets section grouped by asset kind. Show a summary count and friendly display name, source and status badges, and a thumbnail for each existing visual asset. Link assets to the scenes that use them; show open-file and copy-path actions only when the file exists. Keep asset IDs and long paths inside collapsed file details. Planned, missing, or unavailable files must have a clear placeholder and must not produce a broken image or file link. Generate friendly labels from the asset description, falling back to a readable form of the ID; never hardcode project- or character-specific IDs in the renderer. Keep this section self-contained and responsive.
   - Keep the HTML self-contained and usable offline. Preserve visible keyboard focus, accessible copy feedback, and responsive layouts at the renderer's 800px and 560px breakpoints. The default palette is cream/green/orange/blue. When supplied references show clear brand colors, use verified six-digit hex values with `--brand-accent` and optionally `--brand-secondary`; otherwise leave both unset. The HTML renderer rejects colors below 4.5:1 contrast on the text backgrounds. This changes accents only; the renderer layout and Markdown output stay the same.
   - Before delivery, inspect the rendered page at 360, 768, 1280 and 1600 CSS pixels. Check for horizontal overflow, readable timeline and scene hierarchy, working prompt disclosures/copy buttons, collapsed asset paths, and visible keyboard focus. Report any viewport that could not be visually checked; do not claim it was tested.
10. **Approval gates**: present the production sheet with explicit wording that approving it authorizes one storyboard contact-sheet preview only; state the image tool and any known cost, and disclose when cost is unknown. On approval, mark the sheet approved and preview authorized; generate and render the ordered contact sheet, then set `storyboard_preview_status=awaiting_review`. If the user requests changes, revise the preview they asked to change, use a versioned asset, and ask for review again. A change to approved scene or panel content resets the relevant storyboard authorizations and returns the sheet to review. If generation fails or the tool is unavailable, report it and do not automatically retry or switch to a paid route. Once the preview is approved, ask a separate yes/no question stating the tool, exact number of full-size stills and any known cost. Only an explicit yes sets `storyboard_images_authorized=true` and permits one still per panel. A no sets `storyboard_images_status=declined`. Never purchase credits. Keep `workflow.production_authorized=false` unless video production is separately authorized.

## Output contract

- Master: `production.json` (machine-readable and canonical).
- Human review: `production-sheet.html` (works offline in a browser, copy buttons), optionally `.md`.
- Storyboard: the ordered contact sheet appears at project level after its approval gate; full stills appear in their associated scene previews only after the separate image-set authorization.
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

Python 3.10+ and `jsonschema` (see `requirements.txt`) for schema validation; the custom semantic checks also run without `jsonschema`, but the full schema does not.

Read [workflow + handoff](references/agent-handoff.md) only when a downstream agent integration is requested. `examples/naturgenic-ugc.json` is a **fictional instructional sample**, with deliberately unverified pet-safety claim; do not treat it as verified manufacturer evidence.
