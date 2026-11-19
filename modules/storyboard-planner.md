# Storyboard Planner — Module 05

- Plan shots that convey information, relation, emotion and product proof, not random variety.
- Select a purposeful shot size (EWS/WS/MS/CU/ECU), perspective/angle (Eye Level/OTS/POV/Dutch/Low/High), and camera movement (Static/Tilt/Pan/Dolly In/Dolly Out/Truck/Follow).
- Describe screen direction, framing, action, reaction and product placement. Do not confuse pan/tilt (rotation) with dolly/truck (camera displacement).
- For UGC, allow handheld imperfection and smartphone framing where fitting; use macro closeups only when viewer benefits.
- A storyboard **description** is not a rendered frame. Define an ordered panel for each key beat in `visual.storyboard_panels`; a scene may have multiple panels. Generate one contact-sheet preview only after the user approves the sheet with explicit preview authorization.
- Keep panel descriptions and human-facing notes in the project language; compose model-facing contact-sheet and individual image prompts in English. Preserve any supplied dialogue, exact copy, and product names verbatim in the original language inside those prompts.
- For each panel, store relevant source IDs in optional `reference_asset_ids` and its English generation prompt in `image_prompt`. In the prompt, state each Ref ID and its role (such as product, character, wardrobe, or location); reference only assets that exist in the manifest. If none is usable, state that no image reference is attached and continue from the written description. Use model-native image-reference syntax only when support for the named model/version is verified; otherwise keep the ID/role mapping model-neutral and note the attachment limitation.
- After the contact-sheet preview is approved, prepare and store all panel image prompts, render them in the HTML/Markdown sheet for review and copying, then wait for separate authorization before generating full-size stills.
- After presenting the contact sheet, wait for its approval. If approved, ask separately before generating the full image set; the approved panel list is the exact image count and mapping, one full still per panel. Register the contact sheet and each real still as `storyboard` assets; map full stills with each panel's `image_asset_id` and the scene's `storyboard_asset_ids`.
- The HTML/Markdown renderers show the contact sheet at project level and full stills inside their scene. Keep paths relative to the production JSON folder so offline previews load.
- Continuity: faces, wardrobe, bottle orientation, hand positions, left/right geography, props, light, object permanence, cast count, audio perspective.

Deliver to `scenes[].visual` and `scenes[].continuity`.
