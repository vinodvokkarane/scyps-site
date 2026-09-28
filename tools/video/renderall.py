"""Render every video's frames at 24 fps, resumably, within a time budget; then encode the finished ones."""
import asyncio, json, os, sys, time, subprocess
FPS = 24; BUDGET = float(sys.argv[1]) if len(sys.argv) > 1 else 240; T0 = time.time()
V = json.load(open('/home/claude/video/videos/index.json'))
def todo():
    out = []
    for v in V:
        d = f"/home/claude/video/frames/{v['name']}"; os.makedirs(d, exist_ok=True)
        have = set(os.listdir(d)); n = int(round(v['duration'] * FPS))
        miss = [i for i in range(n) if f"f{i:05d}.jpg" not in have]
        if miss: out.append((v, miss))
    return out
async def worker(b, q):
    while q and time.time() - T0 < BUDGET:
        v, idxs = q.pop(0)
        W, H = (1280, 720) if v['fmt'] == 'h' else (720, 1280)
        pg = await b.new_page(viewport={"width": W, "height": H})
        await pg.goto(f"file:///home/claude/video/videos/{v['name']}.html"); await pg.wait_for_timeout(700)
        for i in idxs:
            if time.time() - T0 > BUDGET: break
            await pg.evaluate(f"render({i / FPS})")
            await pg.screenshot(path=f"/home/claude/video/frames/{v['name']}/f{i:05d}.jpg", type="jpeg", quality=92)
        await pg.close()
async def main():
    jobs = []
    for v, miss in todo():
        k = 3 if len(miss) > 400 else 1
        jobs += [(v, miss[j::k]) for j in range(k)]
    async with async_playwright() as p:
        b = await p.chromium.launch()
        await asyncio.gather(*[worker(b, jobs) for _ in range(7)])
        await b.close()
from playwright.async_api import async_playwright
asyncio.run(main())
left = todo(); done = [v for v in V if v["name"] not in {x[0]["name"] for x in left}] if len(sys.argv) < 3 else []
os.makedirs('/home/claude/video/out', exist_ok=True)
for v in done:
    mp4 = f"/home/claude/video/out/{v['name']}.mp4"
    if not os.path.exists(mp4):
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(FPS), '-i', f"/home/claude/video/frames/{v['name']}/f%05d.jpg",
                        '-c:v', 'libx264', '-preset', 'medium', '-crf', '23', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', '-tune', 'animation', mp4], check=True)
print('finished:', len(done), 'of', len(V), '| still rendering:', [(x[0]['name'], len(x[1])) for x in left][:6], '| elapsed', round(time.time() - T0))
