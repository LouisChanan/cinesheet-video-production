# MiniMax H3 prompt adapter

Write one H3 prompt per planned clip in `scenes[].video.prompt`. Match its timing to the scene duration. Check the selected app, API, or local checkpoint for supported input roles, reference limits, duration, aspect ratio, resolution, and audio controls. Record any unverified requirement in `scenes[].video.unverified_capabilities`. Use the provider's settings for duration, ratio, and resolution. [MiniMax H3 API reference](https://platform.minimax.io/docs/api-reference/video-generation-v2-create)

## Choose the input mode

| Mode | Input and prompt direction |
| --- | --- |
| T2VA | Text only. Establish the opening composition in words and develop the action to the end of the clip. |
| I2VA | First frame. Anchor `<Picture 1>` at `0.00` seconds in `[Shot 1]`. Preserve the visible identity and layout as the scene moves forward. |
| FL2VA | First and last frames. Start from Picture 1 in Shot 1 and reach Picture 2 in the last shot. Describe the physical changes that connect them. Prefer a continuous shot when the brief allows it. |
| L2VA | Last frame. Start from a plausible earlier state and converge on `<Picture 1>` in the final shot. |
| Ref2VA | Reference image, video, or audio. Specify which asset guides each subject, composition, movement, or sound. Use this format when the target supports reference mode and the files are usable. |

For I2VA, FL2VA, and L2VA, use the alignment line from section 2.1 of the Base guide first, then a blank line. For a last frame, use the final shot number and clip duration to two decimal places, such as `8.00` for an eight-second clip. [MiniMax Base prompt guide](https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/docs/VIDEO_PROMPT_WRITING_GUIDE_base_en.md)

Map each prompt label to an existing asset ID and its role. List the usable assets in `scenes[].video.reference_asset_ids` in attachment order and mirror that order when attaching files. An approved character sheet can guide identity and wardrobe in Ref2VA. For the official API, choose either the first/last frame roles or the reference roles for each request. If an intended reference is missing or unsupported, document the gap in the sheet. When no usable reference remains, draft from the written description and label that draft as text only. [MiniMax H3 API reference](https://platform.minimax.io/docs/api-reference/video-generation-v2-create)

## Write the scene

- Open with style, framing, lighting, subject position, and the identity details that must hold. Describe visible action in order and finish on a clear state. Put camera direction and pace into the shot description, such as a slow push toward a product label.
- Mark the opening shot with `[Shot 1]` and leave it untimed. For subsequent cuts, use `[Shot 2] At MM:SS.mmm, ...` and increase the cut times within the clip. Count from the beginning of this clip.
- Write directions in English by default. Preserve dialogue, lyrics, on-screen text, and brand names verbatim. Assign speakers `(S1)`, `(S2)` in order of first speech and reuse their IDs across shots. Use `<d>[Language] ...</d>` for speech and lyrics and double quotes for visible text. Keep speech in the scene's audio plan if the target's spoken-language support is unverified.
- Describe dialogue and sounds tied to actions in the shot where they occur. Use `overall_soundscape` for ambience and physical sounds across the clip. Use `non_diegetic_music` for music heard only by the audience or `N/A` when there is none.

For the four Base modes, use these fields in order after any alignment line: `integrated_multimodal_description`, `overall_soundscape`, `non_diegetic_music`. [MiniMax Base prompt guide](https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/docs/VIDEO_PROMPT_WRITING_GUIDE_base_en.md)

For Ref2VA, use `subject_definitions`, `summary`, `retention_analysis`, `detailed_description`, `overall_soundscape`, and `non_diegetic_music` in that order. Number each label type from 1, define references once, and reuse their labels. Use `<Subject N>` for a person, object, or other reusable visual element and cite its source image or video in the definition. Use standalone `<Picture N>` for a frame or composition anchor, `<Video N>` for an edit source or video structure, and `<Audio N>` for an audio source. Start the summary with a task type such as `[reference generation]`. In the retention section, state what is kept, transferred, copied, or used as guidance. In the detailed description, state the overall style before the first shot, then show where each reference takes effect. [MiniMax full-reference prompt guide](https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/docs/VIDEO_PROMPT_WRITING_GUIDE_ref_en.md)

Keep `scenes[].video.negative_prompt` for review and express essential constraints in the main prompt, such as “the barista keeps the same navy apron throughout.” MiniMax's public H3 creation API lists no separate negative prompt parameter. Pass a separate negative prompt only when the chosen integration documents that input. [MiniMax H3 API reference](https://platform.minimax.io/docs/api-reference/video-generation-v2-create)

## Examples

### T2VA · 6 seconds

Use text only.

```text
integrated_multimodal_description: [Shot 1] Live-action close-up of a cream mug on a light wood café counter. A barista sets a teaspoon to the right of the mug. The camera eases forward and holds on the mug and spoon.

overall_soundscape: A low refrigerator hum and a soft tap as the spoon touches the counter.

non_diegetic_music: N/A
```

### I2VA · 6 seconds

Attach asset `cafe_opening` as the first frame, `<Picture 1>`.

```text
For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced.

integrated_multimodal_description: [Shot 1] Begin with the eye-level framing in <Picture 1> (asset cafe_opening). Keep the barista's navy apron, the mug's starting position, and the counter layout. The barista nudges the cream mug forward, keeping its handle to the right. The camera holds on the mug as it comes to rest.

overall_soundscape: Quiet room tone under the brief scrape of the mug on wood.

non_diegetic_music: N/A
```

### Ref2VA · 8 seconds

Use `cast_barista` and `product_mug` as reference images in that order. Use `score_ref` as an audio reference.

```text
subject_definitions:
<Subject 1> is the barista in <Picture 1> (asset cast_barista), with round glasses and a navy apron.
<Subject 2> is the cream mug with a blue rim in <Picture 2> (asset product_mug).
<Audio 1> is the rhythm reference for the score (asset score_ref).

summary:
[reference generation + audio reference] <Subject 1> sets <Subject 2> on a café counter. <Audio 1> guides the rhythm of the score.

retention_analysis:
<Subject 1> (appears in [Shot 1]): fully_preserved - Keep the round glasses and navy apron.
<Subject 2> (appears in [Shot 1]): fully_preserved - Keep the mug's shape, cream glaze, and blue rim.
<Audio 1>: reference - Follow the spacing of the beats in a new brushed drum score.

detailed_description:
Warm live-action café scene with soft window light.
[Shot 1] In an eye-level medium shot, <Subject 1> lowers <Subject 2> onto the light wood counter. The base taps the wood. The camera slowly moves toward the blue rim and holds once the mug is still.

overall_soundscape: Low café room tone and the soft ceramic tap.

non_diegetic_music: An original brushed drum score follows the slow, evenly spaced beats of <Audio 1> and fades as the camera settles.
```

### Thai dialogue and visible text · T2VA · 8 seconds

Preserve the spoken line `กาแฟมาแล้วค่ะ!` and sign `กาแฟสด`. Use the speech direction when Thai dialogue is supported by the chosen generator.

```text
integrated_multimodal_description: [Shot 1] Live-action medium shot of a barista in a navy apron behind a light wood café counter. A card beside her reads "กาแฟสด". The barista (S1) slides a cream mug forward and says brightly: <d>[Thai] กาแฟมาแล้วค่ะ!</d>
[Shot 2] At 00:04.000, cut to a close-up as the cream mug comes to rest with its handle facing right. Hold on the mug to the end.

overall_soundscape: A low refrigerator hum and the sound of ceramic sliding on wood.

non_diegetic_music: N/A
```

Sources checked on 2026-11-20. [MiniMax H3 prompt-writing skill](https://github.com/MiniMax-AI/MiniMax-H3/blob/main/skills/h3-prompt-writing/SKILL.md)
