#!/usr/bin/env python3
"""The Advanced Communication Networks Laboratory website, built as a subsite of the center site at /acnl/.

    python3 build_acnl_site.py          (build_site.py runs this at the end of every build)

Everything comes from the same records the center site uses: the director's profile and CV, the ACNL research
record (acnl_records.json, 204 publications since 2002), the awards where the director is an investigator, the
students he advises, the lab's alumni, and the lab photos. Pages: index, research, people, publications,
projects, software, join.
"""
import os, sys, json, re, datetime, importlib.util, html, collections

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("bs", os.path.join(HERE, "build_site.py")); bs = importlib.util.module_from_spec(spec)
_argv = sys.argv; sys.argv = ["build_site.py", "/tmp/acnl_site_throwaway.html"]; sys.path.insert(0, HERE); spec.loader.exec_module(bs); sys.argv = _argv
esc = bs.esc
OUT = os.path.join(HERE, "acnl"); os.makedirs(OUT, exist_ok=True)
D = bs.FACULTY["director"]
R = json.load(open(os.path.join(HERE, "acnl_records.json"), encoding="utf-8"))
SITE = "https://smartcyberphysical.org/"
year = datetime.date.today().year

# ---------------------------------------------------------------- shared pieces
students = [s for s in bs.STUDENTS if s.get("advisor") == D["name"]]
projects = [p for p in bs.PROJECTS if D["name"] in {n for n, _ in bs.project_people(p)} or "Vokkarane" in p.get("team", "")]
active = [p for p in projects if p.get("tag") in ("Active", "New in 2026")]
center_papers = [p for p in bs.P if "Vokkarane" in p["faculty"]]
n_rec = len(R); n_read = sum(1 for r in R if r.get("read", True)); n_journal = sum(1 for r in R if r["kind"] == "journal")
threads = collections.Counter(r["thread"] for r in R)
by_year = collections.Counter(r["year"] for r in R)
alumni_phd = bs.ALUMNI_PHD_OLD
alumni_postdoc = bs.ALUMNI_POSTDOC
spot = max(bs.SPOTLIGHTS, key=lambda s: s["ym"]) if bs.SPOTLIGHTS else None

def img(key): return bs.img_src(key)
def head(p): return bs.stu_avatar(p)

NAV = [("index", "Home", "index.html"), ("research", "Research", "research.html"), ("insights", "Insights", "insights.html"),
       ("people", "People", "people.html"), ("publications", "Publications", "publications.html"), ("projects", "Projects", "projects.html"),
       ("software", "Software", "software.html"), ("join", "Join", "join.html")]

CSS = """
:root{--navy:#0E2036;--ink:#0E2036;--ink-2:#3A4756;--ink-3:#5B6B82;--line:#D5DCE5;--bg:#F6F8FB;--surface:#fff;--acc:#B23A2C;--acc-2:#F4E3E0;--teal:#0A777F;--radius:14px}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){--ink:#EEF2F7;--ink-2:#C9D3DF;--ink-3:#9AA8BA;--line:#2C3B4F;--bg:#0F1826;--surface:#16223A;--acc:#F08A7C;--acc-2:#3A2320}}
:root[data-theme=dark]{--ink:#EEF2F7;--ink-2:#C9D3DF;--ink-3:#9AA8BA;--line:#2C3B4F;--bg:#0F1826;--surface:#16223A;--acc:#F08A7C;--acc-2:#3A2320}
@font-face{font-family:Fraunces;src:url(../fonts/fraunces-latin-full-normal.woff2) format("woff2");font-weight:300 900;font-display:swap}
@font-face{font-family:"IBM Plex Sans";src:url(../fonts/ibm-plex-sans-latin-400-normal.woff2) format("woff2");font-weight:400;font-display:swap}
@font-face{font-family:"IBM Plex Sans";src:url(../fonts/ibm-plex-sans-latin-500-normal.woff2) format("woff2");font-weight:500;font-display:swap}
@font-face{font-family:"IBM Plex Sans";src:url(../fonts/ibm-plex-sans-latin-600-normal.woff2) format("woff2");font-weight:600;font-display:swap}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;font-family:"IBM Plex Sans",system-ui,sans-serif;color:var(--ink);background:var(--bg);font-size:17px;line-height:1.55}
a{color:var(--teal);text-decoration:none}a:hover{text-decoration:underline}img{max-width:100%}
h1,h2,h3{font-family:Fraunces,Georgia,serif;font-weight:500;letter-spacing:-.01em;line-height:1.12}h1{font-size:clamp(34px,5vw,52px);margin:0 0 12px}h2{font-size:clamp(26px,3vw,34px);margin:0 0 14px}h3{font-size:21px;margin:22px 0 8px}
.wrap{max-width:1120px;margin:0 auto;padding:0 20px}
.strip{background:var(--navy);color:#C9DCEA;font-size:13px}.strip .wrap{display:flex;justify-content:space-between;gap:16px;min-height:30px;align-items:center}.strip a{color:#fff}
.top{background:var(--surface);border-bottom:1px solid var(--line);position:sticky;top:0;z-index:20}
.top .wrap{display:flex;align-items:center;gap:16px;min-height:62px}
.brand{display:flex;align-items:baseline;gap:10px;color:var(--ink);text-decoration:none;flex:none}.brand b{font-family:Fraunces,serif;font-size:24px;letter-spacing:.02em}.brand span{font-size:13px;color:var(--ink-3);white-space:nowrap}
.top nav{margin-left:auto;overflow-x:auto;scrollbar-width:none}.top nav::-webkit-scrollbar{display:none}.top nav ul{display:flex;gap:2px;list-style:none;margin:0;padding:0;flex-wrap:nowrap}.top nav a{display:block;padding:8px 11px;border-radius:8px;color:var(--ink-2);font-size:15px;white-space:nowrap}.top nav a.on,.top nav a:hover{background:var(--acc-2);color:var(--ink);text-decoration:none}
@media (max-width:900px){.brand span{display:none}}@media (max-width:600px){.top nav a{padding:8px 9px;font-size:14px}}
.hero{padding:56px 0 40px;border-bottom:1px solid var(--line);background:linear-gradient(180deg,var(--surface),var(--bg))}
.hero .grid{display:grid;grid-template-columns:1.3fr 1fr;gap:40px;align-items:center}@media (max-width:820px){.hero .grid{grid-template-columns:1fr}}
.kick{font-size:13px;letter-spacing:.1em;text-transform:uppercase;color:var(--acc);font-weight:600;margin:0 0 10px}
.lead{font-size:20px;color:var(--ink-2);max-width:40em}.hero img{border-radius:var(--radius);border:1px solid var(--line)}
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:26px 0 0}@media (max-width:640px){.stats{grid-template-columns:repeat(2,1fr)}}
.stats div{border-top:2px solid var(--acc);padding-top:8px;font-size:14px;color:var(--ink-3)}.stats b{display:block;font-family:Fraunces,serif;font-size:32px;color:var(--ink);line-height:1.05}
section{padding:44px 0}section+section{border-top:1px solid var(--line)}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:18px}
.card{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);padding:20px 22px}.card h3{margin:0 0 8px;font-size:20px}.card p{margin:0 0 8px;color:var(--ink-2)}.card .m{font-size:14px;color:var(--ink-3)}
.pi{display:grid;grid-template-columns:220px 1fr;gap:28px;align-items:start}@media (max-width:640px){.pi{grid-template-columns:1fr}}.pi img{border-radius:var(--radius);width:100%;height:auto}.pi img.avatar{width:220px;height:220px;border-radius:50%;object-fit:cover}
.stu{display:grid;grid-template-columns:110px 1fr;gap:18px;background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);padding:18px}.stu img.avatar{width:110px;height:110px;border-radius:50%;object-fit:cover}.stu h3{margin:0 0 4px}.stu .st{color:var(--ink-3);font-size:14px;margin:0 0 8px}.stu p{margin:0 0 6px;font-size:15.5px}
.stus{display:grid;grid-template-columns:repeat(auto-fill,minmax(420px,1fr));gap:16px}@media (max-width:480px){.stus{grid-template-columns:1fr}.stu{grid-template-columns:1fr}}
.list{list-style:none;margin:0;padding:0}.list li{padding:10px 0;border-bottom:1px solid var(--line)}.list b{color:var(--ink)}.list .v{display:block;font-size:14px;color:var(--ink-3)}
.pub{padding:10px 0;border-bottom:1px solid var(--line);font-size:15.5px}.pub .a{color:var(--ink-2)}.pub .t{font-weight:600}.pub .v{display:block;font-size:13.5px;color:var(--ink-3)}
.filters{display:flex;flex-wrap:wrap;gap:8px 10px;align-items:center;margin:0 0 14px}.filters .lab{font-size:13px;color:var(--ink-3);min-width:56px}.filters select,.filters input{font:inherit;font-size:15px;padding:7px 10px;border:1px solid var(--line);border-radius:8px;background:var(--surface);color:var(--ink)}
.count{font-size:14px;color:var(--ink-3);margin:0 0 10px}
.chip{display:inline-block;border:1px solid var(--line);border-radius:999px;padding:2px 10px;font-size:12.5px;color:var(--ink-2);margin:2px 4px 2px 0;background:var(--surface)}
.thread{display:grid;grid-template-columns:1fr 3fr;gap:20px;padding:18px 0;border-bottom:1px solid var(--line)}@media (max-width:640px){.thread{grid-template-columns:1fr}}.thread h3{margin:0}.thread .n{font-size:14px;color:var(--ink-3)}
.two{display:grid;grid-template-columns:1fr 1fr;gap:32px}@media (max-width:820px){.two{grid-template-columns:1fr}}
.note{font-size:14px;color:var(--ink-3)}.btn{display:inline-block;background:var(--acc);color:#fff;border-radius:999px;padding:10px 18px;font-weight:600}.btn:hover{text-decoration:none;filter:brightness(1.08)}
.foot{border-top:1px solid var(--line);padding:30px 0 40px;font-size:14px;color:var(--ink-3)}.foot .wrap{display:flex;flex-wrap:wrap;gap:20px 40px;justify-content:space-between}
.cloud{width:100%;height:auto;display:block;font-family:"IBM Plex Sans",sans-serif;font-weight:600}.cloud a text:hover{text-decoration:underline}.chart{width:100%;height:auto;display:block}.sfig{margin:24px 0;background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);padding:12px;max-width:680px}.sfig img{border-radius:8px}.sfig figcaption{font-size:14px;color:var(--ink-3);margin-top:8px}
.deck{position:relative;aspect-ratio:760/406;border-radius:var(--radius);overflow:hidden;border:1px solid var(--line);background:#0E2036}
.deck img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;opacity:0;transition:opacity .9s}.deck img.on{opacity:1}
.deck .dots{position:absolute;left:0;right:0;bottom:10px;display:flex;justify-content:center;gap:8px;align-items:center}
.deck .dots button{width:11px;height:11px;border-radius:50%;border:2px solid #fff;background:transparent;padding:0;cursor:pointer}.deck .dots button[aria-pressed=true]{background:#fff}
.deck .dots .pp{width:auto;height:auto;border-radius:999px;padding:2px 10px;font:600 12px "IBM Plex Sans",sans-serif;color:#fff;background:rgba(14,32,54,.55)}
.deckcap{position:absolute;left:12px;top:10px;margin:0;font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:#fff;background:rgba(14,32,54,.55);padding:3px 8px;border-radius:6px}
.archs{display:grid;grid-template-columns:repeat(auto-fit,minmax(340px,1fr));gap:18px;align-items:start}.archs img{width:100%;height:auto;display:block}
.figs{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:16px}.figs figure{margin:0;background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);padding:12px}.figs img{border-radius:8px;display:block}.figs figcaption{font-size:13.5px;color:var(--ink-3);margin-top:8px}
"""

def shell(name, title, desc, body, depth=0):
    up = "../" * depth
    nav = "".join(f'<li><a href="{up}{href}"{" class=\"on\"" if key == name else ""}>{label}</a></li>' for key, label, href in NAV)
    return f'''<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title><meta name="description" content="{esc(desc)}"><link rel="canonical" href="{SITE}acnl/{name}.html">
<link rel="icon" href="{img("favicon")}"><style>{CSS.replace("url(../fonts/", "url(" + up + "../fonts/")}</style></head><body>
<div class="strip"><div class="wrap"><span>A laboratory of the <a href="{up}../index.html">Center for Smart Cyber-Physical Systems</a>, UMass Lowell</span><span><a href="{up}../index.html">Back to the center</a></span></div></div>
<header class="top"><div class="wrap"><a class="brand" href="{up}index.html"><b>ACNL</b><span>Advanced Communication Networks Laboratory</span></a>
<nav aria-label="Lab pages"><ul>{nav}</ul></nav></div></header>
<main>{body}</main>
<footer class="foot"><div class="wrap"><div><b>Advanced Communication Networks Laboratory</b><br>Electrical and Computer Engineering, University of Massachusetts Lowell<br>Director: <a href="{up}people.html">{esc(D["name"])}</a>, <a href="mailto:{esc(D["email"])}">{esc(D["email"])}</a>, {esc(D["phone"])}</div>
<div>A laboratory of the <a href="{up}../index.html">Center for Smart Cyber-Physical Systems</a>.<br>Records shared with the center site; rebuilt with it.<br>&copy; {year} University of Massachusetts Lowell</div></div></footer>
</body></html>'''

def write(name, title, desc, body, sub=""):
    depth = 1 if sub else 0
    page = shell(name if not sub else sub, title, desc, body, depth=depth)
    # every link on the lab site opens in a new tab, as the director asked; mail links and jumps within a page stay put
    page = re.sub(r'<a (?![^>]*\btarget=)(?=[^>]*href="(?!mailto:|#))', '<a target="_blank" rel="noopener" ', page)
    folder = os.path.join(OUT, sub) if sub else OUT; os.makedirs(folder, exist_ok=True)
    open(os.path.join(folder, f"{name}.html"), "w", encoding="utf-8").write(page)

# ---------------------------------------------------------------- research threads (from the record)
THREAD_TEXT = {
    "Elastic and SDM optical networks": "How fiber networks add capacity without losing it: multi-band spectrum, multi-core and multi-fiber space-division multiplexing, and quality-of-transmission-aware allocation that decides route, band, core, channel, and modulation together. The current center of the lab's optical work.",
    "Physical layer modeling": "Models of noise, nonlinear interference, inter-core crosstalk, and pulse shaping that let planning and control tools reason about what a link can actually carry.",
    "Smart grid resilience and security": "Restoring observability and communication after attacks and disasters, detecting intrusions and false data in real time, federated learning across grid sites, and co-simulating the grid with its network. The lab's fastest-growing thread and the base of the SUMMIT testbed.",
    "Advance reservation and scheduling": "Scheduling bandwidth ahead of time for science and data-center traffic: sliding and flexible windows, lightpath switching, and multi-domain circuits, including work on ESnet's OSCARS.",
    "Manycast and anycast": "Delivering to any k of m candidate destinations, and protecting those services against failures, for distributed computing and content.",
    "Survivability and protection": "Keeping service up through failures: protection and restoration for unicast, multicast, and anycast connections, and for the grid's communication layer.",
    "OBS contention and QoS": "The lab's origins: optical burst switching, contention resolution, burst segmentation, and quality of service in bufferless optical networks.",
    "OBS architecture": "Signaling and architecture for optical burst and packet switched networks.",
    "TCP over OBS": "How transport protocols behave over burst-switched optical networks, and how to keep throughput up when bursts are dropped.",
    "Wireless sensor and access networks": "Reliability, coverage, and energy in wireless sensor networks, including work with the reliability engineering group.",
    "Energy and carbon-aware networking": "Routing and grooming that follow renewable energy and electricity price across the network.",
    "Edge computing and IoT": "Edge and IoT systems, including the DeepFood work on image-based dietary assessment.",
    "Reliability modeling": "Reliability analysis of cloud storage and other multi-state systems.",
    "Other collaborations": "Papers with collaborators outside the lab's main threads.",
}

# ---------------------------------------------------------------- analysis helpers for the insights page and student pages
THEMES = [   # (label, pattern over the title, search term for the publications page)
    ("optical burst switching", r"burst[- ]switch|\bobs\b|burst", "burst"),
    ("advance reservation", r"advance reservation|advanced reservation|sliding|scheduled", "reservation"),
    ("wavelength routing", r"wavelength|\brwa\b|lightpath", "wavelength"),
    ("elastic optical networks", r"elastic|flex[- ]?grid|spectrum", "elastic"),
    ("multi-band and space-division", r"multi-?band|space[- ]division|\bsdm\b|multi-?core|multi-?fiber|spatial", "multi-band"),
    ("quality of transmission", r"\bqot\b|quality of transmission|physical layer|impairment|nonlinear", "QoT"),
    ("manycast and anycast", r"manycast|anycast", "anycast"),
    ("multicast", r"multicast", "multicast"),
    ("survivability and protection", r"surviv|protect|restor|failure|fault", "protection"),
    ("smart grid", r"\bgrid\b|\bpmu\b|distribution system|microgrid|power system|substation", "grid"),
    ("attacks and intrusion detection", r"attack|intrusion|cyber|anomaly|false data|malware|security", "attack"),
    ("wireless sensor networks", r"wireless sensor|\bwsn", "sensor"),
    ("reliability", r"reliab", "reliability"),
    ("TCP over optical", r"\btcp\b", "TCP"),
    ("quality of service", r"\bqos\b|quality of service|differentiat", "QoS"),
    ("energy and carbon", r"energy|carbon|emission|renewable|green|electricity", "energy"),
    ("machine learning and AI", r"learning|neural|\bai\b|reinforcement|federated|intelligen|agent", "learning"),
    ("data centers and cloud", r"data center|datacenter|cloud", "data center"),
    ("science networks", r"esnet|oscars|science network|circuit", "ESnet"),
    ("scheduling", r"schedul", "scheduling"),
    ("software-defined networks", r"software[- ]defined|\bsdn\b|openflow", "software-defined"),
    ("simulation and benchmarking", r"simulat|benchmark|fusion", "simulat"),
    ("6G and edge", r"\b6g\b|\b5g\b|edge", "edge"),
    ("resilience", r"resilien", "resilien"),
]
def term_weights():
    out = []
    for label, pat, q in THEMES:
        n = sum(1 for r in R if re.search(pat, r["title"], re.I))
        if n >= 3: out.append((label, n, q))
    return sorted(out, key=lambda t: -t[1])

PALETTE = ["#B23A2C", "#0A777F", "#044978", "#8E5BB2", "#C77C00", "#2CA58D", "#3F8FD2", "#5B8C5A"]
def word_cloud_svg(W=960, H=500):
    """A cloud of the lab's research themes: size by how many of the 204 titles touch the theme, placed on a spiral
    without overlap. Each theme links to the publications page, searched for a matching term."""
    import math
    tw = term_weights()
    if not tw: return ""
    mx, mn = tw[0][1], tw[-1][1]
    placed, out = [], []
    cx, cy = W / 2, H / 2
    for k, (t, w, q) in enumerate(tw):
        fs = 15 + 36 * ((w - mn) / (mx - mn or 1)) ** 0.7
        bw, bh = 0.56 * fs * len(t) + 12, fs * 1.15
        ang, r = k * 0.9, 0.0
        for _ in range(9000):
            x, y = cx + r * math.cos(ang), cy + r * 0.62 * math.sin(ang)
            box = (x - bw / 2, y - bh / 2, x + bw / 2, y + bh / 2)
            if box[0] > 8 and box[2] < W - 8 and box[1] > 8 and box[3] < H - 8 and \
               not any(box[0] < p[2] and box[2] > p[0] and box[1] < p[3] and box[3] > p[1] for p in placed):
                placed.append(box)
                col = PALETTE[k % len(PALETTE)]
                out.append(f'<a href="publications.html?q={esc(q)}"><text x="{x:.0f}" y="{y + fs * 0.35:.0f}" font-size="{fs:.0f}" text-anchor="middle" fill="{col}"><title>{esc(t)}: {w} of {n_rec} papers</title>{esc(t)}</text></a>')
                break
            ang += 0.25; r += 0.55
    return f'<svg class="cloud" viewBox="0 0 {W} {H}" role="img" aria-label="Word cloud of the research themes in the paper titles">{"".join(out)}</svg>'

def bar_chart(pairs, W=960, H=220, color="var(--acc)", label_every=1, fmt=str):
    """A simple vertical bar chart as inline SVG: pairs of (label, value)."""
    if not pairs: return ""
    n = len(pairs); mx = max(v for _, v in pairs) or 1
    ML, MB, MT = 34, 34, 12; bw = (W - ML - 10) / n
    bars = []
    for i, (lab, v) in enumerate(pairs):
        h = (H - MB - MT) * v / mx; x = ML + i * bw
        bars.append(f'<rect x="{x + 2:.1f}" y="{H - MB - h:.1f}" width="{bw - 4:.1f}" height="{h:.1f}" rx="3" fill="{color}"><title>{esc(str(lab))}: {fmt(v)}</title></rect>')
        if i % label_every == 0: bars.append(f'<text x="{x + bw / 2:.1f}" y="{H - MB + 16}" text-anchor="middle" font-size="11.5" fill="var(--ink-3)">{esc(str(lab))}</text>')
        if v and h > 16: bars.append(f'<text x="{x + bw / 2:.1f}" y="{H - MB - h + 13:.1f}" text-anchor="middle" font-size="11" fill="#fff">{fmt(v)}</text>')
    return f'<svg class="chart" viewBox="0 0 {W} {H}" role="img" aria-label="Bar chart">{"".join(bars)}</svg>'

def papers_of(name):
    key = bs._person_key(name)
    return sorted([r for r in R if key in r.get("author_keys", [])], key=lambda r: -r["year"])

def pub_line(r):
    kinds = {"journal": "Journal", "conference": "Conference", "chapter": "Chapter", "book": "Book"}
    doi = r.get("doi") or ""; t = f'<a href="https://doi.org/{esc(doi)}">{esc(r["title"])}</a>' if doi else esc(r["title"])
    return f'<div class="pub"><span class="a">{esc(", ".join(r["authors"]))}.</span> <span class="t">{t}</span><span class="v">{kinds.get(r["kind"], r["kind"])}, {r["year"]}, {esc(r["thread"])}</span></div>'

def page_insights():
    yrs = sorted(by_year); per_year = [(y, by_year.get(y, 0)) for y in range(min(yrs), max(yrs) + 1)]
    th = threads.most_common()
    tools = collections.Counter(t for r in R for t in r["tags"].get("tool", [])).most_common(10)
    meth = collections.Counter(t for r in R for t in r["tags"].get("method", [])).most_common(10)
    metr = collections.Counter(t for r in R for t in r["tags"].get("metric", [])).most_common(10)
    topo = collections.Counter(t for r in R for t in r["tags"].get("topology", [])).most_common(8)
    coau = collections.Counter(a for r in R for a in r["authors"] if bs._person_key(a) != bs._person_key(D["name"])).most_common(12)
    stu_first = sum(1 for r in R if r.get("students") and r["author_keys"] and r["author_keys"][0] in r["students"])
    sch = bs.SCHOLAR_DATA.get(D["name"]) or {}
    def tbl(items, unit):
        return '<ul class="list">' + "".join(f'<li><b>{esc(t)}</b><span class="v">{n} {unit}</span></li>' for t, n in items) + "</ul>"
    body = f'''<section><div class="wrap"><p class="kick">Insights</p><h1>{n_rec} publications, read as one body of work</h1>
<p class="lead">What the lab has worked on, with what, and with whom, from its own record since 2002. The themes below are sized by how many of the {n_rec} paper titles touch them; click one to see the papers.</p>
<div class="card" style="padding:8px 10px 4px;margin:18px 0 0">{word_cloud_svg()}</div>
<div class="two" style="margin-top:36px"><div><h2>Papers per year</h2>{bar_chart(per_year, label_every=2)}<p class="note">{n_rec} publications, {n_journal} in journals. The record is the director's CV; {n_read} of the papers are read and summarized on the center's <a href="../acnl.html">research record</a>.</p></div>
<div><h2>Research threads</h2>{bar_chart([(t.split(" and ")[0].split(",")[0][:22], n) for t, n in th], H=220, color="var(--teal)")}<ul class="list" style="margin-top:8px">{"".join(f"<li><b>{esc(t)}</b><span class=v>{n} publications</span></li>" for t, n in th)}</ul></div></div>
<h2 style="margin-top:40px">How the work is done</h2><p class="note">Counted from the {n_read} papers that have been read; a paper can use several.</p>
<div class="cards"><div class="card"><h3>Methods</h3>{tbl(meth, "papers")}</div><div class="card"><h3>Tools and platforms</h3>{tbl(tools, "papers")}</div><div class="card"><h3>What is measured</h3>{tbl(metr, "papers")}</div><div class="card"><h3>Network topologies</h3>{tbl(topo, "papers")}</div></div>
<h2 style="margin-top:40px">Who the lab writes with</h2><div class="two"><div><ul class="list">{"".join(f"<li><b>{esc(a)}</b><span class=v>{n} joint publications</span></li>" for a, n in coau)}</ul></div>
<div><p>{stu_first} of the {n_rec} publications have a student of the lab as first author. The director's Google Scholar profile lists {sch.get("citations", 0):,} citations, an h-index of {sch.get("h", 0)}, and an i10-index of {sch.get("i10", 0)}{(", as of " + esc(sch["date"])) if sch.get("date") else ""}.</p><p>The center's <a href="../insights.html">Insights page</a> places the lab's recent work among the center's 14 research clusters, and the <a href="../people.html#collab">collaboration graph</a> shows who the director works with across the center.</p></div></div>
</div></section>'''
    write("insights", "Insights | ACNL", f"The lab's {n_rec} publications read as one body of work: research terms, papers per year, threads, methods, tools, and co-authors.", body)

def slug(name): return re.sub(r"[^a-z]+", "-", re.sub(r"\(.*?\)", "", name).lower()).strip("-")

def page_students():
    for s in students:
        ps = papers_of(s["name"]); first = [r for r in ps if r["author_keys"] and r["author_keys"][0] == bs._person_key(s["name"])]
        fig = f'<figure class="sfig"><img src="{img(s["fig"])}" alt="" width="640" height="420"><figcaption>{esc(s.get("figcap", ""))}</figcaption></figure>' if s.get("fig") and bs.IMG.get(s["fig"]) else ""
        sp = [x for x in bs.SPOTLIGHTS if s["name"] in x["students"]]
        spot_html = "".join(f'<p><a href="../../spotlight.html#{esc(x["ym"])}">Student spotlight, {esc(bs.spotlight_label(x))}: {esc(x["title"])}</a></p>' for x in sp)
        links = []
        if s["name"] in bs.SCHOLAR:
            gs = bs.SCHOLAR_DATA.get(s["name"]) or {}
            figs = ", ".join(v for v in (f'{gs["citations"]:,} citations' if gs.get("citations") else "", f'h-index {gs["h"]}' if gs.get("h") else "", f'i10-index {gs["i10"]}' if gs.get("i10") else "") if v)
            links.append(f'<a href="https://scholar.google.com/citations?user={esc(bs.SCHOLAR[s["name"]])}">Google Scholar</a>' + (f' ({figs})' if figs else ""))
        if s.get("linkedin"): links.append(f'<a href="{esc(s["linkedin"])}">LinkedIn</a>')
        threads_s = collections.Counter(r["thread"] for r in ps).most_common(3)
        body = f'''<section><div class="wrap"><p class="kick"><a href="../people.html">People</a> / doctoral student</p>
<div class="pi"><div>{head(s)}</div><div><h1 style="font-size:clamp(30px,4vw,40px)">{esc(s["name"])}</h1><p class="st">{esc(s["status"])}. Advised by {esc(D["name"])}.</p>
<p>{esc(s.get("focus", ""))}</p>{spot_html}<p class="note">{" · ".join(links)}</p>
<div class="stats" style="grid-template-columns:repeat(3,1fr);max-width:480px"><div><b>{len(ps)}</b>publications in the lab record</div><div><b>{len(first)}</b>as first author</div><div><b>{sum(1 for r in ps if r["kind"] == "journal")}</b>journal articles</div></div>
{("<p class=note style=margin-top:10px>Working mostly on " + esc(", ".join(t for t, _ in threads_s)) + ".</p>") if threads_s else ""}
</div></div>
{fig}
<h2 style="margin-top:30px">Publications</h2>{"".join(pub_line(r) for r in ps) or "<p class=note>No publications in the lab record yet.</p>"}
</div></section>'''
        write(slug(s["name"]), f"{s['name']} | ACNL", f"{s['name']}, {s['status']} in the Advanced Communication Networks Laboratory at UMass Lowell.", body, sub="students")

# ---------------------------------------------------------------- pages
# ---------------------------------------------------------------- project pages
PX = json.load(open(os.path.join(HERE, "acnl_projects.json"), encoding="utf-8"))["projects"]
FUND = json.load(open(os.path.join(HERE, "acnl_funders.json"), encoding="utf-8")) if os.path.exists(os.path.join(HERE, "acnl_funders.json")) else {}
TITLES = {}
for p_ in bs.P:
    if p_.get("doi"): TITLES[p_["doi"].lower()] = {"title": p_["title"], "year": p_["year"], "authors": p_["authors"], "venue": p_["venue"], "details": p_.get("details", ""), "doi": p_["doi"]}
for r_ in R:
    if r_.get("doi") and r_["doi"].lower() not in TITLES:
        TITLES[r_["doi"].lower()] = {"title": r_["title"], "year": r_["year"], "authors": r_["authors"], "venue": "", "details": "", "doi": r_["doi"]}
REC_BY_DOI = {r["doi"].lower(): r for r in R if r.get("doi")}

def pslug(p):
    base = p["title"].split(":")[0] if ":" in p["title"][:40] else " ".join(p["title"].split()[:5])
    return re.sub(r"[^a-z0-9]+", "-", base.lower()).strip("-")

def pextra(p):
    for k, v in PX.items():
        if p["title"].startswith(k): return v
    return {"award": [], "threads": [], "lessons": []}

def years_of(p):
    ys = [int(y) for y in re.findall(r"(20\d\d)", p.get("period", ""))]
    return (min(ys), max(ys) if len(ys) > 1 else (min(ys) + 3 if "onward" in p.get("period", "") or len(ys) == 1 else min(ys))) if ys else (None, None)

def acknowledged(p):
    aw = [a.lower() for a in pextra(p).get("award", [])]
    if not aw: return []
    seen, out = set(), []
    for d, fs in FUND.items():
        if not fs: continue
        if any(any(a in x.lower() for a in aw) for f in fs for x in f.get("award", [])):
            t = TITLES.get(d.lower())
            if t and t["title"] not in seen: seen.add(t["title"]); out.append(t)
    return sorted(out, key=lambda t: -t["year"])

def related(p, exclude):
    th = set(pextra(p).get("threads", [])); y0, y1 = years_of(p)
    if not th or not y0: return []
    return sorted([r for r in R if r["thread"] in th and y0 <= r["year"] <= y1 + 1 and r["title"] not in exclude], key=lambda r: -r["year"])

LAB_PEOPLE = {bs._person_key(s["name"]): s["name"] for s in students}
for _y, _n, _w in alumni_phd: LAB_PEOPLE[bs._person_key(_n)] = _n
def people_on(recs):
    names = collections.Counter()
    for r in recs:
        for a in r.get("authors", []):
            k = bs._person_key(a)
            if k in LAB_PEOPLE: names[LAB_PEOPLE[k]] += 1
    return names.most_common()

def ack_text(p):
    aw = [a for a in pextra(p).get("award", []) if not a.endswith("TDD")]
    spons = p["sponsor"].split(" (")[0]
    num = f" under Award No. {aw[0]}" if aw else ""
    return f"This material is based upon work supported by the {spons}{num}. Any opinions, findings, and conclusions or recommendations expressed are those of the authors and do not necessarily reflect the views of the sponsor."

def page_project(p):
    x = pextra(p); ack = acknowledged(p); ack_titles = {t["title"] for t in ack}; rel = related(p, ack_titles)
    recs_for_people = [REC_BY_DOI.get(t["doi"].lower(), {"authors": t["authors"]}) for t in ack] or rel
    ppl = people_on(recs_for_people)
    fig = ""
    for fk, ck in (("figure", "figcap"), ("figure2", "figcap2")):
        if x.get(fk) and bs.IMG.get(x[fk]):
            fig += f'<figure class="sfig" style="max-width:none;margin:0"><img src="{img(x[fk])}" alt="" loading="lazy"><figcaption>{esc(x.get(ck, ""))}</figcaption></figure>'
    ack_html = "".join(f'<div class="pub"><span class="a">{esc(", ".join(t["authors"]))}.</span> <span class="t"><a href="https://doi.org/{esc(t["doi"])}">{esc(t["title"])}</a></span><span class="v">{esc(t["venue"])}{", " + esc(t["details"]) if t["details"] else ""} ({t["year"]})</span></div>' for t in ack)
    rel_html = "".join(pub_line(r) for r in rel[:8])
    findings = [r for r in ([REC_BY_DOI.get(t["doi"].lower()) for t in ack] + rel) if r and r.get("read", True) and r.get("finding")][:4]
    find_html = "".join(f'<li><b>{esc(r["title"])}</b> ({r["year"]}): {esc(r["finding"])}</li>' for r in findings)
    lessons = "".join(f"<li>{esc(l)}</li>" for l in x.get("lessons", []))
    ppl_html = ", ".join(f'<a href="../students/{slug(n)}.html">{esc(n)}</a>' if any(s["name"] == n for s in students) else esc(n) for n, _ in ppl)
    inferred = ' <span class="note">(matched from paper acknowledgements by sponsor and year; to be confirmed)</span>' if x.get("award_note") == "inferred" else ""
    body = f'''<section><div class="wrap"><p class="kick"><a href="../projects.html">Projects</a> / {esc(p.get("tag", ""))}</p>
<h1 style="font-size:clamp(28px,3.6vw,42px)">{esc(p["title"])}</h1>
<div class="stats" style="grid-template-columns:repeat(4,1fr)"><div><b style="font-size:24px">{esc(p.get("amount", "") or "")}</b>{esc(p["sponsor"])}</div><div><b style="font-size:24px">{esc(p.get("period", ""))}</b>period</div><div><b style="font-size:24px">{len(ack)}</b>papers acknowledging the award</div><div><b style="font-size:24px">{len(ppl)}</b>lab students and alumni on the work</div></div>
<div class="two" style="margin-top:28px"><div><h2>The project</h2><p>{esc(p.get("desc", ""))}</p><p class="note">{esc(p.get("team", ""))}.</p>
{("<p class=note>Award number: " + esc(", ".join(a for a in x.get("award", []) if not a.endswith("TDD"))) + inferred + "</p>") if x.get("award") else ""}</div>
<div><h2>Students</h2>{("<p>" + ppl_html + "</p><p class=note>From the authors of " + ("the papers acknowledging this award." if ack else "the lab\\'s related work in the project period.") + "</p>") if ppl else "<p class=note>No lab students are identified on this project in the records yet.</p>"}</div></div>
{("<h2 style=margin-top:30px>Architecture</h2><div class=archs>" + fig + "</div>") if fig else ""}
{("<h2 style=margin-top:30px>What the work found</h2><ul class=list>" + find_html + "</ul><p class=note>From the lab\\'s research record, where each paper is summarized as a problem, an approach, and a finding.</p>") if find_html else ""}
{("<h2 style=margin-top:30px>Lessons learned</h2><ul class=list>" + lessons + "</ul>") if lessons else ""}
{("<h2 style=margin-top:30px>Papers acknowledging this award</h2><p class=note>From the funding information publishers register with Crossref.</p>" + ack_html) if ack_html else ""}
{("<h2 style=margin-top:30px>Related work from the lab in this period</h2><p class=note>Papers in the project\\'s research threads from its years; they may or may not acknowledge this award.</p>" + rel_html) if rel_html else ""}
<h2 style="margin-top:30px">Acknowledging this award</h2><div class="card"><p style="margin:0">{esc(ack_text(p))}</p></div>
</div></section>'''
    write(pslug(p), f"{p['title'].split(':')[0]} | ACNL", f"{p['title']}: {p['sponsor']}, {p.get('period', '')}.", body, sub="projects")

def page_index():
    highlights = [
        ("SUMMIT", "A $2.0M NSF instrument, starting October 2026, that links UMass Lowell, NYU, and West Virginia University in one testbed where real control, network, and security hardware closes the loop with a real-time grid simulation.", "../summit.html"),
        ("FUSION", "The lab's open-source optical networking simulator, a shared benchmark for multi-band and space-division multiplexed networks, used across the lab's recent JOCN papers.", "software.html"),
        ("Smart grid cyber resilience", "Intrusion detection, federated learning, and restoration planning for the grid's communication layer, with ONR, Army, and industry support.", "research.html"),
    ]
    hl = "".join(f'<div class="card"><h3><a href="{h}">{esc(t)}</a></h3><p>{esc(d)}</p></div>' for t, d, h in highlights)
    stu = "".join(f'<li><a href="people.html#{esc(s["name"].split()[-1].lower())}">{esc(s["name"])}</a><span class="v">{esc(s["status"])}</span></li>' for s in students)
    sp = ""
    if spot:
        sp = f'<div class="card" style="border-left:4px solid var(--acc)"><p class="kick">Student spotlight, {esc(bs.spotlight_label(spot))}</p><h3><a href="../spotlight.html#{esc(spot["ym"])}">{esc(spot["title"])}</a></h3><p>{esc(spot["deck"])}</p></div>'
    body = f'''<div class="hero"><div class="wrap"><div class="grid"><div>
  <p class="kick">Advanced Communication Networks Laboratory</p>
  <h1>Networks that keep working when it matters</h1>
  <p class="lead">We design and defend the communication networks behind critical infrastructure: the fiber backbone that carries AI and cloud traffic, and the control networks that keep the power grid observable and recoverable under attack. Directed by {esc(D["name"])} at UMass Lowell since 2013, and before that at UMass Dartmouth.</p>
  <div class="stats"><div><b>{n_rec}</b>publications since 2002</div><div><b>{n_journal}</b>journal articles</div><div><b>{len(students)}</b>doctoral students</div><div><b>{len(alumni_phd)}</b>Ph.D. graduates advised or co-advised</div></div>
</div><div class="deck" id="deck" aria-roledescription="carousel" aria-label="Lab life">{"".join(f'<img src="{img(k)}" alt="Members of the Advanced Communication Networks Laboratory" width="760" height="406"' + (' class="on"' if i == 0 else ' loading="lazy"') + '>' for i, k in enumerate(k for k in ["lab1", "lab2", "lab3", "lab4", "lab5", "lab6"] if bs.IMG.get(k)))}
  <div class="dots" role="group" aria-label="Choose a photo">{"".join(f'<button type="button" aria-label="Photo {i + 1}"' + (' aria-pressed="true"' if i == 0 else ' aria-pressed="false"') + '></button>' for i, _ in enumerate(k for k in ["lab1", "lab2", "lab3", "lab4", "lab5", "lab6"] if bs.IMG.get(k)))}<button type="button" class="pp" aria-label="Pause the slideshow">Pause</button></div>
  <p class="deckcap">Lab life</p></div></div></div></div>
<script>(function(){{var d=document.getElementById('deck');if(!d)return;var im=d.querySelectorAll('img'),bt=d.querySelectorAll('.dots button:not(.pp)'),pp=d.querySelector('.pp'),i=0,t=null;
var reduce=window.matchMedia&&window.matchMedia('(prefers-reduced-motion: reduce)').matches;
function go(n){{im[i].classList.remove('on');bt[i].setAttribute('aria-pressed','false');i=(n+im.length)%im.length;im[i].classList.add('on');bt[i].setAttribute('aria-pressed','true');}}
function play(){{stop();t=setInterval(function(){{go(i+1);}},4500);pp.textContent='Pause';pp.setAttribute('aria-label','Pause the slideshow');}}
function stop(){{if(t)clearInterval(t);t=null;pp.textContent='Play';pp.setAttribute('aria-label','Play the slideshow');}}
bt.forEach(function(b,n){{b.addEventListener('click',function(){{go(n);stop();}});}});pp.addEventListener('click',function(){{t?stop():play();}});
d.addEventListener('mouseenter',function(){{if(t){{clearInterval(t);t=0;}}}});d.addEventListener('mouseleave',function(){{if(t===0)play();}});
if(!reduce)play();else stop();}})();</script>
<section><div class="wrap"><h2>Right now</h2><div class="cards">{hl}{sp}</div></div></section>
<section><div class="wrap"><h2>Latest</h2><div class="two"><div><h3 style="margin-top:0">Newest papers</h3>{"".join(pub_line(r) for r in sorted(R, key=lambda r: (-r["year"], r["kind"] != "journal"))[:4])}</div>
<div><h3 style="margin-top:0">Newest awards</h3><ul class="list">{"".join(f"<li><b>{esc(p['title'].split(':')[0])}</b><span class=v>{esc(p['sponsor'].split(' (')[0])}{', ' + esc(p['amount']) if p.get('amount') else ''}{', ' + esc(p['period']) if p.get('period') else ''}</span></li>" for p in active[:4])}</ul><p class="note"><a href="projects.html">All projects</a> · <a href="insights.html">Insights across all {n_rec} papers</a></p></div></div></div></section>
<section><div class="wrap"><div class="two"><div><h2>The people</h2><ul class="list">{stu}</ul><p><a href="people.html">The director, students, and alumni</a></p></div>
<div><h2>Where the work goes</h2><p>The lab's {len(center_papers)} papers since 2019 are part of the <a href="../publications.html">center's record</a>, and its full record back to 2002, {n_rec} publications in {len(threads)} research threads, is read and summarized on the <a href="../acnl.html">research record</a> page. {len(active)} awards are active, headed by SUMMIT.</p><p><a class="btn" href="join.html">Join the lab</a></p></div></div></div></section>'''
    write("index", "Advanced Communication Networks Laboratory, UMass Lowell", f"The ACNL at UMass Lowell: optical networks and smart grid cyber resilience, directed by {D['name']}; {n_rec} publications since 2002.", body)

def page_research():
    order = [t for t, _ in threads.most_common()]
    rows = []
    for t in order:
        rs = sorted([r for r in R if r["thread"] == t], key=lambda r: -r["year"])
        yrs = f'{min(r["year"] for r in rs)} to {max(r["year"] for r in rs)}'
        top = [r for r in rs if r.get("doi")][:3]
        ex = "".join(f'<li><a href="https://doi.org/{esc(r["doi"])}">{esc(r["title"])}</a> <span class="v">{r["year"]}, {esc(r["kind"])}</span></li>' for r in top)
        rows.append(f'<div class="thread"><div><h3>{esc(t)}</h3><p class="n">{len(rs)} publications, {yrs}</p></div><div><p>{esc(THREAD_TEXT.get(t, ""))}</p><ul class="list">{ex}</ul></div></div>')
    figs = "".join(f'<figure><img src="{img(s["fig"])}" alt="" width="520" height="340"><figcaption><b>{esc(s["name"])}</b>: {esc(s.get("figcap", ""))}</figcaption></figure>' for s in students if s.get("fig") and bs.IMG.get(s["fig"]))
    body = f'''<section><div class="wrap"><p class="kick">Research</p><h1>Two questions, twenty years of answers</h1>
<p class="lead">How do you get more out of a fiber network without losing what you added? And how do you keep a power grid's communication layer observable and recoverable when it is attacked? Everything below is a thread of work on one of those questions, from the lab's own record.</p>
<h2 style="margin-top:34px">Current directions</h2><div class="cards">
<div class="card"><h3>Multi-band, space-division optical networks</h3><p>Planning and controlling networks that use several spectral bands and several fiber cores or fibers at once, with quality of transmission built into every decision. Three JOCN articles in 2026 and the FUSION platform.</p></div>
<div class="card"><h3>Grid cyber resilience</h3><p>Detecting attacks in real time, restoring measurement and communication after disasters, and learning across sites without sharing raw data. The base of the SUMMIT testbed, starting October 2026.</p></div>
<div class="card"><h3>AI in the network loop</h3><p>Reinforcement learning and multi-agent methods for resource allocation and restoration, and the trust and verification such agents need before they are allowed to act on infrastructure.</p></div>
</div>
<h2 style="margin-top:34px">Research figures</h2><div class="figs">{figs}</div>
<h2 style="margin-top:34px">The threads, 2002 to {year}</h2>{"".join(rows)}
<p class="note" style="margin-top:14px">Threads and summaries come from the <a href="../acnl.html">research record</a>, where each publication is recorded as a problem, an approach, and a finding.</p></div></section>'''
    write("research", "Research | ACNL", "The lab's research: multi-band SDM optical networks, grid cyber resilience, and AI in the network loop, with its full record since 2002 in research threads.", body)

def page_people():
    stu = "".join(f'''<div class="stu" id="{esc(s["name"].split()[-1].lower())}">{head(s)}<div><h3><a href="students/{slug(s["name"])}.html">{esc(s["name"])}</a></h3><p class="st">{esc(s["status"])}</p><p>{esc(s.get("focus", ""))}</p>
      <p class="st"><a href="students/{slug(s["name"])}.html">Profile and publications</a>{(" · <a href=https://scholar.google.com/citations?user=" + esc(bs.SCHOLAR[s["name"]]) + ">Google Scholar</a>") if s["name"] in bs.SCHOLAR else ""}</p></div></div>''' for s in students)
    phd = "".join(f'<li><b>{esc(n)}</b> <span class="v">Ph.D. {y}{", " + esc(w) if w else ""}</span></li>' for y, n, w in alumni_phd)
    pd = "".join(f'<li><b>{esc(n)}</b> <span class="v">postdoctoral researcher; now {esc(o)}</span></li>' for n, o in alumni_postdoc)
    honors = ["ECE Department Teaching Award, UMass Lowell, 2018 and 2025", "IET Premium Award 2018, best paper in IET Wireless Sensor Systems",
              "Best Paper Awards: IEEE ANTS 2016, ONDM 2015, IEEE GLOBECOM 2005; Top Paper Award, ONDM 2016; Best Poster Award, IPDPS 2013 Ph.D. Forum",
              "Best Computer Science Ph.D. Dissertation Award, University of Texas at Dallas, 2004",
              "Scholar of the Year and Chancellor's Innovation in Teaching Award, UMass Dartmouth, 2010 to 2011",
              "TPC Co-Chair, IEEE HPSR 2028; technical program committees of IEEE GLOBECOM, ICC, ANTS, and ONDM"]
    body = f'''<section><div class="wrap"><p class="kick">People</p><h1>The director, the students, and the alumni</h1>
<div class="pi" style="margin-top:20px"><img src="{img("about_vokkarane")}" alt="{esc(D["name"])}" width="220" height="220"><div>
<h2 style="margin-top:0">{esc(D["name"])}</h2><p class="st">{esc(D["title"])}{"; " + esc(D.get("title2", "")) if D.get("title2") else ""}</p>
<p>Vinod Vokkarane received his Ph.D. in computer science from the University of Texas at Dallas in 2004, where his dissertation won the department's best dissertation award, and founded the laboratory that year at UMass Dartmouth. He moved it to UMass Lowell in 2013, was a visiting scientist at MIT's Research Laboratory of Electronics from 2011 to 2014, and has been Professor of Electrical and Computer Engineering since 2016. He co-founded the Center for Smart Cyber-Physical Systems in 2019 and has directed it since 2021. His work has moved from optical burst switching and advance reservation to today's multi-band, space-division optical networks and the cyber resilience of the power grid.</p>
<p><b>Research areas:</b> {esc(D["areas"])}</p>
<h3>Honors and service</h3><ul class="list">{"".join(f"<li>{esc(h)}</li>" for h in honors)}</ul>
<p class="note"><a href="mailto:{esc(D["email"])}">{esc(D["email"])}</a>, {esc(D["phone"])}, {esc(D.get("office", ""))}. <a href="../people.html">Center profile</a>.</p></div></div>
<h2 style="margin-top:40px">Doctoral students</h2><div class="stus">{stu}</div>
<div class="two" style="margin-top:40px"><div><h2>Ph.D. alumni</h2><ul class="list">{phd}</ul></div><div><h2>Postdoctoral alumni</h2><ul class="list">{pd}</ul><p class="note">Master's and undergraduate alumni are listed on the center's <a href="../alumni.html">alumni page</a>.</p></div></div></div></section>'''
    write("people", "People | ACNL", f"{D['name']} and the doctoral students and alumni of the Advanced Communication Networks Laboratory.", body)

def page_publications():
    kinds = {"journal": "Journal", "conference": "Conference", "chapter": "Chapter", "book": "Book"}
    items = []
    for r in sorted(R, key=lambda r: (-r["year"], r["kind"] != "journal", r["title"])):
        au = ", ".join(r["authors"]); doi = r.get("doi") or ""
        t = f'<a href="https://doi.org/{esc(doi)}">{esc(r["title"])}</a>' if doi else esc(r["title"])
        items.append(f'<div class="pub" data-y="{r["year"]}" data-k="{esc(r["kind"])}" data-t="{esc(r["thread"])}" data-s="{esc((r["title"] + " " + au + " " + r["thread"]).lower())}"><span class="a">{esc(au)}.</span> <span class="t">{t}</span><span class="v">{kinds.get(r["kind"], r["kind"])}, {r["year"]}, {esc(r["thread"])}{"" if r.get("read", True) else " (listed from the CV, not yet read)"}</span></div>')
    yopts = "".join(f'<option value="{y}">{y}</option>' for y in sorted(by_year, reverse=True))
    topts = "".join(f'<option value="{esc(t)}">{esc(t)} ({n})</option>' for t, n in threads.most_common())
    body = f'''<section><div class="wrap"><p class="kick">Publications</p><h1>{n_rec} publications, 2002 to {max(by_year)}</h1>
<p class="lead">{n_journal} journal articles, {sum(1 for r in R if r["kind"] == "conference")} conference papers, and {sum(1 for r in R if r["kind"] in ("chapter", "book"))} chapters and books, from the director's CV, with DOIs where they exist. {n_read} of them are read and summarized on the <a href="../acnl.html">research record</a>.</p>
<div class="filters"><span class="lab">Year</span><select id="fy"><option value="">All</option>{yopts}</select><span class="lab">Type</span><select id="fk"><option value="">All</option><option value="journal">Journal</option><option value="conference">Conference</option><option value="chapter">Chapter</option><option value="book">Book</option></select>
<span class="lab">Thread</span><select id="ft"><option value="">All</option>{topts}</select><span class="lab">Search</span><input id="fs" type="search" placeholder="title, author, or thread"></div>
<p class="count" id="cnt"></p><div id="pubs">{"".join(items)}</div></div></section>
<script>(function(){{var y=document.getElementById('fy'),k=document.getElementById('fk'),t=document.getElementById('ft'),s=document.getElementById('fs'),c=document.getElementById('cnt'),ps=document.querySelectorAll('#pubs .pub');
function run(){{var n=0,q=s.value.trim().toLowerCase();for(var i=0;i<ps.length;i++){{var p=ps[i];var ok=(!y.value||p.dataset.y===y.value)&&(!k.value||p.dataset.k===k.value)&&(!t.value||p.dataset.t===t.value)&&(!q||p.dataset.s.indexOf(q)>=0);p.hidden=!ok;if(ok)n++;}}c.textContent='Showing '+n+' of '+ps.length+' publications';}}
[y,k,t].forEach(function(e){{e.addEventListener('change',run);}});s.addEventListener('input',run);var q=new URLSearchParams(location.search).get('q');if(q){{s.value=q;}}run();}})();</script>'''
    write("publications", "Publications | ACNL", f"All {n_rec} publications of the Advanced Communication Networks Laboratory since 2002, with filters by year, type, and research thread.", body)

def page_projects():
    def row(p):
        return (f'<div class="card"><h3><a href="projects/{pslug(p)}.html">{esc(p["title"])}</a></h3><p class="m">{esc(p["sponsor"])}{" · " + esc(p["amount"]) if p.get("amount") else ""}{" · " + esc(p["period"]) if p.get("period") else ""}</p>'
                f'<p>{esc(p.get("desc", ""))}</p><p class="m">{esc(p.get("team", ""))}</p><p><a href="projects/{pslug(p)}.html">Project page</a>{(" · " + str(len(acknowledged(p))) + " papers acknowledge it") if acknowledged(p) else ""}</p></div>')
    act = "".join(row(p) for p in active); done = "".join(row(p) for p in projects if p not in active)
    body = f'''<section><div class="wrap"><p class="kick">Projects</p><h1>Sponsored research</h1>
<p class="lead">Awards on which the director is an investigator, from the center's records: {len(active)} active and {len(projects) - len(active)} completed since the center was founded in 2019. Sponsors include NSF, ONR, the U.S. Army, DOE, and industry.</p>
<h2 style="margin-top:30px">Active</h2><div class="cards">{act}</div><h2 style="margin-top:40px">Completed</h2><div class="cards">{done}</div></div></section>'''
    write("projects", "Projects | ACNL", "Sponsored research of the Advanced Communication Networks Laboratory: active and completed awards.", body)

def page_software():
    sw = [
        ("FUSION", "Flexible Unified Simulator for Intelligent Optical Networking", "An open-source, modular simulator for conventional, multi-band, and space-division multiplexed optical networks: physical-layer models, routing and spectrum assignment, grooming, survivability, and reinforcement-learning control, with automated tests and deterministic replay so results can be reproduced. Co-founded and led by Ryan McCann; the platform behind the lab's 2026 JOCN papers and its JOCN benchmarking paper.", "https://github.com/SDNNetSim/FUSION"),
        ("NATIG", "Network Attack Testbed In [Power] Grid", "A co-simulation environment that couples a distribution grid with its wireless communication network to study attacks and detection in the loop, led by Kenneth Patrick Watts.", ""),
        ("GridShift safe mode", "Trust-conditioned workload migration for grid-aware AI data centers", "A public, MIT-licensed reference implementation from the SCSP hackathon, led by Ayush Pandey: verified site controllers, signed metering, and a directional migration rule for flexible AI data-center load.", "https://github.com/AYUSHMIT/gridshift-safe-mode"),
    ]
    cards = "".join(f'<div class="card"><h3>{esc(n)}</h3><p class="m">{esc(t)}</p><p>{esc(d)}</p>{("<p><a href=" + esc(u) + ">" + esc(u.replace("https://", "")) + "</a></p>") if u else "<p class=m>Code available on request while the paper is under review.</p>"}</div>' for n, t, d, u in sw)
    body = f'''<section><div class="wrap"><p class="kick">Software</p><h1>Tools the field can build on</h1>
<p class="lead">The lab releases the platforms behind its papers so results can be checked and extended. Cite the paper that introduced each tool when you use it.</p><div class="cards">{cards}</div>
<h2 style="margin-top:36px">Instruments</h2><p>From October 2026 the lab hosts the main site of <a href="../summit.html">SUMMIT</a>, the NSF-funded multi-site smart grid testbed, and it shares the center's optical, RF, and FPGA equipment and its OPAL-RT real-time simulator. The center's <a href="../labs.html">laboratories page</a> lists what each facility can offer collaborators.</p></div></section>'''
    write("software", "Software | ACNL", "Open-source software from the Advanced Communication Networks Laboratory: FUSION, NATIG, and GridShift.", body)

def page_join():
    body = f'''<section><div class="wrap"><p class="kick">Join</p><h1>Work with the lab</h1>
<div class="two"><div>
<h2>Doctoral students</h2><p>The lab takes one or two new Ph.D. students a year, usually with a research assistantship on a sponsored project. Strong applicants have a background in networking, systems, or power systems and can write working code; experience with simulation, optimization, or machine learning helps. Read two recent papers from the <a href="publications.html">publications page</a> and say in your email which problem you want to work on and why. Apply through the <a href="https://www.uml.edu/engineering/electrical-computer/">ECE graduate program</a> and write to the director with your CV and transcript.</p>
<h2>Postdoctoral researchers</h2><p>A postdoctoral research associate position on SUMMIT, to lead federation development across the three sites, is open for a start in late 2026. Details on the center's <a href="../positions.html">positions page</a>.</p>
<h2>Undergraduates and master's students</h2><p>Directed study, capstone, and summer research projects are available on FUSION, on grid co-simulation, and on the lab's testbeds. Write to the director with the course you have taken in networks or security and the project that interests you.</p>
</div><div>
<h2>Companies and agencies</h2><p>The lab works with utilities, network operators, and vendors through sponsored research, testbed access, and joint proposals. SUMMIT opens to collaborators in 2026 to 2027, and the lab's software is open source. Write to the director to discuss a problem, or see the center's <a href="../index.html#sponsors">sponsors and partners</a>.</p>
<h2>Visiting researchers</h2><p>Visiting scholars and sabbatical visitors are welcome for stays of three months or more, with a defined project agreed in advance.</p>
<div class="card" style="margin-top:20px"><h3>Contact</h3><p>{esc(D["name"])}<br>Director, Advanced Communication Networks Laboratory<br>{esc(D["title"])}<br><a href="mailto:{esc(D["email"])}">{esc(D["email"])}</a><br>{esc(D["phone"])}<br>{esc(D.get("office", ""))}<br>University of Massachusetts Lowell, 1 University Ave., Lowell, MA 01854</p></div>
</div></div></div></section>'''
    write("join", "Join | ACNL", "How to join the Advanced Communication Networks Laboratory as a doctoral student, postdoc, undergraduate, visitor, or partner.", body)

if __name__ == "__main__":
    for f in (page_index, page_research, page_insights, page_people, page_students, page_publications, page_projects, page_software, page_join): f()
    for p in projects: page_project(p)
    print(f"wrote acnl/: 8 pages, {len(students)} student pages, {len(projects)} project pages; {n_rec} publications, {len(students)} students, {len(projects)} awards ({len(active)} active)")
