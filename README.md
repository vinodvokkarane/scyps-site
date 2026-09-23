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

Structured data, positions page, Wikidata
  Every page carries schema.org JSON-LD generated from the same records as the visible content: the
  center as a ResearchOrganization (home), every member as a Person with ORCID and Scholar identifiers
  (home, people), every paper as a ScholarlyArticle (publications), SUMMIT as a ResearchProject, and
  the postdoc as a JobPosting (home, positions). Nothing to maintain; it regenerates on every build.
  To check it, paste a page URL into https://validator.schema.org/ or Google's Rich Results Test.

  positions.html lists open roles from the POSITIONS list in build_site.py; edit that list to add or
  close one. It is linked as "Join" in the navigation.

  wikidata-draft.md (in the outputs) has everything needed to create the center's Wikidata item. Once
  it exists, add the Q-number as "sameAs" on the organization in ld_organization().

  After uploading: submit https://smartcyberphysical.org/sitemap.xml to Google Search Console
  (search.google.com/search-console, verify the domain by the DNS TXT record it gives you, added in
  Cloudflare) and to Bing Webmaster Tools. That is what gets the structured data read.

No third-party requests
  The site loads nothing from anyone else. Fonts (Fraunces, IBM Plex Sans, Barlow; SIL OFL) are served
  from fonts/, copied there on every build from the fonts/ folder beside build_site.py. The seven social
  icons are inline SVG (Font Awesome Free, CC BY 4.0; the attribution is in each page's first line).
  One exception, by choice: the visitor counter in the footer (hits.sh). It is the only request the
  site makes to another party. It counts once per visitor session, not per page. Remove the block
  marked "visitor counter" in the script and the #visits span in the footer to drop it. For a second,
  independent figure, GitHub's Insights > Traffic page reports views and unique visitors for the last
  fourteen days; the "Traffic snapshot" workflow records those numbers monthly in traffic.json.

Traffic snapshot (one-time token)
  GitHub keeps traffic figures for fourteen days. The "Traffic snapshot" workflow copies them into
  traffic.json on the 1st and 15th. Reading traffic needs the repository's Administration: read
  permission, which the automatic workflow token cannot have, so it uses a personal token:
    1. GitHub, top right photo > Settings > Developer settings > Personal access tokens >
       Fine-grained tokens > Generate new token.
    2. Name: SCyPS traffic. Expiration: the longest allowed (a year). Resource owner: your account.
       Repository access: Only select repositories > scyps-site.
    3. Permissions > Repository permissions > Administration: Read-only. (Metadata: Read-only is added
       by itself.) Nothing else. Generate, and copy the token; it is shown once.
    4. The site repository > Settings > Secrets and variables > Actions > New repository secret.
       Name: TRAFFIC_TOKEN. Value: the token.
  The token expires. When it does, the snapshot run fails with "403 ... or has expired"; generate a
  new one the same way and update the secret. A calendar reminder a week before expiry saves a gap.

Sending the newsletter (director@smartcyberphysical.org)
  The site cannot send mail, and Cloudflare Email Routing only forwards mail in. Sending goes through
  Resend (resend.com), which lets the domain send authenticated mail from a GitHub workflow. The free
  plan allows 3,000 messages a month and 100 a day; the newsletter uses about 22 a month. Sending
  pauses at the cap rather than charging.

  A. One-time setup, about fifteen minutes, most of it waiting for DNS

  1. Create a Resend account at resend.com. Any login works; use the UML address so a colleague can
     take it over later.

  2. Add the domain. Domains > Add Domain > smartcyberphysical.org. Region: US East. Resend shows
     three DNS records. Leave that page open.

  3. Add those three records in Cloudflare. Cloudflare dashboard > smartcyberphysical.org > DNS >
     Add record. For each, set Proxy status to DNS only (grey cloud), like the site's records:

       Type   Name                 Content
       TXT    resend._domainkey    p=MIGf...  (the long DKIM key)
       CNAME  rsend                rsend.forge.rmta.net
       CNAME  send                 send.forge.rmta.net

     Copy the values from the Resend page, not from here: the DKIM key is specific to your account
     and the dashboard truncates it on screen, so click it to expand before copying. A key with
     characters missing fails silently. (Verified for this domain in September 2026.)

  4. Add a DMARC record, which Resend does not create but mail providers now expect. Same DNS page:

       Type  Name      Content
       TXT   _dmarc    v=DMARC1; p=none; rua=mailto:Vinod_Vokkarane@uml.edu

     p=none means "report, do not reject", which is enough to pass the check. If a DMARC record
     already exists (Cloudflare Email Routing sometimes adds one), edit it rather than adding a second.

  5. Back in Resend, click Verify. Green within a few minutes, occasionally an hour. Until it is
     verified, Resend will send only to the account's own address, so nothing can go out by mistake.

  6. Create the API key. Resend > API Keys > Create API Key. Name: "SCyPS newsletter". Permission:
     Sending access. Domain: smartcyberphysical.org. Copy the key; it is shown once.

  7. Store it in the repository. GitHub > the site repository > Settings > Secrets and variables >
     Actions > New repository secret. Name: RESEND_API_KEY. Value: the key. Save.

  8. Make replies work. Leave Resend's "Enable Receiving" switch off; Cloudflare handles inbound mail.
     Cloudflare > Email > Email Routing > Create address: director, forwarding to
     Vinod_Vokkarane@uml.edu. Cloudflare sends a verification message to that inbox; click the link.
     The newsletter also sets Reply-To to the UML address, so replies reach a person either way.

  9. Check recipients.txt in the repository. One address per line; lines starting with # are
     ignored. Add students and anyone new. Recipients are sent as BCC.

  10. Test. GitHub > Actions > Send newsletter > Run workflow. Month: blank (the previous month).
      To: director. Run. The issue arrives in the UML inbox within a minute with [Preview] in the
      subject. If it does not, open the run: the log names the failure (unverified domain, missing
      key, or an empty recipients file are the three that happen).

  B. The monthly cycle after that, with no one doing anything

  Day 1   "Monthly newsletter" builds the previous month's issue from the site's records, commits it
          to newsletters/, and mails a [Preview] to the director.
  Day 4   "Send newsletter" mails the issue to everyone in recipients.txt and writes a line to
          newsletters/sent.log.

  The three days are the review window. If the preview is wrong (a misattributed paper, an award
  that is not public yet), set a repository variable to stop the send: Settings > Secrets and
  variables > Actions > Variables > New repository variable, name NEWSLETTER_HOLD, value true. The
  scheduled send skips while that is set. Fix the data, rebuild, then send by hand (Actions > Send
  newsletter > Run workflow, To: list) and delete the variable.

  C. Things to know
  - Resend's terms forbid cold email. A newsletter to colleagues and named collaborators is fine;
    do not add addresses of people who have not worked with the center.
  - The sender is director@smartcyberphysical.org; the display name is the center's. If the domain
    ever changes with the center's name, the domain has to be verified in Resend again and FROM in
    send_newsletter.py updated.
  - Resend keeps 30 days of delivery logs (Resend > Emails). newsletters/sent.log in the repository
    is the permanent record of what was sent when.
  - Unsubscribe requests arrive as replies with the subject "Unsubscribe" (the link in the footer).
    Remove the address from recipients.txt; nothing is automatic about that, by design.

Monthly newsletter
  Every month the site can write an issue from its own records: new papers, new awards, milestones,
  and what starts next month, with a "work with us" close. Three files per issue land in newsletters/:
    YYYY-MM.html        the web issue, in the site's design, listed at newsletters/index.html
    YYYY-MM-email.html  the same issue laid out for email (tables, inline styles, hosted logo)
    YYYY-MM.txt         plain text
  The "Structured data, positions page, Wikidata
  Every page carries schema.org JSON-LD generated from the same records as the visible content: the
  center as a ResearchOrganization (home), every member as a Person with ORCID and Scholar identifiers
  (home, people), every paper as a ScholarlyArticle (publications), SUMMIT as a ResearchProject, and
  the postdoc as a JobPosting (home, positions). Nothing to maintain; it regenerates on every build.
  To check it, paste a page URL into https://validator.schema.org/ or Google's Rich Results Test.

  positions.html lists open roles from the POSITIONS list in build_site.py; edit that list to add or
  close one. It is linked as "Join" in the navigation.

  wikidata-draft.md (in the outputs) has everything needed to create the center's Wikidata item. Once
  it exists, add the Q-number as "sameAs" on the organization in ld_organization().

  After uploading: submit https://smartcyberphysical.org/sitemap.xml to Google Search Console
  (search.google.com/search-console, verify the domain by the DNS TXT record it gives you, added in
  Cloudflare) and to Bing Webmaster Tools. That is what gets the structured data read.

No third-party requests
  The site loads nothing from anyone else. Fonts (Fraunces, IBM Plex Sans, Barlow; SIL OFL) are served
  from fonts/, copied there on every build from the fonts/ folder beside build_site.py. The seven social
  icons are inline SVG (Font Awesome Free, CC BY 4.0; the attribution is in each page's first line).
  One exception, by choice: the visitor counter in the footer (hits.sh). It is the only request the
  site makes to another party. It counts once per visitor session, not per page. Remove the block
  marked "visitor counter" in the script and the #visits span in the footer to drop it. For a second,
  independent figure, GitHub's Insights > Traffic page reports views and unique visitors for the last
  fourteen days; the "Traffic snapshot" workflow records those numbers monthly in traffic.json.

Monthly newsletter" workflow runs on the first of each month for the previous month, commits
  the issue, and attaches the email and text versions to the run so you can download them. It can be
  run by hand for any month: Actions > Structured data, positions page, Wikidata
  Every page carries schema.org JSON-LD generated from the same records as the visible content: the
  center as a ResearchOrganization (home), every member as a Person with ORCID and Scholar identifiers
  (home, people), every paper as a ScholarlyArticle (publications), SUMMIT as a ResearchProject, and
  the postdoc as a JobPosting (home, positions). Nothing to maintain; it regenerates on every build.
  To check it, paste a page URL into https://validator.schema.org/ or Google's Rich Results Test.

  positions.html lists open roles from the POSITIONS list in build_site.py; edit that list to add or
  close one. It is linked as "Join" in the navigation.

  wikidata-draft.md (in the outputs) has everything needed to create the center's Wikidata item. Once
  it exists, add the Q-number as "sameAs" on the organization in ld_organization().

  After uploading: submit https://smartcyberphysical.org/sitemap.xml to Google Search Console
  (search.google.com/search-console, verify the domain by the DNS TXT record it gives you, added in
  Cloudflare) and to Bing Webmaster Tools. That is what gets the structured data read.

No third-party requests
  The site loads nothing from anyone else. Fonts (Fraunces, IBM Plex Sans, Barlow; SIL OFL) are served
  from fonts/, copied there on every build from the fonts/ folder beside build_site.py. The seven social
  icons are inline SVG (Font Awesome Free, CC BY 4.0; the attribution is in each page's first line).
  One exception, by choice: the visitor counter in the footer (hits.sh). It is the only request the
  site makes to another party. It counts once per visitor session, not per page. Remove the block
  marked "visitor counter" in the script and the #visits span in the footer to drop it. For a second,
  independent figure, GitHub's Insights > Traffic page reports views and unique visitors for the last
  fourteen days; the "Traffic snapshot" workflow records those numbers monthly in traffic.json.

Monthly newsletter > Run workflow > month YYYY-MM.
  Locally: python3 build_site.py index.html --newsletter=2026-08

  Sending is automated through Resend; see "Sending the newsletter" above. Read the preview that
  arrives on the 1st; the opening line and the paper list are automatic, so a mis-attributed paper in
  the site's records would reach subscribers on the 4th unless you set NEWSLETTER_HOLD.

Google Scholar figures
  Every profile with an ID in SCHOLAR (build_site.py) is refreshed each Monday by the weekly job:
  faculty, alumni, and current students. Students show the figures on their card on the Students
  page. To add a student, put the name exactly as written in STUDENTS and the user= part of their
  Scholar URL into SCHOLAR; the figures appear after the next Monday run, or at once through the
  manual route below.

  Scholar has no API and blocks automated requests from data-centre addresses, which includes GitHub
  Actions, so the weekly job reads Scholar through SerpApi:
    1. Create a free account at serpapi.com and copy the API key from the dashboard.
    2. In the repository: Settings > Secrets and variables > Actions > New repository secret.
       Name: SERPAPI_KEY   Value: the key.
    3. The refresh step in .github/workflows/refresh.yml must hand the key to refresh.py:
         - name: Pull new publications, NSF awards, and Scholar counts
           run: python3 refresh.py
           env:
             SERPAPI_KEY: ${{ secrets.SERPAPI_KEY }}
  Budget: about 34 lookups a run, 140 to 170 a month, inside SerpApi's free plan (250 a month and
  50 an hour when this was written). refresh.py reads the stalest profiles first and stops at 45
  lookups a run (SCHOLAR_MAX_PER_RUN), so a growing roster cannot push a run past either limit; what a
  run leaves out goes first the following week. SCHOLAR_MIN_DAYS (default 6) skips profiles read in
  the last six days, so a manual run mid-week costs almost nothing.
  Without the key the job still tries a direct fetch, which usually fails from GitHub.

  Every figure is checked against the profile's own name before it is stored. If an ID in SCHOLAR
  opens someone else's profile, the refresh log says so and the figure is rejected. Three IDs were once
  shifted by one position and a card showed another person's citations; the check prevents a repeat.

  The manual route still works: Actions > Update Google Scholar figures, paste "Name citations h i10".

Insights page (insights.html)
  The center's records read together: a map of all papers grouped into research clusters, the
  collaboration matrix among the director and center faculty, the outside literature the papers cite
  most, citation reach, the doctoral students and alumni as they appear in the record, and which awards
  match which clusters. Everything is computed at build time; nothing runs in the visitor's browser
  beyond tap-to-focus on the map.
    insights.py          the computation and the page (called by build_site.py after the other pages)
    insights_names.json  hand-written cluster names and summaries, keyed by each cluster's anchor DOI
    graph_fetch.py       Crossref reference lists and citation counts for every DOI (weekly, via refresh.py)
    graph_auto.json      what graph_fetch.py wrote; commit it with the rest
  Clusters are found with the Louvain method over three ties between papers: shared references (half the
  weight), title and venue terms (a third), shared authors (the rest). They can change shape as papers
  and references arrive. To see the current clusters with their anchor DOIs and top terms:
    python3 insights.py --explain
  A cluster whose anchor DOI is in insights_names.json shows its written name and summary; any other is
  labelled from its own terms until a name is added. Names are keyed to anchors rather than positions so
  a rebuild never attaches a summary to the wrong cluster.
  The one dependency is networkx; build_site.py installs it on the GitHub runner if it is missing.
  Reference lists are open for nearly all of the group's publishers; abstracts are not (Crossref has them
  for almost none of these DOIs), which is why the graph rests on structure rather than text. Adding
  full-text extraction (methods, testbeds, results) is the planned next step.

Structured data, positions page, Wikidata
  Every page carries schema.org JSON-LD generated from the same records as the visible content: the
  center as a ResearchOrganization (home), every member as a Person with ORCID and Scholar identifiers
  (home, people), every paper as a ScholarlyArticle (publications), SUMMIT as a ResearchProject, and
  the postdoc as a JobPosting (home, positions). Nothing to maintain; it regenerates on every build.
  To check it, paste a page URL into https://validator.schema.org/ or Google's Rich Results Test.

  positions.html lists open roles from the POSITIONS list in build_site.py; edit that list to add or
  close one. It is linked as "Join" in the navigation.

  wikidata-draft.md (in the outputs) has everything needed to create the center's Wikidata item. Once
  it exists, add the Q-number as "sameAs" on the organization in ld_organization().

  After uploading: submit https://smartcyberphysical.org/sitemap.xml to Google Search Console
  (search.google.com/search-console, verify the domain by the DNS TXT record it gives you, added in
  Cloudflare) and to Bing Webmaster Tools. That is what gets the structured data read.

No third-party requests
  The site loads nothing from anyone else. Fonts (Fraunces, IBM Plex Sans, Barlow; SIL OFL) are served
  from fonts/, copied there on every build from the fonts/ folder beside build_site.py. The seven social
  icons are inline SVG (Font Awesome Free, CC BY 4.0; the attribution is in each page's first line).
  One exception, by choice: the visitor counter in the footer (hits.sh). It is the only request the
  site makes to another party. It counts once per visitor session, not per page. Remove the block
  marked "visitor counter" in the script and the #visits span in the footer to drop it. For a second,
  independent figure, GitHub's Insights > Traffic page reports views and unique visitors for the last
  fourteen days; the "Traffic snapshot" workflow records those numbers monthly in traffic.json.

Traffic snapshot (one-time token)
  GitHub keeps traffic figures for fourteen days. The "Traffic snapshot" workflow copies them into
  traffic.json on the 1st and 15th. Reading traffic needs the repository's Administration: read
  permission, which the automatic workflow token cannot have, so it uses a personal token:
    1. GitHub, top right photo > Settings > Developer settings > Personal access tokens >
       Fine-grained tokens > Generate new token.
    2. Name: SCyPS traffic. Expiration: the longest allowed (a year). Resource owner: your account.
       Repository access: Only select repositories > scyps-site.
    3. Permissions > Repository permissions > Administration: Read-only. (Metadata: Read-only is added
       by itself.) Nothing else. Generate, and copy the token; it is shown once.
    4. The site repository > Settings > Secrets and variables > Actions > New repository secret.
       Name: TRAFFIC_TOKEN. Value: the token.
  The token expires. When it does, the snapshot run fails with "403 ... or has expired"; generate a
  new one the same way and update the secret. A calendar reminder a week before expiry saves a gap.

Sending the newsletter (director@smartcyberphysical.org)
  The site cannot send mail by itself and Cloudflare Email Routing only forwards, so sending goes
  through Resend (resend.com), which lets the domain send authenticated mail. One-time setup:
    1. Create a Resend account. Add the domain smartcyberphysical.org. Resend shows three DNS records
       (a DKIM TXT record, and an MX plus SPF TXT on a "send." subdomain). Add them in Cloudflare's DNS
       page, all DNS-only (grey cloud). Click Verify in Resend. Takes a few minutes.
    2. In Resend, create an API key with sending permission. In the repository: Settings > Secrets
       and variables > Actions > New repository secret: RESEND_API_KEY.
    3. In Cloudflare, Email > Email Routing: create director@smartcyberphysical.org forwarding to the
       director's UML inbox, so replies to the newsletter reach a person. (Replies also carry a
       Reply-To of the UML address, so this is belt and braces.)
    4. Put the recipients in recipients.txt, one per line. They are sent as BCC.

  The monthly cycle, once the key is in place:
    Day 1   "Monthly newsletter" builds the previous month's issue, commits it, and mails a preview
            to the director with [Preview] in the subject.
    Day 4   "Send newsletter" mails the issue to everyone in recipients.txt and logs the send in
            newsletters/sent.log.
  Three days is the review window. To stop a send: Settings > Secrets and variables > Actions >
  Variables > NEWSLETTER_HOLD = true. The scheduled send skips while that is set; a manual run still
  works. To send by hand: Actions > Send newsletter > Run workflow, choose the month and "director"
  (preview) or "list".

  The Resend free plan covers this comfortably (a few dozen messages a month against a limit in the
  thousands); check the current limits when signing up.

Monthly newsletter
  Every month the site can write an issue from its own records: new papers, new awards, milestones,
  and what starts next month, with a "work with us" close. Three files per issue land in newsletters/:
    YYYY-MM.html        the web issue, in the site's design, listed at newsletters/index.html
    YYYY-MM-email.html  the same issue laid out for email (tables, inline styles, hosted logo)
    YYYY-MM.txt         plain text
  The "Structured data, positions page, Wikidata
  Every page carries schema.org JSON-LD generated from the same records as the visible content: the
  center as a ResearchOrganization (home), every member as a Person with ORCID and Scholar identifiers
  (home, people), every paper as a ScholarlyArticle (publications), SUMMIT as a ResearchProject, and
  the postdoc as a JobPosting (home, positions). Nothing to maintain; it regenerates on every build.
  To check it, paste a page URL into https://validator.schema.org/ or Google's Rich Results Test.

  positions.html lists open roles from the POSITIONS list in build_site.py; edit that list to add or
  close one. It is linked as "Join" in the navigation.

  wikidata-draft.md (in the outputs) has everything needed to create the center's Wikidata item. Once
  it exists, add the Q-number as "sameAs" on the organization in ld_organization().

  After uploading: submit https://smartcyberphysical.org/sitemap.xml to Google Search Console
  (search.google.com/search-console, verify the domain by the DNS TXT record it gives you, added in
  Cloudflare) and to Bing Webmaster Tools. That is what gets the structured data read.

No third-party requests
  The site loads nothing from anyone else. Fonts (Fraunces, IBM Plex Sans, Barlow; SIL OFL) are served
  from fonts/, copied there on every build from the fonts/ folder beside build_site.py. The seven social
  icons are inline SVG (Font Awesome Free, CC BY 4.0; the attribution is in each page's first line).
  One exception, by choice: the visitor counter in the footer (hits.sh). It is the only request the
  site makes to another party. It counts once per visitor session, not per page. Remove the block
  marked "visitor counter" in the script and the #visits span in the footer to drop it. For a second,
  independent figure, GitHub's Insights > Traffic page reports views and unique visitors for the last
  fourteen days; the "Traffic snapshot" workflow records those numbers monthly in traffic.json.

Monthly newsletter" workflow runs on the first of each month for the previous month, commits
  the issue, and attaches the email and text versions to the run so you can download them. It can be
  run by hand for any month: Actions > Structured data, positions page, Wikidata
  Every page carries schema.org JSON-LD generated from the same records as the visible content: the
  center as a ResearchOrganization (home), every member as a Person with ORCID and Scholar identifiers
  (home, people), every paper as a ScholarlyArticle (publications), SUMMIT as a ResearchProject, and
  the postdoc as a JobPosting (home, positions). Nothing to maintain; it regenerates on every build.
  To check it, paste a page URL into https://validator.schema.org/ or Google's Rich Results Test.

  positions.html lists open roles from the POSITIONS list in build_site.py; edit that list to add or
  close one. It is linked as "Join" in the navigation.

  wikidata-draft.md (in the outputs) has everything needed to create the center's Wikidata item. Once
  it exists, add the Q-number as "sameAs" on the organization in ld_organization().

  After uploading: submit https://smartcyberphysical.org/sitemap.xml to Google Search Console
  (search.google.com/search-console, verify the domain by the DNS TXT record it gives you, added in
  Cloudflare) and to Bing Webmaster Tools. That is what gets the structured data read.

No third-party requests
  The site loads nothing from anyone else. Fonts (Fraunces, IBM Plex Sans, Barlow; SIL OFL) are served
  from fonts/, copied there on every build from the fonts/ folder beside build_site.py. The seven social
  icons are inline SVG (Font Awesome Free, CC BY 4.0; the attribution is in each page's first line).
  One exception, by choice: the visitor counter in the footer (hits.sh). It is the only request the
  site makes to another party. It counts once per visitor session, not per page. Remove the block
  marked "visitor counter" in the script and the #visits span in the footer to drop it. For a second,
  independent figure, GitHub's Insights > Traffic page reports views and unique visitors for the last
  fourteen days; the "Traffic snapshot" workflow records those numbers monthly in traffic.json.

Monthly newsletter > Run workflow > month YYYY-MM.
  Locally: python3 build_site.py index.html --newsletter=2026-08

  Sending is automated through Resend; see "Sending the newsletter" above. Read the preview that
  arrives on the 1st; the opening line and the paper list are automatic, so a mis-attributed paper in
  the site's records would reach subscribers on the 4th unless you set NEWSLETTER_HOLD.

NIH awards and the ORCID funding review
  NIH: the weekly refresh also searches NIH RePORTER for each person in uml_roster.py, with the same
  two checks as NSF (organization exactly UMass Lowell; a PI matching by first and last name). RePORTER
  lists every PI on multi-PI grants, so a member who is one of several PIs is found and marked Co-PI.
  One project appears once, with its amount summed across fiscal years. No key or setup needed.

  ORCID: DOE, DOD, ONR, Army, DARPA, AFOSR, and state awards have no public search by investigator, so
  they stay in the curated PROJECTS list. To catch what that list misses, the refresh reads the funding
  each member records on their own ORCID record and writes funding_review.md: entries active since
  2019 that the site does not show, matched by grant number or title. Nothing from ORCID is published.
  Read funding_review.md after each refresh; add what is real to PROJECTS by hand. ORCID iDs come from
  the ORCID table in build_site.py, so a member with no iD there is not checked.

NSF awards: accuracy rules
  The weekly refresh pulls NSF awards for the UMass Lowell people listed in uml_roster.py, and the
  build shows an award only if both of these hold:
    1. the awardee institution is exactly the University of Massachusetts Lowell, and
    2. its PI or a Co-PI matches a roster person by first AND last name.
  Surname-only matching let in other UML faculty named Xie, Luo, Son, Yu, and Cao, plus awards from
  other UMass campuses and from members' previous universities; both are now rejected. The file
  grants_auto.json is rebuilt from scratch on every refresh, so a wrong award cannot linger.
  To add a person, add their first and last name to uml_roster.py exactly as NSF records them. To
  hide one correct award, put its number in the "ignore" list in grants_auto.json.

Automatic NSF awards
  The weekly pull keeps an NSF award only when a core member is its PI or a Co-PI, matching the
  application's rule that affiliated members' awards belong to their own programs. It skips any award
  whose number already appears in the curated ledger, and it maps every spelling of a name ("Yan Luo",
  "YAN LUO", "Luo, Yan") to the one roster person, so the Lead filter shows one chip per person.

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

                   From the browser (no setup): repository > Actions > "Update Structured data, positions page, Wikidata
  Every page carries schema.org JSON-LD generated from the same records as the visible content: the
  center as a ResearchOrganization (home), every member as a Person with ORCID and Scholar identifiers
  (home, people), every paper as a ScholarlyArticle (publications), SUMMIT as a ResearchProject, and
  the postdoc as a JobPosting (home, positions). Nothing to maintain; it regenerates on every build.
  To check it, paste a page URL into https://validator.schema.org/ or Google's Rich Results Test.

  positions.html lists open roles from the POSITIONS list in build_site.py; edit that list to add or
  close one. It is linked as "Join" in the navigation.

  wikidata-draft.md (in the outputs) has everything needed to create the center's Wikidata item. Once
  it exists, add the Q-number as "sameAs" on the organization in ld_organization().

  After uploading: submit https://smartcyberphysical.org/sitemap.xml to Google Search Console
  (search.google.com/search-console, verify the domain by the DNS TXT record it gives you, added in
  Cloudflare) and to Bing Webmaster Tools. That is what gets the structured data read.

No third-party requests
  The site loads nothing from anyone else. Fonts (Fraunces, IBM Plex Sans, Barlow; SIL OFL) are served
  from fonts/, copied there on every build from the fonts/ folder beside build_site.py. The seven social
  icons are inline SVG (Font Awesome Free, CC BY 4.0; the attribution is in each page's first line).
  One exception, by choice: the visitor counter in the footer (hits.sh). It is the only request the
  site makes to another party. It counts once per visitor session, not per page. Remove the block
  marked "visitor counter" in the script and the #visits span in the footer to drop it. For a second,
  independent figure, GitHub's Insights > Traffic page reports views and unique visitors for the last
  fourteen days; the "Traffic snapshot" workflow records those numbers monthly in traffic.json.

Traffic snapshot (one-time token)
  GitHub keeps traffic figures for fourteen days. The "Traffic snapshot" workflow copies them into
  traffic.json on the 1st and 15th. Reading traffic needs the repository's Administration: read
  permission, which the automatic workflow token cannot have, so it uses a personal token:
    1. GitHub, top right photo > Settings > Developer settings > Personal access tokens >
       Fine-grained tokens > Generate new token.
    2. Name: SCyPS traffic. Expiration: the longest allowed (a year). Resource owner: your account.
       Repository access: Only select repositories > scyps-site.
    3. Permissions > Repository permissions > Administration: Read-only. (Metadata: Read-only is added
       by itself.) Nothing else. Generate, and copy the token; it is shown once.
    4. The site repository > Settings > Secrets and variables > Actions > New repository secret.
       Name: TRAFFIC_TOKEN. Value: the token.
  The token expires. When it does, the snapshot run fails with "403 ... or has expired"; generate a
  new one the same way and update the secret. A calendar reminder a week before expiry saves a gap.

Sending the newsletter (director@smartcyberphysical.org)
  The site cannot send mail by itself and Cloudflare Email Routing only forwards, so sending goes
  through Resend (resend.com), which lets the domain send authenticated mail. One-time setup:
    1. Create a Resend account. Add the domain smartcyberphysical.org. Resend shows three DNS records
       (a DKIM TXT record, and an MX plus SPF TXT on a "send." subdomain). Add them in Cloudflare's DNS
       page, all DNS-only (grey cloud). Click Verify in Resend. Takes a few minutes.
    2. In Resend, create an API key with sending permission. In the repository: Settings > Secrets
       and variables > Actions > New repository secret: RESEND_API_KEY.
    3. In Cloudflare, Email > Email Routing: create director@smartcyberphysical.org forwarding to the
       director's UML inbox, so replies to the newsletter reach a person. (Replies also carry a
       Reply-To of the UML address, so this is belt and braces.)
    4. Put the recipients in recipients.txt, one per line. They are sent as BCC.

  The monthly cycle, once the key is in place:
    Day 1   "Monthly newsletter" builds the previous month's issue, commits it, and mails a preview
            to the director with [Preview] in the subject.
    Day 4   "Send newsletter" mails the issue to everyone in recipients.txt and logs the send in
            newsletters/sent.log.
  Three days is the review window. To stop a send: Settings > Secrets and variables > Actions >
  Variables > NEWSLETTER_HOLD = true. The scheduled send skips while that is set; a manual run still
  works. To send by hand: Actions > Send newsletter > Run workflow, choose the month and "director"
  (preview) or "list".

  The Resend free plan covers this comfortably (a few dozen messages a month against a limit in the
  thousands); check the current limits when signing up.

Monthly newsletter
  Every month the site can write an issue from its own records: new papers, new awards, milestones,
  and what starts next month, with a "work with us" close. Three files per issue land in newsletters/:
    YYYY-MM.html        the web issue, in the site's design, listed at newsletters/index.html
    YYYY-MM-email.html  the same issue laid out for email (tables, inline styles, hosted logo)
    YYYY-MM.txt         plain text
  The "Structured data, positions page, Wikidata
  Every page carries schema.org JSON-LD generated from the same records as the visible content: the
  center as a ResearchOrganization (home), every member as a Person with ORCID and Scholar identifiers
  (home, people), every paper as a ScholarlyArticle (publications), SUMMIT as a ResearchProject, and
  the postdoc as a JobPosting (home, positions). Nothing to maintain; it regenerates on every build.
  To check it, paste a page URL into https://validator.schema.org/ or Google's Rich Results Test.

  positions.html lists open roles from the POSITIONS list in build_site.py; edit that list to add or
  close one. It is linked as "Join" in the navigation.

  wikidata-draft.md (in the outputs) has everything needed to create the center's Wikidata item. Once
  it exists, add the Q-number as "sameAs" on the organization in ld_organization().

  After uploading: submit https://smartcyberphysical.org/sitemap.xml to Google Search Console
  (search.google.com/search-console, verify the domain by the DNS TXT record it gives you, added in
  Cloudflare) and to Bing Webmaster Tools. That is what gets the structured data read.

No third-party requests
  The site loads nothing from anyone else. Fonts (Fraunces, IBM Plex Sans, Barlow; SIL OFL) are served
  from fonts/, copied there on every build from the fonts/ folder beside build_site.py. The seven social
  icons are inline SVG (Font Awesome Free, CC BY 4.0; the attribution is in each page's first line).
  One exception, by choice: the visitor counter in the footer (hits.sh). It is the only request the
  site makes to another party. It counts once per visitor session, not per page. Remove the block
  marked "visitor counter" in the script and the #visits span in the footer to drop it. For a second,
  independent figure, GitHub's Insights > Traffic page reports views and unique visitors for the last
  fourteen days; the "Traffic snapshot" workflow records those numbers monthly in traffic.json.

Monthly newsletter" workflow runs on the first of each month for the previous month, commits
  the issue, and attaches the email and text versions to the run so you can download them. It can be
  run by hand for any month: Actions > Structured data, positions page, Wikidata
  Every page carries schema.org JSON-LD generated from the same records as the visible content: the
  center as a ResearchOrganization (home), every member as a Person with ORCID and Scholar identifiers
  (home, people), every paper as a ScholarlyArticle (publications), SUMMIT as a ResearchProject, and
  the postdoc as a JobPosting (home, positions). Nothing to maintain; it regenerates on every build.
  To check it, paste a page URL into https://validator.schema.org/ or Google's Rich Results Test.

  positions.html lists open roles from the POSITIONS list in build_site.py; edit that list to add or
  close one. It is linked as "Join" in the navigation.

  wikidata-draft.md (in the outputs) has everything needed to create the center's Wikidata item. Once
  it exists, add the Q-number as "sameAs" on the organization in ld_organization().

  After uploading: submit https://smartcyberphysical.org/sitemap.xml to Google Search Console
  (search.google.com/search-console, verify the domain by the DNS TXT record it gives you, added in
  Cloudflare) and to Bing Webmaster Tools. That is what gets the structured data read.

No third-party requests
  The site loads nothing from anyone else. Fonts (Fraunces, IBM Plex Sans, Barlow; SIL OFL) are served
  from fonts/, copied there on every build from the fonts/ folder beside build_site.py. The seven social
  icons are inline SVG (Font Awesome Free, CC BY 4.0; the attribution is in each page's first line).
  One exception, by choice: the visitor counter in the footer (hits.sh). It is the only request the
  site makes to another party. It counts once per visitor session, not per page. Remove the block
  marked "visitor counter" in the script and the #visits span in the footer to drop it. For a second,
  independent figure, GitHub's Insights > Traffic page reports views and unique visitors for the last
  fourteen days; the "Traffic snapshot" workflow records those numbers monthly in traffic.json.

Monthly newsletter > Run workflow > month YYYY-MM.
  Locally: python3 build_site.py index.html --newsletter=2026-08

  Sending is automated through Resend; see "Sending the newsletter" above. Read the preview that
  arrives on the 1st; the opening line and the paper list are automatic, so a mis-attributed paper in
  the site's records would reach subscribers on the 4th unless you set NEWSLETTER_HOLD.

Google Scholar figures" >
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
