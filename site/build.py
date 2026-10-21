"""Builds dist/ (index.html + img/) from template.html and data.json. Run fetch_data.py first."""
import json
import pathlib
import shutil

ROOT = pathlib.Path(__file__).resolve().parent
DIST = ROOT / 'dist'
data = json.loads((ROOT / 'data.json').read_text())
site_url = json.loads((ROOT / 'site.json').read_text())['siteUrl']

html = ((ROOT / 'template.html').read_text()
        .replace('__DATA__', json.dumps(data, ensure_ascii=False))
        .replace('__SITE_URL__', site_url))
shutil.rmtree(DIST, ignore_errors=True)
shutil.copytree(ROOT / 'img', DIST / 'img', ignore=shutil.ignore_patterns('CREDITS.txt'))
(DIST / 'index.html').write_text(html)
print('dist/index.html', len(html), 'bytes,', len(data['events']), 'events')
