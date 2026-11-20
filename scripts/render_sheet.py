#!/usr/bin/env python3
"""Render machine-canonical production JSON as offline HTML or Markdown."""
import argparse
import html
import os
import re
import sys
import tempfile
from pathlib import Path
from urllib.parse import quote

from production_state import (
    IMAGE_SUFFIXES,
    assess_storyboard,
    asset_path,
    asset_status,
    is_character_sheet,
    scene_panel_records,
)
from validate_production import load_and_check_file

STYLE="""
:root{color-scheme:light;--ink:#193b32;--muted:#62736a;--green:#1f5847;--orange:#a84c08;--blue:#26549c;--line:#d9d5c9;--paper:#fffdf8;--ground:#f5f1e8;--soft:#eee9dc;--focus:#135fc2}
*{box-sizing:border-box}
html{scroll-behavior:smooth;scroll-padding-top:18px}
body{margin:0;background:var(--ground);color:var(--ink);font:16px/1.65 system-ui,-apple-system,'Segoe UI',sans-serif;overflow-wrap:anywhere}
main{max-width:1240px;margin:0 auto;padding:clamp(22px,4vw,56px) clamp(18px,4vw,48px) 84px}
h1,h2,h3,p,figure{margin-top:0}
h1{font-size:clamp(2rem,4.5vw,3.7rem);line-height:1.08;letter-spacing:-.035em;margin:10px 0 18px;max-width:18ch}
h2{font-size:clamp(1.35rem,2.2vw,1.8rem);line-height:1.2;letter-spacing:-.02em;margin:0}
h3{font-size:1rem;margin:0 0 7px}
p{margin-bottom:12px}
a{color:inherit}
.eyebrow,.section-kicker{font-size:.72rem;font-weight:800;letter-spacing:.14em;text-transform:uppercase;color:var(--green)}
.page-header{position:relative;padding:4px 0 26px;border-bottom:1px solid var(--line)}
.page-header:before{content:"";display:block;width:76px;height:5px;background:linear-gradient(90deg,var(--orange) 0 68%,var(--blue) 68%);margin-bottom:18px}
.hero-row{display:flex;justify-content:space-between;align-items:end;gap:28px}
.hero-copy{min-width:0}
.hero-summary{max-width:68ch;color:#42574e;font-size:1.05rem;margin:0}
.meta-row{display:flex;flex-wrap:wrap;gap:8px 18px;margin-top:18px;color:var(--muted);font-size:.86rem}
.meta-item{display:inline-flex;align-items:center;gap:7px}
.meta-item:before{content:"";width:6px;height:6px;border-radius:50%;background:var(--orange)}
.review-notice{margin:18px 0;padding:12px 16px;border-left:4px solid var(--orange);background:#fff5e6;color:#68461f}
.approval-summary{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,170px),1fr));gap:12px 20px;margin:20px 0 0}
.approval-summary dt{color:var(--muted);font-size:.77rem}
.approval-summary dd{margin:1px 0 0;color:var(--green);font-size:.91rem;font-weight:750}
.approval-warning{margin:10px 0 0;color:#68461f;font-size:.86rem}
.section-heading{display:flex;align-items:baseline;justify-content:space-between;gap:16px;margin-bottom:14px}
.section-heading p{color:var(--muted);font-size:.88rem;margin:0}
.timeline-section{padding:26px 0 30px;border-bottom:1px solid var(--line)}
.timeline{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));border-top:1px solid var(--line);border-bottom:1px solid var(--line)}
.timeline-item{display:grid;grid-template-columns:minmax(76px,104px) minmax(0,1fr);gap:14px;align-items:center;padding:14px 16px 14px 0;text-decoration:none;min-width:0}
.timeline-item+.timeline-item{border-left:1px solid var(--line);padding-left:16px}
.timeline-item:hover .timeline-title{text-decoration:underline;text-decoration-color:var(--orange);text-underline-offset:4px}
.timeline-thumb{display:block;width:100%;aspect-ratio:3/4;object-fit:cover;background:var(--soft)}
.timeline-thumb-empty{display:grid;place-items:center;width:100%;aspect-ratio:3/4;background:var(--soft);color:var(--muted);font-size:.7rem;text-align:center;padding:8px}
.timeline-copy{min-width:0}
.timeline-time{display:block;color:var(--orange);font-size:.75rem;font-weight:800;letter-spacing:.07em;margin-bottom:5px}
.timeline-title{display:block;font-weight:750;line-height:1.3}
.timeline-index{display:block;color:var(--muted);font-size:.72rem;letter-spacing:.1em;margin-top:7px}
.brief-section{display:grid;grid-template-columns:minmax(155px,.32fr) minmax(0,1fr);gap:24px;padding:28px 0;border-bottom:1px solid var(--line)}
.brief-content{min-width:0}
.brief-lead{font-size:1.02rem;max-width:76ch;margin-bottom:14px}
.brief-hook{border-left:3px solid var(--orange);padding-left:13px;color:#4d5e55}
details{min-width:0}
summary{cursor:pointer}
summary:focus-visible,button:focus-visible,a:focus-visible{outline:3px solid var(--focus);outline-offset:3px;border-radius:3px}
.brief-details,.cast-details,.asset-details,.audio-details,.continuity-details,.prompt-disclosure,.contact-details{border-top:1px solid var(--line);margin-top:12px;padding-top:10px}
.brief-details>summary,.cast-details>summary,.asset-details>summary,.audio-details>summary,.continuity-details>summary,.prompt-disclosure>summary,.contact-details>summary{font-weight:750;color:var(--green);min-height:36px;display:flex;align-items:center;justify-content:space-between;gap:12px;list-style:none}
summary::-webkit-details-marker{display:none}
summary:after{content:"＋";color:var(--orange);font-weight:800}
details[open]>summary:after{content:"−"}
.detail-meta{font-size:.78rem;color:var(--muted);font-weight:500;text-align:right}
.cast-section{padding:20px 0 26px;border-bottom:1px solid var(--line)}
.cast-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:18px;padding:8px 0 4px}
.cast-person{padding:4px 12px 4px 0;border-right:1px solid var(--line)}
.cast-person:last-child{border-right:0}
.cast-person p{margin:0 0 6px}
.cast-name{font-size:1.05rem;font-weight:800}
.cast-id,.small{color:var(--muted);font-size:.84rem}
.cast-reference{display:block;width:min(100%,180px);margin:10px 0 6px;text-decoration:none}
.cast-reference img{display:block;width:100%;aspect-ratio:2/3;object-fit:cover;background:var(--soft);border:1px solid var(--line)}
.cast-reference span{display:block;margin-top:4px;color:var(--muted);font-size:.72rem}
.cast-reference.character-sheet{width:min(100%,520px)}
.cast-reference.character-sheet img{aspect-ratio:auto;height:auto;object-fit:contain}
.scene{padding:34px 0 40px;border-bottom:1px solid var(--line);scroll-margin-top:20px}
.scene-head{display:grid;grid-template-columns:58px minmax(0,1fr) auto;gap:16px;align-items:center;margin-bottom:20px}
.scene-number{display:grid;place-items:center;width:46px;height:46px;border:1px solid var(--orange);color:var(--orange);font-weight:850;font-size:.9rem}
.scene-title-wrap{min-width:0}
.scene-title-wrap .section-kicker{margin:0 0 4px}
.scene-time{font-size:.86rem;font-weight:800;white-space:nowrap;color:var(--green);border-bottom:2px solid var(--orange);padding:3px 0}
.scene-grid{display:grid;grid-template-columns:minmax(0,.92fr) minmax(0,1.08fr);gap:clamp(22px,4vw,52px);align-items:start}
.scene-media,.scene-content{min-width:0}
.storyboard-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,210px),1fr));gap:14px;align-items:start}
.storyboard-panel{min-width:0}
.storyboard-frame{margin:0;background:var(--soft)}
.storyboard-frame a{display:block}
.storyboard-frame img{display:block;width:100%;height:auto;max-height:680px;object-fit:contain;background:var(--soft)}
.storyboard-frame figcaption{display:flex;justify-content:space-between;gap:8px;padding:8px 2px 2px;font-size:.8rem;line-height:1.4;color:var(--muted)}
.storyboard-empty{border-left:3px solid var(--line);padding:9px 12px;color:var(--muted)}
.scene-location{margin:0 0 18px}
.scene-location h3{display:flex;justify-content:space-between;gap:8px;margin:0 0 8px;color:var(--green)}
.scene-location figure{margin:0}
.scene-location-image{display:block;width:100%;height:auto;max-height:460px;object-fit:contain;background:var(--soft);border:1px solid var(--line)}
.scene-location figcaption,.scene-location-status{display:block;margin-top:5px;color:var(--muted);font-size:.78rem}
.ref-list{display:flex;flex-wrap:wrap;gap:6px;margin:10px 0}
.ref-chip{display:inline-flex;align-items:center;gap:6px;padding:5px 8px;border:1px solid #c8d4bc;color:var(--green);font-size:.76rem;background:#f1f4e9;overflow-wrap:anywhere}
.ref-chip b{color:var(--orange);font-size:.68rem;letter-spacing:.06em}
.ref-chip>*{min-width:0}
.scene-action{font-size:1rem;line-height:1.7;max-width:66ch}
.scene-facts{display:grid;grid-template-columns:repeat(auto-fit,minmax(145px,1fr));gap:12px;margin:18px 0;padding:14px 0;border-top:1px solid var(--line);border-bottom:1px solid var(--line)}
.fact-label{display:block;margin-bottom:3px;color:var(--muted);font-size:.69rem;font-weight:800;letter-spacing:.1em;text-transform:uppercase}
.fact-value{font-size:.89rem;line-height:1.45}
.dialogue-list{list-style:none;margin:12px 0;padding:0}
.dialogue-list li{padding:7px 0;border-bottom:1px solid #e9e4d8}
.dialogue-speaker{display:inline-block;min-width:76px;color:var(--green);font-size:.82rem;font-weight:800}
.text-chip{display:inline-block;margin:3px 6px 3px 0;padding:4px 8px;background:#eaf0f8;color:var(--blue);font-weight:750;font-size:.8rem}
.prompt-stack{display:grid;gap:8px;margin-top:18px}
.prompt-disclosure{margin:0;padding:0;border-top:1px solid var(--line)}
.prompt-disclosure>summary{min-height:48px}
.prompt-body{padding:3px 0 14px}
.prompt{white-space:pre-wrap;word-break:break-word;overflow-wrap:anywhere;background:#173f35;color:#fffdf8;padding:16px;margin:0 0 10px;font: .88rem/1.65 ui-monospace,SFMono-Regular,Menlo,monospace;border-left:3px solid var(--orange)}
.prompt code{font:inherit}
.negative-prompt{background:#f0eadc;color:#334a40}
.scene-review ul{margin:4px 0 12px;padding-left:20px;font-size:.89rem}
button{min-height:44px;padding:10px 15px;border:1px solid var(--green);background:var(--green);color:#fffdf8;cursor:pointer;font:inherit;font-weight:800;font-size:.82rem}
button:hover{background:#174536}
.audio-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:14px;padding-top:12px}
.audio-grid p{margin:0;font-size:.9rem}
.continuity-copy{padding-top:9px;max-width:72ch}
.asset-section,.claims-section,.qc-section{padding:28px 0;border-bottom:1px solid var(--line)}
.asset-intro{margin:10px 0 0;color:var(--muted);font-size:.86rem}
.asset-groups{display:grid;gap:24px;padding-top:16px}
.asset-group-heading{display:flex;align-items:baseline;justify-content:space-between;gap:12px;padding-bottom:7px;border-bottom:1px solid var(--line)}
.asset-group-heading h3{margin:0;color:var(--green);font-size:.95rem}
.asset-group-count{color:var(--muted);font-size:.75rem}
.asset-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,280px),1fr));gap:0 20px}
.asset-card{display:grid;grid-template-columns:88px minmax(0,1fr);gap:14px;align-items:start;padding:14px 0;border-bottom:1px solid var(--line);min-width:0}
.asset-card-no-preview{grid-template-columns:1fr}
.asset-card-media{min-width:0}
.asset-thumb-link{display:block}
.asset-thumb{display:block;width:100%;aspect-ratio:3/4;object-fit:cover;background:var(--soft);border:1px solid var(--line)}
.asset-thumb-wide{aspect-ratio:16/9;object-fit:contain}
.asset-thumb-empty{display:grid;place-items:center;width:100%;aspect-ratio:3/4;padding:6px;background:var(--soft);color:var(--muted);font-size:.68rem;text-align:center}
.asset-thumb-empty.asset-thumb-wide{aspect-ratio:16/9}
.asset-card-content{min-width:0}
.asset-card-top{display:flex;align-items:flex-start;justify-content:space-between;gap:8px}
.asset-name{font-weight:800;line-height:1.35;overflow-wrap:anywhere}
.asset-badges{display:flex;flex-wrap:wrap;gap:5px;margin-top:7px}
.asset-badge{display:inline-flex;align-items:center;padding:3px 7px;border:1px solid var(--line);color:var(--muted);font-size:.67rem;font-weight:750;line-height:1.3}
.asset-badge.status-present{border-color:#b9d1c3;background:#edf4ef;color:var(--green)}
.asset-badge.status-planned,.asset-badge.status-missing,.asset-badge.status-withheld{border-color:#e2c891;background:#fbf4e6;color:#805510}
.asset-description{display:block;color:var(--muted);font-size:.79rem;line-height:1.5;margin-top:8px}
.asset-scenes{display:flex;flex-wrap:wrap;align-items:center;gap:5px;margin-top:9px}
.asset-scenes-label{color:var(--muted);font-size:.69rem}
.asset-scene-link{padding:3px 7px;border:1px solid #c8d4bc;background:#f1f4e9;color:var(--green);font-size:.68rem;font-weight:750;text-decoration:none}
.asset-actions{display:flex;flex-wrap:wrap;align-items:center;gap:8px;margin-top:8px}
.asset-link{display:inline-block;color:var(--blue);font-size:.77rem;font-weight:750}
.asset-file{margin:2px 0 0}
.asset-file>summary,.asset-id-details>summary{min-height:32px;color:var(--blue);font-size:.72rem;font-weight:700}
.asset-file code{display:block;max-width:100%;padding:8px;background:var(--soft);overflow-wrap:anywhere;word-break:break-word;font-size:.7rem}
.asset-file button{margin-top:6px}
.asset-id-details{margin-top:4px}
.asset-id-details code{font-size:.7rem;color:var(--muted);overflow-wrap:anywhere}
.claims-list{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:14px;padding-top:8px}
.claim{padding:12px 0;border-top:1px solid var(--line)}
.claim p{margin:0 0 5px}
.claim-status{font-size:.76rem;color:var(--muted)}
.qc-section ul{margin-bottom:0;padding-left:20px}
.footer-note{padding-top:24px;color:var(--muted);font-size:.78rem}
.storyboard-contact-sheet{display:block;width:min(100%,760px);height:auto;margin:14px 0}
.sr-only{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}
@media(max-width:800px){
 main{padding:24px 22px 58px}
 .hero-row{display:block}
 .timeline-item{grid-template-columns:70px minmax(0,1fr);gap:10px;padding-right:10px}
 .timeline-item+.timeline-item{padding-left:10px}
 .timeline-thumb,.timeline-thumb-empty{aspect-ratio:3/4}
 .brief-section{grid-template-columns:1fr;gap:6px}
 .scene-grid{grid-template-columns:1fr;gap:20px}
 .scene-media{max-width:680px}
 .scene-head{grid-template-columns:46px minmax(0,1fr) auto;gap:11px}
 .scene-number{width:40px;height:40px}
}
@media(max-width:560px){
 body{font-size:15px}
 main{padding:18px 16px 46px}
 h1{font-size:2.15rem;max-width:15ch}
 .hero-summary{font-size:.96rem}
 .meta-row{gap:6px 12px;font-size:.79rem}
 .timeline{grid-template-columns:1fr;border-bottom:0}
 .timeline-item,.timeline-item+.timeline-item{grid-template-columns:54px minmax(0,1fr);gap:12px;padding:9px 0;border-left:0;border-bottom:1px solid var(--line)}
 .timeline-thumb,.timeline-thumb-empty{width:54px;height:72px;aspect-ratio:auto}
 .timeline-title{font-size:.92rem}
 .timeline-index{margin-top:3px}
 .section-heading{align-items:start;flex-direction:column;gap:4px}
 .scene{padding:26px 0 30px}
 .scene-head{grid-template-columns:38px minmax(0,1fr);gap:10px;margin-bottom:14px}
 .scene-number{width:34px;height:34px;font-size:.78rem}
 .scene-time{grid-column:2;justify-self:start;margin-top:2px}
 .storyboard-grid{grid-template-columns:1fr}
 .storyboard-frame img{max-height:none}
 .scene-facts,.audio-grid,.claims-list{grid-template-columns:1fr}
 .cast-grid,.asset-list{grid-template-columns:1fr}
 .cast-person{border-right:0;border-bottom:1px solid var(--line);padding-bottom:12px}
 .asset-row{grid-template-columns:minmax(0,1fr) auto}
 .prompt{font-size:.8rem;padding:12px}
 button{width:100%}
}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
@media print{body{background:#fff}main{max-width:100%;padding:0 12px}.page-header,.timeline-section,.brief-section,.cast-section,.scene,.asset-section,.claims-section,.qc-section{break-inside:avoid;border-color:#bbb}.timeline-item{break-inside:avoid}button{display:none}.prompt{color:#111;background:#eee;white-space:pre-wrap}.asset-file>summary{display:none}.asset-file:not([open])>code{display:block}}
"""

def e(value):
    return html.escape(str(value), quote=True)


FILE_STATUS_LABELS = {
    "present": "Available",
    "planned": "Planned",
    "missing": "File missing",
    "withheld": "Outside the current review",
    "unavailable": "Preview unavailable",
}


def asset_href(asset, base_dir, output_dir=None):
    path = asset_path(asset, base_dir).resolve()
    output_folder = Path(output_dir or base_dir).absolute()
    try:
        relative = os.path.relpath(path, start=output_folder.resolve())
        # Browsers remove ".." segments before following directory symlinks.
        browser_target = Path(os.path.normpath(output_folder / relative))
        if browser_target.resolve() != path:
            relative = os.path.relpath(path, start=output_folder)
    except ValueError:
        # On Windows, files on different drives cannot be linked relatively.
        return path.as_uri()
    return quote(Path(relative).as_posix(), safe="/-._~")


class SheetAssets:
    def __init__(self, production, base_dir, output_dir):
        self.base_dir = Path(base_dir or Path.cwd())
        self.output_dir = Path(output_dir or self.base_dir)
        self.by_id = {asset["id"]: asset for asset in production["assets"]}
        self.storyboard = assess_storyboard(production, self.by_id, self.base_dir)

    def status(self, asset, *, image=False, panel=False):
        status = asset_status(asset, self.base_dir)
        if status != "present":
            return status
        if panel and (asset.get("kind") != "storyboard" or asset["id"] == self.storyboard.preview_id):
            return "unavailable"
        if not self.storyboard.allows_asset(asset):
            return "withheld"
        if image and asset_path(asset, self.base_dir).suffix.lower() not in IMAGE_SUFFIXES:
            return "unavailable"
        return "present"

    def href(self, asset, *, image=False, panel=False):
        if self.status(asset, image=image, panel=panel) == "present":
            return asset_href(asset, self.base_dir, self.output_dir)
        return None


def approval_summary(workflow, storyboard):
    sheet = {"draft": "Draft", "review": "In review", "approved": "Approved"}[workflow["approval_status"]]
    preview_status = workflow.get("storyboard_preview_status", "not_started")
    preview = {
        "not_started": "Planned",
        "awaiting_review": "Draft · Awaiting review",
        "approved": "Approved",
        "changes_requested": "Changes requested",
        "failed": "Generation failed",
    }[preview_status]
    if preview_status in {"awaiting_review", "approved"} and not storyboard.preview_visible:
        preview = "Preview unavailable"
    stills = {
        "not_started": "Awaiting authorization",
        "generated": "Complete" if storyboard.full_image_ids else "Set unavailable",
        "declined": "Declined",
        "failed": "Generation failed",
    }[workflow.get("storyboard_images_status", "not_started")]
    if workflow.get("storyboard_images_authorized") and workflow.get("storyboard_images_status", "not_started") == "not_started":
        stills = "Authorized · Awaiting images"
    video = "Authorized" if sheet == "Approved" and workflow["production_authorized"] else "Not authorized"
    return (
        ("Production sheet", sheet),
        ("Storyboard contact sheet", preview),
        ("Full storyboard stills", stills),
        ("Video production", video),
    )


def prompt_html(text, identifier, button_label, *, negative=False):
    css_class = "prompt negative-prompt" if negative else "prompt"
    content = e(text).replace("\r", "&#13;")
    return (
        f'<pre class="{css_class}" id="{e(identifier)}"><code>{content}</code></pre>'
        f'<button type="button" class="copy-btn" data-copy-target="{e(identifier)}" '
        f'data-copy-label="{button_label}">{button_label}</button>'
    )


def image_prompt_details(panel):
    prompt = panel.get("image_prompt")
    if not prompt:
        return ""
    identifier = "image-prompt-" + quote(panel["id"], safe="-_.")
    return (
        '<details class="prompt-disclosure"><summary><span>AI Image Prompt</span></summary>'
        '<div class="prompt-body">' + prompt_html(prompt, identifier, "Copy Image Prompt") + '</div></details>'
    )


def reference_list_html(ids, assets, label="Reference assets"):
    if not ids:
        return ""
    chips = []
    for aid in ids:
        asset = assets.by_id.get(aid, {})
        href = assets.href(asset)
        name = f'<a href="{e(href)}">{e(aid)}</a>' if href else f'<span>{e(aid)}</span>'
        status = FILE_STATUS_LABELS[assets.status(asset)] if asset else "Unknown asset"
        meta = f'{asset.get("kind", "asset")} · {status}'
        chips.append(f'<span class="ref-chip"><b>REF</b> {name} <span>· {e(meta)}</span></span>')
    return f'<div class="ref-list" aria-label="{e(label)}">' + "".join(chips) + "</div>"


def storyboard_preview_html(scene, assets):
    panels = scene_panel_records(scene, assets.by_id)
    if not panels:
        return '<p class="storyboard-empty">No storyboard panels linked</p>'
    figures = []
    for index, panel in enumerate(panels, 1):
        aid = panel["image_asset_id"]
        label = panel["description"] or panel["id"]
        asset = assets.by_id.get(aid, {})
        href = assets.href(asset, image=True, panel=True)
        if href:
            caption = f"Frame {index:02d}" if aid in assets.storyboard.full_image_ids else "Reference frame"
            panel_html = (
                f'<figure class="storyboard-frame"><a href="{e(href)}">'
                f'<img loading="lazy" src="{e(href)}" alt="{e(label)}"></a>'
                f'<figcaption><span>{e(label)}</span><span>{caption}</span></figcaption></figure>'
            )
        else:
            status = assets.status(asset, image=True, panel=True)
            panel_html = (
                f'<div class="storyboard-empty"><span>{e(label)}</span>'
                f'<span class="asset-status {status}">{FILE_STATUS_LABELS[status]}</span></div>'
            )
        panel_html += reference_list_html(panel.get("reference_asset_ids", []), assets)
        panel_html += image_prompt_details(panel)
        figures.append(f'<div class="storyboard-panel">{panel_html}</div>')
    return f'<div class="storyboard-grid" data-count="{len(figures)}">' + "".join(figures) + "</div>"


def scene_location_assets(scene, assets):
    result = []
    seen = set()
    for aid in scene["video"].get("reference_asset_ids", []):
        asset = assets.by_id.get(aid)
        if asset and asset.get("kind") == "location" and aid not in seen:
            result.append(asset)
            seen.add(aid)
    return result


def scene_location_html(scene, assets, approval_status):
    location = scene["continuity"].get("location", "").strip()
    refs = scene_location_assets(scene, assets)
    if not refs:
        label = location or "Location not confirmed"
        return (
            '<div class="scene-location"><h3>Location reference</h3>'
            f'<p class="small">{e(label)}</p>'
            '<p class="scene-location-status">Planned · no location image linked</p></div>'
        )
    parts = ['<div class="scene-location"><h3>Location reference</h3>']
    for asset in refs:
        status = assets.status(asset, image=True)
        label = (
            "Approved" if status == "present" and approval_status == "approved"
            else "Draft" if status == "present" else FILE_STATUS_LABELS[status]
        )
        name = asset_display_name(asset)
        href = assets.href(asset, image=True)
        if href:
            parts.append(
                '<figure><a href="' + e(href) + '"><img class="scene-location-image" loading="lazy" src="'
                + e(href) + '" alt="Location reference: ' + e(name) + '"></a>'
                + '<figcaption>Location reference · ' + e(name) + ' · ' + e(label) + '</figcaption></figure>'
            )
        else:
            parts.append(
                '<p class="scene-location-status">Location reference · ' + e(name) + ' · ' + e(label) + '</p>'
            )
    return "".join(parts) + "</div>"


def scene_location_markdown(scene, assets, approval_status):
    location = scene["continuity"].get("location", "").strip() or "Location not confirmed"
    lines = ["", "**Location reference**", "", f"**Location** · {markdown_text(location)}"]
    refs = scene_location_assets(scene, assets)
    if not refs:
        lines += ["", "Location reference · Planned · no location image linked"]
        return lines
    for asset in refs:
        status = assets.status(asset, image=True)
        label = (
            "Approved" if status == "present" and approval_status == "approved"
            else "Draft" if status == "present" else FILE_STATUS_LABELS[status]
        )
        href = assets.href(asset, image=True)
        name = markdown_text(asset_display_name(asset))
        if href:
            lines += ["", f"![Location reference · {label} · {name}]({href})"]
        else:
            lines += ["", f"Location reference · {name} · {label}"]
    return lines


def project_storyboard_preview_html(workflow, assets, review_label):
    asset = assets.by_id.get(assets.storyboard.preview_id, {})
    href = assets.href(asset, image=True)
    in_review = (
        workflow["approval_status"] != "approved"
        or workflow.get("storyboard_preview_status") in {"awaiting_review", "changes_requested"}
    )
    opened = " open" if in_review else ""
    media = (
        f'<a href="{e(href)}"><img class="storyboard-contact-sheet" src="{e(href)}" alt="Ordered storyboard contact sheet"></a>'
        if href else '<p class="storyboard-empty">No contact-sheet image available.</p>'
    )
    return (
        f'<details class="contact-details"{opened}><summary><span>Contact sheet</span>'
        f'<span class="detail-meta">{e(review_label)}</span></summary>{media}</details>'
    )


def timeline_html(scenes, assets):
    items=[]
    for index,scene in enumerate(scenes,1):
        panels=scene_panel_records(scene,assets.by_id)
        first=panels[0] if panels else {}
        aid=first.get('image_asset_id')
        asset=assets.by_id.get(aid,{})
        href=assets.href(asset,image=True,panel=True)
        if href:
            thumb=f'<img class="timeline-thumb" loading="lazy" src="{e(href)}" alt="">'
        else:
            thumb='<span class="timeline-thumb-empty">Frame<br>'+str(index)+'</span>'
        start=scene.get('start_seconds',0);end=start+scene.get('duration_seconds',0)
        items.append(
            '<a class="timeline-item" href="#'+e(scene['id'])+'" aria-label="Go to scene '+str(index)+', '+e(scene['narrative_beat'])+'">'
            +thumb+'<span class="timeline-copy"><span class="timeline-time">'+str(start).zfill(2)+'–'+str(end).zfill(2)+'s</span>'
            +'<span class="timeline-title">'+e(scene['narrative_beat'])+'</span><span class="timeline-index">SCENE '+str(index).zfill(2)+'</span></span></a>'
        )
    total=(scenes[-1].get('start_seconds',0)+scenes[-1].get('duration_seconds',0)) if scenes else 0
    return '<section class="timeline-section" aria-labelledby="timeline-heading"><div class="section-heading"><div><p class="section-kicker">Story at a glance</p><h2 id="timeline-heading">Storyboard timeline</h2></div><p>'+str(len(scenes))+' scenes · '+str(total)+' seconds</p></div><nav class="timeline" aria-label="Scene timeline">'+''.join(items)+'</nav></section>'


def asset_display_name(asset):
    aid=asset.get('id','asset')
    description=asset.get('description','').strip()
    if description:
        candidate=re.split(r'[;.!?]',description,maxsplit=1)[0].strip()
        if len(candidate)>64:candidate=candidate[:61].rstrip()+'…'
        if candidate:return candidate
    return aid.replace('_',' ').replace('-',' ').title()


def asset_scene_usage(assets,scenes,characters):
    usage={asset.get('id'):set() for asset in assets}
    character_by_id={character.get('id'):character for character in characters}
    for scene_index,scene in enumerate(scenes,1):
        sid=scene.get('id');label='Scene '+str(scene_index).zfill(2)
        visual=scene.get('visual',{})
        for panel in visual.get('storyboard_panels',[]):
            refs=list(panel.get('reference_asset_ids',[]))
            if panel.get('image_asset_id'):refs.append(panel['image_asset_id'])
            for aid in refs:
                if aid in usage:usage[aid].add((sid,label))
        for aid in visual.get('storyboard_asset_ids',[]):
            if aid in usage:usage[aid].add((sid,label))
        for aid in scene.get('video',{}).get('reference_asset_ids',[]):
            if aid in usage:usage[aid].add((sid,label))
        for cid in scene.get('continuity',{}).get('character_ids',[]):
            character=character_by_id.get(cid,{})
            for aid in character.get('reference_asset_ids',[]):
                if aid in usage:usage[aid].add((sid,label))
    return usage


def character_references(character, assets):
    rows = []
    for aid in character.get("reference_asset_ids", []):
        asset = assets.by_id.get(aid, {})
        if asset.get("kind") == "character":
            rows.append((asset, is_character_sheet(character["id"], aid)))
    return sorted(rows, key=lambda item: not item[1])


def character_image_label(is_sheet, status, sheet_approved):
    if is_sheet:
        if status != "present":
            return "Character sheet · " + FILE_STATUS_LABELS[status]
        return "Character sheet · Approved" if sheet_approved else "Character sheet · Draft"
    return "Character reference" if status == "present" else "Character reference · " + FILE_STATUS_LABELS[status]


def cast_html(characters, assets, sheet_approved):
    if not characters:
        return ""
    rows = []
    for character in characters:
        images = []
        references = character_references(character, assets)
        for asset, is_sheet in references:
            label = character_image_label(is_sheet, assets.status(asset, image=True), sheet_approved)
            href = assets.href(asset, image=True)
            if href:
                css_class = "cast-reference character-sheet" if is_sheet else "cast-reference"
                alt = ("Character sheet for " if is_sheet else "Character reference for ") + character["name"]
                images.append(
                    f'<a class="{css_class}" href="{e(href)}"><img src="{e(href)}" alt="{e(alt)}">'
                    f'<span>{e(label)}</span></a>'
                )
            else:
                images.append(f'<p class="storyboard-empty">{e(label)}</p>')
        if not any(is_sheet for _, is_sheet in references):
            images.insert(0, '<p class="storyboard-empty">Character sheet · Planned</p>')
        rows.append(
            f'<article class="cast-person"><p><span class="cast-name">{e(character["name"])}</span> '
            f'<span class="cast-id">({e(character["id"])})</span></p>'
            + "".join(images)
            + f'<p>{e(character["identity_lock"])}</p><p class="small"><strong>Costume</strong> · '
            f'{e(character["wardrobe_lock"])}</p></article>'
        )
    opened = "" if sheet_approved else " open"
    return (
        f'<section class="cast-section"><details class="cast-details"{opened}><summary>'
        '<span>Cast & continuity</span><span class="detail-meta">'
        f'{len(characters)} characters</span></summary><div class="cast-grid">'
        + "".join(rows) + "</div></details></section>"
    )


def asset_rows_html(assets, scenes, characters):
    usage=asset_scene_usage(assets.by_id.values(),scenes,characters)
    grouped={'product':[],'character':[],'storyboard':[],'location':[],'audio':[],'other':[]}
    for asset in assets.by_id.values():
        grouped[asset["kind"]].append(asset)
    labels={'product':'สินค้าและแบรนด์','character':'ตัวละคร','storyboard':'Storyboard','location':'สถานที่','audio':'เสียง','other':'อื่น ๆ'}
    kind_labels={'product':'สินค้า','character':'ตัวละคร','storyboard':'Storyboard','location':'สถานที่','audio':'เสียง','other':'ไฟล์อื่น'}
    status_labels={'present':'พร้อมใช้','planned':'วางแผน','missing':'ไม่พบไฟล์','withheld':'อยู่นอกชุดที่รีวิว'}
    source_labels={'user':'ผู้ใช้ให้มา','generated':'สร้างด้วย AI','licensed':'ได้รับอนุญาต','unknown':'ไม่ระบุที่มา'}
    sheet_ids={asset["id"] for ch in characters for asset, is_sheet in character_references(ch, assets) if is_sheet}
    groups_html=[]
    for kind,items in grouped.items():
        if not items:continue
        cards=[]
        for asset in items:
            aid=asset['id'];path=asset.get('path')
            source=asset.get('source','unknown');description=asset.get('description','')
            display_name=asset_display_name(asset)
            display_status=assets.status(asset)
            preview=assets.href(asset,image=True)
            href=assets.href(asset)
            wide=aid==assets.storyboard.preview_id or aid in sheet_ids or asset.get('kind')=='location'
            if preview:
                thumb_class='asset-thumb asset-thumb-wide' if wide else 'asset-thumb'
                media='<a class="asset-thumb-link" href="'+e(preview)+'"><img class="'+thumb_class+'" loading="lazy" src="'+e(preview)+'" alt="Preview: '+e(display_name)+'"></a>'
            else:
                empty_class='asset-thumb-empty asset-thumb-wide' if wide else 'asset-thumb-empty'
                media='<div class="'+empty_class+'">'+e(FILE_STATUS_LABELS[display_status] if display_status!='present' else 'No image preview')+'</div>'
            scene_items=sorted(usage.get(aid,[]),key=lambda item:item[1])
            if scene_items:
                scene_links='<div class="asset-scenes"><span class="asset-scenes-label">ใช้ใน</span>'+''.join('<a class="asset-scene-link" href="#'+e(sid)+'">'+e(label)+'</a>' for sid,label in scene_items)+'</div>'
            else:
                scene_links='<div class="asset-scenes"><span class="asset-scenes-label">ระดับโปรเจกต์</span></div>'
            if href:
                action='<a class="asset-link" href="'+e(href)+'">เปิดไฟล์</a>'
            elif path and display_status=='missing':
                action='<span class="small">ไม่พบไฟล์ในตำแหน่งนี้</span>'
            else:
                action=''
            if href:
                slug=quote(str(aid),safe='-_.')
                file_details='<details class="asset-file"><summary>รายละเอียดไฟล์และตำแหน่ง</summary><p><span class="fact-label">Asset ID</span><code>'+e(aid)+'</code></p><p><span class="fact-label">File path</span><code id="asset-path-'+e(slug)+'">'+e(path)+'</code></p><button type="button" class="copy-btn" data-copy-target="asset-path-'+e(slug)+'" data-copy-label="คัดลอก path">คัดลอก path</button></details>'
            else:
                file_details='<details class="asset-id-details"><summary>ดู Asset ID</summary><code>'+e(aid)+'</code></details>'
            card_class='asset-card' if preview else 'asset-card asset-card-no-preview'
            kind_label=kind_labels.get(asset.get('kind','other'),asset.get('kind','other'))
            source_label=source_labels.get(source,source)
            status_label=status_labels.get(display_status,display_status)
            badges='<div class="asset-badges"><span class="asset-badge">'+e(kind_label)+'</span><span class="asset-badge">'+e(source_label)+'</span><span class="asset-badge status-'+e(display_status)+'">'+e(status_label)+'</span></div>'
            cards.append('<article class="'+card_class+'"><div class="asset-card-media">'+media+'</div><div class="asset-card-content"><strong class="asset-name">'+e(display_name)+'</strong>'+badges+'<span class="asset-description">'+e(description)+'</span>'+scene_links+'<div class="asset-actions">'+action+'</div>'+file_details+'</div></article>')
        group_id='asset-group-'+quote(str(kind),safe='-_.')
        groups_html.append('<section class="asset-group" aria-labelledby="'+e(group_id)+'"><div class="asset-group-heading"><h3 id="'+e(group_id)+'">'+e(labels.get(kind,kind.title()))+'</h3><span class="asset-group-count">'+str(len(items))+' รายการ</span></div><div class="asset-grid">'+''.join(cards)+'</div></section>')
    ready=sum(assets.status(asset)=='present' for asset in assets.by_id.values())
    summary=str(len(assets.by_id))+' assets · '+str(ready)+' พร้อมใช้'
    return '<section class="asset-section"><details class="asset-details"><summary><span>Project assets · ไฟล์และภาพอ้างอิง</span><span class="detail-meta">'+e(summary)+'</span></summary><p class="asset-intro">รวมไฟล์ที่ผู้ใช้นำมา ภาพที่สร้าง และภาพอ้างอิงที่ใช้ในโปรเจกต์</p><div class="asset-groups">'+''.join(groups_html)+'</div></details></section>'


def video_prompt_html(scene, assets):
    video=scene['video'];scene_id=quote(str(scene['id']),safe='-_.')
    prompt_id='video-prompt-'+scene_id;negative_id='negative-prompt-'+scene_id
    model=e(video.get('model','Model unspecified'))
    body=reference_list_html(video["reference_asset_ids"],assets,"Video reference assets")
    body+=prompt_html(video["prompt"],prompt_id,"Copy Video Prompt")
    negative=video.get('negative_prompt','')
    if negative:
        body+='<h3>Negative Prompt</h3>'+prompt_html(negative,negative_id,"Copy Negative Prompt",negative=True)
    return '<details class="prompt-disclosure"><summary><span>AI Video Prompt</span><span class="detail-meta">'+model+'</span></summary><div class="prompt-body">'+body+'</div></details>'


def contrast_ratio(foreground, background):
    def luminance(color):
        channels=[int(color[i:i+2],16)/255 for i in (1,3,5)]
        channels=[channel/12.92 if channel<=.04045 else ((channel+.055)/1.055)**2.4 for channel in channels]
        return .2126*channels[0]+.7152*channels[1]+.0722*channels[2]
    light,dark=sorted((luminance(foreground),luminance(background)),reverse=True)
    return (light+.05)/(dark+.05)


def theme_css(brand_accent=None, brand_secondary=None):
    values=[]
    backgrounds={
        '--orange':('#fffdf8','#f5f1e8'),
        '--blue':('#fffdf8','#f5f1e8','#eaf0f8'),
    }
    for variable, value in (('--orange',brand_accent),('--blue',brand_secondary)):
        if value is None:
            continue
        if not re.fullmatch(r'#[0-9a-fA-F]{6}',str(value)):
            raise ValueError('Brand colors must use six-digit hex values (#RRGGBB)')
        if min(contrast_ratio(value,background) for background in backgrounds[variable]) < 4.5:
            raise ValueError(variable+' brand color must have at least 4.5:1 contrast with sheet text backgrounds')
        values.append(variable+':'+value)
    return ':root{'+ ';'.join(values)+'}' if values else ''


COPY_SCRIPT = """
const copyTimers = new WeakMap();
const copyLive = document.getElementById("copy-live");
let announcementTimer;

function fallbackCopy(value, button) {
    const field = document.createElement("textarea");
    field.value = value;
    field.readOnly = true;
    field.tabIndex = -1;
    field.style.cssText = "position:fixed;top:0;left:0;opacity:0";
    document.body.appendChild(field);
    try {
        field.select();
        return document.execCommand("copy");
    } catch {
        return false;
    } finally {
        field.remove();
        button.focus({preventScroll: true});
    }
}

document.addEventListener("click", async (event) => {
    const button = event.target.closest("[data-copy-target]");
    if (!button) return;
    const node = document.getElementById(button.dataset.copyTarget);
    if (!node) return;

    let copied;
    try {
        await navigator.clipboard.writeText(node.textContent);
        copied = true;
    } catch {
        copied = fallbackCopy(node.textContent, button);
    }
    clearTimeout(copyTimers.get(button));
    clearTimeout(announcementTimer);
    button.textContent = copied ? "Copied!" : "Copy failed";
    copyLive.textContent = copied ? "Copied to clipboard" : "Could not copy to clipboard";
    copyTimers.set(button, setTimeout(() => {
        button.textContent = button.dataset.copyLabel;
    }, 1500));
    announcementTimer = setTimeout(() => { copyLive.textContent = ""; }, 1500);
});
"""


def scene_review_lists(scene):
    return (
        ("Unverified model capabilities", scene["video"]["unverified_capabilities"]),
        ("Acceptance criteria", scene["acceptance_criteria"]),
    )


def render_html(d, base_dir=None, brand_accent=None, brand_secondary=None, *, output_dir=None):
    p=d['project'];creative=d['creative'];scenes=d['scenes'];workflow=d['workflow']
    assets=SheetAssets(d,base_dir,output_dir)
    characters=d.get('characters',[]);character_by_id={c['id']:c for c in characters}
    status=workflow.get('approval_status','draft')
    approval=approval_summary(workflow,assets.storyboard)
    summary=creative.get('concept') or p.get('objective','')
    parts=['<!DOCTYPE html><html lang="'+e(p['language'])+'"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">','<title>'+e(p['title'])+' — CineSheet</title>','<style>'+STYLE+theme_css(brand_accent,brand_secondary)+'</style></head><body><main>']
    parts += [
        '<header class="page-header"><p class="eyebrow">CineSheet · AI Video Production</p><div class="hero-row"><div class="hero-copy"><h1>'+e(p['title'])+'</h1><p class="hero-summary">'+e(summary)+'</p></div></div>',
        '<div class="meta-row"><span class="meta-item">'+e(p['kind'])+'</span><span class="meta-item">'+e(p['duration_seconds'])+' seconds</span><span class="meta-item">'+e(p['aspect_ratio'])+'</span><span class="meta-item">'+e(p['model'])+'</span></div>',
        '<dl class="approval-summary" aria-label="Approval status">'
        +''.join(f'<div><dt>{e(label)}</dt><dd>{e(value)}</dd></div>' for label,value in approval)+'</dl>',
    ]
    for warning in assets.storyboard.warnings:
        parts += [f'<p class="approval-warning">{e(warning)}</p>']
    parts += ['</header>']
    if status!='approved':
        parts += ['<aside class="review-notice"><strong>Review scope</strong> · Written plan and the draft visuals shown here.</aside>']
    parts += [timeline_html(scenes,assets)]
    parts += [project_storyboard_preview_html(workflow,assets,approval[1][1])]
    parts += ['<section class="brief-section" aria-labelledby="brief-heading"><div><p class="section-kicker">The idea</p><h2 id="brief-heading">Creative brief</h2></div><div class="brief-content">']
    parts += ['<p class="brief-lead">'+e(creative.get('concept',''))+'</p>']
    parts += ['<p class="brief-hook"><strong>Hook</strong> · '+e(creative.get('hook',''))+'</p>']
    parts += ['<details class="brief-details"><summary><span>More project context</span><span class="detail-meta">Goal · audience · message · tone · CTA</span></summary><div class="audio-grid">']
    for key,label in [('objective','Goal'),('target_audience','Audience'),('key_message','Key message'),('tone','Tone'),('cta','CTA')]:
        parts += ['<div><span class="fact-label">'+label+'</span><p>'+e(p.get(key,''))+'</p></div>'] if key in ('objective','target_audience') else ['<div><span class="fact-label">'+label+'</span><p>'+e(creative.get(key,''))+'</p></div>']
    parts += ['</div></details></div></section>']
    parts += [cast_html(characters,assets,status=='approved')]
    for index,scene in enumerate(scenes,1):
        visual=scene['visual'];audio=scene['audio'];continuity=scene['continuity']
        start=scene['start_seconds'];end=start+scene['duration_seconds']
        parts += ['<section class="scene" id="'+e(scene['id'])+'" aria-labelledby="heading-'+e(scene['id'])+'">']
        parts += ['<div class="scene-head"><span class="scene-number" aria-hidden="true">'+str(index).zfill(2)+'</span><div class="scene-title-wrap"><p class="section-kicker">Scene '+str(index).zfill(2)+'</p><h2 id="heading-'+e(scene['id'])+'">'+e(scene['narrative_beat'])+'</h2></div><span class="scene-time">'+str(start).zfill(2)+'–'+str(end).zfill(2)+'s</span></div>']
        parts += ['<div class="scene-grid"><div class="scene-media">'+scene_location_html(scene,assets,workflow["approval_status"])+storyboard_preview_html(scene,assets)+'</div><div class="scene-content">']
        parts += ['<p class="scene-action">'+e(scene['story_action'])+'</p>']
        facts=[('Shot size',visual.get('shot_size','')),('Angle',visual.get('angle','')),('Movement',visual.get('movement',''))]
        parts += ['<div class="scene-facts">'+''.join('<div><span class="fact-label">'+label+'</span><span class="fact-value">'+e(value)+'</span></div>' for label,value in facts)+'</div>']
        parts += ['<p class="small">'+e(visual.get('framing_note',''))+'</p>']
        if audio.get('dialogue'):
            lines=[]
            for line in audio['dialogue']:
                speaker=character_by_id.get(line['speaker_id'],{}).get('name',line['speaker_id'])
                lines.append('<li><span class="dialogue-speaker">'+e(speaker)+'</span><span lang="'+e(line['language'])+'">'+e(line['text'])+'</span></li>')
            parts += ['<h3>Dialogue</h3><ul class="dialogue-list">'+''.join(lines)+'</ul>']
        on_screen=scene.get('on_screen_text',[])
        text_html=''.join('<span class="text-chip">'+e(text)+'</span>' for text in on_screen) if on_screen else '<span class="small">None planned</span>'
        parts += ['<div><span class="fact-label">On-screen text · add in edit</span>'+text_html+'</div>']
        parts += ['<details class="audio-details"><summary><span>Sound plan</span><span class="detail-meta">Ambience · SFX · BGM</span></summary><div class="audio-grid"><div><span class="fact-label">Ambience</span><p>'+e(audio.get('ambience',''))+'</p></div><div><span class="fact-label">SFX</span><p>'+e(', '.join(audio.get('sfx',[])))+'</p></div><div><span class="fact-label">BGM</span><p>'+e(audio.get('bgm',''))+'</p></div></div></details>']
        parts += ['<details class="continuity-details"><summary><span>Continuity notes</span><span class="detail-meta">'+str(len(continuity.get('character_ids',[])))+' characters</span></summary><p class="continuity-copy"><strong>Wardrobe</strong> · '+e(continuity.get('wardrobe_note',''))+'</p><p class="continuity-copy"><strong>Location</strong> · '+e(continuity.get('location',''))+'</p><p class="continuity-copy"><strong>Props</strong> · '+e(', '.join(continuity.get('props',[])))+'</p></details>']
        review_lists = [
            f'<h3>{e(label)}</h3><ul>' + ''.join(f'<li>{e(item)}</li>' for item in items) + '</ul>'
            for label,items in scene_review_lists(scene) if items
        ]
        if review_lists:
            parts += ['<div class="scene-review">'+''.join(review_lists)+'</div>']
        parts += ['<div class="prompt-stack">'+video_prompt_html(scene,assets)+'</div></div></div></section>']
    parts += [asset_rows_html(assets,scenes,characters)]
    if d.get('product_claims'):
        claim_rows=[]
        for claim in d['product_claims']:
            claim_rows.append('<article class="claim"><p><strong>'+e(claim.get('text',''))+'</strong></p><p class="claim-status">'+e(claim.get('verification',''))+' · permitted copy: '+e(claim.get('permitted_copy',''))+'</p><p class="small">'+e(claim.get('evidence',''))+'</p></article>')
        parts += ['<section class="claims-section"><details class="asset-details"><summary><span>Claims & evidence</span><span class="detail-meta">'+str(len(claim_rows))+' claims</span></summary><div class="claims-list">'+''.join(claim_rows)+'</div></details></section>']
    parts += ['<section class="qc-section"><details class="asset-details"><summary><span>QC & delivery</span><span class="detail-meta">'+e(d['delivery'].get('resolution',''))+' · '+e(d['delivery'].get('fps',''))+' fps · '+e(d['delivery'].get('container',''))+'</span></summary><ul>']
    for note in workflow.get('qc_notes',[]):parts += ['<li>'+e(note)+'</li>']
    parts += [
        '</ul></details></section>',
        '<p class="footer-note">Review document generated from the production JSON.</p>',
        '<div class="sr-only" id="copy-live" aria-live="polite" aria-atomic="true"></div>',
        '</main><script>'+COPY_SCRIPT+'</script></body></html>',
    ]
    return '\n'.join(parts)

def markdown_text(value):
    escaped = html.escape(str(value), quote=False)
    return re.sub(r"([\\\[\]*_`])", r"\\\1", escaped)


def markdown_prompt(label, prompt):
    fence = "`" * max(3, max((len(run) for run in re.findall(r"`+", prompt)), default=0) + 1)
    return ["", f"**{label}**", "", fence + "text", prompt, fence]


def markdown_references(ids, assets, label):
    if not ids:
        return []
    lines = ["", f"**{label}**", ""]
    for aid in ids:
        asset = assets.by_id.get(aid, {})
        href = assets.href(asset)
        name = markdown_text(aid)
        if href:
            name = f"[{name}]({href})"
        status = FILE_STATUS_LABELS[assets.status(asset)] if asset else "Unknown asset"
        lines.append(f'- {name} · {e(asset.get("kind", "asset"))} · {status}')
    return lines


def render_markdown(d, base_dir=None, *, output_dir=None):
    assets = SheetAssets(d, base_dir, output_dir)
    project, creative, workflow = d["project"], d["creative"], d["workflow"]
    approval = approval_summary(workflow, assets.storyboard)
    lines = [
        f'# {markdown_text(project["title"])}',
        "",
        f'**CineSheet 1.0** · {e(project["kind"])} · {e(project["duration_seconds"])}s · '
        f'{e(project["aspect_ratio"])} · {markdown_text(project["model"])}',
        "",
        "## Approval status",
        "",
    ]
    lines += [f"- **{label}** · {value}" for label, value in approval]
    for warning in assets.storyboard.warnings:
        lines += ["", markdown_text(warning)]
    preview = assets.by_id.get(assets.storyboard.preview_id, {})
    preview_href = assets.href(preview, image=True)
    lines += ["", "## Storyboard Contact Sheet", "", f'**{approval[1][1]}**', ""]
    lines.append(
        f"![Ordered storyboard contact sheet]({preview_href})"
        if preview_href else "No contact-sheet image available."
    )
    lines += ["", "## Creative Brief", ""]
    lines += [f"- **{key.replace('_',' ').title()}** · {markdown_text(creative[key])}"
              for key in ("concept", "hook", "key_message", "tone", "cta")]

    characters = {character["id"]: character for character in d["characters"]}
    if characters:
        lines += ["", "## Cast"]
    for character in characters.values():
        lines += [
            "", f'### {markdown_text(character["name"])} ({markdown_text(character["id"])})', "",
            markdown_text(character["identity_lock"]),
            "", f'**Costume** · {markdown_text(character["wardrobe_lock"])}',
        ]
        references = character_references(character, assets)
        if not any(is_sheet for _, is_sheet in references):
            lines += ["", "Character sheet · Planned"]
        for asset, is_sheet in references:
            status = assets.status(asset, image=True)
            label = character_image_label(is_sheet, status, workflow["approval_status"] == "approved")
            href = assets.href(asset, image=True)
            lines += ["", label]
            if href:
                lines += ["", f'![{label} for {markdown_text(character["name"])}]({href})']

    lines += ["", "## Storyboard & Prompts"]
    for scene in d["scenes"]:
        visual, audio, video = scene["visual"], scene["audio"], scene["video"]
        start = scene["start_seconds"]
        end = start + scene["duration_seconds"]
        shot = " · ".join(markdown_text(visual[key]) for key in ("shot_size", "angle", "movement"))
        lines += [
            "", f'### {scene["id"]} · {start}–{end}s · {markdown_text(scene["narrative_beat"])}',
            "", markdown_text(scene["story_action"]),
            "", f"**Shot** · {shot}",
        ]
        lines += scene_location_markdown(scene, assets, workflow["approval_status"])
        panels = scene_panel_records(scene, assets.by_id)
        if not panels:
            lines += ["", "No storyboard panels linked."]
        for panel in panels:
            aid = panel["image_asset_id"]
            asset = assets.by_id.get(aid, {})
            label = markdown_text(panel["description"] or panel["id"])
            href = assets.href(asset, image=True, panel=True)
            if href:
                role = "Storyboard frame" if aid in assets.storyboard.full_image_ids else "Reference frame"
                lines += ["", f"![{role} · {label}]({href})", "", f"*{label}*"]
            else:
                status = FILE_STATUS_LABELS[assets.status(asset, image=True, panel=True)]
                lines += ["", f"**Storyboard panel** · {label} · {status}"]
            lines += markdown_references(panel.get("reference_asset_ids", []), assets, "Reference assets")
            if panel.get("image_prompt"):
                lines += markdown_prompt("AI Image Prompt", panel["image_prompt"])
        for spoken in audio["dialogue"]:
            speaker = characters.get(spoken["speaker_id"], {}).get("name", spoken["speaker_id"])
            lines += ["", f'**{markdown_text(speaker)}** · {markdown_text(spoken["text"])}']
        lines += ["", "**On-screen text · add in edit**", ""]
        lines += [f"- {markdown_text(text)}" for text in scene["on_screen_text"]] or ["None planned"]
        lines += [
            "", f'**Ambience** · {markdown_text(audio["ambience"])}',
            "", f'**SFX** · {markdown_text(", ".join(audio["sfx"]))}',
            "", f'**BGM** · {markdown_text(audio["bgm"])}',
        ]
        for label, items in scene_review_lists(scene):
            if items:
                lines += ["", f"**{label}**", "", *(f"- {markdown_text(item)}" for item in items)]
        lines += ["", f'**Video model** · {markdown_text(video["model"])}']
        lines += markdown_references(video["reference_asset_ids"], assets, "Video reference assets")
        lines += markdown_prompt("AI Video Prompt", video["prompt"])
        if video["negative_prompt"]:
            lines += markdown_prompt("Negative Prompt", video["negative_prompt"])

    lines += ["", "## Project assets", ""]
    for aid, asset in assets.by_id.items():
        href = assets.href(asset)
        name = markdown_text(asset_display_name(asset))
        if href:
            name = f"[{name}]({href})"
        lines.append(f"- {name} ({markdown_text(aid)}) · {FILE_STATUS_LABELS[assets.status(asset)]}")
    if d["product_claims"]:
        lines += ["", "## Claims & evidence", ""]
    for claim in d["product_claims"]:
        lines.append(
            f'- {markdown_text(claim["text"])} · {e(claim["verification"])} · '
            f'Permitted copy {claim["permitted_copy"]} · {markdown_text(claim["evidence"])}'
        )
    delivery = d["delivery"]
    lines += [
        "", "## QC & Delivery", "",
        f'{markdown_text(delivery["resolution"])} · {delivery["fps"]} fps · {markdown_text(delivery["container"])}',
        "",
    ]
    lines += [f"- {markdown_text(note)}" for note in workflow["qc_notes"]]
    return "\n".join(lines).rstrip() + "\n"


def check_export_destination(output, production, assets):
    targets = [production, *(asset_path(asset, production.parent) for asset in assets)]
    resolved_output = output.resolve()
    for target in targets:
        if target is None:
            continue
        same_path = target.resolve() == resolved_output
        if same_path or (output.is_file() and target.is_file() and output.samefile(target)):
            raise ValueError("Output would overwrite the production JSON or a referenced asset. Choose a different --out path.")


def write_export(output, markup):
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=output.parent, delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(markup)
        temporary.replace(output)
    finally:
        if temporary:
            temporary.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("production", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--format", choices=["html", "markdown"], default="html")
    parser.add_argument("--brand-accent", help="Optional verified brand accent as #RRGGBB (HTML only)")
    parser.add_argument("--brand-secondary", help="Optional verified secondary brand color as #RRGGBB (HTML only)")
    args = parser.parse_args()
    try:
        production = args.production.resolve()
        data, errors, warnings = load_and_check_file(production)
        for warning in warnings:
            print("WARNING:", warning)
        if errors:
            print("Cannot render invalid JSON:\n" + "\n".join(errors), file=sys.stderr)
            return 1
        output = args.out.absolute()
        check_export_destination(output, production, data["assets"])
        if args.format == "markdown":
            markup = render_markdown(data, production.parent, output_dir=output.parent)
        else:
            markup = render_html(data, production.parent, args.brand_accent, args.brand_secondary, output_dir=output.parent)
        write_export(output, markup)
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"Cannot render sheet: {exc}", file=sys.stderr)
        return 1
    print(f"Created: {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
