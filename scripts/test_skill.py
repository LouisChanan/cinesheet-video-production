#!/usr/bin/env python3
"""Regression checks using the bundled example and temporary corrupt files."""
import copy,json,sys,tempfile
from pathlib import Path
from validate_production import check_file
from render_sheet import asset_display_name,contrast_ratio,render_html,render_markdown


def assert_editorial_html(markup, scenes):
    assert '<meta name="viewport" content="width=device-width,initial-scale=1">' in markup
    assert markup.index('<section class="timeline-section"') < markup.index('<section class="brief-section"')
    assert markup.count('class="timeline-item"') == len(scenes)
    assert markup.count('data-copy-label="Copy Video Prompt"') == len(scenes)
    assert markup.count('<details class="prompt-disclosure">') >= len(scenes)
    assert 'summary:focus-visible,button:focus-visible,a:focus-visible' in markup
    assert '@media(max-width:800px)' in markup and '@media(max-width:560px)' in markup
    if '<details class="asset-file">' in markup:
        assert '<details class="asset-file"><summary>รายละเอียดไฟล์และตำแหน่ง</summary>' in markup
    else:
        assert '<details class="asset-id-details"><summary>ดู Asset ID</summary>' in markup
    assert '<details class="asset-file" open' not in markup
    assert 'Project assets · ไฟล์และภาพอ้างอิง' in markup
    assert 'asset-group-heading' in markup and 'สินค้าและแบรนด์' in markup
    assert 'ผู้ใช้ให้มา' in markup or 'สร้างด้วย AI' in markup
    if '<details class="asset-file">' in markup:
        assert 'คัดลอก path' in markup
    assert 'id="copy-live" aria-live="polite"' in markup
    assert 'navigator.clipboard.writeText' in markup and 'document.execCommand("copy")' in markup
    head = markup.partition('</head>')[0].lower()
    assert '<link rel=' not in head and '<script src=' not in markup.lower()
    for scene in scenes:
        start = markup.index('<section class="scene" id="'+scene['id']+'"')
        next_scene = markup.find('<section class="scene" id="', start + 1)
        block = markup[start:next_scene if next_scene >= 0 else len(markup)]
        assert block.index('<div class="scene-media">') < block.index('<p class="scene-action">')
        assert 'href="#'+scene['id']+'"' in markup

root=Path(__file__).resolve().parents[1]
example=root/'examples/naturgenic-ugc.json'
schema=root/'schemas/production.schema.json'
errors,warnings=check_file(example,schema)
assert not errors,(errors,warnings)
d=json.loads(example.read_text(encoding='utf-8'))
html=render_html(d)
md=render_markdown(d)
assert_editorial_html(html,d['scenes'])
assert asset_display_name({'id':'planned_character_look_refs','description':'Character look references; consistent wardrobe and face'}) == 'Character look references'
assert asset_display_name({'id':'arbitrary_asset_17','description':''}) == 'Arbitrary Asset 17'
assert '--orange:#a84c08' in html and '--blue:#26549c' in html
assert contrast_ratio('#a84c08','#fffdf8')>=4.5 and contrast_ratio('#a84c08','#f5f1e8')>=4.5
brand_html=render_html(d,brand_accent='#a84c08',brand_secondary='#34578a')
assert_editorial_html(brand_html,d['scenes'])
assert ':root{--orange:#a84c08;--blue:#34578a}' in brand_html
try:
    render_html(d,brand_accent='orange')
except ValueError:
    pass
else:
    raise AssertionError('Invalid brand color should be rejected')
try:
    render_html(d,brand_accent='#e87924')
except ValueError:
    pass
else:
    raise AssertionError('Low-contrast brand color should be rejected')
assert 'class="timeline-thumb-empty"' in html and 'class="storyboard-empty"' in html
assert 'NATURGENIC' in html and 'scene_03' in html and '3' in md
assert 'Pet-safe' in html and 'unverified' in html
assert 'image previews appear only when their linked files are present' in html
with tempfile.TemporaryDirectory() as temp:
    temp=Path(temp)
    (temp/'character-ref.png').write_bytes(b'preview')
    (temp/'storyboard-contact.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg"/>',encoding='utf-8')
    asset_data=copy.deepcopy(d)
    asset_data['assets'] += [
        {'id':'test_character_ref','kind':'character','path':'character-ref.png','source':'generated','status':'present','description':'Test character reference'},
        {'id':'test_contact_sheet','kind':'storyboard','path':'storyboard-contact.svg','source':'generated','status':'present','description':'Test contact sheet'},
    ]
    asset_data['characters'][0]['reference_asset_ids']=['test_character_ref']
    scene=asset_data['scenes'][0]
    panels=scene['visual'].setdefault('storyboard_panels',[])
    if panels:
        panels[0].setdefault('reference_asset_ids',[]).append('test_contact_sheet')
    asset_html=render_html(asset_data,temp)
    assert 'ตัวละคร' in asset_html and 'Storyboard' in asset_html
    assert 'class="asset-thumb asset-thumb-wide"' in asset_html
    assert 'class="asset-scene-link" href="#'+scene['id']+'"' in asset_html
    assert 'class="cast-reference"' in asset_html and 'Character reference for ' in asset_html
    assert 'คัดลอก path' in asset_html
    unavailable=copy.deepcopy(asset_data)
    unavailable['assets'] += [
        {'id':'planned_visual','kind':'storyboard','path':'not-created-yet.png','source':'planned','status':'planned','description':'Planned visual asset'},
        {'id':'missing_visual','kind':'character','path':'gone.png','source':'user','status':'present','description':'Unavailable visual asset'},
    ]
    unavailable['characters'][0]['reference_asset_ids']=['missing_visual']
    unavailable['workflow'].update({'storyboard_preview_status':'awaiting_review','storyboard_preview_asset_id':'planned_visual'})
    unavailable['scenes'][0]['visual']['storyboard_panels']=[{'id':'unavailable_panel','description':'Unavailable visual panel','image_asset_id':'missing_visual'}]
    unavailable_html=render_html(unavailable,temp)
    assert 'src="not-created-yet.png"' not in unavailable_html and 'href="not-created-yet.png"' not in unavailable_html
    assert 'src="gone.png"' not in unavailable_html and 'href="gone.png"' not in unavailable_html
    assert 'Unavailable visual asset' in unavailable_html and 'Unavailable visual panel' in unavailable_html and 'ไม่พบไฟล์' in unavailable_html
    assert 'status-missing' in unavailable_html and 'Storyboard contact sheet awaiting_review' in unavailable_html
    assert 'class="cast-reference"' not in unavailable_html
    unavailable_md=render_markdown(unavailable,temp)
    assert not any('![' in line and any(path in line for path in ('not-created-yet.png','gone.png')) for line in unavailable_md.splitlines())
with tempfile.TemporaryDirectory() as temp:
    temp=Path(temp)
    bad=copy.deepcopy(d)
    bad['scenes'][1]['start_seconds']=12
    path=temp/'bad.json';path.write_text(json.dumps(bad,ensure_ascii=False),encoding='utf-8')
    errors,_=check_file(path,schema)
    assert any('starts at 12' in e for e in errors),errors
    bad=copy.deepcopy(d)
    bad['assets'][0]['status']='planned'
    bad['scenes'][0]['audio']['dialogue'][0]['speaker_id']='unknown'
    path.write_text(json.dumps(bad,ensure_ascii=False),encoding='utf-8')
    errors,_=check_file(path,schema)
    assert any('unknown' in e for e in errors),errors
    bad=copy.deepcopy(d)
    bad['product_claims'][-1]['permitted_copy']=True
    path.write_text(json.dumps(bad,ensure_ascii=False),encoding='utf-8')
    errors,_=check_file(path,schema)
    assert any('Unverified claim' in e for e in errors),errors
    bad=copy.deepcopy(d)
    bad['scenes'][2]['duration_seconds']=9
    path.write_text(json.dumps(bad,ensure_ascii=False),encoding='utf-8')
    errors,_=check_file(path,schema)
    assert any('total 29s' in e for e in errors),errors
    staged=copy.deepcopy(d)
    for asset in staged['assets']:
        if asset.get('status')=='present' and asset.get('path'):
            asset['path']=str((example.parent/asset['path']).resolve())
    for name in ('contact-sheet.png','frame-01.png','frame-02.png','frame-03.png'):
        (temp/name).write_bytes(b'test image asset')
    staged['workflow']['approval_status']='approved'
    staged['assets'] += [
        {'id':'contact_sheet','kind':'storyboard','path':'contact-sheet.png','source':'generated','status':'present','description':'Ordered contact sheet'},
        {'id':'frame_01','kind':'storyboard','path':'frame-01.png','source':'generated','status':'present','description':'Kitchen setup'},
        {'id':'frame_02','kind':'storyboard','path':'frame-02.png','source':'generated','status':'present','description':'Cat enters'},
        {'id':'frame_03','kind':'storyboard','path':'frame-03.png','source':'generated','status':'present','description':'Plate falls'},
    ]
    staged['workflow'].update({
        'storyboard_preview_authorized':True,
        'storyboard_preview_status':'awaiting_review',
        'storyboard_preview_asset_id':'contact_sheet',
        'storyboard_images_authorized':False,
        'storyboard_images_status':'not_started',
    })
    staged['scenes'][0]['visual']['storyboard_panels']=[
        {'id':'panel_01','description':'Kitchen setup','image_asset_id':None}
    ]
    staged['scenes'][2]['visual']['storyboard_panels']=[
        {'id':'panel_02','description':'Cat enters','image_asset_id':None},
        {'id':'panel_03','description':'Plate falls','image_asset_id':None},
    ]
    pending=temp/'pending.json'
    pending.write_text(json.dumps(staged,ensure_ascii=False),encoding='utf-8')
    errors,_=check_file(pending,schema)
    assert not errors,errors
    legacy_complete=copy.deepcopy(staged)
    legacy_complete['workflow']['storyboard_preview_status']='approved'
    legacy_complete['workflow']['storyboard_images_authorized']=True
    legacy_complete['workflow']['storyboard_images_status']='generated'
    legacy_complete['scenes'][0]['visual']['storyboard_panels'][0]['image_asset_id']='frame_01'
    legacy_complete['scenes'][0]['visual']['storyboard_asset_ids']=['frame_01']
    legacy_complete['scenes'][2]['visual']['storyboard_panels'][0]['image_asset_id']='frame_02'
    legacy_complete['scenes'][2]['visual']['storyboard_panels'][1]['image_asset_id']='frame_03'
    legacy_complete['scenes'][2]['visual']['storyboard_asset_ids']=['frame_02','frame_03']
    legacy_path=temp/'legacy-complete.json'
    legacy_path.write_text(json.dumps(legacy_complete,ensure_ascii=False),encoding='utf-8')
    errors,_=check_file(legacy_path,schema)
    assert not errors,errors
    html_preview=render_html(staged,temp)
    md_preview=render_markdown(staged,temp)
    assert 'src="contact-sheet.png"' in html_preview
    assert 'class="asset-status planned"' in html_preview and 'Kitchen setup' in html_preview
    assert 'contact-sheet.png' in md_preview and 'awaiting_review' in md_preview
    # Old panel records remain valid without the new optional prompt/reference fields.
    referenced=copy.deepcopy(staged)
    referenced['scenes'][0]['visual']['storyboard_panels'][0].update({
        'reference_asset_ids':['bottle'],
        'image_prompt':'English image prompt. Ref bottle: preserve the exact cleaner bottle and label.',
    })
    referenced['scenes'][2]['visual']['storyboard_panels'][0]['image_prompt']='English image prompt. No reference image is attached; follow the written cat entrance description.'
    referenced['scenes'][2]['visual']['storyboard_panels'][1]['image_prompt']='English image prompt. No reference image is attached; show the plate falling as described.'
    ref_pending=temp/'ref-pending.json'
    ref_pending.write_text(json.dumps(referenced,ensure_ascii=False),encoding='utf-8')
    errors,_=check_file(ref_pending,schema)
    assert not errors,errors
    ref_html=render_html(referenced,temp)
    ref_md=render_markdown(referenced,temp)
    assert_editorial_html(ref_html,referenced['scenes'])
    assert 'AI Image Prompt' in ref_html and 'aria-label="Reference assets"' in ref_html and 'data-copy-label="Copy Image Prompt"' in ref_html
    assert 'English image prompt. Ref bottle' in ref_html and 'bottle <span>· product</span>' in ref_html
    assert 'AI Image Prompt' in ref_md and 'Reference assets:** bottle' in ref_md
    bad=copy.deepcopy(referenced)
    bad['scenes'][0]['visual']['storyboard_panels'][0]['reference_asset_ids']=['unknown_ref']
    invalid_ref=ref_pending.with_name('invalid-ref.json')
    invalid_ref.write_text(json.dumps(bad,ensure_ascii=False),encoding='utf-8')
    errors,_=check_file(invalid_ref,schema)
    assert any('unknown source asset: unknown_ref' in e for e in errors),errors
    bad=copy.deepcopy(staged)
    bad['workflow']['storyboard_images_authorized']=True
    unauthorized=pending.with_name('unauthorized.json')
    unauthorized.write_text(json.dumps(bad,ensure_ascii=False),encoding='utf-8')
    errors,_=check_file(unauthorized,schema)
    assert any('approved storyboard preview' in e for e in errors),errors
    complete=copy.deepcopy(referenced)
    complete['workflow']['storyboard_preview_status']='approved'
    complete['workflow']['storyboard_images_authorized']=True
    complete['workflow']['storyboard_images_status']='generated'
    complete['scenes'][0]['visual']['storyboard_panels'][0]['image_asset_id']='frame_01'
    complete['scenes'][0]['visual']['storyboard_asset_ids']=['frame_01']
    complete['scenes'][2]['visual']['storyboard_panels'][0]['image_asset_id']='frame_02'
    complete['scenes'][2]['visual']['storyboard_panels'][1]['image_asset_id']='frame_03'
    complete['scenes'][2]['visual']['storyboard_asset_ids']=['frame_02','frame_03']
    completed=temp/'completed.json'
    completed.write_text(json.dumps(complete,ensure_ascii=False),encoding='utf-8')
    errors,_=check_file(completed,schema)
    assert not errors,errors
    completed_html=render_html(complete,temp)
    completed_md=render_markdown(complete,temp)
    assert all(name in completed_html for name in ('contact-sheet.png','frame-01.png','frame-02.png','frame-03.png'))
    assert all(name in completed_md for name in ('contact-sheet.png','frame-01.png','frame-02.png','frame-03.png'))
    bad=copy.deepcopy(complete)
    bad['scenes'][2]['visual']['storyboard_panels'][1]['image_asset_id']=None
    path=temp/'incomplete.json';path.write_text(json.dumps(bad,ensure_ascii=False),encoding='utf-8')
    errors,_=check_file(path,schema)
    assert any('missing a full image' in e for e in errors),errors
print('PASS: example, staged storyboard gates, HTML/Markdown and validation cases')
