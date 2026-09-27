"""Find overlapping text on every page of the site, at desktop and phone widths.
Checks SVG <text> elements against each other, and visible HTML text boxes against each other
(leaf elements with their own text), reporting pairs whose boxes overlap by more than a few pixels."""
import asyncio, glob, os, sys, json
from playwright.async_api import async_playwright
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
pages = sorted(glob.glob(ROOT + "/*.html")) + sorted(glob.glob(ROOT + "/acnl/**/*.html", recursive=True)) + sorted(glob.glob(ROOT + "/newsletters/*.html"))
pages = [p for p in pages if not p.endswith("newsletters/index.html")]
JS = """() => {
  const out = [];
  const vis = el => { const s = getComputedStyle(el); if (s.visibility === 'hidden' || s.display === 'none' || +s.opacity === 0) return false;
      const bb = el.getBoundingClientRect(); if (bb.width <= 2 || bb.height <= 2) return false;
      if ((s.clip && s.clip.startsWith('rect(0')) || (s.clipPath && s.clipPath.startsWith('inset(50'))) return false;
      let p = el; while (p && p !== document.body) { const ps = getComputedStyle(p); if (ps.display === 'none' || +ps.opacity < 0.2 || p.hidden) return false; p = p.parentElement; } return true; };
  // SVG text
  for (const svg of document.querySelectorAll('svg')) {
    const ts = [...svg.querySelectorAll('text')].filter(t => t.textContent.trim() && vis(t));
    const bs = ts.map(t => t.getBoundingClientRect());
    for (let i = 0; i < ts.length; i++) for (let j = i + 1; j < ts.length; j++) {
      const a = bs[i], b = bs[j];
      const ox = Math.min(a.right, b.right) - Math.max(a.left, b.left), oy = Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top);
      if (ox > 3 && oy > 3) out.push(['svg', ts[i].textContent.trim().slice(0, 30), ts[j].textContent.trim().slice(0, 30), Math.round(ox), Math.round(oy)]);
    }
  }
  // HTML leaf text
  const els = [...document.body.querySelectorAll('*')].filter(e => !(e.closest('svg')) && [...e.childNodes].some(n => n.nodeType === 3 && n.textContent.trim().length > 1) && vis(e));
  // clip each text box to the scrolling or clipping containers it sits in, so text scrolled out of view does not count
  const clipOf = e => { let c = {left: -1e9, top: -1e9, right: 1e9, bottom: 1e9}; let p = e.parentElement;
      while (p && p !== document.body) { const s = getComputedStyle(p);
        if (s.overflowX !== 'visible' || s.overflowY !== 'visible') { const r = p.getBoundingClientRect();
          c = {left: Math.max(c.left, r.left), top: Math.max(c.top, r.top), right: Math.min(c.right, r.right), bottom: Math.min(c.bottom, r.bottom)}; }
        p = p.parentElement; } return c; };
  const rs = els.map(e => { const r = document.createRange(); r.selectNodeContents(e); const c = clipOf(e);
      return [...r.getClientRects()].map(a => ({left: Math.max(a.left, c.left), top: Math.max(a.top, c.top), right: Math.min(a.right, c.right), bottom: Math.min(a.bottom, c.bottom)})).filter(a => a.right - a.left > 1 && a.bottom - a.top > 1); });
  for (let i = 0; i < els.length; i++) for (let j = i + 1; j < els.length; j++) {
    if (els[i].contains(els[j]) || els[j].contains(els[i])) continue;
    let hit = null;
    for (const a of rs[i]) { for (const b of rs[j]) {
      const ox = Math.min(a.right, b.right) - Math.max(a.left, b.left), oy = Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top);
      if (ox > 4 && oy > 4) { hit = [Math.round(ox), Math.round(oy)]; break; } } if (hit) break; }
    if (hit) out.push(['html', els[i].textContent.trim().slice(0, 30), els[j].textContent.trim().slice(0, 30), hit[0], hit[1]]);
  }
  return out;
}"""
async def main():
    found = {}
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for w, h in ((1280, 900), (390, 844)):
            pg = await b.new_page(viewport={"width": w, "height": h})
            for f in pages:
                await pg.goto("file://" + f); await pg.wait_for_timeout(250)
                r = await pg.evaluate(JS)
                if r: found[f"{os.path.relpath(f, ROOT)} @{w}"] = r
            await pg.close()
        await b.close()
    import collections
    sig = collections.defaultdict(set)
    for k, v in found.items():
        for x in v: sig[(x[0], x[1][:22], x[2][:22])].add(k)
    for (kind, a, b), where in sorted(sig.items(), key=lambda t: -len(t[1])):
        print(f"{len(where):3} pages | {kind} | {a!r} x {b!r} | e.g. {sorted(where)[0]}")
    json.dump({k: v for k, v in found.items()}, open('/tmp/overlaps.json', 'w'), indent=0)
    print(f"pages checked: {len(pages)} x 2 widths; pages with overlaps: {len(found)}")
asyncio.run(main())
