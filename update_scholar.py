#!/usr/bin/env python3
"""Update the Google Scholar figures the site prints, without hand-editing build_site.py.

Google Scholar has no API and blocks automated readers, so the numbers have to come from the
profile pages themselves. Two ways to get them in:

1. Paste. Open each profile, copy the three numbers in the "Cited by" box (Citations, h-index,
   i10-index, the "All" column), and run:

       python3 update_scholar.py
       Vokkarane 5863 36 95
       Xie 6358 40 110
       <blank line to finish>

   First token is any unique part of the person's name; the rest are the numbers in profile order.
   Two numbers (citations and h-index) are enough; i10 is optional.

2. Scheduled. refresh.py tries to read the same pages weekly from GitHub Actions. Google often
   blocks datacenter addresses, so treat that as a bonus, not the plan.

Everything lands in scholar.json with the date it was entered, and the site prints that date.
"""
import json, os, re, sys, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
STORE = os.path.join(HERE, "scholar.json")

def known_names():
    src = open(os.path.join(HERE, "build_site.py"), encoding="utf-8").read()
    block = src[src.index("SCHOLAR = {"):src.index("ORCID = {")]
    return dict(re.findall(r'"([^"]+)":\s*"([A-Za-z0-9_\-]{12})"', block))

def match(token, names):
    t = token.lower().strip()
    hits = [n for n in names if t in n.lower()]
    if len(hits) == 1: return hits[0]
    if not hits: print(f"  no name matches '{token}'"); return None
    print(f"  '{token}' matches several: {', '.join(hits)}"); return None

def main():
    names = known_names()
    data = json.load(open(STORE)) if os.path.exists(STORE) else {}
    today = datetime.date.today().isoformat()
    print("Paste one line per person: <name> <citations> <h-index> [i10-index]. Blank line to finish.")
    print("Profiles:")
    for n, sid in sorted(names.items()):
        cur = data.get(n)
        state = (f"{cur['citations']:,} citations" + (f", h {cur['h']}" if cur.get('h') else ", h-index missing") + f" ({cur['date']})") if cur else "no figures yet"
        print(f"  {n:26s} https://scholar.google.com/citations?user={sid}&hl=en   [{state}]")
    print()
    changed = 0
    for line in sys.stdin:
        line = line.strip()
        if not line: break
        parts = line.replace(",", " ").split()
        nums = [p for p in parts if p.isdigit()]
        token = " ".join(p for p in parts if not p.isdigit())
        if len(nums) < 2 or not token:
            print("  expected: <name> <citations> <h-index> [i10]"); continue
        name = match(token, names)
        if not name: continue
        entry = {"citations": int(nums[0]), "h": int(nums[1]), "date": today}
        if len(nums) > 2: entry["i10"] = int(nums[2])
        data[name] = entry; changed += 1
        print(f"  {name}: {entry['citations']:,} citations, h {entry['h']}")
    if changed:
        json.dump(data, open(STORE, "w"), indent=1, sort_keys=True)
        print(f"\nwrote {STORE} ({changed} updated). Now run: python3 build_site.py index.html")
    else:
        print("\nnothing changed")

if __name__ == "__main__":
    main()
