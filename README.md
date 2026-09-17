SCyPS site: how it stays current
=================================

Files
  build_site.py      all curated content and all four page templates:
                       index.html         home: about, research, projects, sponsors, and teasers that link on
                                          to people, publications, and news
                       people.html        director, faculty, affiliated researchers, external collaborators
                       students.html      doctoral students and the lab-life gallery
                       alumni.html        Ph.D. graduates, postdoctoral alumni, and the giving box
                       publications.html  the full searchable, filterable list
                       news.html          auto-generated from the last three months of papers, awards, and
                                          milestones, filterable by type, with a live stream of the newest
                                          papers in the right column
                       research-*.html    one page per research thrust (grid, ai, fiber, edge, chip,
                                          health): the question it asks, what the group builds, the faculty
                                          on it, its projects and tools, and its recent papers
                       summit.html        the NSF MRI SUMMIT project page
  images.json        embedded photos and figures
  logos/             sponsor logos (see logos/README.txt for the expected file names)
  refresh.py         scheduled data pull (see below)
  pubs_auto.json     papers found by refresh.py after the curated list was written
  grants_auto.json   NSF awards found by refresh.py that were not in the curated ledger
  scholar.json       citation figures the site prints, each with the date it was read
  update_scholar.py  paste figures off the Scholar profile pages into scholar.json
  scholar_auto.json  figures refresh.py managed to read on its own, if any
  .github/workflows/refresh.yml   the weekly data job
  .github/workflows/scholar.yml   the Scholar update you run by hand from the Actions tab

Before you publish
  SITE_URL at the top of build_site.py must match the live address. It feeds the canonical links,
  the social-card metadata, robots.txt, and sitemap.xml. It is currently set to
  https://vinodvokkarane.github.io/scyps-site/ — change it if the site moves to scyps.uml.edu.

  og-card.png is referenced by the social metadata but is not generated. Drop a 1200x630 image with
  that name in the repository root, or the link previews on LinkedIn and X will fall back to nothing.

  Known limits, so they are decisions rather than surprises:
    - The visitor counter is a third-party image from hits.sh. It counts image loads, not people,
      and it sends each visitor's page address to that service.
    - Google Fonts and Font Awesome load from Google and Cloudflare. Both are third-party requests
      on every page view. Self-hosting the four font files would remove them.
    - Citation figures print the date they were read. Anything older than about six months is
      labelled as not refreshed, so a stale number cannot pass as current.
    - The publication list counts every paper by any of the 18 faculty, not only work done under the
      center. Use it as a reach figure, not as center output, in reports.

Build by hand
  python3 refresh.py          # optional: pull new data
  python3 build_site.py index.html      # writes all thirteen pages next to it

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
    Scholar        Google has no API and blocks automated readers, so this step often fails. The reliable
                   route is to enter them yourself, either way below. Each figure is stored with the date it
                   was entered and the site prints that date.

                   From the browser (no setup): repository > Actions > "Update Google Scholar figures" >
                   Run workflow. Paste one line per person into the box, one per line:
                       Vokkarane 5990 37 96
                       Chigan 1450 18 24
                   Name fragment, citations, h-index, optional i10-index. The job writes scholar.json,
                   bumps the version, rebuilds both pages, and commits. Pages redeploys on its own.

                   From a checkout: `python3 update_scholar.py` prints every profile link and takes the
                   same lines on standard input, then `python3 build_site.py index.html`.
    News           news.html builds itself on every run from three sources: papers dated in the last three
                   months, awards whose period starts in that window, and hand-written entries in NEWS that
                   fall in it. If fewer than six items land in three months the window widens automatically
                   until it finds six, and the page says which span it is showing. Journal issues dated up to
                   four months ahead are included and labeled "issue" so a December issue does not read as
                   something that already happened. To add something the data cannot know, put it in NEWS.

  Reviewing what it added
    refresh_log.json lists every change from the last run. To reject an automatic entry, delete it from
    the overlay file and add its DOI (papers) or award id (grants) to that file's "ignore" list; it will
    not be re-added. To promote an entry, copy it into build_site.py.
