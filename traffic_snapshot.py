#!/usr/bin/env python3
"""Record GitHub's traffic figures for the site's repository so they outlive GitHub's 14-day window.

GitHub keeps two weeks of views and unique visitors. Run every two weeks from the workflow, this
appends each day's figures to traffic.json and keeps a monthly roll-up the annual report can quote.

Needs GITHUB_TOKEN (provided automatically in Actions) and GITHUB_REPOSITORY (owner/repo).
"""
import json, os, urllib.request, datetime, collections

repo = os.environ.get("GITHUB_REPOSITORY", "")
token = os.environ.get("GITHUB_TOKEN", "")
if not repo or not token:
    raise SystemExit("GITHUB_REPOSITORY and GITHUB_TOKEN are required")
HERE = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(HERE, "traffic.json")
data = json.load(open(path)) if os.path.exists(path) else {"days": {}, "months": {}, "popular": {}}

def get(what):
    req = urllib.request.Request(f"https://api.github.com/repos/{repo}/traffic/{what}",
                                 headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"})
    return json.loads(urllib.request.urlopen(req, timeout=60).read().decode("utf-8"))

views = get("views")
for d in views.get("views", []):
    day = d["timestamp"][:10]
    data["days"][day] = {"views": d["count"], "visitors": d["uniques"]}

# monthly roll-up: views sum; visitors are per-day uniques, so the month figure is the day-max
# (an honest floor: GitHub does not deduplicate visitors across days)
months = collections.defaultdict(lambda: {"views": 0, "visitors_peak_day": 0, "days_recorded": 0})
for day, v in sorted(data["days"].items()):
    m = months[day[:7]]
    m["views"] += v["views"]; m["visitors_peak_day"] = max(m["visitors_peak_day"], v["visitors"]); m["days_recorded"] += 1
data["months"] = dict(months)

pop = get("popular/paths")
data["popular"] = {datetime.date.today().isoformat(): [{"path": p["path"], "views": p["count"], "visitors": p["uniques"]} for p in pop[:10]]}
data["updated"] = datetime.date.today().isoformat()
json.dump(data, open(path, "w"), indent=1)
print(f"recorded {len(views.get('views', []))} days; {len(data['days'])} days on file; months: {list(data['months'])[-3:]}")
