# Character & Asset Planner — Module 04

- Assign unique IDs for every person, animal, product, environment and reference file. Never merge identities from distinct references.
- Record `identity_lock`, `wardrobe_lock`, physical relations and persistent props (actor position, dominant hand, bottle location, animal behavior, time of day).
- Make one character sheet per planned character: a close-up portrait, then full-body front and back views in one sheet. Leave the faces blank in the front/back views; keep hairstyle, wardrobe, accessories and silhouette consistent. A supplied layout example does not transfer the pictured person's identity or appearance.
- Record asset `source` as `user`, `generated`, `licensed`, or `unknown`. Set `status` separately to `present`, `planned`, or `missing`. Set `present` after the file exists. Use the [approval gates](../SKILL.md#approval-gates) for linking current character sheets.
- Create one environment reference per distinct location, with a stable versioned `location_<slug>_v1` ID and `kind=location`. Link it from every scene at that location via `video.reference_asset_ids`; reuse the same asset across those scenes. Use a `planned` asset when the location image is pending and do not invent a location when the brief leaves it unresolved.
- Clearly mark any recognizable real person and seek rights/consent if likeness generation/distribution applies. Never imply rights from an image alone.
- Product: preserve actual label, cap, size and color. When model text rendering is uncertain, use the original packshot during compositing instead of fabricated typography.
- Pets: stage the animal safely away from application surfaces, not sniffing or licking chemicals. Don't claim 'pet safe' without substantiation.

Deliver to `characters`, `assets`, `continuity`, and `product_claims`.
