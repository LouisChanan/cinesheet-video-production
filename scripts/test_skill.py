#!/usr/bin/env python3
"""Offline regression checks for CineSheet validation and export."""

import copy
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from urllib.parse import unquote

from production_state import STORYBOARD_KEYS
from render_sheet import asset_display_name, contrast_ratio, render_html, render_markdown
from validate_production import check_file


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples/naturgenic-ugc.json"
H3_PROMPT = (
    "integrated_multimodal_description: [Shot 1] A barista (S1) says: <d>[Thai] กาแฟมาแล้วค่ะ!</d>\n\n"
    "overall_soundscape: A cup taps the counter.\n\nnon_diegetic_music: N/A"
)


def read_example():
    return json.loads(EXAMPLE.read_text(encoding="utf-8"))


def write_manifest(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return path


def add_image(data, folder, aid, path, kind, *, width=480, height=270, source="generated"):
    target = folder / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 120 60">'
        '<rect width="120" height="60" fill="#eee9dc"/>'
        '<rect x="6" y="6" width="32" height="48" fill="#a84c08"/>'
        '<rect x="44" y="6" width="32" height="48" fill="#1f5847"/>'
        '<rect x="82" y="6" width="32" height="48" fill="#26549c"/></svg>',
        encoding="utf-8",
    )
    data["assets"].append({
        "id": aid, "kind": kind, "path": path, "source": source,
        "status": "present", "description": aid.replace("_", " "),
    })
    return target


def draft_with_images(folder):
    data = read_example()
    data["workflow"].update(
        approval_status="review",
        storyboard_preview_authorized=True,
        storyboard_preview_status="awaiting_review",
        storyboard_preview_asset_id="contact_v1",
        storyboard_images_authorized=False,
        storyboard_images_status="not_started",
    )
    add_image(data, folder, "contact_v1", "assets/ภาพรวม storyboard.svg", "storyboard")
    for character in data["characters"]:
        cid = character["id"]
        aid = f"character_sheet_{cid}_v1"
        add_image(data, folder, aid, f"assets/แผ่นตัวละคร {cid} #1.svg", "character")
        character["reference_asset_ids"] = [aid]
    add_image(data, folder, "wardrobe_ref", "assets/wardrobe.svg", "character", source="user")
    data["characters"][0]["reference_asset_ids"].append("wardrobe_ref")
    for scene, descriptions in zip(data["scenes"], (("Kitchen setup",), ("Wipe",), ("Cat enters", "End frame"))):
        scene["visual"]["storyboard_panels"] = [
            {"id": f"{scene['id']}_panel_{index}", "description": description, "image_asset_id": None}
            for index, description in enumerate(descriptions, start=1)
        ]
    first = data["scenes"][0]
    first["visual"]["storyboard_panels"][0].update(
        image_prompt="Medium shot from the written brief. No product photo is attached.",
        reference_asset_ids=["bottle"],
    )
    first["video"].update(model="MiniMax-H3", prompt=H3_PROMPT, reference_asset_ids=["wardrobe_ref"])
    return data


def add_full_set(data, folder):
    data["workflow"].update(
        approval_status="approved",
        storyboard_preview_status="approved",
        storyboard_images_authorized=True,
        storyboard_images_status="generated",
    )
    for scene in data["scenes"]:
        image_ids = []
        for panel in scene["visual"]["storyboard_panels"]:
            aid = panel["id"] + "_still"
            add_image(data, folder, aid, f"assets/{aid}.svg", "storyboard", width=270, height=480)
            panel["image_asset_id"] = aid
            image_ids.append(aid)
        scene["visual"]["storyboard_asset_ids"] = image_ids


def run_cli(script, *args, without_dependencies=False):
    options = ["-B", "-E", "-S"] if without_dependencies else ["-B"]
    return subprocess.run(
        [sys.executable, *options, str(ROOT / "scripts" / script), *(str(arg) for arg in args)],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
    )


class ExampleTests(unittest.TestCase):
    def test_example_and_editorial_layout(self):
        data = read_example()
        errors, warnings = check_file(EXAMPLE)
        self.assertFalse(errors, errors)
        self.assertTrue(any("bottle" in warning for warning in warnings))
        self.assertTrue(any("claim_pet" in warning for warning in warnings))
        self.assertTrue(all(not claim["permitted_copy"] for claim in data["product_claims"]))
        self.assertTrue(all("bottle" not in scene["video"]["reference_asset_ids"] for scene in data["scenes"]))
        self.assertNotIn("เช็ดคราบมันง่าย", EXAMPLE.read_text(encoding="utf-8"))

        markup = render_html(data, EXAMPLE.parent)
        self.assertIn('<meta name="viewport" content="width=device-width,initial-scale=1">', markup)
        self.assertLess(markup.index('class="timeline-section"'), markup.index('class="brief-section"'))
        self.assertEqual(markup.count('class="timeline-item"'), len(data["scenes"]))
        for scene in data["scenes"]:
            sid = scene["id"]
            self.assertIn(f'href="#{sid}"', markup)
            section = markup.split(f'<section class="scene" id="{sid}"', 1)[1].split("</section>", 1)[0]
            self.assertLess(section.index('class="scene-media"'), section.index('class="scene-action"'))
        for token in (
            "summary:focus-visible,button:focus-visible,a:focus-visible", "@media(max-width:800px)",
            "@media(max-width:560px)", 'class="asset-id-details"', "Project assets · ไฟล์และภาพอ้างอิง",
            "สินค้าและแบรนด์", 'id="copy-live" aria-live="polite"', "navigator.clipboard.writeText",
            'document.execCommand("copy")', 'class="timeline-thumb-empty"', "Pet-safe", "unverified",
        ):
            self.assertIn(token, markup)
        self.assertEqual(markup.count('data-copy-label="Copy Video Prompt"'), len(data["scenes"]))
        self.assertNotIn("<link rel=", markup.partition("</head>")[0].lower())
        self.assertNotIn("<script src=", markup.lower())

    def test_asset_names_and_brand_contrast(self):
        self.assertEqual(
            asset_display_name({"id": "look_refs", "description": "Character look references; wardrobe and face"}),
            "Character look references",
        )
        self.assertEqual(asset_display_name({"id": "arbitrary_asset_17", "description": ""}), "Arbitrary Asset 17")
        for background in ("#fffdf8", "#f5f1e8"):
            self.assertGreaterEqual(contrast_ratio("#a84c08", background), 4.5)
        data = read_example()
        self.assertIn("--orange:#a84c08", render_html(data))
        self.assertIn(":root{--orange:#a84c08;--blue:#34578a}", render_html(data, brand_accent="#a84c08", brand_secondary="#34578a"))
        for value in ("orange", "#e87924"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                render_html(data, brand_accent=value)

    def test_schema_errors_and_missing_dependency_at_both_entry_points(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            data = read_example()
            data["scenes"][0] = None
            manifest = write_manifest(folder / "invalid.json", data)
            out = folder / "existing.html"
            out.write_text("Existing export", encoding="utf-8")
            for script, options in (
                ("validate_production.py", ()), ("render_sheet.py", ("--out", out)),
            ):
                with self.subTest(script=script):
                    result = run_cli(script, manifest, *options)
                    message = result.stdout + result.stderr
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn("Schema /scenes/0", message)
                    self.assertNotIn("Traceback", message)
                    result = run_cli(script, EXAMPLE, *options, without_dependencies=True)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn("python -m pip install -r requirements.txt", result.stdout + result.stderr)
            self.assertEqual(out.read_text(encoding="utf-8"), "Existing export")


class StoryboardTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.folder = Path(temp.name)
        self.path = self.folder / "production.json"
        self.draft = draft_with_images(self.folder)

    def check(self, data):
        return check_file(write_manifest(self.path, data))

    def assert_valid(self, data):
        errors, warnings = self.check(data)
        self.assertFalse(errors, errors)
        return warnings

    def assert_invalid(self, data, expected):
        errors, _ = self.check(data)
        self.assertTrue(any(expected in error for error in errors), errors)

    def outputs(self, data):
        return render_html(data, self.folder), render_markdown(data, self.folder)

    def test_draft_pack_and_parity(self):
        self.assert_valid(self.draft)
        markup, markdown = self.outputs(self.draft)
        self.assertIn('<details class="contact-details" open>', markup)
        self.assertIn('<details class="cast-details" open>', markup)
        self.assertEqual(markup.count('class="cast-reference character-sheet"'), 3)
        self.assertIn('class="cast-reference"', markup)
        self.assertIn('class="asset-status planned"', markup)
        self.assertIn('class="asset-thumb asset-thumb-wide"', markup)
        self.assertIn('class="asset-scene-link" href="#scene_01"', markup)
        self.assertIn('data-copy-label="Copy Image Prompt"', markup)
        self.assertIn("คัดลอก path", markup)
        for output in (markup, markdown):
            for text in (
                "Production sheet", "Draft · Awaiting review", "Character sheet · Draft",
                "Full storyboard stills", "Video production", "Not authorized", "Negative Prompt",
                "On-screen text", "แต่งงานได้ 7 วัน!", "Video reference assets", "wardrobe",
                "Unverified model capabilities", "Acceptance criteria", "No product photo is attached.",
            ):
                self.assertIn(text, output)
            self.assertNotIn("bottle.png", output)
        self.assertIn("&lt;d&gt;[Thai] กาแฟมาแล้วค่ะ!&lt;/d&gt;", markup)
        self.assertIn(H3_PROMPT, markdown)

    def test_text_only_approval_and_later_contact(self):
        data = read_example()
        data["workflow"].update(
            storyboard_preview_authorized=False, storyboard_preview_status="not_started",
            storyboard_preview_asset_id=None, storyboard_images_authorized=False,
            storyboard_images_status="not_started",
        )
        data["assets"].append({
            "id": "character_sheet_wife_v1", "kind": "character", "source": "generated",
            "path": "pending-character.svg", "status": "planned", "description": "Planned wife sheet",
        })
        data["characters"][0]["reference_asset_ids"] = ["character_sheet_wife_v1"]
        for status in ("review", "approved"):
            data["workflow"]["approval_status"] = status
            self.assert_valid(data)
            for output in self.outputs(data):
                self.assertIn("Character sheet · Planned", output)
                self.assertIn("No contact-sheet image available.", output)
                self.assertIn("Not authorized", output)
                self.assertNotIn("pending-character.svg", output)
        add_image(data, self.folder, "later_contact", "assets/later.svg", "storyboard")
        data["workflow"].update(
            storyboard_preview_authorized=True, storyboard_preview_status="awaiting_review",
            storyboard_preview_asset_id="later_contact",
        )
        self.assert_valid(data)
        for output in self.outputs(data):
            self.assertIn("assets/later.svg", output)
            self.assertIn("Draft · Awaiting review", output)
        data["workflow"]["storyboard_preview_status"] = "approved"
        self.assert_valid(data)

    def test_authorized_set_and_incomplete_set(self):
        data = self.draft
        data["workflow"].update(
            approval_status="approved", storyboard_preview_status="approved",
            storyboard_images_authorized=True,
        )
        self.assert_valid(data)
        self.assertIn("Authorized · Awaiting images", self.outputs(data)[0])

        add_full_set(data, self.folder)
        self.assert_valid(data)
        for output in self.outputs(data):
            self.assertIn("scene_03_panel_2_still.svg", output)
            self.assertIn("Complete", output)
            self.assertIn("Not authorized", output)
        data["scenes"][2]["visual"]["storyboard_panels"][1]["image_asset_id"] = None
        self.assert_invalid(data, "missing a full image")
        for output in self.outputs(data):
            self.assertNotIn("scene_01_panel_1_still.svg", output)
            self.assertIn("Set unavailable", output)

    def test_staged_links_require_authorization_and_never_self_reference(self):
        data = self.draft
        aid = "early_still"
        add_image(data, self.folder, aid, "assets/early.svg", "storyboard")
        visual = data["scenes"][0]["visual"]
        panel = visual["storyboard_panels"][0]
        panel["image_asset_id"] = aid
        visual["storyboard_asset_ids"] = [aid]
        for status in ("not_started", "declined", "failed"):
            data["workflow"]["storyboard_images_status"] = status
            self.assert_invalid(data, "before an authorized set is complete")
            for output in self.outputs(data):
                self.assertNotIn("early.svg", output)
        panel["reference_asset_ids"] = [aid]
        self.assert_invalid(data, "cannot use its own image")
        panel["image_asset_id"] = None
        panel["reference_asset_ids"] = []
        visual["storyboard_asset_ids"] = []
        data["workflow"].update(
            approval_status="approved", storyboard_preview_status="approved",
            storyboard_images_authorized=True, storyboard_images_status="failed",
        )
        self.assert_valid(data)
        for output in self.outputs(data):
            self.assertIn("Generation failed", output)
            self.assertNotIn("early.svg", output)

    def test_preview_and_full_set_invariants(self):
        complete = copy.deepcopy(self.draft)
        add_full_set(complete, self.folder)
        data = copy.deepcopy(complete)
        data["workflow"]["storyboard_images_authorized"] = False
        self.assert_invalid(data, "require explicit storyboard_images_authorized=true")
        data = copy.deepcopy(complete)
        data["workflow"]["storyboard_preview_status"] = "awaiting_review"
        self.assert_invalid(data, "approved storyboard preview")
        data = copy.deepcopy(complete)
        data["scenes"][2]["visual"]["storyboard_asset_ids"].reverse()
        self.assert_invalid(data, "match panel image assets in order")
        data = copy.deepcopy(complete)
        visual = data["scenes"][2]["visual"]
        visual["storyboard_panels"][0]["image_asset_id"] = "scene_01_panel_1_still"
        visual["storyboard_asset_ids"][0] = "scene_01_panel_1_still"
        self.assert_invalid(data, "own full image asset and file")
        data = copy.deepcopy(complete)
        visual = data["scenes"][0]["visual"]
        visual["storyboard_panels"][0]["image_asset_id"] = "contact_v1"
        visual["storyboard_asset_ids"] = ["contact_v1"]
        self.assert_invalid(data, "cannot use the contact sheet")
        data = copy.deepcopy(self.draft)
        data["workflow"]["storyboard_preview_authorized"] = False
        self.assert_invalid(data, "requires preview authorization")
        for output in self.outputs(data):
            self.assertNotIn("storyboard.svg", output)

    def test_revised_content_returns_to_review(self):
        data = self.draft
        add_full_set(data, self.folder)
        data["workflow"]["production_authorized"] = True
        self.assert_valid(data)
        data["scenes"][0]["story_action"] = "Updated first scene action."
        data["workflow"].update(
            approval_status="review", storyboard_images_authorized=False, storyboard_images_status="not_started",
            storyboard_preview_authorized=False, storyboard_preview_asset_id=None, storyboard_preview_status="not_started",
        )
        self.assert_invalid(data, "Production authorization requires")
        for scene in data["scenes"]:
            for panel in scene["visual"]["storyboard_panels"]:
                panel["image_asset_id"] = None
            scene["visual"]["storyboard_asset_ids"] = []
        data["workflow"]["production_authorized"] = False
        self.assert_valid(data)
        self.assertTrue((self.folder / "assets/scene_01_panel_1_still.svg").is_file())
        for output in self.outputs(data):
            self.assertIn("Updated first scene action.", output)
            self.assertNotIn("scene_01_panel_1_still.svg", output)
            self.assertNotIn("storyboard.svg", output)

    def test_legacy_generated_frames_are_withheld_but_source_refs_are_readable(self):
        data = read_example()
        self.assertTrue(STORYBOARD_KEYS.isdisjoint(data["workflow"]))
        add_image(data, self.folder, "old_still", "assets/old-still.svg", "storyboard")
        add_image(data, self.folder, "user_frame", "assets/user-frame.svg", "storyboard", source="user")
        data["scenes"][0]["visual"]["storyboard_asset_ids"] = ["old_still", "user_frame"]
        warnings = self.assert_valid(data)
        self.assertTrue(any("approval is unrecorded" in warning for warning in warnings))
        for output in self.outputs(data):
            self.assertIn("approval is unrecorded", output)
            self.assertNotIn("old-still.svg", output)
            self.assertIn("user-frame.svg", output)
            self.assertIn("Reference frame", output)

    def test_missing_character_image_has_no_broken_link(self):
        data = self.draft
        aid = "character_sheet_wife_v1"
        asset = next(asset for asset in data["assets"] if asset["id"] == aid)
        path = self.folder / asset["path"]
        path.unlink()
        self.assert_invalid(data, "marked present but file does not exist")
        asset["status"] = "missing"
        self.assert_valid(data)
        for output in self.outputs(data):
            self.assertIn("Character sheet · File missing", output)
            self.assertNotIn("wife%20%231.svg", output)

    def test_timing_claims_and_reference_validation(self):
        cases = [
            ("wrong start", lambda data: data["scenes"][1].update(start_seconds=12), "starts at 12"),
            ("wrong total", lambda data: data["scenes"][2].update(duration_seconds=9), "total 29s"),
            ("unknown speaker", lambda data: data["scenes"][0]["audio"]["dialogue"][0].update(speaker_id="x"), "speaker ID unknown"),
            ("unverified claim", lambda data: data["product_claims"][-1].update(permitted_copy=True), "Unverified claim"),
            ("unknown panel ref", lambda data: data["scenes"][0]["visual"]["storyboard_panels"][0].update(
                reference_asset_ids=["x"]), "unknown source asset"),
            ("wrong character ref", lambda data: data["characters"][0].update(reference_asset_ids=["contact_v1"]), "kind=character"),
        ]
        for label, edit, expected in cases:
            with self.subTest(case=label):
                data = copy.deepcopy(self.draft)
                edit(data)
                self.assert_invalid(data, expected)

    def test_export_links_resolve_from_output_and_preserve_input(self):
        write_manifest(self.path, self.draft)
        before = self.path.read_bytes()
        for directory in (self.folder, self.folder / "export" / "review"):
            for format_name, extension in (("html", "html"), ("markdown", "md")):
                with self.subTest(directory=directory, format=format_name):
                    output = directory / f"sheet.{extension}"
                    result = run_cli("render_sheet.py", self.path, "--out", output, "--format", format_name)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    text = output.read_text(encoding="utf-8")
                    pattern = r'<img[^>]* src="([^"]+)"' if format_name == "html" else r'!\[[^\]]+\]\(([^)]+)\)'
                    links = re.findall(pattern, text)
                    self.assertGreaterEqual(len(links), 4)
                    self.assertTrue(any("%E0" in link and "%20" in link and "%23" in link for link in links), links)
                    for link in links:
                        self.assertTrue((output.parent / unquote(link)).is_file(), link)
        self.assertEqual(self.path.read_bytes(), before)

    def test_export_rejects_existing_inputs_and_aliases(self):
        write_manifest(self.path, self.draft)
        contact = self.folder / "assets/ภาพรวม storyboard.svg"
        for target in (self.path, contact):
            with self.subTest(target=target):
                before = target.read_bytes()
                result = run_cli("render_sheet.py", self.path, "--out", target)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("Output would overwrite", result.stderr)
                self.assertEqual(target.read_bytes(), before)
        alias = self.folder / "alias.html"
        try:
            os.link(self.path, alias)
        except OSError:
            return
        result = run_cli("render_sheet.py", self.path, "--out", alias)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Output would overwrite", result.stderr)
        self.assertTrue(self.path.samefile(alias))


if __name__ == "__main__":
    unittest.main(verbosity=2)
