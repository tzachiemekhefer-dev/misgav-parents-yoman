"""Mirrors the sheet "יומן משפז משגב" into the two public calendars.

Each row goes to the calendar named in its יומן column (הורים משגב or צוות משגב). Only events this script created (tag source=gantt-tashpaz) are touched: missing ones
are added, changed ones updated, rows that left the sheet (or the parents' calendar) deleted.

    python3 tools/sync_calendars.py            # show what would change
    python3 tools/sync_calendars.py --apply    # do it

Acts as tzachi.emek.hefer@gmail.com (token outside the repo, see README).
"""
import datetime as dt
import sys

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

TOKEN = '/home/am/.config/secrets/tzachi.emek.hefer@gmail.com/google/token.json'
SHEET = '1fkQP7x0A0EV-gstjc_oy2_ArF9QKMv7FBotPRLpKLNU'
CALENDARS = {
    'הורים משגב': 'cd5d688778e1a2d1446de86c2049401996c2a4c85cf62029ca814053b19abc82@group.calendar.google.com',
    'צוות משגב': '329440dca224a5c0244fd9bd3358e1d0deeeaa5ebe009a0c9607420491645fa5@group.calendar.google.com',
}
TAG = {'source': 'gantt-tashpaz'}
SHEETS_EPOCH = dt.date(1899, 12, 30)

creds = Credentials.from_authorized_user_file(TOKEN)
creds.refresh(Request())
sheets = build('sheets', 'v4', credentials=creds, cache_discovery=False)
cal = build('calendar', 'v3', credentials=creds, cache_discovery=False)


def sheet_events():
    rows = sheets.spreadsheets().values().get(spreadsheetId=SHEET, range='אירועים!A1:Z',
                                              valueRenderOption='UNFORMATTED_VALUE').execute()['values']
    head = rows[0]
    col = {name: head.index(name) for name in ['מתאריך', 'עד תאריך', 'אירוע', 'סוג', 'יומן', 'פירוט מהגאנט']}
    out = []
    for r in rows[1:]:
        r = r + [''] * (len(head) - len(r))
        if r[col['מתאריך']] == '' or not str(r[col['אירוע']]).strip():
            continue
        start = SHEETS_EPOCH + dt.timedelta(days=int(r[col['מתאריך']]))
        end = SHEETS_EPOCH + dt.timedelta(days=int(r[col['עד תאריך']] or r[col['מתאריך']]))
        desc = '\n'.join(p for p in [f"סוג: {r[col['סוג']]}" if r[col['סוג']] else '', str(r[col['פירוט מהגאנט']])] if p)
        out.append({'cal': str(r[col['יומן']]).strip(), 'summary': str(r[col['אירוע']]).strip(), 'description': desc,
                    'start': start.isoformat(), 'end': (end + dt.timedelta(days=1)).isoformat()})
    unknown = {e['cal'] for e in out} - set(CALENDARS)
    if unknown:
        sys.exit(f'unknown value in column יומן: {unknown}')
    return out


def key(e):
    return (e['start'], e['end'], e['summary'])


def calendar_events(cid):
    items, page = [], None
    while True:
        r = cal.events().list(calendarId=cid, pageToken=page, maxResults=2500,
                              privateExtendedProperty='source=gantt-tashpaz').execute()
        items += r['items']
        page = r.get('nextPageToken')
        if not page:
            return {(i['start']['date'], i['end']['date'], i['summary']): i for i in items}


def main(apply):
    rows = sheet_events()
    wanted = {name: [e for e in rows if e['cal'] == name] for name in CALENDARS}
    for name, cid in CALENDARS.items():
        want = {key(e): e for e in wanted[name]}
        have = calendar_events(cid)
        add = [want[k] for k in want if k not in have]
        drop = [have[k] for k in have if k not in want]
        upd = [(have[k], want[k]) for k in want if k in have and have[k].get('description', '') != want[k]['description']]
        print(f'{name}: {len(want)} in sheet, {len(have)} in calendar -> +{len(add)} -{len(drop)} ~{len(upd)}')
        for e in add:
            print('   +', e['start'], e['summary'])
        for e in drop:
            print('   -', e['start']['date'], e['summary'])
        for old, _ in upd:
            print('   ~', old['start']['date'], old['summary'])
        if not apply:
            continue
        for e in add:
            cal.events().insert(calendarId=cid, sendUpdates='none', body={
                'summary': e['summary'], 'description': e['description'], 'start': {'date': e['start']},
                'end': {'date': e['end']}, 'transparency': 'transparent',
                'extendedProperties': {'private': TAG}}).execute()
        for e in drop:
            cal.events().delete(calendarId=cid, eventId=e['id'], sendUpdates='none').execute()
        for old, new in upd:
            cal.events().patch(calendarId=cid, eventId=old['id'], sendUpdates='none',
                               body={'description': new['description']}).execute()
    if not apply:
        print('\ndry run - rerun with --apply to make these changes')


main('--apply' in sys.argv)
