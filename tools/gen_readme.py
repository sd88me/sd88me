#!/usr/bin/env python3
"""Regenerates README.md from the plugin catalog and the community-signals counts.

Run by .github/workflows/update-readme.yml every night. Categories and all static text live in this file,
so edit them here, not in README.md (it is overwritten).

  python3 tools/gen_readme.py                       # fetch live data
  python3 tools/gen_readme.py --catalog c.json --counts n.json --out /tmp/README.md   # offline
"""
import argparse, json, os, re, sys, urllib.request

ap = argparse.ArgumentParser()
ap.add_argument('--catalog'); ap.add_argument('--counts'); ap.add_argument('--out')
args = ap.parse_args()
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = args.out or os.path.join(ROOT, 'README.md')

CATALOG_URLS = [  # first that works wins; the sd88me copy is the old mirror, kept only as a fallback
    'https://open-mpc.github.io/catalog.json',
    'https://raw.githubusercontent.com/sd88me/sd88me.github.io/main/mpc-vst-plugins/catalog.json',
]
COUNTS_URL = 'https://openmpc-signals.open-mpc.workers.dev/api/counts'

def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'sd88me-profile-readme'})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

def load_catalog():
    if args.catalog: return json.load(open(args.catalog))
    for u in CATALOG_URLS:
        try: return fetch(u)
        except Exception as e: print('catalog fetch failed:', u, e, file=sys.stderr)
    sys.exit('no catalog source reachable; leaving README unchanged')

def load_counts():
    """{plugin_id: {likes, working, ...}}; empty if the service is down (the page then shows a dash)."""
    try:
        c = json.load(open(args.counts)) if args.counts else fetch(COUNTS_URL)
        return c.get('counts', c)
    except Exception as e:
        print('counts unavailable, likes shown as a dash:', e, file=sys.stderr)
        return {}

d = load_catalog()
C = load_counts()

P={p['id']:p for p in d['plugins']}
SITE='https://open-mpc.github.io'
def short(s,n=140):
    s=re.sub(r'\s+',' ',s)
    first=s.split(': ')[0] if ': ' in s[:80] and len(s.split(': ')[0])>12 else s.split('. ')[0].rstrip('.')
    return (first if len(first)<=n else first[:n].rsplit(' ',1)[0]+'…')
def badge(repo):
    return (f'[![release](https://img.shields.io/github/v/release/{repo}?include_prereleases&label=&color=2b2f36&labelColor=2b2f36)]'
            f'(https://github.com/{repo}/releases/latest)')
def dl(i):
    n=P[i].get('downloads') or 0
    return f'{n/1000:.1f}k' if n>=1000 else str(n)
def likes(i):
    n = (C.get(i) or {}).get('likes')
    return '–' if n is None else f'♥ {n}'
def thumb(i):
    p=P[i]; u=p.get('screenshot')
    return f'<a href="{SITE}/p/{i}.html"><img src="{u}" width="120" alt="{p["name"]}"></a>' if u else ''
def table(ids,notes={}):
    rows=['| | Plugin | What it is | Type | Downloads | Likes | Latest |','|---|---|---|---|---|---|---|']
    for i in ids:
        p=P[i]
        rows.append(f"| {thumb(i)} | **[{p['name']}]({SITE}/p/{i}.html)** | {notes.get(i) or short(p['summary'])} | {p['kind']} | {dl(i)} | {likes(i)} | {badge(p['repo'])} |")
    return '\n'.join(rows)

orig=['acid','euclidier','maze-sequencer','maze-voice','lucky-dip','crate-digger','daemon','tr-mpc','tr-mpc-tap-fx','skipback','profit-5','profit-08','morpho-pe','sturm-tp','clementine-xt']
emu=['osirus','xenia','vavra','nodalred2x','welle','je8086','ms2kr','jv-880','machinemodule','monomodule','reverbicon-224']
sch=['tr-6w6','tr-8w8','tr-cw78','tr-9w9']
desk=['j106','model-72','acid-303','ottmpc','boris-granular','dexed-dx7']
aw=sorted(i for i in P if i.startswith('aw-'))
used=set(['daemon-listen']+orig+emu+desk+sch+aw+['machinemodule-gen2','machinemodule-tap-gen2','monomodule-fx-gen2','monomodule-one-gen2'])
mine=[i for i,p in P.items() if p['repo'].startswith('sd88me/')]
missing=[i for i in mine if i not in used]; 
new_section = ''
if missing:
    new_section = '## New\n\nJust added, not sorted into a section yet.\n\n' + table(missing) + '\n\n'
    print('NOT PLACED IN ANY SECTION (add to tools/gen_readme.py):', missing, file=sys.stderr)

awrows=['| | Collection | Effects inside | Downloads | Likes | Latest |','|---|---|---|---|---|---|']
for i in aw:
    p=P[i]; n=re.search(r'all (\d+)',p['summary'])
    awrows.append(f"| {thumb(i)} | **[{p['name'].replace('Airwindows Collection: ','')}]({SITE}/p/{i}.html)** | {n.group(1) if n else ''} | {dl(i)} | {likes(i)} | {badge(p['repo'])} |")

def schrow(name,mpc,desc):
    return f"| **[{name}](https://github.com/sd88me/schwung-{name.lower()})** | {desc} | {mpc} | {badge('sd88me/schwung-'+name.lower())} |"

total=sum(p.get('downloads') or 0 for p in P.values() if p['repo'].startswith('sd88me/'))
out=f'''<div align="center">

# sd88me

**Audio plugins, ports and add-ons for Akai MPC / Force, Schwung (Ableton Move) and desktop.**
Free, open source, and built on the machines they run on.

[![Plugin store](https://img.shields.io/badge/Plugin%20store-browse%20all-ff6a00?style=for-the-badge)]({SITE}/)
[![Install guide](https://img.shields.io/badge/How%20to-install-2b2f36?style=for-the-badge)]({SITE}/install.html)
[![Tips](https://img.shields.io/badge/Ko--fi-tip%20jar-ff5e5b?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/sd88me)

[Made by me](#made-by-me) · [Emulator ports](#emulator-ports) · [Schwung](#schwung) · [Other ports](#other-ports) · [Airwindows](#airwindows-collections) · [Tools](#add-ins--tools)

</div>

---

## Get them

Every plugin below has a release page, and the **Latest** badge always shows the current version. Browse, search and install from the **[plugin store]({SITE}/)** or follow the **[install guide]({SITE}/install.html)**. Plugin names link to their store page. Download counts and likes come from the plugin store ({total:,} in total across my plugins, as of {d['generated'][:10]}).

> Plugins that emulate hardware never ship ROMs or firmware. Where one needs ROM files, you supply your own.

## Made by me

Plugins I wrote for the MPC: sequencers, tools and instruments, many inspired by classic hardware. Credits for anything borrowed are on each plugin's page.

{table(orig)}

## Emulator ports

Existing emulator cores (gearmulator, MAME and others) brought to the MPC. The emulation is their work; I built the MPC integration and skins.

{table(emu)}

## Other ports

Open-source DSP from the desktop world, ported to the MPC with a new skin.

{table(desk)}

## Schwung

Modules for [Schwung](https://github.com/sd88me/schwung) on Ableton Move, and the other direction: Schwung modules ported over to the MPC.

### My Move modules

| Module | What it is | Also on MPC | Latest |
|---|---|---|---|
{schrow('acid','[Acid]({SITE}/p/acid.html)','TB-303-style acid sequencer')}
{schrow('maze','[Maze]({SITE}/p/maze-sequencer.html)','Generative sequencer and voice')}
{schrow('clementineXT','[Clementine-XT]({SITE}/p/clementine-xt.html)','Microwave II/XT wavetable synth')}
{schrow('model72','[Model-72]({SITE}/p/model-72.html)','Minimoog Model-D circuit model')}
{schrow('machinemodule','[Machinemodule]({SITE}/p/machinemodule.html)','Elektron Machinedrum sound engine')}
{schrow('kit-builder','—','Drum kit builder')}

### Schwung → MPC

Schwung modules by other authors ported to MPC / Force, with new skins.

{table(sch)}

{new_section}## Airwindows collections

All of [Airwindows](https://www.airwindows.com/), grouped by category: one plugin per collection, each with its own panel, Q-Link badges and built-in manual.

{chr(10).join(awrows)}

## Add-ins & tools

| Project | What it is | Latest |
|---|---|---|
| **[MPC-ForceLink](https://github.com/sd88me/MPC-ForceLink)** | — | {badge('sd88me/MPC-ForceLink')} |

<details>
<summary>Archived: original Force-only versions</summary>

These were the first Force builds and are now superseded by the MPC releases above:
[force-acid](https://github.com/sd88me/force-acid) ·
[force-cratedigger](https://github.com/sd88me/force-cratedigger) ·
[force-dx7](https://github.com/sd88me/force-dx7) ·
[force-jv880](https://github.com/sd88me/force-jv880) ·
[force-maze](https://github.com/sd88me/force-maze) ·
[force-kit-builder](https://github.com/sd88me/force-kit-builder) ·
[force-shadow](https://github.com/sd88me/force-shadow) ·
[force-audio-jack](https://github.com/sd88me/force-audio-jack) ·
[force-euclidier](https://github.com/sd88me/force-euclidier)

</details>

## Found a bug?

Open an issue on the plugin's repo (the **Latest** badge links straight to it) and include your device, MPC OS version and plugin version.

## Tips ☕🍺💐

Everything here is free and stays that way. If a plugin made your track better, a tip at [ko-fi.com/sd88me](https://ko-fi.com/sd88me) buys me a coffee, a beer, or (more importantly) flowers for my wife, for all the studio hours. [Read the full story](https://github.com/sd88me/.github/blob/main/TIPS.md).

---

<sub>Hardware names are trademarks of their respective owners and are used only to describe compatibility. No affiliation or endorsement implied.</sub>
'''
if not out.endswith('\n'): out += '\n'
open(OUT,'w').write(out)
