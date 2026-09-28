"""Build the storyboards for the center's videos from the site's own records.

Writes videos/<name>.html (the engine with the storyboard injected) and videos/index.json (name, format, duration).
Every number and sentence comes from the site's records or the verified research record."""
import json, os, re, sys, base64, importlib.util
HERE = "/home/claude/video"; SITE = "/home/claude/site-live"
sys.path.insert(0, SITE)
spec = importlib.util.spec_from_file_location("bs", SITE + "/build_site.py"); bs = importlib.util.module_from_spec(spec); sys.argv = ["x", "/tmp/none.html"]; spec.loader.exec_module(bs)
os.makedirs(HERE + "/videos", exist_ok=True); os.makedirs(HERE + "/assets/nodes", exist_ok=True)
ENGINE = open(HERE + "/engine.html", encoding="utf-8").read()
URL = "smartcyberphysical.org"
VIDEOS = []

from PIL import Image as _Im
def write(name, fmt, scenes):
    for s_ in scenes:   # image sizes, so the engine never waits on a load
        if s_.get("type") == "image":
            with _Im.open(HERE + "/" + s_["src"].replace("../", "")) as im_: s_["iw"], s_["ih"] = im_.size
    dur = max(s["t1"] for s in scenes)
    sb = {"fmt": fmt, "duration": dur, "scenes": scenes}
    html = ENGINE.replace("<head>", "<head><script>window.SB = " + json.dumps(sb) + ";</script>", 1)
    html = html.replace("url(../site-live/fonts/", "url(../../site-live/fonts/").replace('src="assets/', 'src="../assets/').replace("`<img src=\"assets/", "`<img src=\"../assets/")
    open(f"{HERE}/videos/{name}.html", "w", encoding="utf-8").write(html)
    VIDEOS.append({"name": name, "fmt": fmt, "duration": dur})

def seq(*parts):
    """parts: (seconds, scene dict); returns scenes with t0 and t1 laid end to end"""
    t, out = 0.0, []
    for d, sc in parts: sc = dict(sc); sc["t0"], sc["t1"] = round(t, 3), round(t + d, 3); t += d; out.append(sc)
    return out

def first_clause(s, n=120):
    s = re.sub(r"\s*\([^)]*\)", "", s).split(";")[0].strip()
    if len(s) > n: s = s[:n].rsplit(" ", 1)[0].rstrip(",") + "..."
    return s.rstrip(".") + "."

def sentences(s, n=240):
    parts = re.split(r"(?<=[.!?])\s+", s.strip()); out = ""
    for p in parts:
        if len(out) + len(p) + 1 > n and out: break
        out = (out + " " + p).strip()
    return out

A = "../assets/"
# ---------------------------------------------------------------- 2. seven years in 60 seconds
years = list(range(2019, 2027))
per_year = [(str(y), sum(1 for p in bs.P if p["year"] == y)) for y in years]
n_pubs = len(bs.P)
# the collaboration graph, as drawn on the People page, with the year each pair first worked together
ppl = open(SITE + "/people.html", encoding="utf-8").read()
i = ppl.find('aria-label="Collaboration graph'); seg = ppl[i:ppl.find("</svg>", i)]
nodes = {}
for m in re.finditer(r'<g[^>]*data-name="([^"]+)"[^>]*>\s*<circle cx="([\d.]+)" cy="([\d.]+)"[^>]*stroke="([^"]+)"[^>]*/>(?:<image href="(data:image/[^;]+;base64,[^"]+)")?', seg):
    name, cx, cy, ring, photo = m.groups(); k = bs._person_key(name)
    ph = None
    if photo:
        ext = "png" if "png" in photo[:20] else "jpg"; ph = f"nodes/{k}.{ext}"
        open(f"{HERE}/assets/{ph}", "wb").write(base64.b64decode(photo.split(",", 1)[1]))
    parts = name.replace("M. ", "").replace("G. ", "").replace("A. ", "").split()
    nodes[k] = {"name": name, "short": parts[0] + " " + parts[-1] if len(parts) > 1 else name, "x": float(cx) / 1100, "y": float(cy) / 760, "ring": ring, "photo": (A + ph) if ph else None}
def yr_of(pr):
    m = re.findall(r"(19|20)(\d\d)", pr.get("period", "")); return int(m[0][0] + m[0][1]) if m else 2026
first = {}
for p in bs.P:
    ks = sorted({bs._person_key(a) for a in p["authors"]} & set(nodes))
    for a in range(len(ks)):
        for b in range(a + 1, len(ks)): first[(ks[a], ks[b])] = min(first.get((ks[a], ks[b]), 9999), p["year"])
for pr in bs.PROJECTS:
    ks = sorted({bs._person_key(n) for n, _ in bs.project_people(pr)} & set(nodes))
    for a in range(len(ks)):
        for b in range(a + 1, len(ks)): first[(ks[a], ks[b])] = min(first.get((ks[a], ks[b]), 9999), max(2019, yr_of(pr)))
edges = [{"a": a, "b": b, "year": max(2019, min(y, 2026))} for (a, b), y in sorted(first.items(), key=lambda kv: kv[1])]
edge_keys = {e["a"] for e in edges} | {e["b"] for e in edges}
gnodes = {k: dict(v) for k, v in nodes.items() if k in edge_keys}
xs = [v["x"] for v in gnodes.values()]; ys = [v["y"] for v in gnodes.values()]
for v in gnodes.values():   # fill the frame: stretch the drawing to the available box
    v["x"] = .07 + .86 * (v["x"] - min(xs)) / (max(xs) - min(xs)); v["y"] = .06 + .80 * (v["y"] - min(ys)) / (max(ys) - min(ys))
center = bs._person_key(bs.FACULTY["director"]["name"])
write("seven-years", "h", seq(
    (4.5, {"type": "title", "kicker": "October 2019 to September 2026", "big": "Seven years in sixty seconds", "sub": "The Center for Smart Cyber-Physical Systems at UMass Lowell"}),
    (13, {"type": "bars", "head": "Peer-reviewed papers, year by year", "totlabel": "Papers so far:", "data": per_year,
          "note": "2019 counts October to December, from the center's founding; 2026 counts through September."}),
    (19, {"type": "graph", "head": "Who works with whom, year by year", "nodes": gnodes, "edges": edges, "years": years, "center": center}),
    (12, {"type": "bullets", "head": "Milestones", "img": A + "summit_arch.jpg", "bstep": 1.7, "items_": [
        "2019: the center is founded by five faculty", "2021: Vinod Vokkarane becomes director",
        "2024: ONR post-disaster restoration award, and the DOE CyberCARED consortium",
        "2026: NSF instrumentation award for SUMMIT, a three-university grid testbed", "2026: BOND-AI, printed electronics with industry partners"]}),
    (7, {"type": "stats", "head": "By the numbers", "stats": [[n_pubs, "", "", "peer-reviewed papers since 2019"], [8.0, "$", "M", "in awards the center led", 1], [20, "", "", "faculty in four colleges"], [16, "", "", "doctoral students today"]]}),
    (5, {"type": "end", "big": "Seven years in, and just getting started.", "mid": "Sense. Communicate. Decide with people. Act.", "small": [URL]}),
))

# ---------------------------------------------------------------- 3. student spotlight shorts
students = [s for s in bs.STUDENTS if s.get("advisor") == bs.FACULTY["director"]["name"]]
figs = {"Ayush Pandey": "fig_ayush.png", "Suvhasis Mukhopadhyay": "fig_suvhasis.png"}
for s in students:
    slug = re.sub(r"[^a-z]+", "-", s["name"].lower()).strip("-")
    fig = (s["fig"] + ".jpg") if s.get("fig") else figs.get(s["name"])
    write(f"student-{slug}", "v", seq(
        (3, {"type": "title", "kicker": "Student spotlight", "big": s["name"], "sub": s["status"]}),
        (8, {"type": "person", "photo": A + "head_" + s["photo"] + ".jpg", "name": s["name"], "status": "Advised by Vinod Vokkarane", "line": first_clause(s.get("focus", ""), 130)}),
        (8, {"type": "image", "src": A + fig, "fit": True, "cap": s.get("figcap", ""), "kb": [0, -0.04, 1.0, 0, -0.04, 1.08]}),
        (3.5, {"type": "end", "big": "Meet the lab", "mid": "Advanced Communication Networks Laboratory", "small": [URL + "/acnl"]}),
    ))

# ---------------------------------------------------------------- 4. a paper in 30 seconds (the newest verified summaries)
R = json.load(open(SITE + "/acnl_records.json"))
def rec(prefix): return next(r for r in R if r["title"].startswith(prefix))
venue = {"FUSION: A Unified Benchmarking": "Journal of Optical Communications and Networking, 2026", "QoT-Aware Dynamic": "Journal of Optical Communications and Networking, 2026",
         "QoT-Aware Spectral": "Journal of Optical Communications and Networking, 2026 (invited)"}
for key, slug in [("FUSION: A Unified Benchmarking", "paper-fusion"), ("QoT-Aware Dynamic", "paper-qot-grooming"), ("QoT-Aware Spectral", "paper-spectral-spatial")]:
    r = rec(key)
    title = re.sub(r"\s*\[Invited\]", "", r["title"])
    write(slug, "v", seq(
        (4, {"type": "title", "kicker": "A paper in 30 seconds", "big": title, "sub": venue[key]}),
        (8, {"type": "cards", "meta": "The problem", "cards": [["Why it matters", sentences(r["problem"], 230)]]}),
        (9, {"type": "cards", "meta": "What we found", "cards": [["The result", sentences(r["finding"], 250)]]}),
        (4.5, {"type": "cards", "meta": "Who", "cards": [["Authors", ", ".join(r["authors"])], ["Read it", "doi.org/" + r["doi"]]]}),
        (3, {"type": "end", "big": "More research", "mid": "Advanced Communication Networks Laboratory", "small": [URL + "/acnl.html"]}),
    ))

# ---------------------------------------------------------------- 5. the four thrusts
for key, title, blurb, who in bs.THRUSTS:
    d = bs.THRUST_DETAIL[key]
    write(f"thrust-{key}", "h", seq(
        (6, {"type": "title", "kicker": "Research thrust", "big": title, "sub": d["question"]}),
        (14, {"type": "bullets", "head": "Lines of work", "img": A + f"art_{key}.png", "bstep": 1.6, "items_": [w[0] for w in d["work"]]}),
        (5, {"type": "end", "big": title, "mid": "Co-leads: " + d["leads"], "small": [URL + f"/research-{key}.html"]}),
    ))

# ---------------------------------------------------------------- 6. SUMMIT in 45 seconds
summ = next(p for p in bs.PROJECTS if p["title"].startswith("SUMMIT"))
write("summit", "h", seq(
    (4.5, {"type": "title", "kicker": "NSF Major Research Instrumentation, Award #2511635", "big": "SUMMIT", "sub": "One grid experiment across three universities"}),
    (11, {"type": "image", "src": A + "summit_arch.jpg", "fit": True, "cap": "The UMass Lowell main site, a wide-area software-defined network, and federation sites at NYU Tandon and West Virginia University.", "kb": [0, -0.05, 1.0, 0, -0.05, 1.07]}),
    (12, {"type": "bullets", "head": "What it makes possible", "bstep": 1.8, "items_": [
        "Real-time simulation of the Northeast transmission grid", "Control, networking, and cybersecurity hardware in the loop",
        "Three universities federated over a wide-area network", "Hardware-in-the-loop simulation offered as a service"]}),
    (7, {"type": "stats", "head": "SUMMIT at a glance", "stats": [[2.0, "$", "M", "NSF instrumentation award", 1], [3, "", "", "universities, one testbed"], [4, "", "", "Co-PIs with the PI at UMass Lowell"]]}),
    (5, {"type": "end", "big": "Built at UMass Lowell", "mid": "October 2026 to September 2029", "small": [URL + "/summit.html"]}),
))

# ---------------------------------------------------------------- 7. lab life reel
labs = [("lab1", ""), ("lab2", ""), ("lab3", ""), ("lab4", ""), ("lab5", ""), ("lab6", ""), ("lab7", "Arash Deylamsalehi presenting his research"), ("lab8", "The lab's ESnet OSCARS demonstration at SC15")]
kbs = [[-.02, 0, 1.0, .02, -.01, 1.12], [.02, .01, 1.1, -.02, 0, 1.0], [0, .02, 1.0, 0, -.02, 1.1], [-.02, -.01, 1.1, .02, .01, 1.0]]
parts = [(3, {"type": "title", "kicker": "Advanced Communication Networks Laboratory", "big": "Lab life", "sub": "The people behind the research"})]
for i, (k, c) in enumerate(labs): parts.append((3.4, {"type": "image", "src": A + k + ".jpg", "cap": c, "kb": kbs[i % 4]}))
parts.append((3, {"type": "end", "big": "Come work with us", "small": [URL + "/acnl"]}))
write("lab-life", "h", seq(*parts))

# ---------------------------------------------------------------- 8. come work with us
alums = [v for v in bs.ALUMNI_PROFILES.values() if v.get("role") and v.get("org")][:4]
write("join-us", "v", seq(
    (4, {"type": "title", "kicker": "Ph.D. positions", "big": "Build the systems the world runs on.", "sub": "Doctoral research at the Center for Smart Cyber-Physical Systems, UMass Lowell"}),
    (9, {"type": "bullets", "head": "Four research thrusts", "img": A + "art_cpai.png", "bstep": 1.2, "items_": [t[1] for t in bs.THRUSTS]}),
    (8, {"type": "bullets", "head": "Real instruments, not only simulation", "img": A + "summit_arch.jpg", "bstep": 1.3, "items_": [
        "SUMMIT: a three-university grid testbed", "NATIG: grid and wireless co-simulation", "FUSION: open-source optical network research"]}),
    (8, {"type": "bullets", "head": "Where our Ph.D. graduates go", "bstep": 1.1, "items_": [f"{a['role'].split(',')[0]}, {a['org']}" for a in alums]}),
    (6, {"type": "stats", "head": "The center today", "stats": [[16, "", "", "doctoral students"], [20, "", "", "faculty in four colleges"], [n_pubs, "", "", "papers since 2019"]]}),
    (4, {"type": "end", "big": "Join us", "mid": "Ph.D. positions and how to apply", "small": [URL + "/positions.html"]}),
))
json.dump(VIDEOS, open(HERE + "/videos/index.json", "w"), indent=1)
print(len(VIDEOS), "storyboards:", ", ".join(f"{v['name']} ({v['fmt']}, {v['duration']:.0f}s)" for v in VIDEOS))
print("graph:", len(gnodes), "people,", len(edges), "pairs; by year", {y: sum(1 for e in edges if e["year"] == y) for y in years})
