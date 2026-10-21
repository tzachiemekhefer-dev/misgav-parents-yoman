"""Fetches each page's calendar (public iCal feed) into data.json. No credentials needed."""
import datetime as dt
import json
import pathlib
import re
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent
PAGES = json.loads((ROOT / 'site.json').read_text())['pages']


def unfold(text):
    # RFC 5545: a line starting with a space or tab continues the previous one
    return re.sub(r'\r?\n[ \t]', '', text).splitlines()


def unescape(v):
    return re.sub(r'\\([\\;,nN])', lambda m: '\n' if m.group(1) in 'nN' else m.group(1), v)


def ddmmyyyy(d):
    return d.strftime('%d/%m/%Y')


def fetch(cal_id):
    url = f"https://calendar.google.com/calendar/ical/{urllib.parse.quote(cal_id)}/public/basic.ics"
    with urllib.request.urlopen(url, timeout=60) as r:
        lines = unfold(r.read().decode('utf-8'))
    events, cur = [], None
    for line in lines:
        if line == 'BEGIN:VEVENT':
            cur = {}
        elif line == 'END:VEVENT':
            events.append(cur)
            cur = None
        elif cur is not None and ':' in line:
            name, value = line.split(':', 1)
            cur[name.split(';')[0]] = unescape(value)
    out = []
    for e in events:
        # all-day events only: DTSTART/DTEND are YYYYMMDD and DTEND is exclusive
        start = dt.datetime.strptime(e['DTSTART'][:8], '%Y%m%d').date()
        end = dt.datetime.strptime(e['DTEND'][:8], '%Y%m%d').date() - dt.timedelta(days=1)
        desc = e.get('DESCRIPTION', '').splitlines()
        cat = next((l.split(':', 1)[1].strip() for l in desc if l.startswith('סוג:')), '')
        details = '\n'.join(l for l in desc if not l.startswith('סוג:')).strip().replace('; ', '\n')
        out.append({'start': ddmmyyyy(start), 'end': ddmmyyyy(end), 'title': e.get('SUMMARY', ''), 'cat': cat, 'details': details})
    out.sort(key=lambda x: (x['start'][6:] + x['start'][3:5] + x['start'][:2], x['title']))
    assert out, f'calendar feed returned no events: {cal_id}'
    return out


data = {'generatedAt': dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds'), 'pages': {}}
for page in PAGES:
    data['pages'][page['path']] = fetch(page['calendar']['id'])
    print(f"{page['calendar']['name']}: {len(data['pages'][page['path']])} events")
(ROOT / 'data.json').write_text(json.dumps(data, ensure_ascii=False, indent=1))
print('data.json:', data['generatedAt'])
