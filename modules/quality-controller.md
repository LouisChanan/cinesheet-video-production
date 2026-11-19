# Quality Controller — Module 08

Run `scripts/validate_production.py` and fix errors before marking 'ready for review'. The validator checks schema, scene count/duration/sequence, refs, asset state, approval state and unverified claims when present.

Human/agent semantic QC checklist:
- Narrative: hook, progression, payoff, CTA and authenticity suit requested format.
- Timing: each spoken line and physical beat can plausibly fit; don't rely on total duration alone.
- Visual: each shot has a reason, identities/wardrobe/staging consistent, product label not hallucinated.
- Audio: dialogue prioritized; ambience and SFX synchronize; music does not overpower.
- Policy/rights: consent/usage rights for likeness, music and imagery; no unsupported commercial, medical, environmental or pet-safety claims.
- Engineering: valid JSON; all referenced IDs exist; all scene starts contiguous; no cost-bearing generation before authorization; preview regenerated after change.
- Storyboard: preview generation is authorized only by sheet approval that explicitly names the contact-sheet preview; full-image generation requires preview approval plus separate explicit authorization. Panel IDs/order and scene mapping are stable; each authorized panel gets exactly one image asset, and render previews resolve to present files.
- Honesty: file `present` only if path really exists; otherwise explicitly `planned`/`missing`. A `draft` is not `approved`.

Don't claim full quality assurance from schema validation alone. Report warnings with the reviewer decision.
