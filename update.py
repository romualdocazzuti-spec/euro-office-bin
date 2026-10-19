#!/usr/bin/env python3
"""Refresh the local PKGBUILD from GitHub; optionally build/install with paru."""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import urllib.request

ROOT = Path(__file__).resolve().parent
API = 'https://api.github.com/repos/Euro-Office/DesktopEditors/releases/latest'
BASE = 'https://github.com/Euro-Office/DesktopEditors/releases/download/'


def release_fields(release):
    if release.get('draft') or release.get('prerelease'):
        raise ValueError('La release deve essere stabile e pubblica.')
    tag = release['tag_name']
    if not re.fullmatch(r'v?\d+(?:\.\d+)+(?:-\d+)?', tag):
        raise ValueError(f'Formato versione non previsto: {tag!r}; controllare manualmente.')
    version = tag.removeprefix('v').replace('-', '.')
    assets = [a for a in release['assets'] if re.fullmatch(
        r'euro-office-euro-office_[0-9][0-9A-Za-z.+~_-]*_amd64\.deb', a['name'])]
    if len(assets) != 1:
        raise ValueError('La release non contiene esattamente un .deb amd64 del programma.')
    asset = assets[0]
    if asset['browser_download_url'] != f"{BASE}{tag}/{asset['name']}":
        raise ValueError('URL del pacchetto inatteso.')
    digest = asset.get('digest') or ''
    if not re.fullmatch(r'sha256:[0-9a-f]{64}', digest):
        raise ValueError('Checksum SHA-256 assente: aggiornamento interrotto.')
    return version, tag, asset['name'], digest.split(':')[1]


def replace_field(text, field, value):
    text, count = re.subn(rf'^{re.escape(field)}=.*$', lambda _: f'{field}={value}',
                          text, flags=re.MULTILINE)
    if count != 1:
        raise ValueError(f'Campo {field} assente o duplicato nel PKGBUILD.')
    return text


def refresh(text, fields):
    version, tag, asset, digest = fields
    old_version = re.search(r'^pkgver=(\S+)$', text, re.MULTILINE).group(1)
    comparison = int(subprocess.check_output(['vercmp', version, old_version], text=True))
    if comparison < 0:
        raise ValueError('La release latest è più vecchia del PKGBUILD: downgrade bloccato.')
    if comparison == 0:
        expected = {"_tag": f"'{tag}'", "_deb": f"'{asset}'",
                    'sha256sums': f"('{digest}')"}
        for field, value in expected.items():
            if not re.search(rf'^{re.escape(field)}={re.escape(value)}$', text, re.MULTILINE):
                raise ValueError('Asset o checksum cambiati a parità di versione: controllare manualmente.')
        return text
    for field, value in {'pkgver': version, 'pkgrel': '1', '_tag': f"'{tag}'",
                         '_deb': f"'{asset}'", 'sha256sums': f"('{digest}')"}.items():
        text = replace_field(text, field, value)
    return text


def cleanup(directory=ROOT):
    """Delete only known local build files, after confirming installation."""
    subprocess.run(['pacman', '-Q', 'euro-office-bin'],
                   check=True, stdout=subprocess.DEVNULL)
    patterns = (
        r'\.SRCINFO',
        r'euro-office-euro-office_[0-9][0-9A-Za-z.+~_-]*_amd64\.deb',
        r'euro-office-bin-[0-9][0-9A-Za-z.+~_-]*-x86_64\.pkg\.tar\.(?:zst|xz|gz)',
    )
    for path in sorted(directory.iterdir()):
        if (path.is_file() or path.is_symlink()) and any(
                re.fullmatch(pattern, path.name) for pattern in patterns):
            path.unlink()
            print(f'Eliminato residuo: {path.name}', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--install', action='store_true', help='Installa/aggiorna usando paru -Bi .')
    parser.add_argument('--clean', action='store_true',
                        help='Elimina soltanto i residui locali, senza accesso a GitHub')
    args = parser.parse_args()
    if os.geteuid() == 0:
        raise ValueError('Eseguire come utente normale, senza sudo.')
    if args.clean:
        cleanup()
        return
    request = urllib.request.Request(API, headers={
        'Accept': 'application/vnd.github+json', 'User-Agent': 'euro-office-local-pkgbuild'})
    with urllib.request.urlopen(request, timeout=45) as response:
        release = json.load(response)
    fields = release_fields(release)
    path = ROOT / 'PKGBUILD'
    original = path.read_text()
    updated = refresh(original, fields)
    if updated != original:
        temporary = path.with_name('PKGBUILD.tmp')
        temporary.write_text(updated)
        temporary.replace(path)
        print(f'PKGBUILD aggiornato alla release {fields[1]}.', flush=True)
    else:
        print(f'PKGBUILD già aggiornato: {fields[1]}.', flush=True)
    if args.install:
        pkgrel = re.search(r'^pkgrel=(\S+)$', updated, re.MULTILINE).group(1)
        target = f'{fields[0]}-{pkgrel}'
        installed = subprocess.run(['pacman', '-Q', 'euro-office-bin'],
                                   capture_output=True, text=True)
        if installed.returncode == 0:
            current = installed.stdout.split()[1]
            if int(subprocess.check_output(['vercmp', current, target], text=True)) >= 0:
                print(f'Già installata la versione {current}; nessuna ricostruzione necessaria.')
                cleanup()
                return
        subprocess.run(['paru', '-Bi', '.'], cwd=ROOT, check=True)
        installed = subprocess.check_output(['pacman', '-Q', 'euro-office-bin'], text=True)
        current = installed.split()[1]
        if int(subprocess.check_output(['vercmp', current, target], text=True)) < 0:
            raise ValueError('Versione richiesta non installata: residui conservati.')
        cleanup()
    else:
        print(f'Per installare e pulire: cd "{ROOT}" && python update.py --install')


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError, AttributeError,
            subprocess.CalledProcessError) as error:
        sys.exit(f'Errore: {error}')
