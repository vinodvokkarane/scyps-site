#!/usr/bin/env python3
"""Record GitHub's traffic figures for the site's repository so they outlive GitHub's 14-day window.

GitHub keeps two weeks of views and unique visitors. Run every two weeks from the workflow, this
appends each day's figures to traffic.json and keeps a monthly roll-up the annual report can quote.

Needs GITHUB_TOKEN (provided automatically in Actions) and GITHUB_REPOSITORY (owner/repo).
"""
import json, os, sys, urllib.request, urllib.error, datetime, collections

repo = os.environ.get("GITHUB_REPOSITORY", "")
# Traffic needs the repository's Administration: read permission. The token Actions issues to every
# workflow (GITHUB_TOKEN) cannot be given that permission, so this uses a fine-grained personal token
# stored as the TRAFFIC_TOKEN secret. See README, "Traffic snapshot".
token = os.environ.get("TRAFFIC_TOKEN", "").strip()
if not repo:
    sys.exit("GITHUB_REPOSITORY is required")
if not token:
    sys.exit("TRAFFIC_TOKEN is not set. Create a fine-grained token with Administration: Read-only on this "
             "repository and store it as the TRAFFIC_TOKEN secret (README, Traffic snapshot).")
HERE = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(HERE, "traffic.json")
data = json.load(open(path)) if os.path.exists(path) else {"days": {}, "months": {}, "popular": {}}

def get(what):
    req = urllib.request.Request(f"https://api.github.com/repos/{repo}/traffic/{what}",
                                 headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json",
                                          "X-GitHub-Api-Version": "2022-11-28",
                                          "User-Agent": "scyps-traffic/1.0 (+https://smartcyberphysical.org)"})
    try:
        return json.loads(urllib.request.urlopen(req, timeout=60).read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "ignore")
        sys.exit(f"GitHub refused the traffic request ({e.code}). Its message: {detail}\n"
                 "403 means the token lacks Administration: Read-only on this repository, or has expired. "
                 "401 means the token is wrong or revoked.")

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
