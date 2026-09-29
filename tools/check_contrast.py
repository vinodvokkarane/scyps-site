"""Find text that is hard to read against its own background, in light and dark mode.

For every visible element that draws its own background (buttons, chips, badges, tags, pills) and holds
text, computes the WCAG contrast ratio between the text color and that background. Reports anything under
4.5 (3.0 for text 18.66 px bold or 24 px and larger). Usage: python3 tools/check_contrast.py [page.html ...]"""
import asyncio, glob, os, sys, collections
from playwright.async_api import async_playwright
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
pages = sys.argv[1:] or (sorted(glob.glob(ROOT + "/*.html")) + sorted(glob.glob(ROOT + "/acnl/**/*.html", recursive=True)))
pages = [p if os.path.isabs(p) else os.path.join(ROOT, p) for p in pages]
JS = r"""() => {
  const rgb = s => { const m = s.match(/rgba?\(([^)]+)\)/); if (!m) return null; const p = m[1].split(',').map(Number); return {r: p[0], g: p[1], b: p[2], a: p.length > 3 ? p[3] : 1}; };
  const lum = c => { const f = v => { v /= 255; return v <= .03928 ? v / 12.92 : Math.pow((v + .055) / 1.055, 2.4); }; return .2126 * f(c.r) + .7152 * f(c.g) + .0722 * f(c.b); };
  const ratio = (a, b) => { const x = lum(a), y = lum(b); return (Math.max(x, y) + .05) / (Math.min(x, y) + .05); };
  const out = [];
  for (const e of document.querySelectorAll('body *')){
    if (e.closest('svg')) continue;
    const s = getComputedStyle(e); const bg = rgb(s.backgroundColor);
    if (!bg || bg.a < .6 || s.backgroundImage !== 'none') continue;
    const txt = [...e.childNodes].filter(n => n.nodeType === 3).map(n => n.textContent.trim()).join(' ').trim();
    if (!txt) continue;
    const r = e.getBoundingClientRect(); if (r.width < 4 || r.height < 4 || s.visibility === 'hidden' || s.display === 'none') continue;
    let p = e, hidden = false; while (p) { const ps = getComputedStyle(p); if (ps.display === 'none' || +ps.opacity === 0) { hidden = true; break; } p = p.parentElement; } if (hidden) continue;
    const fg = rgb(s.color); if (!fg) continue;
    const size = parseFloat(s.fontSize), bold = +s.fontWeight >= 600;
    const need = (size >= 24 || (size >= 18.66 && bold)) ? 3 : 4.5; const cr = ratio(fg, bg);
    if (cr < need) out.push([e.tagName.toLowerCase() + (e.className && typeof e.className === 'string' ? '.' + e.className.trim().split(/\s+/).join('.') : ''), txt.slice(0, 40), cr.toFixed(2)]);
  }
  return out;
}"""
async def main():
    found = collections.defaultdict(set)
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for mode in ("light", "dark"):
            pg = await b.new_page(viewport={"width": 1280, "height": 900}, color_scheme=mode)
            await pg.add_init_script(f"try{{localStorage.setItem('scyps-theme','{mode}')}}catch(e){{}}")
            for f in pages:
                await pg.goto("file://" + f); await pg.wait_for_timeout(200)
                await pg.evaluate(f"document.documentElement.setAttribute('data-theme','{mode}')")
                for sel, txt, cr in await pg.evaluate(JS): found[(mode, sel, txt, cr)].add(os.path.relpath(f, ROOT))
            await pg.close()
        await b.close()
    for (mode, sel, txt, cr), ps in sorted(found.items()):
        print(f"{mode:5} | {cr:>5} | {sel[:40]:40} | {txt!r} | {len(ps)} pages, e.g. {sorted(ps)[0]}")
    print(f"pages checked: {len(pages)} x light and dark; low-contrast items: {len(found)}")
asyncio.run(main())
