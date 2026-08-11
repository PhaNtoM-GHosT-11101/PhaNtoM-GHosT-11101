#!/usr/bin/env python3
"""Generate Tokyo Night contribution stats SVGs from the GitHub GraphQL API.

Outputs:
  assets/streak.svg         - current streak, longest streak, total contributions
  assets/contributions.svg  - GitHub-style contribution heatmap

Runs as a GitHub Action (`update-activity.yml`) but works anywhere with a
GITHUB_TOKEN that can read the repo owner's public data.
"""

import datetime
import json
import os
import sys
import urllib.request

USER = os.environ.get("GH_USER", "PhaNtoM-GHosT-11101")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
OUT_DIR = os.environ.get("OUT_DIR", "assets")

# Tokyo Night palette
BG = "#0D1117"
BORDER = "#3b4261"
TEXT = "#a9b1d6"
DIM = "#565f89"
PURPLE = "#7aa2f7"
ORANGE = "#ff9e64"
LEVELS = ["#16161e", "#2b3a67", "#3d5392", "#5c77c4", "#7aa2f7"]

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            contributionCount
            date
          }
        }
      }
    }
  }
}
"""

FONT = "Verdana, 'Segoe UI', Helvetica, Arial, sans-serif"


def fetch_calendar():
    if not TOKEN:
        raise RuntimeError("GITHUB_TOKEN not set")
    body = json.dumps({"query": QUERY, "variables": {"login": USER}}).encode()
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=body,
        headers={
            "Authorization": "Bearer %s" % TOKEN,
            "Content-Type": "application/json",
            "User-Agent": "activity-stats",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.load(resp)
    if "errors" in data:
        raise RuntimeError(data["errors"][0]["message"])
    cal = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    days = {}
    for week in cal["weeks"]:
        for d in week["contributionDays"]:
            days[d["date"]] = d["contributionCount"]
    return cal["totalContributions"], days


def compute_streaks(days):
    dates = sorted(days)
    if not dates:
        return 0, 0
    longest = run = 0
    prev = None
    for date in dates:
        d = datetime.date.fromisoformat(date)
        if prev is not None and (d - prev).days != 1:
            run = 0
        prev = d
        if days[date] > 0:
            run += 1
            longest = max(longest, run)
        else:
            run = 0

    active = [datetime.date.fromisoformat(d) for d in dates if days[d] > 0]
    if not active:
        return 0, longest
    today = datetime.date.today()
    if (today - active[-1]).days > 1:
        return 0, longest
    current = 1
    prev = active[-1]
    for d in reversed(active[:-1]):
        if (prev - d).days == 1:
            current += 1
            prev = d
        else:
            break
    return current, longest


def cell_rect(x, y, size, gap, fill, radius=2):
    return (
        '<rect x="%.1f" y="%.1f" width="%d" height="%d" rx="%d" fill="%s"/>'
        % (x, y, size, size, radius, fill)
    )


def heatmap_grid(days):
    dates = sorted(days)
    if not dates:
        return []
    first = datetime.date.fromisoformat(dates[0])
    start = first - datetime.timedelta(days=first.weekday())
    cols = []
    for w in range(53):
        week_start = start + datetime.timedelta(weeks=w)
        col = []
        for i in range(7):
            d = week_start + datetime.timedelta(days=i)
            col.append((d, days.get(d.isoformat(), 0)))
        cols.append(col)
    return cols, start


def level(count):
    if count <= 0:
        return 0
    if count == 1:
        return 1
    if count == 2:
        return 2
    if count <= 5:
        return 3
    return 4


def render_heatmap(days, total):
    size, gap = 10, 3
    cols, start = heatmap_grid(days)
    width = len(cols) * (size + gap) - gap

    parts = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d 124" font-family="%s">' % (width + 140, FONT)]
    # month labels
    prev_month = None
    for ci, col in enumerate(cols):
        d, _ = col[0]
        m = d.month
        if m != prev_month and ci * (size + gap) < len(cols) * (size + gap) - gap:
            x = 0.0 + ci * (size + gap)
            parts.append(
                '<text x="%.1f" y="12" font-size="8" fill="%s">%s</text>'
                % (x, DIM, datetime.date(2000, m, 1).strftime("%b").upper())
            )
            prev_month = m
    # day cells
    y0 = 20
    for ci, col in enumerate(cols):
        for ri, (_, count) in enumerate(col):
            x = 0.0 + ci * (size + gap)
            y = y0 + ri * (size + gap)
            parts.append(cell_rect(x, y, size, gap, LEVELS[level(count)]))
    # legend
    lx = 0
    ly = y0 + 7 * size + 3 * 7 + 12 + 2
    parts.append('<text x="%.1f" y="%.1f" font-size="9" fill="%s">LESS</text>' % (lx, ly, DIM))
    lx += 30
    for l in range(5):
        parts.append(cell_rect(lx, ly - 8, size, gap, LEVELS[l]))
        lx += size + gap
    parts.append('<text x="%.1f" y="%.1f" font-size="9" fill="%s">MORE</text>' % (lx, ly, DIM))
    parts.append("</svg>")
    return "".join(parts)


def render_streak(current, longest, total, data_start, data_end):
    w, h = 495, 175
    cx = [w / 6, w / 2, 5 * w / 6]
    labels = ["CURRENT STREAK", "LONGEST STREAK", "TOTAL CONTRIBUTIONS"]
    values = ["%d days" % current, "%d days" % longest, "%d" % total]

    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" font-family="%s">' % (w, h, FONT),
        '<rect x="1" y="1" width="%d" height="%d" rx="6" fill="%s" stroke="%s" stroke-width="1"/>'
        % (w - 2, h - 2, BG, BORDER),
    ]
    icons = ["\U0001F525", "\u26A1", "\U0001F4C8"]
    for i in range(3):
        parts.append(
            '<text x="%.1f" y="52" text-anchor="middle" font-size="13" fill="%s">%s</text>'
            % (cx[i], DIM, icons[i])
        )
        parts.append(
            '<text x="%.1f" y="70" text-anchor="middle" font-size="11" letter-spacing="1" fill="%s">%s</text>'
            % (cx[i], DIM, labels[i])
        )
        color = ORANGE if i == 0 else (PURPLE if i == 1 else PURPLE)
        parts.append(
            '<text x="%.1f" y="100" text-anchor="middle" font-size="24" font-weight="bold" fill="%s">%s</text>'
            % (cx[i], color, values[i])
        )
    parts.append(
        '<text x="%.1f" y="%d" text-anchor="middle" font-size="10" fill="%s">%s \u2013 %s</text>'
        % (w / 2, h - 14, DIM, data_start, data_end)
    )
    parts.append("</svg>")
    return "".join(parts)


def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def main():
    try:
        total, days = fetch_calendar()
    except Exception as e:
        msg = "stats unavailable \u2014 GitHub API error"
        err = (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 495 175" font-family="%s">'
            '<rect x="1" y="1" width="493" height="173" rx="6" fill="%s" stroke="%s" stroke-width="1"/>'
            '<text x="247" y="85" text-anchor="middle" font-size="14" fill="%s">%s</text>'
            '<text x="247" y="108" text-anchor="middle" font-size="10" fill="%s">%s</text>'
            "</svg>"
            % (FONT, BG, BORDER, ORANGE, msg, DIM, str(e)[:80])
        )
        write(os.path.join(OUT_DIR, "streak.svg"), err)
        write(os.path.join(OUT_DIR, "contributions.svg"), err)
        print("error: %s" % e, file=sys.stderr)
        sys.exit(1)

    current, longest = compute_streaks(days)
    dates = sorted(days)
    start = datetime.date.fromisoformat(dates[0])
    end = dates[-1] and datetime.date.fromisoformat(dates[-1])
    fmt = "%b %d, %Y"
    write(
        os.path.join(OUT_DIR, "streak.svg"),
        render_streak(current, longest, total, start.strftime(fmt), end.strftime(fmt)),
    )
    write(
        os.path.join(OUT_DIR, "contributions.svg"),
        render_heatmap(days, total),
    )
    print(
        "ok: streak=%d longest=%d total=%d (%s .. %s)"
        % (current, longest, total, start.isoformat(), end.isoformat())
    )


if __name__ == "__main__":
    main()