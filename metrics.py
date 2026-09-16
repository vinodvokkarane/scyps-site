#!/usr/bin/env python3
"""Fetch citation metrics for the SCyPS faculty and write metrics.json.

    python3 metrics.py openalex     # preferred: OpenAlex author profiles (needs normal internet)
    python3 metrics.py crossref     # fallback: computed from Crossref citation counts per paper

build_site.py reads metrics.json and prints the figures on each faculty card.
OpenAlex counts run close to Google Scholar; Crossref counts are lower because Crossref only
sees citations that publishers deposit, so the source is printed next to every figure.
"""
import json, sys, time, urllib.request, urllib.parse, datetime

UA = {"User-Agent": "SCyPS-site-builder/1.0 (mailto:SCyPS@uml.edu)"}

# name, family, given prefix, institution keyword for OpenAlex, and (for Crossref) disambiguation rules
FACULTY = [
    ("Vinod M. Vokkarane", "Vokkarane", "V", "Lowell", {}),
    ("Orlando Arias", "Arias", "Orlando", "Lowell", {}),
    ("Lewis Tseng", "Tseng", "Lewis", "Lowell", {}),
    ("Seung Woo Son", "Son", "Seung", "Lowell",
     {"aff": ["Massachusetts Lowell", "Argonne", "Northwestern", "Pennsylvania State", "Penn State", "UMass Lowell"],
      "coauthors": ["Kandemir", "Choudhary", "Wei-keng Liao", "Wei-Keng Liao", "Aekyeung Moon", "Arias", "Chaisson", "Azzaoui", "Minjun Choi",
                    "Jeongseob Ahn", "Rajeev Thakur", "Robert Ross", "Ankit Agrawal", "Jungeun Yoon", "Yunhee Jeong", "Eunsang Yu", "Sangmin Seo"]}),
    ("Sukesh Aghara", "Aghara", "S", "Lowell", {}),
    ("Yuzhang Lin", "Lin", "Yuzhang", "New York University",
     {"aff": ["New York University", "Massachusetts Lowell", "Northeastern", "Tsinghua"],
      "coauthors": ["Abur", "Vokkarane", "Zahidul Islam", "Edib", "Heqing Huang", "Guibin Chen", "Wentao Zhang", "Nitish Sharma",
                    "Junbo Zhao", "Fei Ding", "Yiyun Yao", "Ogle", "Sasaninia", "Arias", "Sai Qian Zhang", "Hongfu Liu", "Yangmin Ding"]}),
    ("Yan Luo", "Luo", "Yan", "Lowell",
     {"aff": ["Massachusetts Lowell", "UMass Lowell"],
      "coauthors": ["Vokkarane", "Yu Cao", "Guanling Chen", "Benyuan Liu", "Tingshu Hu", "Inalpolat", "Niezrecki", "Sabato", "Yunsheng Ma",
                    "Hengyong Yu", "Jomol Mathew", "Laxmi Bhuyan", "Jun Yang", "Hao Wang", "Chunhua Wang", "Tian Guo", "Cody Cutler", "Kshitij Jerath"]}),
    ("Yuanchang Xie", "Xie", "Yuanchang", "Lowell", {}),
    ("Yu Cao", "Cao", "Yu", "Lowell",
     {"aff": ["Massachusetts Lowell", "UMass Lowell"],
      "coauthors": ["Yan Luo", "Vokkarane", "Guanling Chen", "Benyuan Liu", "Yunsheng Ma", "Jomol Mathew", "Chang Liu", "Peiyuan Zhou", "Xu Ran", "Shuai Chen"]}),
    ("Chunxiao (Tricia) Chigan", "Chigan", "Chunxiao", "Lowell", {}),
    ("Murat Inalpolat", "Inalpolat", "Murat", "Lowell", {}),
    ("Paul Robinette", "Robinette", "Paul", "Lowell", {}),
    ("Hengyong Yu", "Yu", "Hengyong", "Lowell",
     {"aff": ["Massachusetts Lowell", "Wake Forest", "Virginia Tech", "UMass Lowell"],
      "coauthors": ["Ge Wang", "Dayang Wang", "Shuo Han", "Bahareh Morovati", "Li Zhou", "Panpan Wu", "Changsheng Fang", "Yang Chen", "Yongshun Xu",
                    "Mengzhou Li", "Chuang Niu", "Fenglei Fan", "Feng-Lei Fan", "Ying Chu", "Wenxiang Cong", "Ziping Zhao", "Boce Zhang"]}),
    ("Alkim Akyurtlu", "Akyurtlu", "Alkim", "Lowell", {}),
    ("Christopher Niezrecki", "Niezrecki", "Christopher", "Lowell", {}),
    ("Oshadha Ranasingha", "Ranasingha", "Oshadha", "Lowell", {}),
    ("Anurag Srivastava", "Srivastava", "Anurag", "West Virginia",
     {"aff": ["West Virginia", "Washington State", "Mississippi State", "Pacific Northwest"],
      "coauthors": ["Zhang", "Venkataramanan", "Pipattanasomporn", "Rahman", "Schulz", "Bose", "Vaiman"]}),
]

def get(url):
    return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120))

def openalex(name, inst):
    d = get("https://api.openalex.org/authors?" + urllib.parse.urlencode({"search": name, "per_page": 15, "mailto": "SCyPS@uml.edu"}))
    for a in d.get("results", []):
        insts = (a.get("last_known_institutions") or []) + [x.get("institution") or {} for x in (a.get("affiliations") or [])]
        if inst.lower() in json.dumps(insts).lower():
            return {"citations": a.get("cited_by_count", 0), "h": (a.get("summary_stats") or {}).get("h_index", 0),
                    "works": a.get("works_count", 0), "id": a.get("id")}
    return None

def crossref(family, given, rules, full_name=None, max_pages=6):
    """Relevance-ranked pages of Crossref works for the name, strictly filtered to this author."""
    counts, seen, dry = [], set(), 0
    for page in range(max_pages):
        d = get("https://api.crossref.org/works?" + urllib.parse.urlencode({
            "query.author": full_name or family, "rows": 1000, "offset": page * 1000, "sort": "relevance",
            "select": "DOI,author,type,is-referenced-by-count"}))["message"]
        items = d.get("items", []); before = len(seen)
        for it in items:
            if it.get("type") in ("posted-content", "peer-review", "component", "grant"):
                continue
            me = None
            for a in it.get("author", []):
                fam = a.get("family", "").lower(); giv = a.get("given", "").lower().replace("-", " ").replace(".", "").strip()
                if fam == family.lower() and (not given or giv.startswith(given.lower())):
                    me = a; break
            if not me or it["DOI"] in seen:
                continue
            if rules:
                affs = " ".join(x.get("name", "") for x in me.get("affiliation", []))
                ok = any(k.lower() in affs.lower() for k in rules.get("aff", []))
                if not ok and not affs:
                    names = [((a.get("given", "") + " " + a.get("family", "")).strip()) for a in it.get("author", [])]
                    ok = any(any(c.lower() in n.lower() for n in names) for c in rules.get("coauthors", []))
                if not ok:
                    continue
            seen.add(it["DOI"]); counts.append(it.get("is-referenced-by-count", 0))
        dry = dry + 1 if len(seen) == before else 0
        if len(items) < 1000 or dry >= 1:
            break
        time.sleep(1.0)
    counts.sort(reverse=True)
    h = sum(1 for i, c in enumerate(counts, 1) if c >= i)
    return {"citations": sum(counts), "h": h, "works": len(counts)}

def main():
    source = (sys.argv[1] if len(sys.argv) > 1 else "openalex").lower()
    out = {"_source": "OpenAlex" if source == "openalex" else "Crossref", "_date": datetime.date.today().isoformat()}
    only = sys.argv[2] if len(sys.argv) > 2 else None
    for name, family, given, inst, rules in FACULTY:
        if only and only.lower() not in name.lower(): continue
        try:
            m = openalex(name, inst) if source == "openalex" else crossref(family, given, rules, full_name=name.replace(" M.", "").replace(" (Tricia)", ""))
        except Exception as e:
            print(f"{name}: failed ({e})"); m = None
        if m:
            out[name] = m; print(f"{name:28s} citations {m['citations']:>7,}  h {m['h']:>3}  works {m['works']:>4}")
        else:
            print(f"{name:28s} no match")
        time.sleep(0.3)
    fn = "metrics.json" if not only else f"metrics_{only.split()[-1].lower()}.json"
    json.dump(out, open(fn, "w"), indent=1)
    print("wrote", fn)

if __name__ == "__main__":
    main()
