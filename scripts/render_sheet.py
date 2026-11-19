#!/usr/bin/env python3
"""Render machine-canonical production JSON as offline HTML or Markdown."""
import argparse, json, html, re
from pathlib import Path
from urllib.parse import quote

STYLE="""
:root{color-scheme:light;--ink:#193b32;--muted:#62736a;--green:#1f5847;--orange:#a84c08;--blue:#26549c;--line:#d9d5c9;--paper:#fffdf8;--ground:#f5f1e8;--soft:#eee9dc;--focus:#135fc2}
*{box-sizing:border-box}
html{scroll-behavior:smooth;scroll-padding-top:18px}
body{margin:0;background:var(--ground);color:var(--ink);font:16px/1.65 system-ui,-apple-system,'Segoe UI',sans-serif}
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
.status-label{font-weight:800;text-transform:uppercase;letter-spacing:.08em;color:var(--green)}
.review-notice{margin:18px 0;padding:12px 16px;border-left:4px solid var(--orange);background:#fff5e6;color:#68461f}
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
.storyboard-frame img{display:block;width:100%;max-height:680px;aspect-ratio:9/16;object-fit:cover;background:var(--soft)}
.storyboard-frame figcaption{display:flex;justify-content:space-between;gap:8px;padding:8px 2px 2px;font-size:.8rem;line-height:1.4;color:var(--muted)}
.storyboard-empty{border-left:3px solid var(--line);padding:9px 12px;color:var(--muted)}
.ref-list{display:flex;flex-wrap:wrap;gap:6px;margin:10px 0}
.ref-chip{display:inline-flex;align-items:center;gap:6px;padding:5px 8px;border:1px solid #c8d4bc;color:var(--green);font-size:.76rem;background:#f1f4e9;overflow-wrap:anywhere}
.ref-chip b{color:var(--orange);font-size:.68rem;letter-spacing:.06em}
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
.negative-prompt{background:#f0eadc;color:#334a40}
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
.asset-card-content{min-width:0}
.asset-card-top{display:flex;align-items:flex-start;justify-content:space-between;gap:8px}
.asset-name{font-weight:800;line-height:1.35;overflow-wrap:anywhere}
.asset-badges{display:flex;flex-wrap:wrap;gap:5px;margin-top:7px}
.asset-badge{display:inline-flex;align-items:center;padding:3px 7px;border:1px solid var(--line);color:var(--muted);font-size:.67rem;font-weight:750;line-height:1.3}
.asset-badge.status-present{border-color:#b9d1c3;background:#edf4ef;color:var(--green)}
.asset-badge.status-planned,.asset-badge.status-missing{border-color:#e2c891;background:#fbf4e6;color:#805510}
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

def e(x): return html.escape(str(x),quote=True)

def asset_href(asset, base_dir):
    path=Path(asset['path'])
    if path.is_absolute():
        try:path=path.resolve().relative_to(Path(base_dir).resolve())
        except ValueError:return path.resolve().as_uri()
    return quote(path.as_posix(),safe='/-._~')

def image_prompt_details(panel):
    prompt=panel.get('image_prompt')
    if not prompt:return ''
    prompt_id='image-prompt-'+quote(str(panel.get('id','panel')),safe='-_.')
    return (
        '<details class="prompt-disclosure"><summary><span>AI Image Prompt</span>'
        '<span class="detail-meta">English · copy-ready</span></summary><div class="prompt-body">'
        '<pre class="prompt" id="'+e(prompt_id)+'">'+e(prompt)+'</pre>'
        '<button type="button" class="copy-btn" data-copy-target="'+e(prompt_id)+'" data-copy-label="Copy Image Prompt">Copy Image Prompt</button>'
        '</div></details>'
    )


def scene_panel_records(scene, assets_by_id):
    visual=scene.get('visual',{})
    panels=visual.get('storyboard_panels',[])
    if panels:return panels
    return [
        {'id':aid,'description':assets_by_id.get(aid,{}).get('description',aid),'image_asset_id':aid}
        for aid in visual.get('storyboard_asset_ids',[])
    ]


def storyboard_preview_html(scene, assets_by_id, base_dir):
    panels=scene_panel_records(scene,assets_by_id)
    if not panels:
        status=scene.get('visual',{}).get('storyboard_status','planned')
        return '<p class="storyboard-empty">No storyboard image linked · '+e(status)+'</p>'
    figures=[]
    for index,panel in enumerate(panels,1):
        aid=panel.get('image_asset_id')
        label=panel.get('description') or panel.get('id','Storyboard panel')
        asset=assets_by_id.get(aid) if aid else None
        if not asset or asset.get('status')!='present' or not asset.get('path') or not asset_file_exists(asset.get('path'),base_dir):
            status=asset.get('status','planned') if asset else 'planned'
            if asset and asset.get('status')=='present' and asset.get('path') and not asset_file_exists(asset.get('path'),base_dir):status='missing'
            panel_html='<div class="storyboard-empty"><span>'+e(label)+'</span><span class="asset-status '+e(status)+'">'+e(status)+'</span></div>'
        else:
            href=asset_href(asset,base_dir)
            panel_html=f'<figure class="storyboard-frame"><a href="{e(href)}"><img loading="lazy" src="{e(href)}" alt="{e(label)}"></a><figcaption><span>{e(label)}</span><span>Frame {index:02d}</span></figcaption></figure>'
        refs=panel.get('reference_asset_ids',[])
        if refs:
            labels=[]
            for ref_id in refs:
                ref=assets_by_id.get(ref_id,{})
                labels.append('<span class="ref-chip"><b>REF</b> '+e(ref_id)+' <span>· '+e(ref.get('kind','asset'))+'</span></span>')
            panel_html+='<div class="ref-list" aria-label="Reference assets">'+''.join(labels)+'</div>'
        panel_html+=image_prompt_details(panel)
        figures.append('<div class="storyboard-panel">'+panel_html+'</div>')
    return '<div class="storyboard-grid" data-count="'+str(len(figures))+'">'+''.join(figures)+'</div>'


def project_storyboard_preview_html(d, assets_by_id, base_dir):
    workflow=d.get('workflow',{})
    if 'storyboard_preview_status' not in workflow:return ''
    status=workflow.get('storyboard_preview_status','not_started')
    aid=workflow.get('storyboard_preview_asset_id')
    asset=assets_by_id.get(aid) if aid else None
    if asset and asset.get('status')=='present' and asset.get('path') and asset_file_exists(asset.get('path'),base_dir):
        href=asset_href(asset,base_dir)
        return '<details class="contact-details"><summary><span>Contact sheet</span><span class="detail-meta">'+e(status)+'</span></summary><a href="'+e(href)+'"><img class="storyboard-contact-sheet" loading="lazy" src="'+e(href)+'" alt="Ordered storyboard contact sheet"></a></details>'
    note='Storyboard contact sheet '+status+'; no preview image file linked.'
    return '<details class="contact-details"><summary><span>Contact sheet</span><span class="detail-meta">'+e(status)+'</span></summary><p class="storyboard-empty">'+e(note)+'</p></details>'


def timeline_html(scenes,assets_by_id,base_dir):
    items=[]
    for index,scene in enumerate(scenes,1):
        panels=scene_panel_records(scene,assets_by_id)
        first=panels[0] if panels else {}
        aid=first.get('image_asset_id')
        asset=assets_by_id.get(aid) if aid else None
        if asset and asset.get('status')=='present' and asset.get('path') and asset_file_exists(asset.get('path'),base_dir):
            href=asset_href(asset,base_dir)
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


def asset_file_exists(path,base_dir):
    if not path:return False
    candidate=Path(path)
    if not candidate.is_absolute():candidate=Path(base_dir)/candidate
    return candidate.is_file()


def asset_rows_html(assets,base_dir,scenes=None,characters=None):
    scenes=scenes or [];characters=characters or []
    usage=asset_scene_usage(assets,scenes,characters)
    grouped={'product':[],'character':[],'storyboard':[],'location':[],'other':[]}
    for asset in assets:
        kind=asset.get('kind','other')
        grouped[kind if kind in grouped else 'other'].append(asset)
    labels={'product':'สินค้าและแบรนด์','character':'ตัวละคร','storyboard':'Storyboard','location':'สถานที่','other':'อื่น ๆ'}
    kind_labels={'product':'สินค้า','character':'ตัวละคร','storyboard':'Storyboard','location':'สถานที่','audio':'เสียง','other':'ไฟล์อื่น'}
    status_labels={'present':'พร้อมใช้','planned':'วางแผน','missing':'ไม่พบไฟล์'}
    source_labels={'user':'ผู้ใช้ให้มา','generated':'สร้างด้วย AI','planned':'วางแผน','unknown':'ไม่ระบุที่มา'}
    image_exts={'.png','.jpg','.jpeg','.webp','.gif','.svg'}
    groups_html=[]
    for kind,items in grouped.items():
        if not items:continue
        cards=[]
        for asset in items:
            aid=asset.get('id','asset');path=asset.get('path');status=asset.get('status','planned')
            source=asset.get('source','unknown');description=asset.get('description','')
            display_name=asset_display_name(asset);exists=asset_file_exists(path,base_dir)
            display_status=status if status!='present' or exists else 'missing'
            is_image=bool(path and Path(path).suffix.lower() in image_exts)
            preview=is_image and exists and status=='present'
            wide=bool(path and (Path(path).suffix.lower()=='.svg' or 'contact sheet' in aid.lower()))
            if preview:
                href=asset_href(asset,base_dir)
                thumb_class='asset-thumb asset-thumb-wide' if wide else 'asset-thumb'
                media='<a class="asset-thumb-link" href="'+e(href)+'"><img class="'+thumb_class+'" loading="lazy" src="'+e(href)+'" alt="Preview: '+e(display_name)+'"></a>'
            else:
                media='<div class="asset-thumb-empty">'+('Preview unavailable' if path else 'No preview')+'</div>'
            scene_items=sorted(usage.get(aid,[]),key=lambda item:item[1])
            if scene_items:
                scene_links='<div class="asset-scenes"><span class="asset-scenes-label">ใช้ใน</span>'+''.join('<a class="asset-scene-link" href="#'+e(sid)+'">'+e(label)+'</a>' for sid,label in scene_items)+'</div>'
            else:
                scene_links='<div class="asset-scenes"><span class="asset-scenes-label">ระดับโปรเจกต์</span></div>'
            if path and exists and status=='present':
                href=asset_href(asset,base_dir)
                action='<a class="asset-link" href="'+e(href)+'">เปิดไฟล์</a>'
            elif path and display_status=='missing':
                action='<span class="small">ไม่พบไฟล์ในตำแหน่งนี้</span>'
            else:
                action=''
            if path:
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
    ready=sum(1 for asset in assets if asset.get('status')=='present' and asset_file_exists(asset.get('path'),base_dir))
    summary=str(len(assets))+' assets · '+str(ready)+' พร้อมใช้'
    return '<section class="asset-section"><details class="asset-details"><summary><span>Project assets · ไฟล์และภาพอ้างอิง</span><span class="detail-meta">'+e(summary)+'</span></summary><p class="asset-intro">รวมไฟล์ที่ผู้ใช้นำมา ภาพที่สร้าง และภาพอ้างอิงที่ใช้ในโปรเจกต์</p><div class="asset-groups">'+''.join(groups_html)+'</div></details></section>'


def video_prompt_html(scene):
    video=scene['video'];scene_id=quote(str(scene['id']),safe='-_.')
    prompt_id='video-prompt-'+scene_id;negative_id='negative-prompt-'+scene_id
    model=e(video.get('model','Model unspecified'))
    body='<pre class="prompt" id="'+e(prompt_id)+'">'+e(video.get('prompt',''))+'</pre>'
    body+='<button type="button" class="copy-btn" data-copy-target="'+e(prompt_id)+'" data-copy-label="Copy Video Prompt">Copy Video Prompt</button>'
    negative=video.get('negative_prompt','')
    if negative:
        body+='<h3>Negative Prompt</h3><pre class="prompt negative-prompt" id="'+e(negative_id)+'">'+e(negative)+'</pre>'
        body+='<button type="button" class="copy-btn" data-copy-target="'+e(negative_id)+'" data-copy-label="Copy Negative Prompt">Copy Negative Prompt</button>'
    return '<details class="prompt-disclosure"><summary><span>AI Video Prompt</span><span class="detail-meta">'+model+' · English</span></summary><div class="prompt-body">'+body+'</div></details>'


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


def render_html(d, base_dir=None, brand_accent=None, brand_secondary=None):
    p=d['project'];creative=d['creative'];scenes=d['scenes'];workflow=d['workflow']
    base_dir=Path(base_dir or Path.cwd())
    assets=d.get('assets',[]);assets_by_id={a['id']:a for a in assets}
    characters=d.get('characters',[]);character_by_id={c['id']:c for c in characters}
    status=workflow.get('approval_status','draft')
    summary=creative.get('concept') or p.get('objective','')
    parts=['<!DOCTYPE html><html lang="th"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">','<title>'+e(p['title'])+' — CineSheet</title>','<style>'+STYLE+theme_css(brand_accent,brand_secondary)+'</style></head><body><main>']
    parts += [
        '<header class="page-header"><p class="eyebrow">CineSheet · AI Video Production</p><div class="hero-row"><div class="hero-copy"><h1>'+e(p['title'])+'</h1><p class="hero-summary">'+e(summary)+'</p></div></div>',
        '<div class="meta-row"><span class="meta-item">'+e(p['kind'])+'</span><span class="meta-item">'+e(p['duration_seconds'])+' seconds</span><span class="meta-item">'+e(p['aspect_ratio'])+'</span><span class="meta-item">'+e(p['model'])+'</span><span class="meta-item status-label">'+e(status)+'</span></div></header>'
    ]
    if status!='approved':
        parts += ['<aside class="review-notice"><strong>Draft / Review</strong> — Not final production authorization. '+e('; '.join(workflow.get('qc_notes',[])))+'</aside>']
    parts += [timeline_html(scenes,assets_by_id,base_dir)]
    contact=project_storyboard_preview_html(d,assets_by_id,base_dir)
    if contact:parts += [contact]
    parts += ['<section class="brief-section" aria-labelledby="brief-heading"><div><p class="section-kicker">The idea</p><h2 id="brief-heading">Creative brief</h2></div><div class="brief-content">']
    parts += ['<p class="brief-lead">'+e(creative.get('concept',''))+'</p>']
    parts += ['<p class="brief-hook"><strong>Hook</strong> · '+e(creative.get('hook',''))+'</p>']
    parts += ['<details class="brief-details"><summary><span>More project context</span><span class="detail-meta">Goal · audience · message · tone · CTA</span></summary><div class="audio-grid">']
    for key,label in [('objective','Goal'),('target_audience','Audience'),('key_message','Key message'),('tone','Tone'),('cta','CTA')]:
        parts += ['<div><span class="fact-label">'+label+'</span><p>'+e(p.get(key,''))+'</p></div>'] if key in ('objective','target_audience') else ['<div><span class="fact-label">'+label+'</span><p>'+e(creative.get(key,''))+'</p></div>']
    parts += ['</div></details></div></section>']
    if characters:
        cast_rows=[]
        for character in characters:
            reference_html=''
            for ref_id in character.get('reference_asset_ids',[]):
                ref=assets_by_id.get(ref_id,{})
                if ref.get('kind')=='character' and ref.get('status')=='present' and ref.get('path') and asset_file_exists(ref.get('path'),base_dir):
                    href=asset_href(ref,base_dir)
                    reference_html+='<a class="cast-reference" href="'+e(href)+'"><img loading="lazy" src="'+e(href)+'" alt="Character reference for '+e(character['name'])+'"><span>Character reference · '+e(ref_id)+'</span></a>'
            cast_rows.append('<article class="cast-person"><p><span class="cast-name">'+e(character['name'])+'</span> <span class="cast-id">('+e(character['id'])+')</span></p>'+reference_html+'<p>'+e(character['identity_lock'])+'</p><p class="small"><strong>Costume</strong> · '+e(character['wardrobe_lock'])+'</p></article>')
        parts += ['<section class="cast-section"><details class="cast-details"><summary><span>Cast & continuity</span><span class="detail-meta">'+str(len(characters))+' characters</span></summary><div class="cast-grid">'+''.join(cast_rows)+'</div></details></section>']
    for index,scene in enumerate(scenes,1):
        visual=scene['visual'];audio=scene['audio'];continuity=scene['continuity']
        start=scene['start_seconds'];end=start+scene['duration_seconds']
        parts += ['<section class="scene" id="'+e(scene['id'])+'" aria-labelledby="heading-'+e(scene['id'])+'">']
        parts += ['<div class="scene-head"><span class="scene-number" aria-hidden="true">'+str(index).zfill(2)+'</span><div class="scene-title-wrap"><p class="section-kicker">Scene '+str(index).zfill(2)+'</p><h2 id="heading-'+e(scene['id'])+'">'+e(scene['narrative_beat'])+'</h2></div><span class="scene-time">'+str(start).zfill(2)+'–'+str(end).zfill(2)+'s</span></div>']
        parts += ['<div class="scene-grid"><div class="scene-media">'+storyboard_preview_html(scene,assets_by_id,base_dir)+'</div><div class="scene-content">']
        parts += ['<p class="scene-action">'+e(scene['story_action'])+'</p>']
        facts=[('Shot size',visual.get('shot_size','')),('Angle',visual.get('angle','')),('Movement',visual.get('movement',''))]
        parts += ['<div class="scene-facts">'+''.join('<div><span class="fact-label">'+label+'</span><span class="fact-value">'+e(value)+'</span></div>' for label,value in facts)+'</div>']
        parts += ['<p class="small">'+e(visual.get('framing_note',''))+'</p>']
        if audio.get('dialogue'):
            lines=[]
            for line in audio['dialogue']:
                speaker=character_by_id.get(line['speaker_id'],{}).get('name',line['speaker_id'])
                lines.append('<li><span class="dialogue-speaker">'+e(speaker)+'</span>'+e(line['text'])+'</li>')
            parts += ['<h3>Dialogue</h3><ul class="dialogue-list">'+''.join(lines)+'</ul>']
        on_screen=scene.get('on_screen_text',[])
        text_html=''.join('<span class="text-chip">'+e(text)+'</span>' for text in on_screen) if on_screen else '<span class="small">None planned</span>'
        parts += ['<div><span class="fact-label">On-screen text · add in edit</span>'+text_html+'</div>']
        parts += ['<details class="audio-details"><summary><span>Sound plan</span><span class="detail-meta">Ambience · SFX · BGM</span></summary><div class="audio-grid"><div><span class="fact-label">Ambience</span><p>'+e(audio.get('ambience',''))+'</p></div><div><span class="fact-label">SFX</span><p>'+e(', '.join(audio.get('sfx',[])))+'</p></div><div><span class="fact-label">BGM</span><p>'+e(audio.get('bgm',''))+'</p></div></div></details>']
        parts += ['<details class="continuity-details"><summary><span>Continuity notes</span><span class="detail-meta">'+str(len(continuity.get('character_ids',[])))+' characters</span></summary><p class="continuity-copy"><strong>Wardrobe</strong> · '+e(continuity.get('wardrobe_note',''))+'</p><p class="continuity-copy"><strong>Location</strong> · '+e(continuity.get('location',''))+'</p><p class="continuity-copy"><strong>Props</strong> · '+e(', '.join(continuity.get('props',[])))+'</p></details>']
        parts += ['<div class="prompt-stack">'+video_prompt_html(scene)+'</div></div></div></section>']
    parts += [asset_rows_html(assets,base_dir,scenes,characters)]
    if d.get('product_claims'):
        claim_rows=[]
        for claim in d['product_claims']:
            claim_rows.append('<article class="claim"><p><strong>'+e(claim.get('text',''))+'</strong></p><p class="claim-status">'+e(claim.get('verification',''))+' · permitted copy: '+e(claim.get('permitted_copy',''))+'</p><p class="small">'+e(claim.get('evidence',''))+'</p></article>')
        parts += ['<section class="claims-section"><details class="asset-details"><summary><span>Claims & evidence</span><span class="detail-meta">'+str(len(claim_rows))+' claims</span></summary><div class="claims-list">'+''.join(claim_rows)+'</div></details></section>']
    parts += ['<section class="qc-section"><details class="asset-details"><summary><span>QC & delivery</span><span class="detail-meta">'+e(d['delivery'].get('resolution',''))+' · '+e(d['delivery'].get('fps',''))+' fps · '+e(d['delivery'].get('container',''))+'</span></summary><ul>']
    for note in workflow.get('qc_notes',[]):parts += ['<li>'+e(note)+'</li>']
    parts += ['</ul></details></section>','<p class="footer-note">Generated from one canonical production JSON; image previews appear only when their linked files are present. This sheet does not imply that video or audio was rendered.</p>','<div class="sr-only" id="copy-live" aria-live="polite" aria-atomic="true"></div>','</main><script>document.addEventListener("click",async event=>{const button=event.target.closest("[data-copy-target]");if(!button)return;const node=document.getElementById(button.dataset.copyTarget);if(!node)return;const value=node.innerText;try{await navigator.clipboard.writeText(value)}catch(error){const field=document.createElement("textarea");field.value=value;field.setAttribute("readonly","");field.style.position="fixed";field.style.opacity="0";document.body.appendChild(field);field.select();document.execCommand("copy");field.remove()}const label=button.dataset.copyLabel||button.textContent;button.textContent="Copied!";document.getElementById("copy-live").textContent="Copied to clipboard";window.setTimeout(()=>{button.textContent=label;document.getElementById("copy-live").textContent=""},1500)});</script></body></html>']
    return '\n'.join(parts)

def render_markdown(d, base_dir=None):
    base_dir=Path(base_dir or Path.cwd())
    assets_by_id={a['id']:a for a in d.get('assets',[])}
    p=d['project'];c=d['creative']; lines=[f'# {p["title"]}',f'**CineSheet 1.0** · {p["kind"]} · {p["duration_seconds"]}s · {p["aspect_ratio"]} · {p["model"]}',f'**Status:** {d["workflow"]["approval_status"]}','', '## Creative Brief']
    for key in ('concept','hook','key_message','tone','cta'):lines +=[f'- **{key}:** {c[key]}']
    workflow=d.get('workflow',{})
    if 'storyboard_preview_status' in workflow:
        preview_id=workflow.get('storyboard_preview_asset_id')
        preview=assets_by_id.get(preview_id) if preview_id else None
        lines+=['','## Storyboard Contact Sheet',f'**Status:** {workflow.get("storyboard_preview_status","not_started")}']
        if preview and preview.get('status')=='present' and preview.get('path') and asset_file_exists(preview.get('path'),base_dir):
            lines +=[f'![Storyboard contact sheet]({asset_href(preview,base_dir)})']
        else:
            lines +=['No preview image file linked.']
    lines+=['','## Cast']
    for ch in d['characters']:lines +=[f'- **{ch["name"]} ({ch["id"]})**: {ch["identity_lock"]}; wardrobe: {ch["wardrobe_lock"]}']
    lines+=['','## Storyboard & Prompts']
    for s in d['scenes']:
        v=s['visual']; a=s['audio'];lines +=['',f'### {s["id"]} · {s["start_seconds"]}–{s["start_seconds"]+s["duration_seconds"]}s',s['story_action'],f'**Shot:** {v["shot_size"]} · {v["angle"]} · {v["movement"]}']
        panels=v.get('storyboard_panels',[])
        storyboard_ids=v.get('storyboard_asset_ids',[])
        if panels:
            for panel in panels:
                aid=panel.get('image_asset_id')
                asset=assets_by_id.get(aid) if aid else None
                label=panel.get('description') or panel.get('id','Storyboard panel')
                if asset and asset.get('status')=='present' and asset.get('path') and asset_file_exists(asset.get('path'),base_dir):
                    lines +=[f'![Storyboard {panel.get("id",s["id"])}]({asset_href(asset,base_dir)})',f'*{label}*']
                else:
                    lines +=[f'**Storyboard preview:** {label} — full still {asset.get("status","planned") if asset else "planned"}']
                refs=panel.get('reference_asset_ids',[])
                if refs:
                    ref_labels=[f'{ref_id} — {assets_by_id.get(ref_id,{}).get("description","")}'.rstrip(' —') for ref_id in refs]
                    lines +=['**Reference assets:** '+ '; '.join(ref_labels)]
                image_prompt=panel.get('image_prompt')
                if image_prompt:
                    lines +=['**AI Image Prompt:**','```text',image_prompt,'```']
        elif storyboard_ids:
            for aid in storyboard_ids:
                asset=assets_by_id.get(aid)
                if asset and asset.get('status')=='present' and asset.get('path') and asset_file_exists(asset.get('path'),base_dir):
                    lines +=[f'![Storyboard {s["id"]}]({asset_href(asset,base_dir)})',f'*{asset.get("description",aid)}*']
                elif asset:
                    lines +=[f'**Storyboard preview:** {asset.get("status","planned")} — {asset.get("description",aid)}']
        else:
            lines +=[f'**Storyboard preview:** {v.get("storyboard_status","planned")} — no image linked']
        for spoken in a['dialogue']:lines +=[f'**{spoken["speaker_id"]}:** {spoken["text"]}']
        lines+= [f'**Ambience:** {a["ambience"]}',f'**SFX:** {", ".join(a["sfx"])}',f'**BGM:** {a["bgm"]}','**AI Video Prompt:**','```text',s['video']['prompt'],'```']
    lines+=['','## Claims & Assets']
    for a in d['assets']:lines +=[f'- {a["id"]}: {a["status"]} — {a["path"]}']
    for c in d['product_claims']:lines +=[f'- {c["text"]}: {c["verification"]} (permitted_copy={c["permitted_copy"]})']
    lines+=['','## QC & Delivery']
    for x in d['workflow']['qc_notes']:lines +=['- '+x]
    return '\n'.join(lines)+'\n'

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('production',type=Path)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--format',choices=['html','markdown'],default='html')
    ap.add_argument('--brand-accent',help='Optional verified brand accent as #RRGGBB (HTML only)')
    ap.add_argument('--brand-secondary',help='Optional verified secondary brand color as #RRGGBB (HTML only)')
    args=ap.parse_args()
    from validate_production import check_file
    schema=Path(__file__).resolve().parents[1]/'schemas/production.schema.json'
    errors,warnings=check_file(args.production.resolve(),schema)
    if errors:raise SystemExit('Cannot render invalid JSON:\n'+'\n'.join(errors))
    data=json.loads(args.production.read_text(encoding='utf-8'))
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(render_html(data,args.production.resolve().parent,args.brand_accent,args.brand_secondary) if args.format=='html' else render_markdown(data,args.production.resolve().parent),encoding='utf-8')
    print(f'Created: {args.out}')
    if warnings:print('Warnings: '+str(len(warnings))+' (see validate_production.py)')
