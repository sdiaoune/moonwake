#!/usr/bin/env python3
"""Package tracked public files, never local saves or development artifacts."""
from pathlib import Path
import hashlib
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'release'
FORBIDDEN = {'build', '.git', '.venv', '.tools', 'backups', '__pycache__', 'release'}


def archive(path, files, extras=None):
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        entries = {str(p.relative_to(ROOT)): p.read_bytes() for p in files}
        entries.update(extras or {})
        for name, content in sorted(entries.items()):
            info = zipfile.ZipInfo('Moonwake/' + name, (2026, 10, 5, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            z.writestr(info, content, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def main():
    OUT.mkdir(exist_ok=True)
    paths = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).split(b'\0')
    files = [ROOT / p.decode() for p in paths if p]
    for p in files:
        rel = p.relative_to(ROOT)
        assert not any(part in FORBIDDEN for part in rel.parts), rel
        assert p.suffix not in ('.sav', '.state', '.pyc'), rel
        assert p.name != 'cartridge-install-status.json', rel
    assert (ROOT / 'LICENSE') in files and (ROOT / 'LICENSE-ASSETS') in files
    archive(OUT / 'Moonwake-Source.zip', files)
    play = []
    for p in files:
        parts = p.relative_to(ROOT).parts
        if len(parts) == 1 and p.name in ('README.md', 'LICENSE', 'LICENSE-ASSETS', 'THIRD_PARTY_NOTICES.md'):
            play.append(p)
        elif parts[0] == 'dist' or parts[:2] == ('assets', 'native'):
            play.append(p)
        elif parts[0] == 'docs' and parts[1] != 'audio':
            if parts[1] != 'screenshots' or p.name in ('title-native.png', 'moonwake-teaser.gif', 'teaser-manifest.json'):
                play.append(p)
    archive(OUT / 'Moonwake-Play.zip', play, {'START-HERE.md': (
        '# Welcome to Moonwake\n\n'
        'Load `dist/moonwake.gbc` in a Game Boy Color emulator or a compatible cartridge. '
        'Use FlashGBX for a compatible Chromatic cartridge.\n\n'
        'For the browser preview, run `python3 -m http.server 8000` inside this Moonwake folder, '
        'then open http://localhost:8000/docs/play.html.\n\n'
        'Arrows move; Z jumps; X dashes; Enter pauses; Shift retries. '
        'See `docs/player-guide.md` and the included license notices.\n\n'
        'Source and releases: https://github.com/sdiaoune/moonwake\n'
    ).encode()})
    rom = ROOT / 'dist/moonwake.gbc'
    (OUT / 'moonwake.gbc').write_bytes(rom.read_bytes())
    products = [OUT / n for n in ('moonwake.gbc', 'Moonwake-Play.zip', 'Moonwake-Source.zip')]
    sums = ''.join(hashlib.sha256(p.read_bytes()).hexdigest() + '  ' + p.name + '\n' for p in products)
    (OUT / 'SHA256SUMS.txt').write_text(sums)
    print(sums, end='')


if __name__ == '__main__':
    main()
