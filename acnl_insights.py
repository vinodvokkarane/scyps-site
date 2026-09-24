#!/usr/bin/env python3
"""acnl.html: the Advanced Communication Networks Laboratory's full record, 2002 to 2026, read paper by paper.

Built from acnl_records.json: one record per paper, written from the paper itself (problem, approach, finding,
in our own words, never quoted), plus the tools, topologies, metrics, and methods found in its text, and its
authors from the director's CV (students marked there with an asterisk). No paper text is stored or published.

build_site.py calls render(globals(), footer_html, script_html).
"""
import json, os, re, math, collections, datetime

HERE = os.path.dirname(os.path.abspath(__file__))

GROUP = {  # small threads fold into the nearest large one for the charts; each paper keeps its own label
    "OBS architecture": "OBS contention and QoS",
    "Grid and e-science networking": "Advance reservation and scheduling",
    "Optical packet switching": "Manycast and anycast",
    "Data center and cloud networking": "Elastic and SDM optical networks",
    "Machine learning for networks": "Elastic and SDM optical networks",
    "Tools and reproducibility": "Elastic and SDM optical networks",
    "Physical layer modeling": "Elastic and SDM optical networks",
    "Online social network privacy": "Other collaborations",
    "Reliability modeling": "Other collaborations",
    "Edge computing and IoT": "Other collaborations",
}
ORDER = ["OBS contention and QoS", "TCP over OBS", "Survivability and protection", "Manycast and anycast",
         "Wireless sensor and access networks", "Advance reservation and scheduling", "Energy and carbon-aware networking",
         "Elastic and SDM optical networks", "Smart grid resilience and security", "Other collaborations"]
COLOR = {"OBS contention and QoS": "#1F77B4", "TCP over OBS": "#6A5ACD", "Survivability and protection": "#C2185B",
         "Manycast and anycast": "#E4572E", "Wireless sensor and access networks": "#5B8C5A",
         "Advance reservation and scheduling": "#D4A017", "Energy and carbon-aware networking": "#2CA58D",
         "Elastic and SDM optical networks": "#3F8FD2", "Smart grid resilience and security": "#8E5BB2",
         "Other collaborations": "#8A8F98"}
SUMMARY = {
    "OBS contention and QoS": "Where the lab began, at UT Dallas and then UMass Dartmouth: how an optical burst switch should behave when two bursts want the same port. Burst segmentation, prioritized assembly, early drop and wavelength grouping for absolute QoS, path clustering, burst cloning, retransmission, and forward redundancy, each a different answer to losing data in a network with no optical buffers.",
    "TCP over OBS": "The follow-on question: what those burst losses do to TCP, which reads a random loss as congestion. Split TCP, source ordering to undo reordering from load balancing, coordinated loss recovery across layers, and fairness studies.",
    "Survivability and protection": "A thread that runs the whole record. It starts with dual homing across the IP and optical layers, moves to protecting multicast destinations and many-to-many communication in data centers and content-centric networks, and reaches fast service prioritization for 6G transport.",
    "Manycast and anycast": "Reaching any k of n destinations instead of all of them. Manycast and anycast over OBS and wavelength-routed networks, impairment-aware and crosstalk-aware variants, ILP, tabu search, and ant colony methods, analytical blocking models, and an anycast extension of ESnet's OSCARS for the Marine Corps and the Department of Energy.",
    "Wireless sensor and access networks": "A parallel line with collaborators at UMass Dartmouth and the University of Rhode Island: fault-tolerant dual-homed sensor and access networks, energy-efficient target monitoring, railway and acoustic sensing, and a sustained body of reliability modeling for sensor networks.",
    "Advance reservation and scheduling": "The largest thread, driven by science networks. Advance and immediate reservation, lightpath switching, delayed allocation (the basis of the lab's patent), scheduled multicast and manycast overlays, parallel circuits and path computation for ESnet's OSCARS, and co-scheduling of scientific workflows.",
    "Energy and carbon-aware networking": "Routing and grooming that know where the power comes from and what it costs: renewable-aware overlays and grooming, real-time electricity prices, emissions across power markets, and a machine learning balance of cost against emissions.",
    "Elastic and SDM optical networks": "The current optical line: elastic, multi-band, and space-division multiplexed networks with crosstalk-, nonlinearity-, and QoT-aware allocation, grooming, band and spatial scaling trade-offs, reinforcement learning routing, and the open-source FUSION framework that the recent papers are built on.",
    "Smart grid resilience and security": "The lab's newest thread: keeping the grid observable and recoverable. PMU placement, networking, and routing, cyber restoration after attacks and disasters, distribution system reconfiguration with networked microgrids, cyber-constrained dispatch, and attack detection in smart meters.",
    "Other collaborations": "Work outside the main lines: online social network privacy, reliability of standby systems and storage networks, and food recognition on edge computing.",
}
TOOL_ORDER = ["ns-2", "OMNeT++", "CPLEX", "Gurobi", "MATLAB", "OSCARS", "GENI", "MATPOWER", "Gym environments", "Stable-Baselines", "FUSION"]

def load():
    return json.load(open(os.path.join(HERE, "acnl_records.json"), encoding="utf-8"))

def render(ns, footer_html, script_html):
    esc = ns["esc"]; R = load()
    for r in R: r["group"] = GROUP.get(r["thread"], r["thread"])
    n_read = sum(1 for r in R if r.get("read", True)); n_listed = len(R) - n_read
    years = list(range(min(r["year"] for r in R), max(r["year"] for r in R) + 1))
    by_year = collections.Counter(r["year"] for r in R)
    n_j = sum(1 for r in R if r["kind"] == "journal"); n_c = sum(1 for r in R if r["kind"] == "conference")
    # people
    name_of = {}
    for r in R:
        for a, k in zip(r["authors"], r["author_keys"]): name_of.setdefault(k, a)
    me = "vokkarane_v"
    coauth = collections.Counter(k for r in R for k in set(r["author_keys"]) if k and k != me)
    # Students: the site's own rosters (current students, Ph.D. alumni, postdocs) plus anyone the CV marks with an
    # asterisk. The CV stopped marking students in recent entries, so the roster is what catches the current group.
    def akey(n):
        p = re.sub(r"\*", "", n).replace(".", " ").split()
        return (p[-1].lower() + "_" + p[0][0].lower()) if p else ""
    roster = [s["name"] for s in ns.get("STUDENTS", []) if s.get("advisor", "Vinod M. Vokkarane") == "Vinod M. Vokkarane"] + list(ns.get("ALUMNI_PROFILES", {}).keys()) + [n for n, _ in ns.get("ALUMNI_POSTDOC", [])]
    for n in roster: name_of[akey(n)] = n
    student_keys = {akey(n) for n in roster} | {k for r in R for k in r["students"]}
    students = collections.Counter(k for r in R for k in set(r["author_keys"]) if k in student_keys)
    first_auth = collections.Counter(r["author_keys"][0] for r in R if r["author_keys"] and r["author_keys"][0] in students)
    stud_years = {k: (min(r["year"] for r in R if k in r["author_keys"]), max(r["year"] for r in R if k in r["author_keys"])) for k in students}
    stud_groups = {k: collections.Counter(r["group"] for r in R if k in r["author_keys"]).most_common(1)[0][0] for k in students}
    ext = [(k, n) for k, n in coauth.most_common() if k not in students][:14]

    # ---- stacked bars: papers per year by thread
    groups = [g for g in ORDER if any(r["group"] == g for r in R)]
    ymax = max(by_year.values()); W = 1000; left = 36; bw = (W - left - 10) / len(years)
    bars = []
    for k, y in enumerate(years):
        y0 = 0
        for g in groups:
            n = sum(1 for r in R if r["year"] == y and r["group"] == g)
            if not n: continue
            h = n / ymax * 190
            bars.append(f'<rect x="{left + k * bw + 2:.1f}" y="{215 - y0 - h:.1f}" width="{bw - 4:.1f}" height="{h:.1f}" fill="{COLOR[g]}"><title>{esc(g)}: {n} in {y}</title></rect>')
            y0 += h
        if y % 2 == 0 or len(years) < 14:
            bars.append(f'<text class="ax" x="{left + k * bw + bw / 2:.1f}" y="234" text-anchor="middle">{y}</text>')
    for v in range(0, ymax + 1, 4):
        yy = 215 - v / ymax * 190
        bars.append(f'<line x1="{left}" x2="{W - 10}" y1="{yy:.1f}" y2="{yy:.1f}" class="grid"/><text class="ax" x="{left - 6}" y="{yy + 4:.1f}" text-anchor="end">{v}</text>')
    year_svg = f'<svg class="ich" viewBox="0 0 {W} 244" role="img" aria-label="Papers per year, by research thread">{"".join(bars)}</svg>'
    legend = "".join(f'<span class="lg"><i style="background:{COLOR[g]}"></i>{esc(g)}</span>' for g in groups)

    # ---- the arc: each thread's span as a band
    rows = []
    x0, x1 = 262, 975
    def xp(y): return x0 + (y - years[0]) / (years[-1] - years[0]) * (x1 - x0)
    for j, g in enumerate(groups):
        ys = sorted(r["year"] for r in R if r["group"] == g); yc = collections.Counter(ys)
        y = 18 + j * 30
        rows.append(f'<text class="al" x="{x0 - 10}" y="{y + 5}" text-anchor="end">{esc(g)}</text>')
        rows.append(f'<line x1="{xp(ys[0]):.1f}" x2="{xp(ys[-1]):.1f}" y1="{y}" y2="{y}" stroke="{COLOR[g]}" stroke-width="3" stroke-linecap="round" opacity=".35"/>')
        for yr, n in yc.items():
            rows.append(f'<circle cx="{xp(yr):.1f}" cy="{y}" r="{3 + 2.2 * math.sqrt(n):.1f}" fill="{COLOR[g]}"><title>{esc(g)}: {n} in {yr}</title></circle>')
    for yr in years:
        if yr % 4 == 2 or yr == years[-1]:
            rows.append(f'<text class="ax" x="{xp(yr):.1f}" y="{18 + len(groups) * 30 + 6}" text-anchor="middle">{yr}</text>')
    arc_svg = f'<svg class="ich" viewBox="0 0 1000 {30 + len(groups) * 30}" role="img" aria-label="When each research thread was active">{"".join(rows)}</svg>'

    # ---- thread cards
    cards = []
    for g in groups:
        rs = sorted([r for r in R if r["group"] == g], key=lambda r: (-r["year"], r["title"]))
        yrs = sorted(r["year"] for r in rs)
        tools = collections.Counter(t for r in rs for t in r["tags"]["tool"] if t not in ("ESnet",))
        topo = collections.Counter(t for r in rs for t in r["tags"]["topology"])
        meth = collections.Counter(t for r in rs for t in r["tags"]["method"] if t != "simulation")
        stu = collections.Counter(k for r in rs for k in set(r["author_keys"]) if k in student_keys)
        def chips(c, n=5): return ", ".join(f"{esc(k)} ({v})" for k, v in c.most_common(n)) or "none named"
        key = [r for r in rs if r["kind"] == "journal" and r.get("read", True)][:3] or [r for r in rs if r.get("read", True)][:3] or rs[:3]
        keyl = "".join(f'<li>{link(esc, r)} <span class="v">{r["year"]}</span></li>' for r in key)
        cards.append(f'''<article class="icl" id="t-{slug(g)}" style="--c:{COLOR[g]}">
  <h3><span class="dot"></span>{esc(g)}</h3>
  <p class="meta"><b>{len(rs)}</b> papers, {sum(1 for r in rs if r["kind"]=="journal")} in journals, {yrs[0]} to {yrs[-1]}</p>
  <p class="narr">{esc(SUMMARY.get(g, ""))}</p>
  <dl class="facts"><dt>Methods</dt><dd>{chips(meth)}</dd><dt>Topologies</dt><dd>{chips(topo, 4)}</dd><dt>Tools</dt><dd>{chips(tools, 4)}</dd>
  <dt>Students</dt><dd>{", ".join(esc(name_of.get(k, k)) for k, _ in stu.most_common(6)) or "none marked"}</dd></dl>
  <h4>Journal papers to start with</h4><ul class="ipubs">{keyl}</ul>
</article>''')

    # ---- tools, topologies, methods over time (heat rows)
    def heat(cat, items, label):
        cols = years
        head = "".join(f'<th scope="col"><span>{y if (y % 2 == 0) else ""}</span></th>' for y in cols)
        body = ""
        for it in items:
            cnt = collections.Counter(r["year"] for r in R if it in r["tags"][cat])
            if not cnt: continue
            mx = max(cnt.values())
            tds = "".join(f'<td style="--o:{(0.18 + 0.82 * cnt[y] / mx) if cnt[y] else 0:.2f}" title="{esc(it)}: {cnt[y]} in {y}"></td>' for y in cols)
            body += f'<tr><th scope="row">{esc(it)} <small>{sum(cnt.values())}</small></th>{tds}</tr>'
        return f'<div class="tscroll"><table class="heat"><caption>{esc(label)}</caption><thead><tr><th></th>{head}</tr></thead><tbody>{body}</tbody></table></div>'
    tools_tbl = heat("tool", TOOL_ORDER, "Tools named in the papers, by year")
    topo_tbl = heat("topology", ["NSFNET", "USNET", "ESnet backbone", "Pan-European", "German", "JPN12/48", "IEEE bus system", "Torus/ring/mesh (synthetic)"], "Evaluation topologies, by year")
    meth_tbl = heat("method", ["analytical model", "heuristic", "ILP/MILP", "metaheuristic", "reinforcement learning", "deep learning", "testbed/experiment"], "Methods, by year")
    metric_tbl = heat("metric", ["blocking probability", "burst/packet loss", "throughput", "BER", "OSNR/GSNR/QoT", "spectrum utilization", "fragmentation", "energy/power", "carbon/emissions", "observability", "restoration", "accuracy/F1"], "What the papers measure, by year")

    # ---- people
    st_rows = "".join(
        f'<tr><th scope="row">{esc(name_of.get(k, k))}</th><td>{n}</td><td>{first_auth.get(k, 0)}</td><td>{stud_years[k][0]}{"" if stud_years[k][0]==stud_years[k][1] else " to " + str(stud_years[k][1])}</td>'
        f'<td><span class="gdot" style="--c:{COLOR[stud_groups[k]]}"><i></i>{esc(stud_groups[k])}</span></td></tr>'
        for k, n in sorted(students.items(), key=lambda kv: (-kv[1], kv[0])))
    ext_html = "".join(f'<li>{esc(name_of.get(k, k))} <span class="v">{n} papers</span></li>' for k, n in ext)

    # ---- the searchable record
    items = []
    for r in sorted(R, key=lambda r: (-r["year"], r["title"])):
        tags = r["tags"]["method"][:3] + r["tags"]["topology"][:2] + [t for t in r["tags"]["tool"] if t != "ESnet"][:2]
        detail = (f'<dl class="rd"><dt>Problem</dt><dd>{esc(r["problem"])}</dd><dt>Approach</dt><dd>{esc(r["approach"])}</dd><dt>Finding</dt><dd>{esc(r["finding"])}</dd></dl>'
                  if r.get("read", True) else '<p class="unread">Listed from the CV. No PDF is on file yet, so this one has not been read.</p>')
        tagspans = "".join('<span class="tg">' + esc(t) + '</span>' for t in tags)
        blob = " ".join([r["title"], r["thread"], r["problem"], r["approach"], r["finding"], " ".join(r["authors"]), " ".join(tags)]).lower()
        items.append(f'''<li class="rec" data-g="{esc(slug(r["group"]))}" data-s="{esc(blob)}" style="--c:{COLOR[r["group"]]}">
  <div class="rt">{link(esc, r)}</div>
  <div class="rv">{esc(", ".join(r["authors"]))}. {r["year"]}, {esc(r["kind"])}</div>
  {detail}
  <div class="rtags"><span class="gdot" style="--c:{COLOR[r["group"]]}"><i></i>{esc(r["thread"])}</span>{tagspans}</div>
</li>''')
    filt = '<button class="ichip" type="button" data-g="all" aria-pressed="true">All threads</button>' + "".join(
        f'<button class="ichip" type="button" data-g="{slug(g)}" aria-pressed="false"><i style="background:{COLOR[g]}"></i>{esc(g)}</button>' for g in groups)

    body = f'''<div class="ihero">
  <div class="wrap">
    <p class="crumb"><a href="labs.html">Labs</a></p>
    <h1>The Advanced Communication Networks Laboratory, 2002 to 2026</h1>
    <p class="q">Every publication from the lab, from UT Dallas, UMass Dartmouth, and UMass Lowell. {n_read} of the {len(R)} have been read and recorded: what problem each took on, how, and what it found. The other {n_listed} are listed from the CV until their PDFs are on file. All of them are grouped into the research threads they form and traced through the tools, networks, and people behind them.</p>
    <div class="istats"><div><b>{len(R)}</b>publications</div><div><b>{n_read}</b>read in full</div><div><b>{n_j}</b>journal papers</div><div><b>{len(students)}</b>students and postdocs</div><div><b>{len(groups)}</b>research threads</div></div>
  </div>
</div>
<section class="imapsec">
  <div class="wrap">
    <div class="maphead"><h2>The arc</h2><p>Each row is a research thread; each dot is a year it produced papers, sized by how many. Optical burst switching gives way to scheduling, manycast, and energy-aware networking, then to elastic and space-division optics and the smart grid.</p></div>
    {arc_svg}
    <h3 class="sub">Papers per year</h3>
    <div class="legend">{legend}</div>
    {year_svg}
  </div>
</section>
<section>
  <div class="wrap">
    <div class="shead"><h2>Research threads</h2><p>Each paper was read and assigned to the thread it contributes to. The summaries are written from those records; the methods, topologies, and tools are counted from the papers' own text.</p></div>
    <div class="iclgrid">{"".join(cards)}</div>
  </div>
</section>
<section class="tint">
  <div class="wrap">
    <div class="shead"><h2>How the work was done</h2><p>The instruments of the lab's research over time: which tools the papers name, which networks they are evaluated on, which methods they use, and what they measure. Darker cells mean more papers that year.</p></div>
    <div class="igrid2"><div>{tools_tbl}{meth_tbl}</div><div>{topo_tbl}{metric_tbl}</div></div>
  </div>
</section>
<section>
  <div class="wrap">
    <div class="shead"><h2>People</h2><p>The lab's students and postdocs, from the group's rosters and the director's CV, with their papers in this record, how many they led as first author, their years, and the thread most of their work falls in. Collaborators are the co-authors outside the group who appear most often.</p></div>
    <div class="tscroll"><table class="stbl"><thead><tr><th scope="col">Student or postdoc</th><th scope="col">Papers</th><th scope="col">First author</th><th scope="col">Years</th><th scope="col">Main thread</th></tr></thead><tbody>{st_rows}</tbody></table></div>
    <h3>Most frequent collaborators</h3><ul class="ilist two">{ext_html}</ul>
  </div>
</section>
<section class="tint">
  <div class="wrap">
    <div class="shead"><h2>The record</h2><p>All {len(R)} publications, with the problem, approach, and finding for the {n_read} that have been read. Search any word, author, method, or network, or pick a thread.</p></div>
    <div class="rfilter"><label for="rq" class="vh">Search the record</label><input id="rq" type="search" placeholder="Search: segmentation, NSFNET, Gurobi, Rezaee, observability">
    <div class="legend" id="rg">{filt}</div><p class="rcount" id="rc" aria-live="polite"></p></div>
    <ol class="recs" id="recs">{"".join(items)}</ol>
    <p class="how"><b>How this page is made.</b> The lab\'s papers were read one at a time, and each was recorded in our own words as a problem, an approach, and a finding; no text from the papers is reproduced. Tools, topologies, metrics, and methods are counted from each paper's text. Authors and student status come from the director's CV. The full list comes from the director\'s CV; the {n_listed} publications without a PDF on file count toward the timeline, threads, and people, but not toward tools, methods, or metrics. Records reflect abstracts, introductions, and conclusions; reported numbers from results sections are the next layer.</p>
  </div>
</section>
'''
    css = '''
.ihero{background:var(--navy);color:var(--on-navy);padding:clamp(40px,6vw,72px) 0 clamp(28px,4vw,44px)}
.ihero .crumb{font-size:14px;margin:0 0 10px}.ihero .crumb a{color:var(--on-navy-3)}.ihero h1{color:#fff;max-width:16em;font-size:clamp(32px,4.4vw,54px)}
.ihero .q{font-size:clamp(17px,1.4vw,20px);line-height:1.5;color:var(--on-navy-2);max-width:40em;margin:18px 0 26px}
.istats{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:12px;max-width:820px}
.istats div{border-top:1px solid rgba(255,255,255,.22);padding-top:10px;font-size:13.5px;color:var(--on-navy-2)}
.istats b{display:block;font-family:"Fraunces",Georgia,serif;font-weight:500;font-size:clamp(26px,3vw,38px);line-height:1;color:#fff;margin-bottom:4px}
@media (max-width:640px){.istats{grid-template-columns:1fr 1fr}}
.imapsec{padding:clamp(28px,4vw,48px) 0}.maphead{display:grid;grid-template-columns:minmax(0,.7fr) minmax(0,1.3fr);gap:16px 48px;align-items:end;margin-bottom:12px}
.maphead h2{margin:0}.maphead p{margin:0;color:var(--ink-2)}@media (max-width:820px){.maphead{grid-template-columns:1fr}}
.sub{margin:28px 0 8px;font-size:18px}
.ich{width:100%;height:auto;display:block}.ich .ax{font-size:12.5px;fill:var(--ink-3);font-family:"IBM Plex Sans",sans-serif}
.ich .al{font-size:13px;fill:var(--ink-2);font-family:"IBM Plex Sans",sans-serif}.ich .grid{stroke:var(--line-2)}
.legend{display:flex;flex-wrap:wrap;gap:6px 14px;margin:0 0 8px;font-size:13px;color:var(--ink-2)}
.lg{display:inline-flex;align-items:center;gap:6px}.lg i,.ichip i,.gdot i{width:10px;height:10px;border-radius:50%;display:inline-block}
.lg i{background:var(--c)}.gdot i{background:var(--c)}.gdot{display:inline-flex;align-items:center;gap:6px}
.iclgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:18px}
.icl{border:1px solid var(--line);border-top:4px solid var(--c);border-radius:var(--radius);background:var(--surface);padding:18px 22px}
.icl h3{font-size:20px;margin:0 0 6px;display:flex;align-items:center;gap:9px}.icl .dot{width:12px;height:12px;border-radius:50%;background:var(--c);flex:none}
.icl .meta{font-size:14px;color:var(--ink-3);margin:0 0 8px}.icl .meta b{color:var(--ink)}.icl .narr{font-size:15px;color:var(--ink-2);margin:0 0 10px}
.facts,.rd{border:0!important;box-shadow:none!important;background:none!important;padding:0!important;border-radius:0!important}
.facts{display:grid;grid-template-columns:auto 1fr;gap:3px 12px;font-size:13.5px;margin:0 0 10px}.facts dt{color:var(--ink-3)}.facts dd{margin:0;color:var(--ink-2)}
.icl h4{font-size:12.5px;color:var(--ink-3);margin:10px 0 4px;font-weight:600}
.ipubs{list-style:none;margin:0;padding:0}.ipubs li{margin:0 0 6px;font-size:14px;line-height:1.35}.ipubs .v{color:var(--ink-3);font-size:13px}
.igrid2{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:24px 40px}@media (max-width:980px){.igrid2{grid-template-columns:1fr}}
.tscroll{overflow-x:auto;margin:0 0 22px}
.heat{border-collapse:separate;border-spacing:2px;font-size:12.5px;width:100%}.heat caption{text-align:left;font-weight:600;color:var(--ink-2);font-size:14px;padding-bottom:6px}
.heat thead th{font-weight:400;color:var(--ink-3);height:22px}.heat thead th span{font-size:11px}
.heat th[scope=row]{text-align:left;white-space:nowrap;color:var(--ink-2);font-weight:500;padding-right:8px}.heat th small{color:var(--ink-3);font-weight:400}
.heat td{min-width:12px;height:18px;border-radius:3px;background:color-mix(in srgb,var(--signal) calc(var(--o,0)*100%),var(--bg-2))}
.stbl{border-collapse:collapse;width:100%;font-size:14px;min-width:620px}.stbl th{text-align:left;font-weight:600;color:var(--ink-2);padding:7px 10px;border-bottom:1px solid var(--line)}
.stbl tbody th{color:var(--ink)}.stbl td{padding:7px 10px;border-bottom:1px solid var(--line-2)}
.ilist{list-style:none;margin:0;padding:0;font-size:15px}.ilist li{margin:0 0 7px}.ilist .v{color:var(--ink-3);font-size:13.5px}
.ilist.two{columns:2;column-gap:40px}@media (max-width:640px){.ilist.two{columns:1}}
.rfilter input{width:100%;max-width:560px;font:inherit;font-size:15px;padding:10px 12px;border:1px solid var(--line);border-radius:8px;background:var(--surface);color:var(--ink);margin:0 0 10px}
.ichip{display:inline-flex;align-items:center;gap:7px;border:1px solid var(--line);background:var(--surface);color:var(--ink-2);border-radius:999px;padding:5px 11px 5px 8px;font:inherit;font-size:13px;cursor:pointer}
.ichip[aria-pressed="true"]{border-color:var(--ink);color:var(--ink);font-weight:600}.rcount{font-size:13.5px;color:var(--ink-3);margin:4px 0 12px}
.recs{list-style:none;margin:0;padding:0;display:grid;gap:10px}
.rec{border:1px solid var(--line);border-left:4px solid var(--c);border-radius:8px;background:var(--surface);padding:12px 16px}
.rt{font-size:15.5px;font-weight:600;line-height:1.35}.rv{font-size:13px;color:var(--ink-3);margin:2px 0 8px}
.rd{display:grid;grid-template-columns:auto 1fr;gap:3px 12px;font-size:14px;margin:0 0 8px}.rd dt{color:var(--ink-3)}.rd dd{margin:0;color:var(--ink-2)}
.rtags{display:flex;flex-wrap:wrap;gap:6px 8px;font-size:12.5px;color:var(--ink-2)}.tg{border:1px solid var(--line);border-radius:999px;padding:1px 8px;color:var(--ink-3)}
.unread{font-size:14px;color:var(--ink-3);font-style:italic;margin:0 0 8px}
.how{font-size:14px;color:var(--ink-3);max-width:66em;margin:22px 0 0;line-height:1.55}.how b{color:var(--ink-2)}
.vh{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)}
'''
    js = '''
<script>
(function(){
  var q=document.getElementById('rq'),rg=document.getElementById('rg'),out=document.getElementById('rc');
  var recs=[].slice.call(document.querySelectorAll('#recs .rec')),g='all';
  function apply(){var t=(q.value||'').toLowerCase().trim(),n=0;
    recs.forEach(function(r){var ok=(g==='all'||r.getAttribute('data-g')===g)&&(!t||t.split(/\\s+/).every(function(w){return r.getAttribute('data-s').indexOf(w)>-1;}));
      r.hidden=!ok;if(ok)n++;});
    out.textContent=n===recs.length?'Showing all '+n+' papers':'Showing '+n+' of '+recs.length+' papers'+(n?'':'. Nothing matches; try fewer words.');}
  q.addEventListener('input',apply);
  rg.addEventListener('click',function(e){var b=e.target.closest('.ichip');if(!b)return;g=b.getAttribute('data-g');
    rg.querySelectorAll('.ichip').forEach(function(x){x.setAttribute('aria-pressed',String(x===b));});apply();});
  apply();
})();
</script>'''
    page = ns["page_shell"]("ACNL research record | SCyPS, UMass Lowell",
                            f"The Advanced Communication Networks Laboratory's {len(R)} publications, 2002 to 2026, read and organized by research thread, method, network, and student.",
                            body, footer_html, script_html + js, extra_css=css, active="labs", canonical="acnl.html")
    page = ns["new_tab_links"](page)
    out = os.path.join(os.path.dirname(os.path.abspath(ns["OUT"])) or ".", "acnl.html")
    open(out, "w", encoding="utf-8").write(page)
    print(f"wrote {out}: {len(page)/1024:.0f} KB; {len(R)} papers, {len(students)} students, {len(groups)} threads")

def slug(s): return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")

def link(esc, r):
    t = esc(r["title"])
    return f'<a href="https://doi.org/{esc(r["doi"])}">{t}</a>' if r.get("doi") else t
