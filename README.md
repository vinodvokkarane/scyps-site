SCyPS site: how it stays current
=================================

Files
  build_site.py      all curated content (people, projects, papers through Sept. 2026) and both page templates (index.html, summit.html)
  images.json        embedded photos and figures
  logos/             sponsor logos (see logos/README.txt for the expected file names)
  refresh.py         scheduled data pull (see below)
  pubs_auto.json     papers found by refresh.py after the curated list was written
  grants_auto.json   NSF awards found by refresh.py that were not in the curated ledger
  scholar_auto.json  latest Google Scholar citation counts and h-index
  .github/workflows/refresh.yml   the weekly job

Build by hand
  python3 refresh.py          # optional: pull new data
  python3 build_site.py index.html      # also writes summit.html (the NSF MRI SUMMIT project page) next to it

Automatic updates
  Once this folder is a GitHub repository with Pages turned on, the workflow runs every Monday
  (and on demand from the Actions tab). It runs refresh.py, bumps SITE_VERSION when anything
  changed, rebuilds index.html, and commits. Pages redeploys within a minute of the commit.

  What refresh.py pulls
    Publications   Crossref, per faculty member, with the same affiliation and co-author rules used
                   to vet the curated list. Only works registered in the last 120 days are examined.
    Grants         NSF Awards API, for each faculty member at UMass Lowell, awards starting 2021 or later.
                   Other sponsors (DOE, ONR, Army, state, industry) have no public award API; add those
                   by hand in build_site.py.
    Scholar        "Cited by" and h-index read from each public profile listed in SCHOLAR. Google throttles
                   automated readers; a failed read keeps the previous figure.
    News           not automated; edit NEWS in build_site.py.

  Reviewing what it added
    refresh_log.json lists every change from the last run. To reject an automatic entry, delete it from
    the overlay file and add its DOI (papers) or award id (grants) to that file's "ignore" list; it will
    not be re-added. To promote an entry, copy it into build_site.py.
