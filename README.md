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
                       labs.html          the laboratories and instruments behind the center's work,
                                          and what each offers collaborators
                       summit.html        the NSF MRI SUMMIT project page
  images.json        embedded photos and figures
  logos/             sponsor logos (see logos/README.txt for the expected file names)
  refresh.py         scheduled data pull (see below)
  pubs_auto.json     papers found by refresh.py after the curated list was written
  grants_auto.json   NSF awards found by refresh.py that were not in the curated ledger
  scholar.json       citation figures the site prints, each with the date it was read
  journals.json      one row per journal on the site: impact factor, year, quartile, SJR, source.
                     Empty fields show nothing; fill what you have. The Journal Impact Factor is
                     Clarivate's, from Journal Citation Reports (UML has a licence), so it is entered
                     by hand; quartile and SJR come from SCImago, which the weekly refresh fills in.
                     The values in the file were entered in Sept 2026 from the 2023 JCR (the June 2024
                     release), the most recent edition available to the person who entered them. Two
                     JCR editions have come out since. To bring them current: open JCR, export the
                     journal list, and update the "if" and "if_year" fields.
  update_scholar.py  paste figures off the Scholar profile pages into scholar.json
  scholar_auto.json  figures refresh.py managed to read on its own, if any
  .github/workflows/refresh.yml   the weekly data job
  .github/workflows/scholar.yml   the Scholar update you run by hand from the Actions tab

Before you publish
  SITE_URL at the top of build_site.py is https://smartcyberphysical.org/ and must match the live address.
  A CNAME file in the repository root holds the same domain; GitHub Pages reads it on every deploy, and
  the build never deletes it. If the domain ever changes, change both.

  SITE_URL must match the live address. It feeds the canonical links,
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

Auto-posting to LinkedIn and X
  Two feeds are written on every build:
    feed.xml              every news item, each with a category (Award, Journal, Conference, Chapter,
                          Presentation, Milestone) and a description already written to fit a post,
                          under 270 characters, with the publisher link.
    feed-highlights.xml   only awards, milestones, and talks. Use this one for auto-posting: it is
                          already filtered, so a free posting plan with no filter step still works,
                          and it will not post twenty papers a quarter.

  Wiring it up, once:
    1. Create the accounts if they do not exist. For LinkedIn, ask UML communications for a Showcase
       Page under the university's company page rather than a standalone page; it inherits their
       verification. Put both URLs in the SOCIAL table in build_site.py so the site links to them.
    2. Sign in to Zapier (or Make, or IFTTT) and create a Zap:
         Trigger: RSS by Zapier, "New item in feed", https://<your site>/feed.xml
         Filter:  only continue if Category contains Award  (or Award, Milestone, Presentation)
         Action:  LinkedIn Pages, "Create Share"  and/or  X, "Create Tweet"
         Map the post body to Description, and the link to Link.
    3. Run it once by hand, check what it posted, then turn it on.

  Two things to decide rather than discover:
    - Post volume. Without the filter this posts every paper: 20 or more a quarter, mostly of narrow
      interest, which trains people to scroll past. Filtering to Award and Milestone gives a handful
      of posts a year that are actually worth reading. Journal filtering is a reasonable middle.
    - Cost and access. Zapier's free tier covers a low-volume feed like this. Posting to X through
      its own API now requires a paid tier for most use; going through Zapier avoids that. LinkedIn
      company-page posting works through Zapier's LinkedIn Pages action and needs you to be a page
      admin; posting to a personal profile from an app requires LinkedIn app review.

  The item ids in the feed are content hashes, so a rebuild never makes an old item look new. If you
  edit a news item's title after it has posted, it will post again under the new title.

Animations
  Every moving element is an SVG class: flow (dashes travelling along a path), pulse (opacity),
  spin (rotation), grow (bar height), trace (a segment sweeping a line). Rules that keep them honest:
    - transform-origin lives on the same element as the class. A class on a <g> with the origin on a
      child scales about the canvas corner and the bars drift; that bug has been fixed once already.
    - trace paths carry pathLength="100" so the sweep covers the whole line whatever its length.
    - Figures pause while off screen (IntersectionObserver), so a page with sixty animated elements
      only runs the ones in view.
    - prefers-reduced-motion switches every animation off and draws the dashed paths solid.

Attribution rule
  A paper counts for a member only from the year they joined UMass Lowell (JOIN_YEAR in build_site.py:
  Tseng 2024, Arias 2021). Work done at a previous institution is dropped from the site and from the
  center's counts, so the figures here match what the center can defend in a review.

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
    Journals       quartile and SJR from SCImago's public ranking export, matched by journal name into
                   journals.json. Impact factor is never fetched: Clarivate licenses it, and displaying
                   it publicly is something to check with the library before you do.
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
