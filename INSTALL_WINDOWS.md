# Install CineSheet for Codex (Windows 11)

The ZIP contains **one** standalone Agent Skill. It does not install video models or automation servers.

## Install for your Windows user account

1. Unzip `CineSheet_AI_Video_Production_Skill_v1.0.zip` somewhere temporary. Inside, find `cinesheet-video-production`.
2. In PowerShell, copy the folder:

```powershell
$dest = Join-Path $HOME '.agents\skills\cinesheet-video-production'
New-Item -ItemType Directory -Force (Split-Path $dest) | Out-Null
Copy-Item -Recurse -Force '.\cinesheet-video-production' $dest
py -m pip install 'jsonschema>=4.18,<5'
```

3. Restart Codex if it does not auto-detect new skills. In Codex, type `$cinesheet-video-production` followed by your production brief. The current Codex docs also support repository-scoped install in `.agents/skills/cinesheet-video-production`.

## Example test

```powershell
cd "$HOME\.agents\skills\cinesheet-video-production"
py scripts\validate_production.py examples\naturgenic-ugc.json
py scripts\render_sheet.py examples\naturgenic-ugc.json --out naturgenic-preview.html
start naturgenic-preview.html
```

If `py` is unavailable, install Python 3.10+ and use `python`. You do not have to install this on the same device that runs AI video generation. `production.json` is the handoff to future agents.

**Files are not automatically installed on your machine by downloading this ZIP.**
