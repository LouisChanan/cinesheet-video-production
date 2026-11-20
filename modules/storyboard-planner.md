# Storyboard Planner — Module 05

- Plan shots that convey information, relation, emotion and product proof, not random variety.
- Select a purposeful shot size (EWS/WS/MS/CU/ECU), perspective/angle (Eye Level/OTS/POV/Dutch/Low/High), and camera movement (Static/Tilt/Pan/Dolly In/Dolly Out/Truck/Follow).
- Describe screen direction, framing, action, reaction and product placement. Do not confuse pan/tilt (rotation) with dolly/truck (camera displacement).
- For UGC, allow handheld imperfection and smartphone framing where fitting; use macro closeups only when viewer benefits.
- Define an ordered panel for each key beat in `scenes[].visual.storyboard_panels`. Use as many panels as the scene needs. Prepare the draft contact sheet and review the visuals according to the [approval gates](../SKILL.md#approval-gates).
- Keep panel descriptions and human-facing notes in the project language; compose model-facing contact-sheet and individual image prompts in English. Preserve any supplied dialogue, exact copy, and product names verbatim in the original language inside those prompts.
- For each panel, store relevant source IDs in optional `reference_asset_ids` and its English generation prompt in `image_prompt`. Include the scene's `kind=location` reference when it guides that panel. In the prompt, state each Ref ID and its role (such as product, character, wardrobe, or location); reference only assets that exist in the manifest. If none is usable, state that no image reference is attached and continue from the written description. Use model-native image-reference syntax only when support for the named model/version is verified; otherwise keep the ID/role mapping model-neutral and note the attachment limitation.
- Prepare the panel prompts and map the full images using the [full storyboard set gate](../SKILL.md#approval-gates). Keep the contact sheet at project level and match each completed still to its panel.
- The HTML/Markdown renderers show the contact sheet at project level and full stills inside their scene. Keep paths relative to the production JSON folder so offline previews load.
- Continuity: location layout, faces, wardrobe, bottle orientation, hand positions, left/right geography, props, light, object permanence, cast count, audio perspective. Scene-specific lighting and camera views can vary while the shared location reference remains stable.

Deliver to `scenes[].visual` and `scenes[].continuity`.
