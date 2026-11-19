# Downstream agent handoff (optional extension)

Canonical handoff file: `production.json`. The interactive HTML is a human-facing view, not a parsable execution contract. The schema is the interface contract.

## Gates

- Draft/review: downstream agents may read, estimate or preview **without** charging or publishing.
- Approved: creative/shot plan is signed off. Only when the approval prompt explicitly says so, that approval also authorizes one storyboard contact-sheet preview; it does not authorize full-size stills or video.
- Full storyboard stills: require an approved contact-sheet preview and a separate explicit yes naming the exact image count. Do not buy credits; if the chosen tool requires a purchase or cost cannot be disclosed, stop and ask.
- Video/audio production authorized: requires a **separate explicit permission** after stating model/provider, scope and known cost or spend cap. In v1.0, the skill does not initiate downstream video/audio generation; it may prepare a handoff.
- A later automation implementation should evaluate `workflow.approval_status`, storyboard preview/image authorization states, `production_authorized`, `max_auto_spend_credits`, availability/cost and rights before mutating.

## Agent contract

- Storyboard Image Agent reads the approved `storyboard_panels` in order; it may create the contact sheet only when preview authorization is true, and one full still per panel only when full-image authorization is true. It writes actual filenames back to the manifest only after files exist.
- Video Agent reads scenes in numerical order, references verified assets, creates clips, reports per-scene job IDs and status (outside this v1 schema or via a subsequent versioned schema).
- Audio Agent reads dialogue/ambience/SFX/BGM; never reuse copyrighted voices or music without rights.
- Editing Agent reads scene timing and layout, creates composite and QA report; inspect original product label during finishing.

## Compatibility

Stable schema `schema_version: 1.0.0`; preserve IDs between revisions; when adding breaking fields create a new schema version. Avoid machine-local absolute paths in shared projects. Do not put API keys, passwords, or account tokens in production JSON.

If a downstream agent cannot validate the schema, stop and return a structured error; no silent default to a different model/duration. Missing asset, model capability or approval status => stop at draft/handoff state.
