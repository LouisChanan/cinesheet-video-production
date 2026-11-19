#!/usr/bin/env python3
"""Validate CineSheet JSON schema and its semantic invariants. No external side effects."""
import argparse
import json
import sys
from pathlib import Path


def check_file(path: Path, schema_path: Path):
    errors=[];warnings=[]
    try:
        data=json.loads(path.read_text(encoding='utf-8'))
    except Exception as exc:
        return [f'Cannot parse JSON: {exc}'],warnings
    try:
        import jsonschema
    except ImportError:
        warnings.append('jsonschema not installed: full JSON Schema verification SKIPPED. Run pip install -r requirements.txt')
        jsonschema=None
    if jsonschema:
        try:
            schema=json.loads(schema_path.read_text(encoding='utf-8'))
            validator=jsonschema.Draft202012Validator(schema)
            for error in sorted(validator.iter_errors(data), key=lambda e:list(map(str,e.path))):
                errors.append('Schema /'+ '/'.join(map(str,error.path)) + ': ' + error.message)
        except Exception as exc:
            errors.append(f'Schema unavailable/invalid: {exc}')
    if not isinstance(data,dict):
        return errors+['Root value must be an object'],warnings
    project=data.get('project') or {}; scenes=data.get('scenes') or []
    total=project.get('duration_seconds'); elapsed=0; ids=set(); asset_ids=set(); char_ids=set()
    assets=data.get('assets') or []; chars=data.get('characters') or []; asset_by_id={}
    for a in assets:
        aid=a.get('id');
        if aid in asset_ids:errors.append(f'Duplicate asset ID: {aid}')
        asset_ids.add(aid)
        asset_by_id[aid]=a
        p=a.get('path'); status=a.get('status')
        if status=='present':
            if not p:errors.append(f'Asset {aid} marked present but path absent')
            elif not (path.parent/p).is_file():errors.append(f'Asset {aid} marked present but file does not exist: {p}')
        elif status in ('missing','planned'):
            warnings.append(f'Asset {aid} is {status}; don\'t claim generated/ready')
    for ch in chars:
        cid=ch.get('id')
        if cid in char_ids:errors.append(f'Duplicate character ID: {cid}')
        char_ids.add(cid)
        for aid in ch.get('reference_asset_ids',[]):
            if aid not in asset_ids:errors.append(f'Character {cid} references unknown asset {aid}')
    if not scenes:errors.append('No scenes supplied; draft template is not production-ready')
    storyboard_panel_ids=set()
    for index,s in enumerate(scenes,1):
        sid=s.get('id')
        if sid in ids:errors.append(f'Duplicate scene ID: {sid}')
        ids.add(sid)
        if s.get('sequence') !=index:errors.append(f'{sid} sequence must be {index}')
        if s.get('start_seconds')!=elapsed:errors.append(f'{sid} starts at {s.get("start_seconds")} but must start at {elapsed}')
        duration=s.get('duration_seconds')
        if not isinstance(duration,int) or duration<1:errors.append(f'{sid} invalid duration')
        else:elapsed+=duration
        for cid in s.get('continuity',{}).get('character_ids',[]):
            if cid not in char_ids:errors.append(f'{sid} references unknown character {cid}')
        for d in s.get('audio',{}).get('dialogue',[]):
            if d.get('speaker_id') not in char_ids:errors.append(f'{sid} speaker ID unknown: {d.get("speaker_id")}')
        for aid in s.get('video',{}).get('reference_asset_ids',[]):
            if aid not in asset_ids:errors.append(f'{sid} references unknown video asset: {aid}')
        visual=s.get('visual',{})
        for aid in visual.get('storyboard_asset_ids',[]):
            if aid not in asset_ids:
                errors.append(f'{sid} references unknown storyboard asset: {aid}')
            elif asset_by_id[aid].get('kind')!='storyboard':
                errors.append(f'{sid} storyboard reference is not kind=storyboard: {aid}')
        for panel in visual.get('storyboard_panels',[]):
            panel_id=panel.get('id')
            if panel_id in storyboard_panel_ids:errors.append(f'Duplicate storyboard panel ID: {panel_id}')
            storyboard_panel_ids.add(panel_id)
            for ref_id in panel.get('reference_asset_ids',[]):
                if ref_id not in asset_ids:errors.append(f'{sid} panel {panel_id} references unknown source asset: {ref_id}')
            aid=panel.get('image_asset_id')
            if aid is not None:
                if aid not in asset_ids:errors.append(f'{sid} panel {panel_id} references unknown storyboard asset: {aid}')
                elif asset_by_id[aid].get('kind')!='storyboard':errors.append(f'{sid} panel {panel_id} image is not kind=storyboard: {aid}')
        if s.get('video',{}).get('generation_status')=='completed':
            warnings.append(f'{sid}: generation_status=completed; verify actual output file outside this schema')
        if s.get('visual',{}).get('storyboard_status') in ('generated','approved'):
            warnings.append(f'{sid}: storyboard flagged generated/approved; verify actual frame or user approval')
    if total is not None and elapsed!=total:errors.append(f'All scenes total {elapsed}s, project duration {total}s')
    claim_ids=set()
    for c in data.get('product_claims',[]):
        cid=c.get('id')
        if cid in claim_ids:errors.append(f'Duplicate claim ID: {cid}')
        claim_ids.add(cid)
        if c.get('permitted_copy') and c.get('verification')!='verified':
            errors.append(f'Unverified claim cannot be permitted in advertising copy: {cid}')
        if c.get('verification')!='verified':warnings.append(f'Claim {cid} is {c.get("verification")}; exclude from copy until substantiated')
    workflow=data.get('workflow') or {}
    storyboard_state_keys={
        'storyboard_preview_authorized','storyboard_preview_status','storyboard_preview_asset_id',
        'storyboard_images_authorized','storyboard_images_status'
    }
    if storyboard_state_keys.intersection(workflow):
        preview_authorized=workflow.get('storyboard_preview_authorized',False)
        preview_status=workflow.get('storyboard_preview_status','not_started')
        preview_id=workflow.get('storyboard_preview_asset_id')
        images_authorized=workflow.get('storyboard_images_authorized',False)
        images_status=workflow.get('storyboard_images_status','not_started')
        if preview_authorized and workflow.get('approval_status')!='approved':
            errors.append('Storyboard preview authorization requires approved production sheet')
        if preview_status in ('awaiting_review','approved') and not preview_id:
            errors.append(f'Storyboard preview status={preview_status} requires storyboard_preview_asset_id')
        if preview_id:
            if preview_id not in asset_ids:
                errors.append(f'Unknown storyboard preview asset: {preview_id}')
            elif asset_by_id[preview_id].get('kind')!='storyboard':
                errors.append(f'Storyboard preview asset is not kind=storyboard: {preview_id}')
            elif preview_status in ('awaiting_review','approved') and asset_by_id[preview_id].get('status')!='present':
                errors.append(f'Storyboard preview asset must be present when status={preview_status}: {preview_id}')
        if preview_status in ('awaiting_review','approved','changes_requested') and not preview_authorized:
            errors.append(f'Storyboard preview status={preview_status} requires explicit preview authorization')
        if preview_status=='approved' and workflow.get('approval_status')!='approved':
            errors.append('Storyboard preview cannot be approved before the production sheet')
        if images_authorized and preview_status!='approved':
            errors.append('Full storyboard images require an approved storyboard preview')
        if images_status=='generated':
            if not images_authorized:errors.append('Generated storyboard images require explicit storyboard_images_authorized=true')
            if not storyboard_panel_ids:errors.append('Generated storyboard images require storyboard_panels')
            generated_panel_asset_ids=[]
            for s in scenes:
                panels=s.get('visual',{}).get('storyboard_panels',[])
                if not panels:continue
                panel_asset_ids=[panel.get('image_asset_id') for panel in panels]
                if any(aid is None for aid in panel_asset_ids):
                    errors.append(f'{s.get("id")} is missing a full image for one or more storyboard panels')
                    continue
                generated_panel_asset_ids.extend(panel_asset_ids)
                for aid in panel_asset_ids:
                    if aid in asset_ids and asset_by_id[aid].get('status')!='present':
                        errors.append(f'{s.get("id")} full storyboard image must be present: {aid}')
                    if aid==preview_id:
                        errors.append(f'{s.get("id")} cannot use the contact sheet as a full storyboard still: {aid}')
                if s.get('visual',{}).get('storyboard_asset_ids',[])!=panel_asset_ids:
                    errors.append(f'{s.get("id")} storyboard_asset_ids must match panel image assets in order')
            if len(generated_panel_asset_ids)!=len(set(generated_panel_asset_ids)):
                errors.append('Each storyboard panel must map to its own full image asset')
        if images_status=='declined' and images_authorized:
            errors.append('Declined storyboard image set cannot be authorized')
    if workflow.get('production_authorized'):
        warnings.append('production_authorized=true; this standalone skill STILL does not execute paid generation')
        if workflow.get('approval_status')!='approved':errors.append('Production authorization requires approved Sheet')
    return errors,warnings

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('production',type=Path)
    ap.add_argument('--schema',type=Path,default=Path(__file__).resolve().parents[1]/'schemas/production.schema.json')
    args=ap.parse_args()
    errors,warnings=check_file(args.production.resolve(),args.schema.resolve())
    for x in warnings:print('WARNING:',x)
    for x in errors:print('ERROR:',x)
    if errors:
        print(f'FAILED ({len(errors)} error(s), {len(warnings)} warning(s))')
        sys.exit(1)
    print(f'PASS: production JSON validated ({len(warnings)} warning(s))')
