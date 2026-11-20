# Quality Controller — Module 08

Run `scripts/validate_production.py` and fix errors before marking 'ready for review'. The validator checks schema, scene count/duration/sequence, refs, asset state, approval state and unverified claims when present.

Human/agent semantic QC checklist:
- Narrative: hook, progression, payoff, CTA and authenticity suit requested format.
- Timing: each spoken line and physical beat can plausibly fit; don't rely on total duration alone.
- Visual: each shot has a reason, identities/wardrobe/staging consistent, product label not hallucinated.
- Audio: dialogue prioritized; ambience and SFX synchronize; music does not overpower.
- Policy/rights: consent/usage rights for likeness, music and imagery; no unsupported commercial, medical, environmental or pet-safety claims.
- Engineering: valid JSON; all referenced IDs exist; all scene starts contiguous; no cost-bearing generation before authorization; preview regenerated after change.
- Storyboard. Check the [approval gates](../SKILL.md#approval-gates) against the current files and the user's decisions. Check panel order, one usable still file per completed panel, and that the sheet shows the relevant draft or approved assets.
- Honesty: file `present` only if path really exists; otherwise explicitly `planned`/`missing`. A `draft` is not `approved`.

Don't claim full quality assurance from schema validation alone. Report warnings with the reviewer decision.
