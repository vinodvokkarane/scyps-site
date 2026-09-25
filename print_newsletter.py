#!/usr/bin/env python3
"""Print edition of the center newsletter: one designed PDF built from the same records as the site.

    python3 print_newsletter.py 2026-08

Reads issues/<ym>.json (editorial content: director's letter, the three spotlights) and pulls the month's
papers, awards, and milestones, the roster, and the images from build_site. Writes newsletters/print/<ym>.html,
renders it to PDF with Chromium (Playwright), and writes a cover thumbnail. The site links the PDF from the
newsletters index.
"""
import os, sys, json, re, html, datetime, importlib.util, base64, io

HERE = os.path.dirname(os.path.abspath(__file__))
ym = next((a for a in sys.argv[1:] if re.fullmatch(r"\d{4}-\d{2}", a)), None) or datetime.date.today().strftime("%Y-%m")
spec = importlib.util.spec_from_file_location("bs", os.path.join(HERE, "build_site.py")); bs = importlib.util.module_from_spec(spec)
_argv = sys.argv; sys.argv = ["build_site.py", "/tmp/print_newsletter_throwaway.html"]; sys.path.insert(0, HERE); spec.loader.exec_module(bs); sys.argv = _argv
esc = bs.esc
issue = json.load(open(os.path.join(HERE, "issues", f"{ym}.json"), encoding="utf-8"))
y, m = int(ym[:4]), int(ym[5:7]); label = f"{bs.MONTH_FULL[m]} {y}"
papers, awards, notes, upcoming = bs._month_items(y, m)
img = lambda k: f"data:image/{'png' if bs.IMG[k].startswith('iVBOR') else 'jpeg'};base64,{bs.IMG[k]}"
font = lambda f: "data:font/woff2;base64," + base64.b64encode(open(os.path.join(HERE, "fonts", f), "rb").read()).decode()

core = [p for p in bs.PEOPLE if p["name"] in bs.CORE_NAMES] if hasattr(bs, "PEOPLE") and hasattr(bs, "CORE_NAMES") else []
n_pubs = len(bs.P); n_journal = sum(1 for p in bs.P if p["type"] == "journal")
n_students = len(bs.STUDENTS); n_faculty = 19
awards_all = [p for p in bs.PROJECTS if p.get("tag") in ("Active", "New in 2026")]

def paras(ps): return "".join(f"<p>{esc(t)}</p>" for t in ps)
def spotlight_html(sp, figs):
    who = "".join(f'<div class="who">{bs.stu_avatar(s)}<div><b>{esc(s["name"])}</b><span>{esc(s.get("status", ""))}</span></div></div>'
                  for s in bs._spotlight_students(sp))
    body = "".join((f'<h3>{esc(s["h"])}</h3>' if s.get("h") else "") + paras(s["p"]) for s in sp["sections"])
    figh = "".join(f'<figure><img src="{img(k)}" alt=""><figcaption>{esc(c)}</figcaption></figure>' for k, c in figs)
    pp = "".join(f'<li>{esc(p["title"])}<span>{esc(p.get("note", ""))}. doi:{esc(p["doi"])}</span></li>' for p in sp.get("papers", []))
    return f'''<section class="story">
  <p class="kicker">Student spotlight</p><h2>{esc(sp["title"])}</h2><p class="deck">{esc(sp["deck"])}</p>
  <div class="whos">{who}</div><p class="adv">Advised by {esc(sp["advisor"])}, {esc(sp.get("lab", ""))}</p>
  <div class="cols">{body}{figh}</div>
  <h3>The papers</h3><ul class="papers">{pp}</ul><p class="fund">{esc(sp.get("funding", ""))}</p>
</section>'''

def month_html():
    h = []
    if awards:
        h.append("<h3>New awards</h3>" + "".join(f'<p class="item"><b>{esc(a["title"])}</b> <span class="amt">{esc(a.get("amount", ""))}</span><br><span class="meta">{esc(a["sponsor"])}. {esc(a["team"])}</span></p>' for a in awards))
    if papers:
        h.append("<h3>New papers</h3>" + "".join(f'<p class="item">{esc(", ".join(p["authors"]) if isinstance(p["authors"], list) else p["authors"])}. <b>{esc(p["title"])}</b>. <i>{esc(p["venue"])}</i>, {esc(p["details"])}.' + (f' <span class="meta">doi:{esc(p["doi"])}</span>' if p.get("doi") else "") + "</p>" for p in papers))
    if notes:
        h.append("<h3>Milestones</h3>" + "".join(f'<p class="item">{esc(t)}</p>' for t in notes))
    return "".join(h)

sp = next(s for s in bs.SPOTLIGHTS if s["ym"] == issue["student_spotlight"])
fac = issue["faculty_spotlight"]; proj = issue["project_spotlight"]; letter = issue["letter"]
thrusts = "".join(f'<li><b>{esc(t[1])}</b><span>{esc(t[3])}</span></li>' for t in bs.THRUSTS)
coming = "".join(f'<li><b>{esc(c["when"])}</b> {esc(c["what"])}</li>' for c in issue.get("coming_up", []))
active = "".join(f'<li>{esc(p["title"].split(": ")[0] if len(p["title"]) > 70 and ": " in p["title"] else p["title"])}<span>{esc(p["sponsor"].split(" (")[0])}{", " + esc(p["amount"]) if p.get("amount") else ""}</span></li>' for p in awards_all)

page = f'''<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><title>SCyPS Newsletter, {esc(label)}</title>
<style>
@font-face{{font-family:Fraunces;src:url({font("fraunces-latin-full-normal.woff2")}) format("woff2");font-weight:300 900}}
@font-face{{font-family:Fraunces;src:url({font("fraunces-latin-full-italic.woff2")}) format("woff2");font-weight:300 900;font-style:italic}}
@font-face{{font-family:Plex;src:url({font("ibm-plex-sans-latin-400-normal.woff2")}) format("woff2");font-weight:400}}
@font-face{{font-family:Plex;src:url({font("ibm-plex-sans-latin-400-italic.woff2")}) format("woff2");font-weight:400;font-style:italic}}
@font-face{{font-family:Plex;src:url({font("ibm-plex-sans-latin-500-normal.woff2")}) format("woff2");font-weight:500}}
@font-face{{font-family:Plex;src:url({font("ibm-plex-sans-latin-600-normal.woff2")}) format("woff2");font-weight:600}}
@page{{size:Letter;margin:0.55in 0.6in 0.7in}}
:root{{--navy:#0E2036;--blue:#044978;--teal:#2CA58D;--gold:#D4A017;--ink:#0E2036;--ink2:#3A4756;--ink3:#5B6B82;--line:#D5DCE5;--bg:#F3F7FA}}
*{{box-sizing:border-box}}html,body{{margin:0;padding:0}}
body{{font-family:Plex,Arial,sans-serif;color:var(--ink);font-size:10.1pt;line-height:1.48}}
h1,h2,h3,.mast .name{{font-family:Fraunces,Georgia,serif;font-weight:500;letter-spacing:-.01em}}
h2{{font-size:24pt;line-height:1.1;margin:0 0 6pt}}h3{{font-size:13pt;margin:14pt 0 4pt;color:var(--blue)}}
p{{margin:0 0 7pt}}a{{color:var(--blue);text-decoration:none}}
.pb{{page-break-before:always}}.avoid{{page-break-inside:avoid}}
.mast{{background:var(--navy);color:#fff;margin:0;padding:.28in .32in .26in;border-radius:6pt 6pt 0 0;position:relative}}
.mast .top{{display:flex;justify-content:space-between;align-items:baseline;gap:12pt;font-size:8pt;letter-spacing:.08em;text-transform:uppercase;color:#C9DCEA}}
.mast .name{{font-size:34pt;line-height:1;margin:10pt 0 3pt;color:#fff}}.mast .sub{{font-size:11.5pt;color:#C9DCEA;margin:0}}
.mast img.logo{{height:34px}}
.hero{{margin:0;border-radius:0 0 6pt 6pt;height:1.9in;background:url({img("hero")}) center/cover;position:relative}}
.hero .cap{{position:absolute;left:.32in;bottom:.18in;background:rgba(14,32,54,.85);color:#fff;padding:6pt 10pt;font-size:9pt;max-width:4.6in}}
.lead{{display:grid;grid-template-columns:1.55fr 1fr;gap:.35in;margin-top:.28in}}
.letter p{{font-size:9.9pt;margin-bottom:6pt}}.letter .sig{{margin-top:10pt;font-family:Fraunces,serif;font-style:italic;font-size:12pt}}
.kicker{{font-size:8.5pt;letter-spacing:.1em;text-transform:uppercase;color:var(--ink3);margin:0 0 4pt}}
.box{{background:var(--bg);border-top:3px solid var(--teal);padding:12pt 14pt;font-size:9.6pt}}.box h4{{margin:0 0 6pt;font-family:Fraunces,serif;font-size:13pt;color:var(--navy)}}
.box ol{{margin:0;padding-left:16pt}}.box li{{margin:0 0 3pt}}
.nums{{display:grid;grid-template-columns:repeat(4,1fr);gap:10pt;margin:10pt 0 14pt}}
.nums div{{border-top:2px solid var(--line);padding-top:5pt;font-size:9pt;color:var(--ink3)}}.nums b{{display:block;font-family:Fraunces,serif;font-size:24pt;color:var(--navy);line-height:1.05}}
.thrusts{{list-style:none;margin:0;padding:0;columns:2;column-gap:.3in;font-size:9pt}}.thrusts li{{break-inside:avoid;margin:0 0 6pt;padding-left:9pt;border-left:2px solid var(--teal)}}
.thrusts b{{display:block;font-weight:600;color:var(--navy)}}.thrusts span{{color:var(--ink3)}}
.story .deck{{font-family:Fraunces,serif;font-size:13.5pt;line-height:1.35;color:var(--ink2);margin:0 0 10pt}}
.cols{{columns:2;column-gap:.3in}}.cols h3{{break-after:avoid}}.cols p{{text-align:left}}.cols figure{{break-inside:avoid;margin:6pt auto 10pt;width:64%}}
figure{{margin:0 0 10pt}}figure img{{width:100%;display:block;border:1px solid var(--line)}}figcaption{{font-size:8.6pt;color:var(--ink3);margin-top:4pt}}
.whos{{display:flex;gap:.3in;margin:4pt 0}}.who{{display:flex;align-items:center;gap:8pt}}.who img{{width:44pt;height:44pt;border-radius:50%}}.who b{{display:block;font-size:10.5pt}}.who span{{font-size:9pt;color:var(--ink3)}}
.adv{{font-size:9pt;color:var(--ink3);margin:0 0 10pt}}
.papers{{margin:0;padding-left:14pt;font-size:9.4pt}}.papers li{{margin:0 0 5pt}}.papers span{{display:block;color:var(--ink3);font-size:8.6pt}}
.fund{{font-size:8.6pt;color:var(--ink3);margin-top:8pt}}
.side{{display:grid;grid-template-columns:1fr 2.1in;gap:.3in}}.side p{{font-size:9.7pt;margin-bottom:6pt}}.side h3{{margin-top:10pt}}.side figure img{{border:0}}
.item{{font-size:9.6pt;margin:0 0 6pt}}.item .meta{{color:var(--ink3);font-size:8.8pt}}.amt{{color:var(--teal);font-weight:600}}
.two{{display:grid;grid-template-columns:1fr 1fr;gap:.35in}}
ul.plain{{margin:0;padding-left:14pt;font-size:9.6pt}}ul.awards{{columns:2;column-gap:.3in;font-size:8.5pt}}ul.awards li{{margin-bottom:2.5pt}}ul.awards li{{break-inside:avoid}}ul.plain li{{margin:0 0 4pt}}ul.plain span{{display:block;color:var(--ink3);font-size:8.6pt}}
.foot{{margin-top:14pt;border-top:1px solid var(--line);padding-top:8pt;font-size:8.8pt;color:var(--ink3)}}
.pull{{font-family:Fraunces,serif;font-style:italic;font-size:12.5pt;line-height:1.3;color:var(--blue);border-left:3px solid var(--gold);padding-left:10pt;margin:8pt 0 12pt;break-inside:avoid}}
</style></head><body>

<div class="mast"><div class="top"><span>Center for Smart Cyber-Physical Systems &middot; UMass Lowell</span><span>Volume 1, Number 1 &nbsp;|&nbsp; {esc(label)}</span></div>
<div class="name">SCyPS</div><p class="sub">The center's newsletter: research, people, and what comes next.</p></div>
<div class="hero"><div class="cap">{esc(issue["hero_caption"])}</div></div>

<div class="lead">
  <div class="letter"><p class="kicker">From the director</p><h2>{esc(letter["title"])}</h2>{paras(letter["paragraphs"])}<p class="sig">{esc(letter["signature"])}</p></div>
  <div><div class="box"><h4>In this issue</h4><ol>{"".join(f"<li>{esc(t)}</li>" for t in issue["contents"])}</ol></div>
       <div class="box" style="margin-top:12pt;border-top-color:var(--gold)"><h4>By the numbers</h4>
       <div class="nums" style="grid-template-columns:1fr 1fr;margin:0"><div><b>{n_faculty}</b>faculty, four colleges</div><div><b>{n_pubs}</b>papers since 2019</div><div><b>{n_journal}</b>in journals</div><div><b>{n_students}</b>doctoral students</div></div></div></div>
</div>

<section style="margin-top:14pt"><p class="kicker">The center</p><h2>Eight thrusts, one loop</h2>
<p>Cyber-physical systems sense the physical world, communicate what they sense, decide, and act. The center's research covers every link in that loop, and the eight thrusts below are how its {n_faculty} faculty organize the work. Each thrust has a lead, a page on the center site, and a record of papers and awards that the site keeps current every week.</p>
<ul class="thrusts">{thrusts}</ul>
<h3>Active and new awards ({len(awards_all)})</h3><ul class="plain awards">{active}</ul>
<p class="foot">Full records at <a href="https://smartcyberphysical.org">smartcyberphysical.org</a>, where every paper and award links to its source.</p></section>

<section class="pb story"><p class="kicker">Project spotlight</p><h2>{esc(proj["title"])}</h2><p class="deck">{esc(proj["deck"])}</p>
<figure style="width:50%;margin:0 auto 4pt"><img src="{img("summit_arch")}" alt=""><figcaption>{esc(proj["figure_caption"])}</figcaption></figure>
<div class="cols">{"".join((f'<h3>{esc(s["h"])}</h3>' if s.get("h") else "") + paras(s["p"]) for i, s in enumerate(proj["sections"]))}</div></section>

<section class="pb story"><p class="kicker">Faculty spotlight</p><h2>{esc(fac["title"])}</h2><p class="deck">{esc(fac["deck"])}</p>
<div class="side"><div>{"".join((f'<h3>{esc(s["h"])}</h3>' if s.get("h") else "") + paras(s["p"]) for s in fac["sections"])}</div>
<div><figure><img src="{img("about_aghara")}" alt=""><figcaption>{esc(fac["figure_caption"])}</figcaption></figure>
<div class="box"><h4>{esc(fac["box_title"])}</h4><ul class="plain" style="padding-left:12pt">{"".join(f"<li>{esc(t)}</li>" for t in fac["box_items"])}</ul></div></div></div></section>

<section class="pb">{spotlight_html(sp, [("fig_arash", issue["student_figures"][0]), ("fig_ryan", issue["student_figures"][1])])}</section>

<section class="pb"><p class="kicker">This month</p><h2>{esc(label)} at the center</h2>
<div class="two"><div>{month_html()}</div>
<div><h3>Coming up</h3><ul class="plain">{coming}</ul>
<h3>Work with us</h3><p class="item">Doctoral applicants: write to the faculty member whose work matches yours and copy the director. Companies and agencies: the laboratories page lists what each facility can offer, and the SUMMIT testbed opens to collaborators in 2026 to 2027.</p>
<h3>Support the center</h3><p class="item">Gifts fund student travel, seed projects, and the capstone program. Give at smartcyberphysical.org, or write to the director.</p>
<h3>Contact</h3><p class="item">Vinod M. Vokkarane, Director<br>Vinod_Vokkarane@uml.edu, 978-934-3345<br>Center for Smart Cyber-Physical Systems<br>University of Massachusetts Lowell, 1 University Ave., Lowell, MA 01854<br><a href="https://smartcyberphysical.org">smartcyberphysical.org</a></p></div></div>
<p class="foot">Volume 1, Number 1, {esc(label)}. Published by the Center for Smart Cyber-Physical Systems. Generated from the center's records on {esc(datetime.date.today().strftime("%B %d, %Y"))}.</p></section>
</body></html>'''

out_dir = os.path.join(HERE, "newsletters", "print"); os.makedirs(out_dir, exist_ok=True)
html_path = os.path.join("/tmp", f"scyps-print-{ym}.html"); open(html_path, "w", encoding="utf-8").write(page)   # the HTML is a build artifact, not committed
pdf_path = os.path.join(out_dir, f"SCyPS-Newsletter-{ym}-Vol{issue['volume']}-No{issue['number']}.pdf")
try:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        footer = ('<div style="font-family:Arial,sans-serif;font-size:8px;color:#5B6B82;width:100%;padding:0 0.6in;display:flex;justify-content:space-between">'
                  f'<span>SCyPS Newsletter, Volume {issue["volume"]}, Number {issue["number"]}, {esc(label)}</span>'
                  '<span>Page <span class="pageNumber"></span> of <span class="totalPages"></span></span></div>')
        b = p.chromium.launch(); pg = b.new_page(); pg.goto("file://" + html_path); pg.wait_for_timeout(500)
        pg.pdf(path=pdf_path, format="Letter", print_background=True, display_header_footer=True,
               header_template="<div></div>",
               footer_template=footer,
               margin={"top": "0.55in", "bottom": "0.7in", "left": "0.6in", "right": "0.6in"})
        b.close()
    print("wrote", pdf_path)
    try:   # cover thumbnail for the newsletters index
        import subprocess; subprocess.run(["pdftoppm", "-jpeg", "-r", "80", "-f", "1", "-l", "1", "-singlefile", pdf_path, os.path.join(out_dir, f"{ym}-cover")], check=True)
    except Exception as e: print("cover not made:", e)
except Exception as e:
    print("PDF not rendered (Playwright unavailable here):", e)
