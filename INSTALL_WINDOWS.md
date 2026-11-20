# Install CineSheet for Codex (Windows 11)

The repo contains one standalone Agent Skill. Use the folder containing `SKILL.md` as the install source.

## Install for your Windows user account

1. Open PowerShell in the cloned or extracted repo folder.
2. Copy the Skill files into the user Skill directory and install the Python dependency.

```powershell
$dest = Join-Path $HOME '.agents\skills\cinesheet-video-production'
New-Item -ItemType Directory -Force $dest | Out-Null
$skillFiles = @('SKILL.md', 'adapters', 'agents', 'examples', 'modules', 'references', 'schemas', 'scripts', 'templates', 'requirements.txt')
foreach ($entry in $skillFiles) {
    Copy-Item -Recurse -Force -Path $entry -Destination $dest
}
py -m pip install -r requirements.txt
```

3. Restart Codex if it does not auto-detect the skill. In Codex, type `$cinesheet-video-production` followed by your production brief. For a project installation, use the project's `.agents/skills/cinesheet-video-production` as the destination.

## Example test

```powershell
cd "$HOME\.agents\skills\cinesheet-video-production"
py scripts\validate_production.py examples\naturgenic-ugc.json
py scripts\render_sheet.py examples\naturgenic-ugc.json --out output\naturgenic-preview.html
Start-Process output\naturgenic-preview.html
```

If `py` is unavailable, install Python 3.10+ and use `python`. You do not have to install this on the same device that runs AI video generation. `production.json` is the handoff to future agents.

See the [repo quickstart](README.md) for creating a new production manifest.
