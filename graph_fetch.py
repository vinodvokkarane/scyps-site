#!/usr/bin/env python3
"""Crossref data behind insights.html: each paper's reference list and citation count, plus the titles
of the outside works the group cites most. Written to graph_auto.json, read by build_site.py.

    python3 graph_fetch.py            # refresh everything older than GRAPH_MIN_DAYS (default 6)
    GRAPH_MIN_DAYS=0 python3 graph_fetch.py

Crossref is free and asks only for a mailto in the user agent. Reference lists are open for nearly all
of the group's publishers (29 of 30 in a Sept. 2026 sample); about two thirds of references carry a DOI,
and only those become edges. Abstracts are not fetched: Crossref has them for almost none of these DOIs.
"""
import json, os, re, sys, time, datetime, urllib.request, urllib.parse, contextlib, io, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
STORE = os.path.join(HERE, "graph_auto.json")
UA = {"User-Agent": "SCyPS-site-builder/1.0 (https://smartcyberphysical.org; mailto:SCyPS@uml.edu)"}
TODAY = datetime.date.today()
MIN_DAYS = int(os.environ.get("GRAPH_MIN_DAYS", "6"))
TOP_EXTERNAL = 60      # outside works to fetch titles for

def get(url, timeout=40):
    return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout))

def site_papers():
    """The publication records exactly as the site sees them (after attribution rules)."""
    spec = importlib.util.spec_from_file_location("bs", os.path.join(HERE, "build_site.py"))
    m = importlib.util.module_from_spec(spec)
    argv = sys.argv; sys.argv = ["build_site.py", os.path.join("/tmp", "graph_fetch_throwaway.html")]
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            try: spec.loader.exec_module(m)
            except SystemExit: pass
    finally:
        sys.argv = argv
    return [p for p in m.P if p.get("doi")]

def refresh(dois):
    data = json.load(open(STORE, encoding="utf-8")) if os.path.exists(STORE) else {"works": {}, "external": {}}
    works, ext = data.setdefault("works", {}), data.setdefault("external", {})
    fetched = failed = 0
    for doi in dois:
        k = doi.lower()
        prev = works.get(k, {})
        try:
            if (TODAY - datetime.date.fromisoformat(prev.get("date", "1900-01-01"))).days < MIN_DAYS: continue
        except ValueError: pass
        try:
            msg = get("https://api.crossref.org/works/" + urllib.parse.quote(doi))["message"]
        except Exception as e:
            failed += 1; print(f"graph: {doi} failed ({e})"); continue
        refs = sorted({r["DOI"].lower() for r in (msg.get("reference") or []) if r.get("DOI")})
        works[k] = {"cited_by": int(msg.get("is-referenced-by-count", 0) or 0), "nrefs": int(msg.get("reference-count", 0) or 0),
                    "refs": refs, "date": TODAY.isoformat()}
        fetched += 1
        time.sleep(0.25)
    # the outside works cited by the most group papers: fetch a title once, keep it
    own = set(works)
    count = {}
    for k, w in works.items():
        for r in w.get("refs", []):
            if r not in own: count[r] = count.get(r, 0) + 1
    top = sorted(count, key=lambda d: (-count[d], d))[:TOP_EXTERNAL]
    for d in top:
        if d in ext: continue
        try:
            msg = get("https://api.crossref.org/works/" + urllib.parse.quote(d))["message"]
            au = msg.get("author") or []
            first = (au[0].get("family") or au[0].get("name") or "") if au else ""
            year = ((msg.get("issued") or {}).get("date-parts") or [[None]])[0][0]
            ext[d] = {"title": " ".join((msg.get("title") or [""])[0].split()), "year": year,
                      "venue": " ".join((msg.get("container-title") or [""])[0].split()),
                      "first_author": first, "n_authors": len(au), "cited_by": int(msg.get("is-referenced-by-count", 0) or 0)}
        except Exception as e:
            ext[d] = {"title": "", "year": None, "venue": "", "first_author": "", "n_authors": 0, "cited_by": 0, "error": str(e)[:60]}
        time.sleep(0.25)
    data["date"] = TODAY.isoformat()
    json.dump(data, open(STORE, "w", encoding="utf-8"), indent=0, ensure_ascii=False, sort_keys=True)
    print(f"graph: {fetched} paper(s) fetched, {failed} failed, {len(works)} on file, {len(ext)} outside works titled")
    return fetched, failed

if __name__ == "__main__":
    refresh([p["doi"] for p in site_papers()])
