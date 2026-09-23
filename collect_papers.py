#!/usr/bin/env python3
"""Collect the full text of every publication in the center's record into one zip, for the graph RAG.

Run this on a machine that can reach the publishers (on campus or on the UML VPN, so the library's
subscriptions apply). It works in passes, and every pass is safe to repeat:

    pip install requests pypdf
    python3 collect_papers.py manifest              # 1. scyps-papers/manifest.csv: every DOI and what is known about it
    python3 collect_papers.py oa   --email you@uml.edu   # 2. fetch every legally open copy Unpaywall knows about
    python3 collect_papers.py list                  # 3. scyps-papers/download-list.html: one library link per missing paper
    #    open that page, save each PDF into scyps-papers/inbox/ (any file name), including your own accepted manuscripts
    python3 collect_papers.py match                 # 4. read each inbox PDF, find its DOI or title, file it under scyps-papers/pdf/
    python3 collect_papers.py zip                   # 5. scyps-papers/scyps-papers.zip: the PDFs plus manifest.csv

Files land in a folder beside the site repo, scyps-papers/pdf/<doi with / and . turned into _>.pdf, so every paper has one predictable name and
the manifest ties it back to the site's record. Nothing is fetched from anywhere that is not either open
access or reachable through your own library access; the script never scrapes around a paywall.

Why not fully automatic: 102 of the 187 papers are IEEE, 33 Elsevier, 14 ACM, 6 Optica. Crossref lists a
Creative Commons license for 17. Unpaywall usually finds an open copy for a third to a half of an
engineering corpus (accepted manuscripts, arXiv, repositories); the rest need a subscription, and
publishers block scripted bulk downloads even for subscribers, so those come through the browser.
"""
import csv, io, json, os, re, sys, time, zipfile, contextlib, importlib.util, argparse, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(os.path.dirname(HERE), "scyps-papers")   # a sibling of the site folder: the PDFs must never land in the public repo
PDF, INBOX = os.path.join(ROOT, "pdf"), os.path.join(ROOT, "inbox")
MANIFEST = os.path.join(ROOT, "manifest.csv")
UA = {"User-Agent": "SCyPS-paper-collector/1.0 (mailto:SCyPS@uml.edu)"}
LIBPROXY = "https://libproxy.uml.edu/login?url="          # UML library proxy prefix; adjust if the library uses another

def slug(doi):
    return re.sub(r"[^A-Za-z0-9]+", "_", doi.lower()).strip("_")

def site_papers():
    spec = importlib.util.spec_from_file_location("bs", os.path.join(HERE, "build_site.py"))
    m = importlib.util.module_from_spec(spec)
    argv = sys.argv; sys.argv = ["build_site.py", os.path.join("/tmp", "collect_throwaway.html")]
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            try: spec.loader.exec_module(m)
            except SystemExit: pass
    finally: sys.argv = argv
    return [p for p in m.P if p.get("doi")]

def read_manifest():
    if not os.path.exists(MANIFEST): return []
    return list(csv.DictReader(open(MANIFEST, encoding="utf-8")))

def write_manifest(rows):
    os.makedirs(ROOT, exist_ok=True)
    cols = ["doi", "slug", "year", "type", "title", "venue", "faculty", "publisher", "cc_license", "status", "source", "file", "note"]
    with open(MANIFEST, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader()
        for r in rows: w.writerow({c: r.get(c, "") for c in cols})

def refresh_status(rows):
    for r in rows:
        f = os.path.join(PDF, r["slug"] + ".pdf")
        if os.path.exists(f) and open(f, "rb").read(5) == b"%PDF-":
            r["file"] = os.path.relpath(f, ROOT)
            if r.get("status") not in ("open access", "arxiv", "inbox"): r["status"] = "on file"
        elif r.get("status") in ("open access", "arxiv", "inbox", "on file"):
            r["status"] = "missing"; r["file"] = ""
        elif not r.get("status"):
            r["status"] = "missing"
    return rows

# ---------------------------------------------------------------- 1. manifest
def cmd_manifest(args):
    import requests
    old = {r["doi"].lower(): r for r in read_manifest()}
    rows = []
    for p in site_papers():
        k = p["doi"].lower(); r = old.get(k, {})
        r.update({"doi": p["doi"], "slug": slug(p["doi"]), "year": p["year"], "type": p["type"], "title": p["title"],
                  "venue": p["venue"], "faculty": " ".join(p["faculty"])})
        if not r.get("publisher"):
            try:
                d = requests.get("https://api.crossref.org/works/" + p["doi"], headers=UA, timeout=30).json()["message"]
                r["publisher"] = d.get("publisher", "")
                r["cc_license"] = "yes" if any("creativecommons" in (l.get("URL") or "") for l in d.get("license") or []) else ""
                time.sleep(0.2)
            except Exception as e:
                r["note"] = f"crossref: {e}"[:80]
        rows.append(r)
    write_manifest(refresh_status(rows))
    n = len(rows); have = sum(1 for r in rows if r.get("file"))
    print(f"manifest: {n} papers, {have} on file, {sum(1 for r in rows if r.get('cc_license'))} with a Creative Commons license")

# ---------------------------------------------------------------- 2. open access via Unpaywall
def fetch_pdf(url, dest):
    import requests
    try:
        with requests.get(url, headers={**UA, "Accept": "application/pdf,*/*"}, timeout=60, stream=True, allow_redirects=True) as g:
            if g.status_code != 200: return f"http {g.status_code}"
            data = g.raw.read(5); rest = g.content
            body = data + rest if not rest.startswith(data) else rest
            if not body.startswith(b"%PDF-"): return "not a pdf"
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            open(dest, "wb").write(body); return "ok"
    except Exception as e:
        return str(e)[:60]

def cmd_oa(args):
    import requests
    if not args.email: sys.exit("Unpaywall needs an email: --email you@uml.edu")
    rows = refresh_status(read_manifest()) or sys.exit("run 'manifest' first")
    got = tried = 0
    for r in rows:
        if r.get("file"): continue
        tried += 1
        try:
            u = requests.get(f"https://api.unpaywall.org/v2/{r['doi']}", params={"email": args.email}, headers=UA, timeout=30).json()
        except Exception as e:
            r["note"] = f"unpaywall: {e}"[:80]; continue
        locs = [u.get("best_oa_location")] + (u.get("oa_locations") or [])
        urls = []
        for loc in locs:
            if not loc: continue
            for key in ("url_for_pdf", "url"):
                if loc.get(key) and loc[key] not in urls: urls.append(loc[key])
        for url in urls:
            res = fetch_pdf(url, os.path.join(PDF, r["slug"] + ".pdf"))
            if res == "ok":
                r["status"] = "open access"; r["source"] = url; got += 1
                print(f"  got  {r['doi']}  <- {url[:70]}"); break
        else:
            r["note"] = ("no open copy" if not urls else f"open copy listed but not fetched ({res})")
        time.sleep(0.5)
    write_manifest(refresh_status(rows))
    print(f"open access: tried {tried}, fetched {got}; {sum(1 for r in rows if not r.get('file'))} still missing")

# ---------------------------------------------------------------- 3. the download list for the browser
def cmd_list(args):
    rows = refresh_status(read_manifest()) or sys.exit("run 'manifest' first")
    missing = [r for r in rows if not r.get("file")]
    items = "".join(
        f'<li><a href="{LIBPROXY}https://doi.org/{r["doi"]}" target="_blank" rel="noopener">{r["title"]}</a>'
        f'<br><small>{r["venue"]}, {r["year"]}; {r["publisher"]}; {r["faculty"]}; doi {r["doi"]}</small></li>'
        for r in sorted(missing, key=lambda r: (r["publisher"], -int(r["year"] or 0))))
    html = f"""<!DOCTYPE html><meta charset="utf-8"><title>Papers still to collect</title>
<style>body{{font:15px/1.45 system-ui,sans-serif;max-width:60em;margin:2em auto;padding:0 1em}}li{{margin:0 0 .9em}}small{{color:#555}}</style>
<h1>{len(missing)} papers still to collect</h1>
<p>Each link opens the paper through the library proxy. Save the PDF into <code>scyps-papers/inbox/</code> with any
file name, then run <code>python3 collect_papers.py match</code>. Your own accepted manuscripts can go in the
same folder. Generated {datetime.date.today().isoformat()}.</p><ol>{items}</ol>"""
    out = os.path.join(ROOT, "download-list.html")
    open(out, "w", encoding="utf-8").write(html); os.makedirs(INBOX, exist_ok=True)
    print(f"wrote {out}: {len(missing)} papers; drop the PDFs into {INBOX}")

# ---------------------------------------------------------------- 4. match dropped-in PDFs to the record
def norm(t): return re.sub(r"[^a-z0-9]+", "", (t or "").lower())   # spacing-free, so line breaks inside a title do not matter

def cmd_match(args):
    from pypdf import PdfReader
    rows = refresh_status(read_manifest()) or sys.exit("run 'manifest' first")
    by_doi = {r["doi"].lower(): r for r in rows}
    by_title = {norm(r["title"]): r for r in rows}
    os.makedirs(INBOX, exist_ok=True); os.makedirs(PDF, exist_ok=True)
    matched = unmatched = 0
    for name in sorted(os.listdir(INBOX)):
        path = os.path.join(INBOX, name)
        if not name.lower().endswith(".pdf"): continue
        try:
            reader = PdfReader(path)
            text = " ".join((pg.extract_text() or "") for pg in reader.pages[:2])
        except Exception as e:
            print(f"  skip {name}: {e}"); unmatched += 1; continue
        hit = None
        for d in re.findall(r"10\.\d{4,9}/[^\s\"'<>]+", text):
            d = d.rstrip(".,;)").lower()
            if d in by_doi: hit = by_doi[d]; break
        if not hit:
            nt = norm(text)
            cands = [r for k, r in by_title.items() if len(k) >= 25 and k in nt]
            if cands: hit = max(cands, key=lambda r: len(r["title"]))      # the longest title that appears in full
        if not hit:
            print(f"  ?    {name}: no DOI or title from the record found in its first pages"); unmatched += 1; continue
        dest = os.path.join(PDF, hit["slug"] + ".pdf")
        os.replace(path, dest)
        hit["status"] = "inbox"; hit["source"] = f"inbox/{name}"; hit["file"] = os.path.relpath(dest, ROOT); matched += 1
        print(f"  ok   {name} -> {hit['slug']}.pdf")
    write_manifest(refresh_status(rows))
    print(f"match: {matched} filed, {unmatched} left in inbox; {sum(1 for r in rows if not r.get('file'))} papers still missing")

# ---------------------------------------------------------------- 5. zip
def cmd_zip(args):
    rows = refresh_status(read_manifest()) or sys.exit("run 'manifest' first")
    write_manifest(rows)
    out = os.path.join(ROOT, "scyps-papers.zip")
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(MANIFEST, "manifest.csv")
        for r in rows:
            if r.get("file"): z.write(os.path.join(ROOT, r["file"]), r["file"])
    have = sum(1 for r in rows if r.get("file"))
    print(f"wrote {out}: {have} of {len(rows)} papers, {os.path.getsize(out)/1e6:.1f} MB")

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["manifest", "oa", "list", "match", "zip"])
    ap.add_argument("--email", default=os.environ.get("UNPAYWALL_EMAIL", ""))
    a = ap.parse_args()
    {"manifest": cmd_manifest, "oa": cmd_oa, "list": cmd_list, "match": cmd_match, "zip": cmd_zip}[a.command](a)
