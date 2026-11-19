# Prompt Engineer — Module 06

Use user-selected target model; if unspecified, mark `unspecified` and create model-neutral prompt until user selects one.

Write model-facing image/video instructions and negative prompts in English by default, regardless of the brief language. Keep quoted dialogue, exact on-screen copy, and brand/product names verbatim in their source language; never translate them unless the user asks. Keep the human-facing script and production sheet in the project language. An explicit prompt-language request overrides the English default.

Prompt order (adapt as needed):
1. Format: aspect, intended duration, intended realism/look.
2. References: list each relevant asset ID and its role (for example, product-label lock, character identity, wardrobe, or location); keep the role mapping explicit in the prompt and `reference_asset_ids`.
3. Scene: chronological action with character blocking and who touches what.
4. Shot: camera size/angle/movement and subject focus; don't stack impossible motions.
5. Dialogue: exact speaker-language lines only when model supports audio; otherwise isolate in audio plan.
6. Ambience/SFX/BGM intentions separated, optional where supported.
7. Guardrails/negatives: no duplicate characters, mutated hands, illegible brand, discontinuity, invented written labels.
8. End-state and handoff frame for next shot if required.

For every image/video prompt, use only source references that are registered in `assets` and relevant to that shot. When no usable reference exists, say that no reference image is attached and continue from the written description; never imply a missing or planned file was supplied. Do not present reference media syntax such as `@image1` as supported for every model: use native reference syntax only after confirming that model/version supports it. Otherwise write a clear ID-to-role mapping and treat attachment support as unverified, recording it in `unverified_capabilities` where applicable. Do not use a generated storyboard still as its own source reference.

Deliver to `scenes[].video`, consult `adapters/<model>.md` when model is named.
