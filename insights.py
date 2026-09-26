#!/usr/bin/env python3
"""insights.html: what the center's own records say when they are read together.

Everything on the page is computed from data the site already holds (publications, projects, students,
alumni, faculty) plus graph_auto.json (Crossref reference lists and citation counts, refreshed weekly by
graph_fetch.py). Nothing is generated at page load and nothing is inferred from text the group did not
write: clusters come from shared references, shared authors, and title terms; the names and the short
narratives for clusters are written by hand in insights_names.json, keyed by each cluster's anchor
paper, and fall back to the cluster's own top terms when a cluster changes shape.

    python3 insights.py --explain     # print the clusters with anchors and terms, to write names for

build_site.py calls render(globals(), footer_html, script_html) after the other pages are built.
"""
import json, math, os, re, sys, collections, datetime
import networkx as nx
from networkx.algorithms.community import louvain_communities

HERE = os.path.dirname(os.path.abspath(__file__))
PALETTE = ["#1F77B4", "#E4572E", "#2CA58D", "#8E5BB2", "#D4A017", "#C2185B", "#5B8C5A", "#7F5539", "#3F8FD2",
           "#E8871E", "#6A5ACD", "#B5651D", "#4C9A2A", "#A0522D", "#008B8B", "#9932CC"]
STOP = set("""a an the of for and in on to with from by via using based its at as is are be toward towards under over into
through between among within without during after before new novel approach approaches method methods study analysis
framework system systems network networks conference international ieee acm journal proceedings symposium workshop
transactions letters annual toward case data model models learning deep machine efficient effective improving improved
evaluation towards applications application""".split())

# ---------------------------------------------------------------- helpers
def akey(a):
    """'V. M. Vokkarane' -> 'vokkarane_v'; 'Chunxiao (Tricia) Chigan' -> 'chigan_c'."""
    a = re.sub(r"\(.*?\)", "", a).replace(".", " ").replace("‐", "-").strip()
    parts = a.split()
    if not parts: return ""
    return parts[-1].lower() + "_" + parts[0][0].lower()

def toks(text):
    return [w for w in re.findall(r"[a-z][a-z0-9]{2,}", text.lower().replace("-", " ")) if w not in STOP]

def cos(u, v):
    if len(u) > len(v): u, v = v, u
    return sum(x * v.get(w, 0) for w, x in u.items())

def load_json(name, default):
    p = os.path.join(HERE, name)
    try: return json.load(open(p, encoding="utf-8"))
    except Exception: return default

# ---------------------------------------------------------------- computation
def compute(ns):
    P = ns["P"]; N = len(P)
    G = load_json("graph_auto.json", {"works": {}, "external": {}})
    W, EXT = G.get("works", {}), G.get("external", {})
    names_file = load_json("insights_names.json", {})

    # text vectors (title + venue), reference sets, author sets
    docs = [toks(p["title"] + " " + p["venue"]) for p in P]
    df = collections.Counter(w for d in docs for w in set(d))
    def vec(d):
        c = collections.Counter(d)
        v = {w: (1 + math.log(n)) * math.log(N / (1 + df[w])) for w, n in c.items()}
        s = math.sqrt(sum(x * x for x in v.values())) or 1
        return {w: x / s for w, x in v.items()}
    V = [vec(d) for d in docs]
    own = {p["doi"].lower() for p in P if p.get("doi")}
    refs = [set(W.get(p["doi"].lower(), {}).get("refs", [])) if p.get("doi") else set() for p in P]
    cited = [int(W.get(p["doi"].lower(), {}).get("cited_by", 0)) if p.get("doi") else 0 for p in P]
    auth = [set(akey(a) for a in p["authors"]) for p in P]

    def sim(i, j):
        c = len(refs[i] & refs[j]) / math.sqrt(len(refs[i]) * len(refs[j])) if refs[i] and refs[j] else 0.0
        t = cos(V[i], V[j])
        a = len(auth[i] & auth[j]) / math.sqrt(len(auth[i]) * len(auth[j])) if auth[i] and auth[j] else 0.0
        return 0.5 * c + 0.35 * t + 0.15 * a
    S = [[0.0] * N for _ in range(N)]
    for i in range(N):
        for j in range(i + 1, N):
            S[i][j] = S[j][i] = sim(i, j)
    g = nx.Graph(); g.add_nodes_from(range(N))
    for i in range(N):
        for j in range(i + 1, N):
            if S[i][j] >= 0.10: g.add_edge(i, j, weight=S[i][j])
    for i in range(N):                                  # no paper is left alone: keep its three nearest
        if g.degree(i) < 3:
            for j in sorted((j for j in range(N) if j != i), key=lambda j: -S[i][j])[:3]:
                g.add_edge(i, j, weight=max(S[i][j], 0.02))
    comms = sorted(louvain_communities(g, weight="weight", resolution=1.0, seed=7), key=lambda c: (-len(c), min(c)))
    # tiny communities (under 4 papers) join the neighbour they are most connected to
    merged = True
    while merged:
        merged = False
        for ci, c in enumerate(comms):
            if len(c) >= 4 or len(comms) == 1: continue
            best, bw = None, -1
            for cj, d in enumerate(comms):
                if cj == ci: continue
                w = sum(S[i][j] for i in c for j in d)
                if w > bw: best, bw = cj, w
            comms[best] = comms[best] | c; comms.pop(ci); merged = True; break
    comms = sorted(comms, key=lambda c: (-len(c), min(c)))
    cluster_of = {i: ci for ci, c in enumerate(comms) for i in c}

    # cluster descriptors
    clusters = []
    for ci, c in enumerate(comms):
        c = sorted(c)
        cent = collections.Counter()
        for i in c:
            for w, x in V[i].items(): cent[w] += x
        norm = math.sqrt(sum(x * x for x in cent.values())) or 1
        centroid = {w: x / norm for w, x in cent.items()}
        # distinctive terms: centroid weight relative to corpus frequency
        terms = [w for w, _ in sorted(cent.items(), key=lambda kv: -kv[1] * math.log(N / (1 + df[kv[0]])))[:6]]
        deg = {i: sum(S[i][j] for j in c if j != i) for i in c}
        anchor = max(c, key=lambda i: (deg[i], cited[i], -i))
        anchor_doi = (P[anchor].get("doi") or "").lower()
        nm = names_file.get(anchor_doi) or {}
        fac = collections.Counter(f for i in c for f in P[i]["faculty"])
        years = collections.Counter(P[i]["year"] for i in c)
        clusters.append({
            "id": ci, "papers": c, "n": len(c), "color": PALETTE[ci % len(PALETTE)],
            "terms": terms, "centroid": centroid, "anchor": anchor, "anchor_doi": anchor_doi,
            "name": nm.get("name") or ", ".join(terms[:3]).title(), "named": bool(nm.get("name")),
            "narrative": nm.get("narrative", ""),
            "faculty": fac.most_common(), "years": dict(sorted(years.items())),
            "journal": sum(1 for i in c if P[i]["type"] == "journal"),
            "citations": sum(cited[i] for i in c),
            "top": sorted(c, key=lambda i: (-cited[i], -P[i]["year"]))[:3],
        })
    # neighbouring clusters, by total similarity between them
    for a in clusters:
        links = []
        for b in clusters:
            if b is a: continue
            w = sum(S[i][j] for i in a["papers"] for j in b["papers"])
            links.append((w, b["id"]))
        links.sort(reverse=True)
        a["nearest"] = [cid for w, cid in links[:2] if w > 0]

    # ---------------------------------------------------------------- people
    people = {}   # akey -> {"name", "kind", "group"}
    F = ns["FACULTY"]
    for grp in ("director", "core", "affiliated", "external"):
        for p in ([F[grp]] if grp == "director" else F[grp]):
            people[akey(p["name"])] = {"name": p["name"], "kind": "faculty", "group": grp}
    for st in ns["STUDENTS"]:
        spec = ns["STUDENT_ADVISOR"].get(st["name"])
        k = (spec[0].lower() + "_" + spec[1].lower()) if spec else akey(st["name"])
        people[k] = {"name": st["name"], "kind": "student", "group": "student"}
    for nm_, a in ns["ALUMNI_PROFILES"].items():
        people.setdefault(akey(nm_), {"name": nm_, "kind": "alumni", "group": "alumni"})
    for y, nm_, _ in ns["ALUMNI_PHD"]:
        people.setdefault(akey(nm_), {"name": nm_, "kind": "alumni", "group": "alumni"})
    for nm_, _ in ns["ALUMNI_POSTDOC"]:
        people.setdefault(akey(nm_), {"name": nm_, "kind": "alumni", "group": "alumni"})

    core_people = [F["director"]] + F["core"]
    core_sur = [re.sub(r"\(.*?\)", "", p["name"]).split()[-1] for p in core_people]
    core_keys = core_sur
    # joint papers between core faculty, from the vetted faculty tags on each record (not from author strings,
    # which collide on common surname-plus-initial pairs)
    matrix = {(a, b): 0 for a in core_sur for b in core_sur}
    for p in P:
        present = [f for f in core_sur if f in p["faculty"]]
        for a in present:
            for b in present:
                matrix[(a, b)] += 1
    joint = sorted(((matrix[(a, b)], a, b) for ai, a in enumerate(core_sur) for b in core_sur[ai + 1:] if matrix[(a, b)]), reverse=True)
    n_pairs = len(core_sur) * (len(core_sur) - 1) // 2

    # who is on which paper: core faculty by their tag; students only with their advisor on the paper (the
    # site's own rule); alumni of the director's group only on papers the director is tagged on; affiliated
    # and external faculty by name, which is the one place a common name could be mistaken.
    def gate(k, i):
        who = people[k]
        if who["kind"] == "faculty" and who["group"] in ("director", "core"):
            return re.sub(r"\(.*?\)", "", who["name"]).split()[-1] in P[i]["faculty"]
        if who["kind"] == "student":
            spec = ns["STUDENT_ADVISOR"].get(who["name"])
            return bool(spec) and bool(set(P[i]["faculty"]) & spec[2])
        if who["kind"] == "alumni":
            return "Vokkarane" in P[i]["faculty"]
        return True
    per_person = collections.defaultdict(lambda: {"papers": [], "clusters": collections.Counter(), "first": 0, "journal": 0})
    outside = collections.Counter(); outside_form = {}
    for i, p in enumerate(P):
        for pos, a in enumerate(p["authors"]):
            k = akey(a)
            if k in people and gate(k, i):
                d = per_person[k]; d["papers"].append(i); d["clusters"][cluster_of[i]] += 1
                if pos == 0: d["first"] += 1
                if p["type"] == "journal": d["journal"] += 1
            else:
                outside[k] += 1; outside_form.setdefault(k, a)
    bridges = sorted(((len(d["clusters"]), len(d["papers"]), people[k]["name"], people[k]["kind"], [clusters[c]["name"] for c, _ in d["clusters"].most_common()])
                      for k, d in per_person.items() if len(d["clusters"]) >= 2 and (people[k]["kind"] != "faculty" or people[k]["group"] in ("director", "core"))),
                     key=lambda t: (-t[0], -t[1], t[2]))
    outside_top = [(outside_form[k], n) for k, n in outside.most_common(12)]

    # ---------------------------------------------------------------- intellectual base
    base = collections.Counter(); base_by_cluster = collections.defaultdict(collections.Counter)
    for i in range(N):
        for r in refs[i]:
            if r in own: continue
            base[r] += 1; base_by_cluster[cluster_of[i]][r] += 1
    fac_surnames = {re.sub(r"\(.*?\)", "", p["name"]).split()[-1].lower() for grp in ("director", "core", "affiliated") for p in ([F[grp]] if grp == "director" else F[grp])}
    def base_row(doi, n):
        e = EXT.get(doi, {})
        fa = (e.get("first_author") or "").lower()
        return {"doi": doi, "n": n, "title": e.get("title") or "", "year": e.get("year"), "venue": e.get("venue") or "",
                "first_author": e.get("first_author") or "", "n_authors": e.get("n_authors", 0),
                "own_earlier": bool(fa) and fa.split()[-1] in fac_surnames}
    base_top = [base_row(d, n) for d, n in base.most_common(60) if EXT.get(d, {}).get("title")][:20]
    internal_cites = [(i, j) for i in range(N) for j in range(N) if P[j].get("doi") and P[j]["doi"].lower() in refs[i]]
    for cl in clusters:
        cl["base"] = [base_row(d, n) for d, n in base_by_cluster[cl["id"]].most_common(8) if EXT.get(d, {}).get("title")][:3]

    # ---------------------------------------------------------------- projects <-> clusters
    projects = []
    for pr in ns["PROJECTS"]:
        pv = vec(toks(pr["title"] + " " + pr.get("desc", "")))
        team = {w.lower() for w in re.findall(r"[A-Z][a-zA-Z\-]+", pr.get("team", "") + " " + ns["project_pi"](pr))}
        best = []
        for cl in clusters:
            cl_fac = {f.lower() for f, _ in cl["faculty"]}
            if not (team & cl_fac): continue
            best.append((cos(pv, cl["centroid"]), cl["id"]))
        best.sort(reverse=True)
        projects.append({"pr": pr, "matches": [(s, cid) for s, cid in best if s >= 0.06][:2]})
    for cl in clusters:
        cl["projects"] = sorted(((s, pj["pr"]) for pj in projects for s, cid in pj["matches"] if cid == cl["id"]), key=lambda t: -t[0])[:3]
    unmatched_projects = [pj["pr"] for pj in projects if not pj["matches"]]

    # ---------------------------------------------------------------- students and alumni
    students = []
    for st in ns["STUDENTS"]:
        spec = ns["STUDENT_ADVISOR"].get(st["name"])
        k = (spec[0].lower() + "_" + spec[1].lower()) if spec else akey(st["name"])
        d = per_person.get(k, {"papers": [], "clusters": collections.Counter(), "first": 0, "journal": 0})
        co = collections.Counter()
        for i in d["papers"]:
            for a in P[i]["authors"]:
                kk = akey(a)
                if kk != k and kk not in people: co[outside_form.get(kk, a)] += 1
        students.append({"name": st["name"], "status": st.get("status", ""), "n": len(d["papers"]), "journal": d["journal"], "first": d["first"],
                         "cites": sum(cited[i] for i in d["papers"]),
                         "clusters": [(clusters[c]["name"], n, clusters[c]["color"]) for c, n in d["clusters"].most_common()],
                         "outside": [a for a, _ in co.most_common(2)]})
    alumni = []
    for nm_, a in ns["ALUMNI_PROFILES"].items():
        k = akey(nm_); d = per_person.get(k)
        role, org = a.get("role", ""), a.get("org", "")
        sector = "academia" if re.search(r"professor|lecturer|faculty|university|college|institute of technology", (role + " " + org).lower()) else \
                 "national lab" if re.search(r"national lab|laboratory|nist|nasa", org.lower()) else "industry"
        alumni.append({"name": nm_, "degree": a.get("degree", ""), "role": role, "org": org, "sector": sector,
                       "n": len(d["papers"]) if d else 0, "cites": sum(cited[i] for i in d["papers"]) if d else 0})
    sectors = collections.Counter(a["sector"] for a in alumni)

    # ---------------------------------------------------------------- layout: clusters as islands
    # Islands are placed by a spring layout over the cluster graph (linked clusters land near each other),
    # then pushed apart until no island or label overlaps another, and kept inside the canvas.
    cg = nx.Graph()
    for cl in clusters: cg.add_node(cl["id"])
    for a_ in clusters:
        for b_ in clusters:
            if b_["id"] <= a_["id"]: continue
            w = sum(S[i][j] for i in a_["papers"] for j in b_["papers"])
            if w > 0: cg.add_edge(a_["id"], b_["id"], weight=w)
    lay = nx.spring_layout(cg, weight="weight", seed=11, k=1.4)
    Wc, Hc, M = 1000, 640, 40
    for cl in clusters:
        cl["r"] = 16 + 9 * math.sqrt(cl["n"])
        cl["lw"] = 6.6 * len(cl["name"]) + 8            # label width estimate at 12.5px
        x, y = lay[cl["id"]]
        cl["center"] = [M + 120 + (x + 1) / 2 * (Wc - 2 * M - 240), M + 30 + (y + 1) / 2 * (Hc - 2 * M - 90)]
    def box(cl):   # island plus its label, as a rectangle half-extent
        return max(cl["r"], cl["lw"] / 2) + 10, cl["r"] + 30
    for _ in range(400):
        moved = False
        for a_ in clusters:
            for b_ in clusters:
                if b_["id"] <= a_["id"]: continue
                (ax_, ay_), (bx_, by_) = a_["center"], b_["center"]
                hw, hh = box(a_); hw2, hh2 = box(b_)
                dx, dy = bx_ - ax_, by_ - ay_
                ox, oy = (hw + hw2) - abs(dx), (hh + hh2) - abs(dy)
                if ox > 0 and oy > 0:
                    if ox / (hw + hw2) < oy / (hh + hh2):
                        sh = ox / 2 + 1; sgn = 1 if dx >= 0 else -1
                        a_["center"][0] -= sh * sgn; b_["center"][0] += sh * sgn
                    else:
                        sh = oy / 2 + 1; sgn = 1 if dy >= 0 else -1
                        a_["center"][1] -= sh * sgn; b_["center"][1] += sh * sgn
                    moved = True
        for cl in clusters:
            hw, hh = box(cl)
            cl["center"][0] = min(max(cl["center"][0], hw), Wc - hw)
            cl["center"][1] = min(max(cl["center"][1], cl["r"] + 8), Hc - hh)
        if not moved: break
    pos = {}
    for cl in clusters:
        cxc, cyc = cl["center"]; r = cl["r"]
        sub = g.subgraph(cl["papers"])
        lay2 = nx.spring_layout(sub, weight="weight", seed=7, k=0.9 / math.sqrt(max(cl["n"], 2)))
        xs = [v[0] for v in lay2.values()] or [0]; ys = [v[1] for v in lay2.values()] or [0]
        span = max(max(xs) - min(xs), max(ys) - min(ys), 1e-6)
        for i, (x, y) in lay2.items():
            pos[i] = (cxc + (x - (max(xs) + min(xs)) / 2) / span * 2 * (r - 8), cyc + (y - (max(ys) + min(ys)) / 2) / span * 2 * (r - 8))
    edges_in = [(i, j, d["weight"]) for i, j, d in g.edges(data=True) if cluster_of[i] == cluster_of[j] and d["weight"] >= 0.15]
    edges_out = sorted(((i, j, d["weight"]) for i, j, d in g.edges(data=True) if cluster_of[i] != cluster_of[j]), key=lambda t: -t[2])[:40]

    years = sorted({p["year"] for p in P})
    return {"P": P, "N": N, "clusters": clusters, "cluster_of": cluster_of, "cited": cited, "pos": pos,
            "edges_in": edges_in, "edges_out": edges_out, "internal_cites": internal_cites,
            "matrix": matrix, "core_people": core_people, "core_keys": core_keys, "joint": joint, "n_pairs": n_pairs, "people": people,
            "bridges": bridges, "outside_top": outside_top, "base_top": base_top, "n_base": len(base),
            "n_base3": sum(1 for v in base.values() if v >= 3), "n_refs": sum(len(r) for r in refs),
            "projects": projects, "unmatched_projects": unmatched_projects, "students": students, "alumni": alumni, "sectors": sectors,
            "years": years, "date": G.get("date", ""), "total_cites": sum(cited), "with_refs": sum(1 for r in refs if r)}

# ---------------------------------------------------------------- rendering
def render(ns, footer_html, script_html):
    esc = ns["esc"]; R = compute(ns); P, N, C = R["P"], R["N"], R["clusters"]
    fmt_authors = ns["fmt_authors"]; journal_chip = ns["journal_chip"]
    today = datetime.date.today()

    def paper_li(i, note=""):
        p = P[i]
        t = f'<a href="https://doi.org/{esc(p["doi"])}">{esc(p["title"])}</a>' if p.get("doi") else esc(p["title"])
        return (f'<li class="ipub"><span class="t">{t}</span><span class="v">{esc(p["venue"])}, {p["year"]}{note}'
                f'{(" " + journal_chip(p["venue"])) if p["type"] == "journal" else ""}</span></li>')

    # --- the map
    # --- the map: one tile per cluster, big type, no overlaps. Citation links between clusters appear when a tile
    # is hovered, focused, or chosen in the legend; clicking a tile jumps to that cluster's papers below.
    order = sorted(range(len(C)), key=lambda k: -C[k]["n"])
    cols = 4; TW, TH, GX, GY, MX, MY = 226, 148, 20, 18, 12, 12
    rows = (len(C) + cols - 1) // cols
    Wm, Hm = MX * 2 + cols * TW + (cols - 1) * GX, MY * 2 + rows * TH + (rows - 1) * GY
    tile_at = {}
    for k, cid in enumerate(order):
        rr, cc = divmod(k, cols)
        tile_at[cid] = (MX + cc * (TW + GX), MY + rr * (TH + GY))
    # citations between clusters, from the center's own papers citing each other
    between = {}
    for a_i, b_i in R["internal_cites"]:
        ca, cb = R["cluster_of"][a_i], R["cluster_of"][b_i]
        if ca != cb: between[tuple(sorted((ca, cb)))] = between.get(tuple(sorted((ca, cb))), 0) + 1
    def wrap(text, width_chars):
        words, lines, cur = text.split(), [], ""
        for w in words:
            if cur and len(cur) + 1 + len(w) > width_chars: lines.append(cur); cur = w
            else: cur = (cur + " " + w).strip()
        if cur: lines.append(cur)
        return lines
    svg = [f'<svg class="imap" viewBox="0 0 {Wm} {Hm}" role="img" aria-labelledby="mapTitle mapDesc">',
           '<title id="mapTitle">Map of the center\'s research clusters</title>',
           f'<desc id="mapDesc">{N} papers grouped into {len(C)} research clusters by shared references, shared authors, and title terms, shown as tiles ordered by size. Links between tiles show how often the clusters cite each other.</desc>']
    # related clusters (nearest by shared references, authors, and language) as dashed links; citations as solid ones
    related = set()
    for cl in C:
        for c2 in cl["nearest"][:2]:
            pair = tuple(sorted((cl["id"], c2)))
            if pair not in between: related.add(pair)
    maxb = max(between.values()) if between else 1
    def curve(ca, cb):
        (x1, y1), (x2, y2) = tile_at[ca], tile_at[cb]
        x1, y1, x2, y2 = x1 + TW / 2, y1 + TH / 2, x2 + TW / 2, y2 + TH / 2
        dx, dy = x2 - x1, y2 - y1; L = (dx * dx + dy * dy) ** 0.5 or 1
        mx, my = (x1 + x2) / 2 - dy / L * L * 0.12, (y1 + y2) / 2 + dx / L * L * 0.12
        return f'M{x1:.0f} {y1:.0f}Q{mx:.0f} {my:.0f} {x2:.0f} {y2:.0f}'
    for cid, (x, y) in tile_at.items():
        cl = C[cid]; lines = wrap(cl["name"], 22)
        fs = 17 if len(lines) <= 3 else 15
        if len(lines) > 4: lines = wrap(cl["name"], 30)[:4]
        title = "".join(f'<tspan x="{x + 18:.0f}" dy="{0 if k == 0 else fs * 1.22:.0f}">{esc(t)}</tspan>' for k, t in enumerate(lines))
        who = ", ".join(ns["FULL_NAME"].get(f, f).split()[-1] for f, _ in cl["faculty"][:3])
        yrs = list(cl["years"]); span = f'{yrs[0]} to {yrs[-1]}' if yrs[0] != yrs[-1] else str(yrs[0])
        nb = sum(1 for (a, b) in between if cid in (a, b))
        svg.append(f'<a class="tile" href="#cluster-{cid}" data-c="{cid}" aria-label="{esc(cl["name"])}: {cl["n"]} papers, {span}. Go to its papers.">'
                   f'<rect x="{x}" y="{y}" width="{TW}" height="{TH}" rx="12" fill="var(--surface)" stroke="{cl["color"]}" stroke-width="2"/>'
                   f'<rect x="{x}" y="{y}" width="8" height="{TH}" rx="4" fill="{cl["color"]}"/>'
                   f'<text class="tt" x="{x + 18}" y="{y + 30}" font-size="{fs}">{title}</text>'
                   f'<text class="tm" x="{x + 18}" y="{y + TH - 34}">{cl["n"]} papers, {span}</text>'
                   f'<text class="tm" x="{x + 18}" y="{y + TH - 14}">{esc(who)}</text></a>')
    for ca, cb in sorted(related):
        svg.append(f'<path class="lk rel" d="{curve(ca, cb)}" stroke-width="2.5" data-c="{ca} {cb}"><title>{esc(C[ca]["name"])} and {esc(C[cb]["name"])}: related work (shared references, authors, or language)</title></path>')
    for (ca, cb), n in sorted(between.items(), key=lambda t: t[1]):
        svg.append(f'<path class="lk" d="{curve(ca, cb)}" stroke-width="{3 + 8 * n / maxb:.1f}" data-c="{ca} {cb}"><title>{esc(C[ca]["name"])} and {esc(C[cb]["name"])}: {n} citation{"s" if n != 1 else ""} between their papers</title></path>')
    svg.append('</svg>')
    legend = "".join(f'<button class="ichip" type="button" data-c="{cl["id"]}" aria-pressed="false"><i style="background:{cl["color"]}"></i>{esc(cl["name"])} <small>{cl["n"]}</small></button>' for cl in C)

    # --- cluster cards
    cards = []
    for cl in C:
        who = ", ".join(f'{esc(ns["FULL_NAME"].get(f, f))}' + (f' ({n})' if len(cl["faculty"]) > 1 else "") for f, n in cl["faculty"][:5])
        yrs = list(cl["years"]); span = f'{yrs[0]} to {yrs[-1]}' if yrs[0] != yrs[-1] else str(yrs[0])
        near = ", ".join(C[c]["name"] for c in cl["nearest"])
        base = "".join(f'<li><a href="https://doi.org/{esc(b["doi"])}">{esc(b["title"])}</a> <span class="v">{esc(b["first_author"])}{" et al." if b["n_authors"] > 1 else ""}, {b["year"] or ""}; cited by {b["n"]} of these papers{"; earlier work by a center member" if b["own_earlier"] else ""}</span></li>' for b in cl["base"])
        projs = "".join(f'<li>{esc(pr["title"])} <span class="v">{esc(pr["sponsor"].split(",")[0])}{(", " + esc(pr["period"])) if pr.get("period") else ""}</span></li>' for s, pr in cl["projects"])
        narrative = f'<p class="narr">{esc(cl["narrative"])}</p>' if cl["narrative"] else \
                    f'<p class="narr auto">Named from its own terms: {esc(", ".join(cl["terms"][:6]))}. A written summary is added once the cluster is stable.</p>'
        cards.append(f'''<article class="icl" id="cluster-{cl["id"]}" style="--c:{cl["color"]}">
  <h3><span class="dot"></span>{esc(cl["name"])}</h3>
  <p class="meta"><b>{cl["n"]}</b> papers, {cl["journal"]} in journals, {span}. <b>{cl["citations"]:,}</b> citations on Crossref.{(" Nearest: " + esc(near) + ".") if near else ""}</p>
  <p class="who">{who}</p>
  {narrative}
  <h4>Most cited</h4><ul class="ipubs">{"".join(paper_li(i, f", cited by {R['cited'][i]}") for i in cl["top"])}</ul>
  {("<h4>Builds on</h4><ul class=\"base\">" + base + "</ul>") if base else ""}
  {("<h4>Awards behind this work</h4><ul class=\"base\">" + projs + "</ul>") if projs else ""}
</article>''')

    # --- collaboration matrix
    keys, ppl = R["core_keys"], R["core_people"]
    short = keys
    mx = max(v for (a, b), v in R["matrix"].items() if a != b) or 1
    head = "<tr><th></th>" + "".join(f'<th scope="col"><span>{esc(s)}</span></th>' for s in short) + "</tr>"
    rows = ""
    for ai, a in enumerate(keys):
        cells = ""
        for bi, b in enumerate(keys):
            v = R["matrix"][(a, b)]
            if ai == bi: cells += f'<td class="self" title="{esc(ppl[ai]["name"])}: {v} papers in the record">{v}</td>'
            else:
                op = 0.12 + 0.88 * (v / mx) if v else 0
                cells += (f'<td style="--o:{op:.2f}" title="{esc(ppl[ai]["name"])} and {esc(ppl[bi]["name"])}: {v} joint paper{"s" if v != 1 else ""}">{v or ""}</td>')
        rows += f'<tr><th scope="row">{esc(short[ai])}</th>{cells}</tr>'
    matrix_html = f'<table class="cmx"><caption>Joint papers between the director and center faculty, 2019 to {today.year}</caption><thead>{head}</thead><tbody>{rows}</tbody></table>'
    joint_html = "; ".join(f'{esc(a)} and {esc(b)}, {n}' for n, a, b in R["joint"])
    never_html = f'{len(R["joint"])} of the {R["n_pairs"]} possible pairs have a joint paper in the record: {joint_html}.' if R["joint"] else ""
    bridges_html = "".join(f'<li><b>{esc(n)}</b> <span class="v">{esc(k)}; {np} papers across {nc} clusters: {esc(", ".join(cls))}</span></li>' for nc, np, n, k, cls in R["bridges"][:10])
    outside_html = "".join(f'<li>{esc(a)} <span class="v">{n} papers</span></li>' for a, n in R["outside_top"])

    # --- base works
    base_html = "".join(f'<li><a href="https://doi.org/{esc(b["doi"])}">{esc(b["title"])}</a> <span class="v">{esc(b["first_author"])}{" et al." if b["n_authors"] > 1 else ""}, {b["year"] or ""}, {esc(b["venue"])}. Cited by <b>{b["n"]}</b> of the center\'s papers{"; earlier work by a center member" if b["own_earlier"] else ""}</span></li>' for b in R["base_top"][:15])

    # --- impact: top cited, citations by cluster, papers by year stacked
    top_cited = sorted(range(N), key=lambda i: (-R["cited"][i], -P[i]["year"]))[:10]
    top_html = "".join(paper_li(i, f", <b>{R['cited'][i]}</b> citations") for i in top_cited)
    ymax = max(sum(1 for i in range(N) if P[i]["year"] == y) for y in R["years"])
    bw = 900 / len(R["years"])
    bars = []
    for k, y in enumerate(R["years"]):
        y0 = 0
        for cl in C:
            n = cl["years"].get(y, 0)
            if not n: continue
            h = n / ymax * 200
            bars.append(f'<rect x="{50 + k * bw + 6:.1f}" y="{230 - y0 - h:.1f}" width="{bw - 12:.1f}" height="{h:.1f}" fill="{cl["color"]}" data-c="{cl["id"]}"><title>{esc(cl["name"])}: {n} in {y}</title></rect>')
            y0 += h
        tot = sum(1 for i in range(N) if P[i]["year"] == y)
        bars.append(f'<text class="ax" x="{50 + k * bw + bw / 2:.1f}" y="250" text-anchor="middle">{y}</text><text class="ax" x="{50 + k * bw + bw / 2:.1f}" y="{230 - y0 - 6:.1f}" text-anchor="middle">{tot}</text>')
    year_svg = f'<svg class="ich" viewBox="0 0 1000 260" role="img" aria-label="Papers per year, stacked by cluster">{"".join(bars)}</svg>'
    cmax = max(cl["citations"] for cl in C) or 1
    cbars = "".join(f'<li style="--c:{cl["color"]}"><span class="lab">{esc(cl["name"])}</span><span class="bar" style="width:{cl["citations"] / cmax * 100:.1f}%"></span><span class="num">{cl["citations"]:,} <small>{cl["n"]} papers, {cl["citations"] / cl["n"]:.0f} each</small></span></li>' for cl in sorted(C, key=lambda c: -c["citations"]))

    # --- students, alumni
    st_rows = "".join(
        f'<tr><th scope="row">{esc(s["name"])}<small>{esc(s["status"])}</small></th><td>{s["n"]}</td><td>{s["journal"]}</td><td>{s["first"]}</td><td>{s["cites"]}</td>'
        f'<td class="cls">{"".join(f"<span style=\"--c:{col}\"><i></i>{esc(nm)} ({n})</span>" for nm, n, col in s["clusters"]) or "<span class=\"v\">no papers in the record yet</span>"}</td>'
        f'<td>{esc(", ".join(s["outside"])) or ""}</td></tr>' for s in R["students"])
    al_rows = "".join(
        f'<li><b>{esc(a["name"])}</b> <span class="v">{esc(a["degree"])}. {esc(a["role"])}{", " + esc(a["org"]) if a["org"] else ""}{f". {a['n']} paper{'s' if a['n'] != 1 else ''} in the center record, {a['cites']} citation{'s' if a['cites'] != 1 else ''}" if a["n"] else ""}</span></li>'
        for a in sorted(R["alumni"], key=lambda a: (a["sector"], a["name"])))
    sec = R["sectors"]
    sect_html = ", ".join(f'{sec[k]} in {k}' for k in ("academia", "industry", "national lab") if sec.get(k))

    # --- projects with no cluster match
    un_html = "".join(f'<li>{esc(pr["title"])} <span class="v">{esc(pr["sponsor"].split(",")[0])}</span></li>' for pr in R["unmatched_projects"])

    n_named = sum(1 for cl in C if cl["named"])
    body = f'''<div class="ihero">
  <div class="wrap">
    <p class="crumb">Reading the record as a whole</p>
    <h1>Insights</h1>
    <p class="q">{N} papers, {len(R["projects"])} sponsored projects, {len(R["students"])} doctoral students, and {len(R["alumni"])} alumni, read together. Every figure on this page is computed from the center's own records and Crossref; nothing is generated when the page loads.</p>
    <div class="istats"><div><b>{N}</b>papers since 2019</div><div><b>{R["total_cites"]:,}</b>citations on Crossref</div><div><b>{R["n_base"]:,}</b>outside works the papers cite</div><div><b>{len(C)}</b>research clusters</div></div>
  </div>
</div>
<section class="imapsec">
  <div class="wrap">
    <div class="maphead"><h2>The map</h2><p>Each tile is a research cluster: papers that cite the same literature, share authors, or use the same language, with the largest clusters first. Hover over a tile to see its links: solid lines are citations between the clusters\' papers, dashed lines are related work. Click a tile to go to its papers. </p></div>
    <div class="legend" id="legend">{legend}<button class="ichip all" type="button" data-c="all" aria-pressed="true">Show all</button></div>
    <div class="mapwrap">{"".join(svg)}</div>
    <p class="mapnote">{len(R["internal_cites"])} citations run between the center's own papers. {R["with_refs"]} of {N} papers have open reference lists on Crossref, {R["n_refs"]:,} references with DOIs between them.</p>
  </div>
</section>
<section>
  <div class="wrap">
    <div class="shead"><h2>Clusters</h2><p>Found by community detection over the ties above, then named by hand from what the papers actually study. {n_named} of {len(C)} clusters carry a written summary; the rest are labelled from their own terms until they settle.</p></div>
    <div class="iclgrid">{"".join(cards)}</div>
  </div>
</section>
<section class="tint">
  <div class="wrap">
    <div class="shead"><h2>Who works with whom</h2><p>Co-authorship among the director and center faculty in the publication record, the people whose work spans more than one cluster, and the co-authors outside the site's roster who appear most often.</p></div>
    <div class="igrid2">
      <div><div class="tscroll">{matrix_html}</div>
        {("<p class=\"never\">" + never_html + "</p>") if never_html else ""}</div>
      <div>
        <h3>Bridges between clusters</h3><ul class="ilist">{bridges_html or "<li>None yet.</li>"}</ul>
        <h3>Most frequent co-authors outside the roster</h3><ul class="ilist two">{outside_html}</ul>
      </div>
    </div>
  </div>
</section>
<section>
  <div class="wrap">
    <div class="shead"><h2>What the work builds on</h2><p>The outside papers cited by the most center papers. {R["n_base3"]} works are cited by three or more; these are the ones cited most. A center member's own earlier work is marked.</p></div>
    <ol class="base big">{base_html}</ol>
  </div>
</section>
<section class="tint">
  <div class="wrap">
    <div class="shead"><h2>Reach</h2><p>Citation counts are Crossref's, which only see citations publishers deposit, so they run below Google Scholar. They are comparable across the center's papers because every paper is counted the same way.</p></div>
    <div class="igrid2">
      <div><h3>Most cited papers</h3><ol class="ipubs">{top_html}</ol></div>
      <div><h3>Citations by cluster</h3><ul class="cbars">{cbars}</ul></div>
    </div>
    <h3>Papers per year, by cluster</h3>
    {year_svg}
  </div>
</section>
<section>
  <div class="wrap">
    <div class="shead"><h2>Students and alumni</h2><p>Doctoral students in the director's group as they appear in the record, and where the center's graduates and postdocs went: {sect_html}.</p></div>
    <div class="tscroll"><table class="stbl"><thead><tr><th scope="col">Student</th><th scope="col">Papers</th><th scope="col">Journal</th><th scope="col">First author</th><th scope="col">Citations</th><th scope="col">Clusters</th><th scope="col">Co-authors outside the roster</th></tr></thead><tbody>{st_rows}</tbody></table></div>
    <h3>Alumni</h3><ul class="ilist two">{al_rows}</ul>
  </div>
</section>
<section class="tint">
  <div class="wrap">
    <div class="shead"><h2>Funding and the clusters</h2><p>Each award is matched to the clusters whose language it shares and whose faculty it names; matches appear on the cluster cards above. {len(R["unmatched_projects"])} of {len(R["projects"])} awards match no cluster by that test, either because their output is not yet in the publication record or because the people named on the award are not the ones whose papers carry its language.</p></div>
    {("<ul class=\"ilist two\">" + un_html + "</ul>") if un_html else ""}
    <p class="how"><b>How this page is made.</b> Publications, projects, students, alumni, and faculty are the site's own records. Reference lists and citation counts come from Crossref, refreshed weekly ({esc(R["date"] or today.isoformat())}). Two papers are tied by the cosine of their shared references (half the weight), of their title and venue terms (a third), and of their shared authors (the rest); communities are found with the Louvain method on those ties, with small communities merged into their nearest neighbour. Cluster names and summaries are written by hand and keyed to each cluster's anchor paper, so they survive weekly rebuilds and fall back to the cluster's own terms if it changes shape. Full-text extraction, which would add methods, testbeds, and reported results to this graph, is the next step.</p>
  </div>
</section>
'''
    css = '''
.ihero{background:var(--navy);color:var(--on-navy);padding:clamp(40px,6vw,72px) 0 clamp(28px,4vw,44px)}
.ihero .crumb{color:var(--on-navy-3);font-size:14px;margin:0 0 10px}.ihero h1{color:#fff;max-width:none}
.ihero .q{font-size:clamp(17px,1.4vw,20px);line-height:1.5;color:var(--on-navy-2);max-width:40em;margin:18px 0 26px}
.istats{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;max-width:820px}
.istats div{border-top:1px solid rgba(255,255,255,.22);padding-top:10px;font-size:13.5px;color:var(--on-navy-2)}
.istats b{display:block;font-family:"Fraunces",Georgia,serif;font-weight:500;font-size:clamp(26px,3vw,38px);line-height:1;color:#fff;margin-bottom:4px}
@media (max-width:640px){.istats{grid-template-columns:1fr 1fr}}
.imapsec{padding:clamp(28px,4vw,48px) 0 0}
.maphead{display:grid;grid-template-columns:minmax(0,.7fr) minmax(0,1.3fr);gap:16px 48px;align-items:end;margin-bottom:16px}
.maphead h2{margin:0}.maphead p{margin:0;color:var(--ink-2)}
@media (max-width:820px){.maphead{grid-template-columns:1fr}}
.legend{display:flex;flex-wrap:wrap;gap:6px 8px;margin:0 0 10px}
.ichip{display:inline-flex;align-items:center;gap:7px;border:1px solid var(--line);background:var(--surface);color:var(--ink-2);border-radius:999px;padding:5px 11px 5px 7px;font:inherit;font-size:13px;cursor:pointer}
.ichip i{width:11px;height:11px;border-radius:50%;display:inline-block}.ichip small{color:var(--ink-3)}
.ichip[aria-pressed="true"]{border-color:var(--ink);color:var(--ink);font-weight:600}
.mapwrap{border:1px solid var(--line);border-radius:var(--radius);background:var(--surface);overflow:hidden}
@media (max-width:640px){.mapwrap{overflow-x:auto}.imap{min-width:760px}}
.imap{width:100%;height:auto;display:block;font-family:"IBM Plex Sans",sans-serif}
.imap .tile{cursor:pointer;outline:none;text-decoration:none}.imap .tile text{text-decoration:none}.imap .tile rect:first-child{transition:stroke-width .15s}
.imap .tile:hover rect:first-child,.imap .tile:focus-visible rect:first-child,.imap .tile.on rect:first-child{stroke-width:4}
.imap .tt{font-weight:600;fill:var(--ink)}.imap .tm{font-size:13.5px;fill:var(--ink-2)}
.imap .lk{fill:none;stroke:var(--signal);stroke-opacity:0;stroke-linecap:round;transition:stroke-opacity .15s;pointer-events:none}.imap .lk.on{filter:drop-shadow(0 0 2px var(--surface))}
.imap.focus .lk{stroke-opacity:0}.imap.focus .lk.on{stroke-opacity:.75}.imap .lk.rel{stroke-dasharray:7 6;stroke:var(--ink-3)}.imap.focus .lk.rel.on{stroke-opacity:.6}
.imap.focus .tile{opacity:.35}.imap.focus .tile.on{opacity:1}
.mapnote{font-size:13.5px;color:var(--ink-3);margin:10px 0 0}
.iclgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:18px}
.icl{border:1px solid var(--line);border-left:4px solid var(--c);border-radius:var(--radius);background:var(--surface);padding:20px 22px}
.icl.on{box-shadow:0 0 0 3px var(--c)}
.icl h3{font-size:20px;margin:0 0 6px;display:flex;align-items:center;gap:9px}.icl .dot{width:12px;height:12px;border-radius:50%;background:var(--c);flex:none}
.icl .meta{font-size:14px;color:var(--ink-3);margin:0 0 4px}.icl .meta b{color:var(--ink)}
.icl .who{font-size:14px;color:var(--ink-2);margin:0 0 10px}
.icl .narr{font-size:15px;color:var(--ink-2);margin:0 0 12px}.icl .narr.auto{color:var(--ink-3);font-style:italic}
.icl h4{font-size:12.5px;letter-spacing:.02em;color:var(--ink-3);margin:12px 0 4px;font-weight:600}
.ipubs{list-style:none;margin:0;padding:0}.ipubs li{margin:0 0 8px}.ipub .t{display:block;font-size:14.5px;line-height:1.35}.ipub .v{display:block;font-size:13px;color:var(--ink-3)}
ol.ipubs{padding-left:22px;list-style:decimal}
.base{list-style:none;margin:0;padding:0;font-size:14px}.base li{margin:0 0 8px;line-height:1.4}.base .v{display:block;font-size:13px;color:var(--ink-3)}
.base.big{padding-left:26px;list-style:decimal;font-size:15px;max-width:60em}.base.big li{margin:0 0 12px}
.igrid2{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:28px 48px}
@media (max-width:860px){.igrid2{grid-template-columns:1fr}}
.cmx{border-collapse:separate;border-spacing:3px;font-size:13px;width:100%}.cmx caption{caption-side:bottom;font-size:13px;color:var(--ink-3);text-align:left;padding-top:8px}
.cmx th{font-weight:500;color:var(--ink-2);padding:2px 4px;text-align:left;white-space:nowrap}.cmx thead th{vertical-align:bottom;height:78px}.cmx thead th span{writing-mode:vertical-rl;transform:rotate(180deg);display:inline-block}
.cmx td{width:38px;height:34px;text-align:center;border-radius:5px;background:color-mix(in srgb,var(--signal) calc(var(--o,0)*100%),var(--bg-2));color:var(--ink);font-weight:500}
.cmx td.self{background:transparent;color:var(--ink-3);font-weight:400}
.never{font-size:14px;color:var(--ink-3);margin:12px 0 0;max-width:60em}
.ilist{list-style:none;margin:0 0 22px;padding:0;font-size:15px}.ilist li{margin:0 0 8px;line-height:1.4}.ilist .v{color:var(--ink-3);font-size:13.5px}
.ilist.two{columns:2;column-gap:40px}.ilist.two li{break-inside:avoid}@media (max-width:640px){.ilist.two{columns:1}}
.cbars{list-style:none;margin:0;padding:0}.cbars li{display:grid;grid-template-columns:minmax(0,230px) minmax(0,1fr) 128px;gap:10px;align-items:center;margin:0 0 9px;font-size:13px}
.cbars .lab{color:var(--ink-2);line-height:1.25}.cbars .bar{display:block;height:14px;border-radius:3px;background:var(--c);min-width:2px}
.cbars .num{color:var(--ink);font-weight:600;white-space:nowrap}.cbars .num small{display:block;font-weight:400;color:var(--ink-3)}
.ich{width:100%;height:auto;display:block;margin:8px 0 0}.ich .ax{font-size:13px;fill:var(--ink-3);font-family:"IBM Plex Sans",sans-serif}
.tscroll{overflow-x:auto;max-width:100%;margin:0 0 22px}.wrap [class*="grid"]>div,.wrap [class*="grid"]>section{min-width:0}.stbl{border-collapse:collapse;width:100%;font-size:14px;min-width:760px}
.stbl th{text-align:left;font-weight:600;color:var(--ink-2);padding:8px 10px;border-bottom:1px solid var(--line);white-space:nowrap}
.stbl tbody th{font-weight:600;color:var(--ink)}.stbl tbody th small{display:block;font-weight:400;color:var(--ink-3);font-size:12.5px}
.stbl td{padding:8px 10px;border-bottom:1px solid var(--line-2);vertical-align:top}
.stbl .cls span{display:inline-flex;align-items:center;gap:6px;margin:0 10px 4px 0;white-space:nowrap}.stbl .cls i{width:9px;height:9px;border-radius:50%;background:var(--c);display:inline-block}
.how{font-size:14px;color:var(--ink-3);max-width:66em;margin:18px 0 0;line-height:1.55}.how b{color:var(--ink-2)}
'''
    js = '''
<script>
(function(){
  var map=document.querySelector('.imap'),legend=document.getElementById('legend');if(!map||!legend)return;
  var pinned='all';
  function show(c){
    var on=String(c);
    var chips=legend.querySelectorAll('.ichip');
    for(var i=0;i<chips.length;i++)chips[i].setAttribute('aria-pressed',chips[i].getAttribute('data-c')===on?'true':'false');
    var cards=document.querySelectorAll('.icl');for(var j=0;j<cards.length;j++)cards[j].classList.toggle('on',cards[j].id==='cluster-'+on);
    var tiles=map.querySelectorAll('.tile'),links=map.querySelectorAll('.lk');
    if(on==='all'){map.classList.remove('focus');for(var t=0;t<tiles.length;t++)tiles[t].classList.remove('on');for(var l=0;l<links.length;l++)links[l].classList.remove('on');return;}
    map.classList.add('focus');
    var near={};near[on]=true;
    for(var l2=0;l2<links.length;l2++){var cs=links[l2].getAttribute('data-c').split(' ');var hit=cs.indexOf(on)>=0;links[l2].classList.toggle('on',hit);if(hit){near[cs[0]]=true;near[cs[1]]=true;}}
    for(var t2=0;t2<tiles.length;t2++)tiles[t2].classList.toggle('on',!!near[tiles[t2].getAttribute('data-c')]);
  }
  legend.addEventListener('click',function(e){var b=e.target.closest('.ichip');if(!b)return;var c=b.getAttribute('data-c');
    pinned=(b.getAttribute('aria-pressed')==='true'&&c!=='all')?'all':c;show(pinned);});
  map.addEventListener('mouseover',function(e){var t=e.target.closest('.tile');if(t)show(t.getAttribute('data-c'));});
  map.addEventListener('mouseout',function(e){var t=e.target.closest('.tile');if(t)show(pinned);});
  map.addEventListener('focusin',function(e){var t=e.target.closest('.tile');if(t)show(t.getAttribute('data-c'));});
  map.addEventListener('focusout',function(){show(pinned);});
  map.addEventListener('click',function(e){var t=e.target.closest('.tile');if(t){pinned=t.getAttribute('data-c');show(pinned);}});
})();
</script>'''
    page = ns["page_shell"]("Insights | SCyPS, UMass Lowell",
                            f"The center's {N} papers, {len(R['projects'])} projects, students, and alumni read together: research clusters, collaboration, the literature the work builds on, and reach.",
                            body, footer_html, script_html + js, extra_css=css, active="insights", canonical="insights.html")
    page = ns["new_tab_links"](page)
    out = os.path.join(os.path.dirname(os.path.abspath(ns["OUT"])) or ".", "insights.html")
    open(out, "w", encoding="utf-8").write(page)
    print(f"wrote {out}: {len(page)/1024:.0f} KB; {len(C)} clusters ({n_named} named), {R['total_cites']:,} citations, {len(R['internal_cites'])} internal citations")
    return R

# ---------------------------------------------------------------- CLI: explain the clusters so names can be written
def _load_site():
    import importlib.util, io, contextlib
    spec = importlib.util.spec_from_file_location("bs", os.path.join(HERE, "build_site.py"))
    m = importlib.util.module_from_spec(spec)
    argv = sys.argv; sys.argv = ["build_site.py", "/tmp/insights_throwaway.html"]
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            try: spec.loader.exec_module(m)
            except SystemExit: pass
    finally: sys.argv = argv
    return m

if __name__ == "__main__":
    m = _load_site(); R = compute(vars(m)); P = R["P"]
    for cl in R["clusters"]:
        print(f'\n== {cl["id"]}: {cl["name"]}  [{"named" if cl["named"] else "auto"}]  n={cl["n"]} cites={cl["citations"]}  anchor={cl["anchor_doi"]}')
        print('   terms:', ", ".join(cl["terms"]), '| faculty:', dict(cl["faculty"]), '| nearest:', [R["clusters"][c]["name"] for c in cl["nearest"]])
        for i in sorted(cl["papers"], key=lambda i: -P[i]["year"]): print(f'   {P[i]["year"]} {P[i]["title"][:96]}')
        print('   projects:', [pr["title"][:50] for s, pr in cl["projects"]])
