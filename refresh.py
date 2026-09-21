#!/usr/bin/env python3
"""Refresh the dynamic content of the SCyPS site and write overlay files that build_site.py reads.

    python3 refresh.py            # everything
    python3 refresh.py pubs       # only publications (Crossref)
    python3 refresh.py grants     # only NSF awards (NSF Awards API)
    python3 refresh.py scholar    # only Google Scholar citation counts

Outputs (all JSON, all safe to commit):
    pubs_auto.json     new papers found since the curated list was written, per faculty rules below
    grants_auto.json   NSF awards to center faculty at UMass Lowell that are not already in the ledger
    scholar_auto.json  latest "Cited by" and h-index read from each public Scholar profile
    refresh_log.json   what changed on the last run

The curated data in build_site.py is never modified; the overlays add to it. Anything questionable
can be deleted from an overlay file by hand and it will not come back (see the "ignore" lists).
"""
import json, re, sys, time, datetime, urllib.request, urllib.parse, os, html

HERE = os.path.dirname(os.path.abspath(__file__))
UA = {"User-Agent": "SCyPS-site-refresh/1.0 (mailto:SCyPS@uml.edu)"}
TODAY = datetime.date.today()

def get_json(url, timeout=120):
    return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout))

def load(name, default):
    p = os.path.join(HERE, name)
    return json.load(open(p)) if os.path.exists(p) else default

def save(name, data):
    json.dump(data, open(os.path.join(HERE, name), "w"), indent=1, ensure_ascii=False)

# ------------------------------------------------------------------ faculty and acceptance rules
# tag, Crossref author query, family, given prefix, affiliation keywords, co-author keywords, venue regex, subject area
def norm(s): return re.sub(r"[\s\-\.]+", " ", (s or "").lower()).strip()

FACULTY = [
    ("Vokkarane", "Vinod Vokkarane", "vokkarane", "v", ["lowell"], [], None, "Optical networks"),
    ("Tseng", "Lewis Tseng", "tseng", "lewis", ["lowell"], [], None, "Distributed systems"),
    ("Arias", "Orlando Arias", "arias", "orlando", ["lowell"], ["vokkarane", "jin", "son", "yavuz", "dai", "sasaninia", "sharifi", "watts", "islam", "lin"],
     r"HOST|Hardware|Security|Trust|Cryptograph|Embedded|Design Automation|CLUSTER|Microarchitect|Computer-Aided", "HPC and hardware"),
    ("Son", "Seung Woo Son", "son", "seung woo", ["lowell"], ["moon", "arias", "chaisson", "choi", "jeong", "eunsang", "jaehoon", "zhaoheng", "agrawal", "choudhary", "liao"],
     r"Cluster|Big Data|IGARSS|Parallel|HPC|Supercomput|ICPP|CCGrid|Data Compression|Storage|IPDPS", "HPC and hardware"),
    ("Aghara", "Sukesh Aghara", "aghara", "sukesh", ["lowell"], [], None, "Nuclear energy and security"),
    ("Lin", "Yuzhang Lin", "lin", "yuzhang", ["lowell", "new york"], ["vokkarane", "islam", "edib", "huang heqing", "chen guibin", "zhang wentao", "zhao junbo", "abur", "sharma nitish", "christou", "xiong jingwei", "ogle", "koehler", "kumar avinash"],
     r"IEEE Transactions on (Power|Smart|Industry|Instrumentation)|Power & Energy Society|Power Systems|Smart Grid|PES General|ISGT|SmartGridComm|PES Innovative", "Smart grid"),
    ("Luo", "Yan Luo", "luo", "yan", ["lowell"], ["cao yu", "liu benyuan", "hu tingshu", "niezrecki", "inalpolat", "sabato", "jerath", "chen guanling", "ma yunsheng", "vokkarane", "xie yuanchang"], None, "Sensing and networks"),
    ("Xie", "Yuanchang Xie", "xie", "yuanchang", ["lowell"], [], None, "Transportation"),
    ("Cao", "Yu Cao", "cao", "yu", ["lowell"], ["luo yan", "liu benyuan", "chen guanling", "ma yunsheng", "vokkarane", "chen shuqiang", "liu chang", "hou peng"], None, "Digital health"),
    ("Chigan", "Chunxiao Chigan", "chigan", "chunxiao", ["lowell"], [], None, "Wireless networks"),
    ("Inalpolat", "Murat Inalpolat", "inalpolat", "murat", ["lowell"], [], None, "Structural dynamics and health monitoring"),
    ("Robinette", "Paul Robinette", "robinette", "paul", ["lowell"], [], None, "Robotics and human-robot interaction"),
    ("Yu", "Hengyong Yu", "yu", "hengyong", ["lowell"], ["wang ge", "wang dayang", "han shuo", "wu panpan", "morovati", "zhou li", "fang changsheng", "xu yongshun", "li mengzhou", "chen yang", "wu zhan", "chu ying", "zhang boce", "niu chuang", "cong wenxiang"],
     r"Medical|Imaging|Physics in Medicine|X-Ray|Biomedical|Tomograph|Radiation|ISBI|ICIP|Image Processing|Neural Networks|Pattern|Computer Vision", "Medical imaging"),
    ("Akyurtlu", "Alkim Akyurtlu", "akyurtlu", "alkim", ["lowell"], [], None, "Printed electronics"),
    ("Niezrecki", "Christopher Niezrecki", "niezrecki", "c", ["lowell"], [], None, "Renewable energy and structural monitoring"),
    ("Ranasingha", "Oshadha Ranasingha", "ranasingha", "oshadha", ["lowell"], [], None, "Printed electronics"),
    ("Chakrabarti", "Supriya Chakrabarti", "chakrabarti", "supriya", ["lowell"], ["cook timothy", "kuravi", "baumgardner", "mendillo", "finn susanna", "hewawasam", "martel jason"],
     r"Astro|Space|Planetary|Geophysical|Atmospheric|Optic|SPIE|Aurora|Ionospher|Exoplanet|Spectrograph|Instrument", "Space instrumentation"),
    ("Evans", "Nicholas Evans", "evans", "nicholas", ["lowell"], ["xie yuanchang", "jiang liming", "vokkarane"], r"Ethic|Bioethic|Philosoph|Hastings|Security Studies|Science and Engineering|Journal of Medical Ethics|Public Health Ethics", "Ethics of technology"),
]
# common surnames: require an affiliation or co-author match (or a venue match) rather than the name alone
STRICT = {"Son", "Lin", "Luo", "Cao", "Yu", "Arias", "Evans", "Chakrabarti"}
TYPES = {"journal-article": "journal", "proceedings-article": "conference", "book-chapter": "chapter"}
EXCL_VENUE = re.compile(r"ECS Meeting Abstracts|SSRN|Research Square|TechRxiv|arXiv|Conversation|Editorial", re.I)
MON = ["", "Jan.", "Feb.", "Mar.", "Apr.", "May", "June", "July", "Aug.", "Sept.", "Oct.", "Nov.", "Dec."]

def accept(it, tag, family, given, affs, coauthors, venue_re):
    me = None
    for a in it.get("author", []):
        if norm(a.get("family")) == family and norm(a.get("given")).startswith(given):
            me = a; break
    if not me: return False
    if tag not in STRICT: return True
    aff = " ".join(x.get("name", "") for x in me.get("affiliation", [])).lower()
    if any(k in aff for k in affs): return True
    names = " ".join(norm(a.get("given")) + " " + norm(a.get("family")) for a in it.get("author", []))
    if any(k in names for k in coauthors): return True
    venue = (it.get("container-title") or [""])[0] + " " + (it.get("event", {}) or {}).get("name", "")
    return bool(venue_re and re.search(venue_re, venue))

def initials(a):
    g = (a.get("given") or "").strip(); f = (a.get("family") or "").strip()
    if not f: return ""
    ini = " ".join(p[0].upper() + "." for p in re.split(r"[\s\-]+", g) if p and p[0].isalpha())
    return (ini + " " + f).strip()

def clean(t): return html.unescape(re.sub(r"<[^>]+>", "", re.sub(r"\s+", " ", t or ""))).strip()

def details_of(it):
    dp = it.get("published", {}).get("date-parts", [[None]])[0]
    y = dp[0]; m = dp[1] if len(dp) > 1 else 0
    bits = []
    if it.get("volume"): bits.append(f"vol. {it['volume']}")
    if it.get("issue"): bits.append(f"no. {it['issue']}")
    if it.get("page"): bits.append(("pp. " if "-" in it["page"] else "art. ") + it["page"])
    bits.append((MON[m] + " " if m else "") + str(y))
    return ", ".join(bits)

def refresh_pubs(known_dois):
    auto = load("pubs_auto.json", {"ignore": [], "entries": []})
    have = set(known_dois) | {e["doi"].lower() for e in auto["entries"]} | set(x.lower() for x in auto.get("ignore", []))
    since = (TODAY - datetime.timedelta(days=120)).isoformat()
    added = []
    for tag, query, family, given, affs, coauthors, venue_re, area in FACULTY:
        try:
            items = get_json("https://api.crossref.org/works?" + urllib.parse.urlencode({
                "query.author": query, "filter": f"from-created-date:{since}", "rows": 200,
                "select": "DOI,title,container-title,published,author,type,volume,issue,page,event"}))["message"]["items"]
        except Exception as e:
            print(f"pubs {tag}: Crossref failed ({e})"); continue
        for it in items:
            doi = it["DOI"].lower()
            if doi in have or it.get("type") not in TYPES: continue
            venue = clean((it.get("container-title") or [""])[0])
            if EXCL_VENUE.search(venue + " " + clean((it.get("title") or [""])[0])): continue
            if not accept(it, tag, family, given, affs, coauthors, venue_re): continue
            dp = it.get("published", {}).get("date-parts", [[None]])[0]
            if not dp or not dp[0] or dp[0] < 2021: continue
            entry = next((e for e in auto["entries"] if e["doi"].lower() == doi), None)
            if entry:
                if tag not in entry["faculty"]: entry["faculty"].append(tag)
                continue
            entry = {"year": dp[0], "authors": [x for x in (initials(a) for a in it.get("author", [])) if x],
                     "title": clean((it.get("title") or [""])[0]), "venue": re.sub(r"^\d{4}\s+", "", venue),
                     "details": details_of(it), "doi": it["DOI"], "type": TYPES[it["type"]], "faculty": [tag], "area": area,
                     "found": TODAY.isoformat()}
            auto["entries"].append(entry); have.add(doi); added.append(f"{tag}: {entry['title'][:70]}")
        time.sleep(1)
    save("pubs_auto.json", auto)
    return added

# ------------------------------------------------------------------ NSF awards
NSF_PIS = ["Vokkarane", "Tseng", "Arias", "Son", "Aghara", "Luo", "Xie", "Cao", "Chigan", "Inalpolat", "Robinette", "Yu", "Akyurtlu", "Niezrecki", "Ranasingha", "Chakrabarti", "Evans"]

def refresh_grants(known_ids, known_titles):
    auto = load("grants_auto.json", {"ignore": [], "awards": []})
    have = {a["id"] for a in auto["awards"]} | set(known_ids) | set(auto.get("ignore", []))
    added = []
    for pi in NSF_PIS:
        url = "https://api.nsf.gov/services/v1/awards.json?" + urllib.parse.urlencode({
            "pdPIName": pi, "awardeeName": "University of Massachusetts Lowell", "dateStart": "01/01/2021",
            "printFields": "id,title,startDate,expDate,fundsObligatedAmt,piFirstName,piLastName,coPDPI,agency,awardeeName,fundProgramName"})
        try:
            awards = get_json(url).get("response", {}).get("award", [])
        except Exception as e:
            print(f"grants {pi}: NSF API failed ({e})"); continue
        for a in awards:
            if a.get("id") in have: continue
            if norm(a.get("piLastName")) != norm(pi): continue
            title = a.get("title", "")
            if any(norm(title) == norm(t) for t in known_titles): continue
            auto["awards"].append({"id": a["id"], "title": title, "pi": f"{a.get('piFirstName','')} {a.get('piLastName','')}".strip(),
                                   "copis": a.get("coPDPI", []), "start": a.get("startDate"), "end": a.get("expDate"),
                                   "amount": a.get("fundsObligatedAmt"), "program": a.get("fundProgramName", ""), "found": TODAY.isoformat()})
            have.add(a["id"]); added.append(f"{pi}: NSF #{a['id']} {title[:60]}")
        time.sleep(0.5)
    save("grants_auto.json", auto)
    return added

# ------------------------------------------------------------------ Google Scholar
def refresh_scholar(scholar_ids):
    """Current Google Scholar figures for every profile.

    Why this is harder than it looks: Scholar has no API, and it refuses automated requests from
    data-centre addresses. GitHub Actions runs on Azure, so a direct fetch from the weekly job is
    usually answered with an "unusual traffic" page. Two routes, tried in order:

      1. SerpApi, if a SERPAPI_KEY secret is set. It fetches Scholar on our behalf and returns the
         figures as JSON; it works from GitHub reliably. The free plan covers this site if Scholar is
         refreshed monthly (19 profiles a month), which is the default below.
      2. A direct fetch of the public profile page, which works from ordinary networks and is kept as
         the fallback.

    Every figure is checked against the profile's own name before it is stored. Three IDs were once
    shifted by one position, and a card showed another person's citations for months; this check
    makes that impossible to repeat silently. A failed or mismatched read keeps the previous value.
    """
    auto = load("scholar_auto.json", {})
    changed, problems = [], []
    key = os.environ.get("SERPAPI_KEY", "").strip()
    # Scholar moves slowly; a monthly refresh is plenty and keeps well inside a free SerpApi plan.
    MIN_DAYS = int(os.environ.get("SCHOLAR_MIN_DAYS", "25"))

    def surname(n):
        n = re.sub(r"\s*\(.*?\)", "", n).strip()
        return (n.split() or [""])[-1].lower()

    for name, sid in scholar_ids.items():
        prev = auto.get(name, {})
        try:
            last = datetime.date.fromisoformat(prev.get("date", "1900-01-01"))
            if (TODAY - last).days < MIN_DAYS:
                continue
        except ValueError:
            pass

        owner, cites, h, i10 = "", None, None, None
        if key:
            try:
                url = ("https://serpapi.com/search.json?engine=google_scholar_author&hl=en&author_id="
                       + urllib.parse.quote(sid) + "&api_key=" + urllib.parse.quote(key))
                data = json.loads(urllib.request.urlopen(url, timeout=60).read().decode("utf-8"))
                owner = (data.get("author") or {}).get("name", "")
                table = (data.get("cited_by") or {}).get("table", [])
                for row in table:
                    if "citations" in row: cites = row["citations"].get("all")
                    if "h_index" in row: h = row["h_index"].get("all")
                    if "i10_index" in row: i10 = row["i10_index"].get("all")
            except Exception as e:
                problems.append(f"{name}: SerpApi failed ({e})")
        if cites is None:
            try:
                req = urllib.request.Request(
                    f"https://scholar.google.com/citations?user={sid}&hl=en",
                    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                                           "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
                             "Accept-Language": "en-US,en;q=0.9"})
                page = urllib.request.urlopen(req, timeout=60).read().decode("utf-8", "ignore")
                if "unusual traffic" in page.lower():
                    problems.append(f"{name}: Scholar blocked the request (set SERPAPI_KEY to fix)")
                    continue
                m = re.search(r'<div id="gsc_prf_in">([^<]+)</div>', page)
                owner = m.group(1) if m else ""
                nums = re.findall(r'<td class="gsc_rsb_std">(\d[\d,]*)</td>', page)
                if len(nums) >= 6:
                    cites, h, i10 = (int(nums[k].replace(",", "")) for k in (0, 2, 4))
            except Exception as e:
                problems.append(f"{name}: fetch failed ({e})")
                continue
            time.sleep(5)

        if cites is None:
            problems.append(f"{name}: no figures on the page")
            continue
        if surname(name) not in owner.lower():
            problems.append(f"{name}: ID {sid} opens the profile of '{owner}'; rejected. Fix SCHOLAR in build_site.py")
            continue
        auto[name] = {"citations": int(cites), "h": int(h or 0), "i10": int(i10 or 0), "date": TODAY.isoformat()}
        if prev.get("citations") != int(cites) or prev.get("h") != int(h or 0):
            changed.append(f"{name}: {int(cites):,} citations, h {h}, i10 {i10}")

    save("scholar_auto.json", auto)
    for p in problems:
        print("scholar:", p)
    return changed + [f"PROBLEM {p}" for p in problems]

# ------------------------------------------------------------------ journal metrics (SCImago, open data)
def refresh_journals(venues):
    """Fill quartile and SJR for each journal from SCImago's ranking export. The Journal Impact Factor
    is Clarivate's and is not fetched; enter it by hand in journals.json from Journal Citation Reports."""
    import csv, io
    path = os.path.join(HERE, "journals.json")
    data = json.load(open(path)) if os.path.exists(path) else {}
    try:
        raw = urllib.request.urlopen(urllib.request.Request("https://www.scimagojr.com/journalrank.php?out=xls", headers=UA), timeout=180).read().decode("utf-8", "ignore")
    except Exception as e:
        print(f"journals: SCImago fetch failed ({e})"); return []
    rows = list(csv.DictReader(io.StringIO(raw), delimiter=";"))
    def key(n): return re.sub(r"[^a-z0-9]+", " ", n.lower()).strip()
    index = {key(row.get("Title", "")): row for row in rows}
    changed = []
    for v in venues:
        row = index.get(key(v))
        if not row: continue
        entry = data.setdefault(v, {})
        q = (row.get("SJR Best Quartile") or "").strip(); sjr = (row.get("SJR") or "").replace(",", ".").strip()
        upd = {}
        if q and q != entry.get("quartile"): upd["quartile"] = q
        if sjr:
            try:
                val = float(sjr)
                if val != entry.get("sjr"): upd["sjr"] = val
            except ValueError: pass
        if upd:
            entry.update(upd); entry.setdefault("source", f"SCImago {TODAY.year}")
            changed.append(f"{v}: {entry.get('quartile','')} SJR {entry.get('sjr','')}")
    json.dump(data, open(path, "w"), indent=1, ensure_ascii=False, sort_keys=True)
    return changed

# ------------------------------------------------------------------ main
def main():
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    # pull what the curated site already knows so the overlays only add
    site = open(os.path.join(HERE, "build_site.py"), encoding="utf-8").read()
    known_dois = [d.lower() for d in re.findall(r'"(10\.[^"]+)", "(?:journal|conference|chapter)"', site)]
    known_ids = re.findall(r"Award #(\d{7})", site)
    known_titles = re.findall(r'"title": "([^"]+)",\n\s+"amount"', site)
    scholar_ids = dict(re.findall(r'"([^"]+)": "([A-Za-z0-9_\-]{12})"', site[site.index("SCHOLAR = {"):site.index("ORCID = {")]))
    log = {"date": TODAY.isoformat()}
    if what in ("all", "pubs"): log["pubs"] = refresh_pubs(known_dois)
    if what in ("all", "grants"): log["grants"] = refresh_grants(known_ids, known_titles)
    if what in ("all", "scholar"): log["scholar"] = refresh_scholar(scholar_ids)
    if what in ("all", "journals"):
        try:
            venues = sorted(json.load(open(os.path.join(HERE, "journals.json"))).keys())
        except Exception:
            venues = []
        log["journals"] = refresh_journals(venues)
    save("refresh_log.json", log)
    for k, v in log.items():
        if isinstance(v, list): print(f"{k}: {len(v)} change(s)"); [print("  ", x) for x in v]

if __name__ == "__main__":
    main()
