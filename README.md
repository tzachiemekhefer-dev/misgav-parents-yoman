# יומן משגב — school year calendar: sheet → calendars → parents' and staff pages

The year plan of בית הספר משגב (תשפ״ז) kept in **one Google Sheet**, mirrored to **two public Google Calendars**,
and shown on two web pages built from one template:

- Parents: https://tzachiemekhefer-dev.github.io/misgav-parents-yoman/
- Staff: https://tzachiemekhefer-dev.github.io/misgav-parents-yoman/staff/ (not linked from the parents' page; `noindex`)

```
Google Sheet "יומן משפז משגב"  --tools/sync_calendars.py-->  הורים משגב / צוות משגב (public calendars)
                                                                  |
                                     public iCal feeds of both calendars
                                                                  v
                                   site/fetch_data.py + build.py --> GitHub Pages (daily + on push)
```

| Part | Where |
|---|---|
| Sheet | Drive of tzachi.emek.hefer@gmail.com, folder מזכירות: "יומן משפז משגב", tab אירועים |
| Calendars | Google Calendar of tzachi.emek.hefer@gmail.com: **הורים משגב** (parents), **צוות משגב** (staff) |
| Pages | [`site/`](site/) (`/` parents, `/staff/` staff), published by [`.github/workflows/pages.yml`](.github/workflows/pages.yml) |

Source of the data: the school's gantt PDF "לוח גאנט משגב תשפז" (Canva), emailed by the school office.

## The sheet

Columns: מתאריך · עד תאריך · יום · מס׳ ימים · אירוע · סוג · **יומן** · פירוט מהגאנט.

- **יומן** decides who sees the row: `הורים משגב` rows go to the parents' calendar and page; `צוות משגב` rows
  (staff meetings, pedagogical weeks) go to the staff calendar. Each row is in exactly one calendar.
- **סוג** is the event type; it colours the row and is the filter on the parents' page
  (חופשה / חג, טיול, אירוע / פעילות, מפגשי הורים, יום זיכרון / ציון, צוות, פדגוגיות).
- One row per event; a multi-day vacation is one row (weekends inside it included).

## Updating the calendars after editing the sheet

```bash
python3 tools/sync_calendars.py            # dry run: lists what would be added / removed / updated
python3 tools/sync_calendars.py --apply
```

It only touches events it created (private tag `source=gantt-tashpaz`). Needs the Google token of
tzachi.emek.hefer@gmail.com at `~/.config/secrets/tzachi.emek.hefer@gmail.com/google/token.json` (outside the repo).

## The page (`site/`)

| File | Role |
|---|---|
| `site.json` | Site URL and one entry per page: path, calendar, texts, filter chips (event types) |
| `fetch_data.py` | Downloads each page's calendar (public iCal feed) into `data.json` (no credentials) |
| `build.py` | Fills `template.html` per page → `dist/index.html`, `dist/staff/index.html` + `dist/img/` |
| `template.html` | The whole page (Hebrew, RTL, mobile-first, light/dark), based on the נוער חלח״צ page |
| `img/` | `logo-misgav.png` (from the gantt PDF), `hero.jpg` (Pexels); sources in `img/CREDITS.txt` |

Shows: a countdown to the next event, filter chips per event type (remembered per device), the current month in full
and later months as collapsible cards, "add to my calendar" per event, and subscribe buttons (Google / iPhone).

```bash
cd site && python3 fetch_data.py && python3 build.py   # then open site/dist/index.html or site/dist/staff/index.html
```

The workflow rebuilds on every push to `main`, daily at 06:17 Israel time, and on demand. The page is a snapshot of
the calendars at build time, so a calendar change reaches the page with the next daily build (or run the workflow).

## Accounts

Google: tzachi.emek.hefer@gmail.com only. GitHub: tzachiemekhefer-dev only (not the machine's default gh account).
The repo contains no secrets.
