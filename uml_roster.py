"""UMass Lowell people whose NSF awards appear on the center site.

One place for this list: refresh.py pulls awards for these people, and build_site.py accepts an award
only when its PI or a Co-PI is one of them. First and last names as NSF records them. External
collaborators and members now at other institutions are not listed; their awards are made elsewhere.
"""
UML_PEOPLE = [
    ("Vinod", "Vokkarane"), ("Sukesh", "Aghara"), ("Orlando", "Arias"), ("Yan", "Luo"),
    ("Seung Woo", "Son"), ("Lewis", "Tseng"), ("Yuanchang", "Xie"),
    ("Alkim", "Akyurtlu"), ("Yu", "Cao"), ("Supriya", "Chakrabarti"), ("Chunxiao", "Chigan"),
    ("Nicholas", "Evans"), ("Murat", "Inalpolat"), ("Christopher", "Niezrecki"), ("Sheree", "Pagsuyoin"),
    ("Oshadha", "Ranasingha"), ("Paul", "Robinette"), ("Hengyong", "Yu"),
]
UML_NAME = "university of massachusetts lowell"

import re as _re

def _n(s):
    """Lower case, letters only, single-letter middle initials dropped: 'Seung-Woo' and 'Seung Woo' agree."""
    toks = _re.findall(r"[a-z]+", (s or "").lower())
    return "".join(t for t in toks if len(t) > 1)

def split_name(full):
    """'Yan Luo', 'Luo, Yan', 'Yan Luo~000123456' (NSF co-PI form) into (first, last)."""
    full = (full or "").split("~")[0].strip()
    if "," in full:
        last, first = [x.strip() for x in full.split(",", 1)]
        return first, last
    parts = full.split()
    return (" ".join(parts[:-1]), parts[-1]) if len(parts) > 1 else ("", full)

def roster_match(first, last):
    """The roster person with this exact first and last name, or None."""
    for f, l in UML_PEOPLE:
        if _n(l) == _n(last) and _n(f) == _n(first):
            return f"{f} {l}"
    return None

def is_uml(awardee):
    a = _re.sub(r"[^a-z ]", " ", (awardee or "").lower())
    a = _re.sub(r"\s+", " ", a).strip()
    return a == UML_NAME or a == "university of massachusetts at lowell"
