"""Find SVG text that sits on a line, an arrow, or the edge of a box.

For every visible <text> in every SVG on the site, samples the outline of every other visible shape in the
same SVG (paths, lines, polylines, polygons, rects, circles, ellipses) every 2 px and reports any shape
whose outline passes through the text's box. Text fully inside a box is fine, because the box's outline
does not cross it. Run at desktop and phone widths: python3 tools/check_text_on_shapes.py [page.html ...]
"""
import asyncio, glob, os, sys, json
from playwright.async_api import async_playwright
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
pages = sys.argv[1:] or (sorted(glob.glob(ROOT + "/*.html")) + sorted(glob.glob(ROOT + "/acnl/**/*.html", recursive=True)))
pages = [p if os.path.isabs(p) else os.path.join(ROOT, p) for p in pages]
JS = r"""(opts) => {
  const out = [];
  const visible = el => { let p = el; while (p && p.tagName !== 'svg') { const s = getComputedStyle(p);
      if (s.display === 'none' || s.visibility === 'hidden' || +s.opacity === 0) return false; p = p.parentElement; } return true; };
  for (const svg of document.querySelectorAll('svg')) {
    if (svg.closest('[data-skip-shapecheck]')) continue;
    const r = svg.getBoundingClientRect(); if (r.width < 60 || r.height < 40) continue;          // icons
    // text drawn with a halo (a wide stroke painted under the letters, as in the collaboration graph) masks any line behind it
    const haloed = t => { const c = getComputedStyle(t); return (c.paintOrder || '').startsWith('stroke') && parseFloat(c.strokeWidth) >= 3 && c.stroke !== 'none'; };
    const texts = [...svg.querySelectorAll('text')].filter(t => t.textContent.trim() && visible(t) && !haloed(t) && !t.closest('defs,marker,clipPath,mask,pattern,symbol'));
    if (!texts.length) continue;
    const boxes = texts.map(t => { const b = t.getBoundingClientRect(); return {t, l: b.left + 1.5, r: b.right - 1.5, tp: b.top + 2, bt: b.bottom - 2}; });
    const shapes = [...svg.querySelectorAll('path,line,polyline,polygon,rect,circle,ellipse')]
      .filter(s => !s.closest('defs,marker,clipPath,mask,pattern,symbol') && visible(s) && s.getTotalLength);
    const fills = shapes.map(s => { const c = getComputedStyle(s); return {s, fill: c.fill, stroke: c.stroke, b: s.getBoundingClientRect()}; });
    for (const s of shapes) {
      const cs = getComputedStyle(s);
      const stroked = cs.stroke && cs.stroke !== 'none' && parseFloat(cs.strokeWidth) > 0 && +cs.strokeOpacity > 0.15;
      const filled = cs.fill && cs.fill !== 'none' && +cs.fillOpacity > 0.15;
      if (!stroked && !filled) continue;
      const sb = s.getBoundingClientRect(); if (sb.width > r.width * 0.97 && sb.height > r.height * 0.97) continue;   // background
      let L; try { L = s.getTotalLength(); } catch (e) { continue; } if (!L) continue;
      const m = s.getScreenCTM(); if (!m) continue;
      const closed = /^(rect|circle|ellipse|polygon)$/.test(s.tagName);
      // text sitting wholly inside a closed box (a label in a pill or a card) is fine
      // a seam between two same-colored pieces of one box (a rounded header plus a square filler) is invisible
      const seam = b => !stroked && fills.some(f => f.s !== s && f.fill === cs.fill && (b.l + b.r) / 2 > f.b.left && (b.l + b.r) / 2 < f.b.right && (b.tp + b.bt) / 2 > f.b.top && (b.tp + b.bt) / 2 < f.b.bottom);
      const cand = boxes.filter(b => !seam(b) && !(sb.right < b.l || sb.left > b.r || sb.bottom < b.tp || sb.top > b.bt) &&
                                     !(closed && b.l >= sb.left - 2 && b.r <= sb.right + 2 && (b.tp + b.bt) / 2 > sb.top && (b.tp + b.bt) / 2 < sb.bottom));
      if (!cand.length) continue;
      const step = Math.max(1.5, L / 4000);
      const hit = new Set();
      for (let d = 0; d <= L; d += step) {
        const p = s.getPointAtLength(d); const x = m.a * p.x + m.c * p.y + m.e, y = m.b * p.x + m.d * p.y + m.f;
        for (const b of cand) if (!hit.has(b) && x > b.l && x < b.r && y > b.tp && y < b.bt) hit.add(b);
      }
      for (const b of hit) out.push([b.t.textContent.trim().slice(0, 40), s.tagName + (s.getAttribute('class') ? '.' + s.getAttribute('class') : ''), (svg.getAttribute('aria-label') || svg.id || svg.getAttribute('viewBox') || '').slice(0, 40)]);
    }
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
                await pg.goto("file://" + f); await pg.wait_for_timeout(300)
                r = await pg.evaluate(JS, {})
                if r: found[f"{os.path.relpath(f, ROOT)} @{w}"] = r
            await pg.close()
        await b.close()
    import collections
    sig = collections.defaultdict(set)
    for k, v in found.items():
        for x in v: sig[(x[0], x[1], x[2])].add(k)
    for (t, s, where), ks in sorted(sig.items(), key=lambda z: (sorted(z[1])[0], z[0][0])):
        print(f"{len(ks):3} | text {t!r} on {s} | svg {where!r} | e.g. {sorted(ks)[0]}")
    print(f"pages checked: {len(pages)} x 2 widths; text-on-shape collisions: {len(sig)}")
asyncio.run(main())
