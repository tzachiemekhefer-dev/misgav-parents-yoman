"""Builds dist/ from template.html, site.json and data.json: one page per entry in site.json
(index.html for parents, staff/index.html for staff) plus dist/img/. Run fetch_data.py first."""
import html
import json
import pathlib
import shutil

ROOT = pathlib.Path(__file__).resolve().parent
DIST = ROOT / 'dist'
site = json.loads((ROOT / 'site.json').read_text())
data = json.loads((ROOT / 'data.json').read_text())
template = (ROOT / 'template.html').read_text()

shutil.rmtree(DIST, ignore_errors=True)
shutil.copytree(ROOT / 'img', DIST / 'img', ignore=shutil.ignore_patterns('CREDITS.txt'))
for page in site['pages']:
    page_data = {'generatedAt': data['generatedAt'], 'calendar': page['calendar'], 'events': data['pages'][page['path']]}
    page_cfg = {k: page[k] for k in ('store', 'cats')}
    out = (template
           .replace('__TITLE__', html.escape(page['title']))
           .replace('__DESCRIPTION__', html.escape(page['description']))
           .replace('__ROBOTS__', '<meta name="robots" content="noindex, nofollow">' if page['noindex'] else '')
           .replace('__H1__', page['h1'])
           .replace('__INTRO__', html.escape(page['intro']))
           .replace('__NOTIFY__', page['notify'])
           .replace('__PAGE_URL__', site['siteUrl'] + page['path'])
           .replace('__SITE_URL__', site['siteUrl'])
           .replace('__HERO_POS__', page['heroPos'])
           .replace('__HERO__', page['hero'])
           .replace('__ROOT__', '../' * page['path'].count('/'))
           .replace('__PAGE__', json.dumps(page_cfg, ensure_ascii=False))
           .replace('__DATA__', json.dumps(page_data, ensure_ascii=False)))
    target = DIST / page['path'] / 'index.html'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(out)
    print(target.relative_to(ROOT), len(out), 'bytes,', len(page_data['events']), 'events')
