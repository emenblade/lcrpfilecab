"""
Renders a blank (no sample data) preview screenshot of every template, for
the bot to show alongside its intake questions. Requires a local HTTP
server serving the repo root (so /assets/... resolves) and headless Chromium.
"""
import json, os, re, subprocess, glob
from PIL import Image

REPO = "/workspace/lcrpfilecab"
CHROME = "/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell"
PORT = 8799
BG = (238, 238, 238)  # matches body { background: #eee } in template-base.css
WIDTH = 820
TALL_HEIGHT = 4500
PADDING = 40

os.makedirs(f"{REPO}/templates/previews", exist_ok=True)
os.makedirs("/tmp/blank_render", exist_ok=True)

server = subprocess.Popen(
    ["python3", "-m", "http.server", str(PORT)],
    cwd=REPO, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
)
import time; time.sleep(1)

try:
    for json_path in sorted(glob.glob(f"{REPO}/templates/*.json")):
        if json_path.endswith("index.json"):
            continue
        with open(json_path) as f:
            manifest = json.load(f)
        tid = manifest["template_id"]
        html_path = f"{REPO}/templates/{manifest['html_file']}"
        with open(html_path) as f:
            html = f.read()

        blank_html = re.sub(r"\{\{[a-zA-Z0-9_]+\}\}", "", html)
        tmp_path = f"{REPO}/templates/_blank_{tid}.html"
        with open(tmp_path, "w") as f:
            f.write(blank_html)

        raw_png = f"/tmp/blank_render/{tid}_raw.png"
        subprocess.run(
            [CHROME, "--headless", "--disable-gpu", "--no-sandbox", "--hide-scrollbars",
             f"--window-size={WIDTH},{TALL_HEIGHT}", f"--screenshot={raw_png}",
             f"http://localhost:{PORT}/templates/_blank_{tid}.html"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True,
        )
        os.remove(tmp_path)

        im = Image.open(raw_png).convert("RGB")
        w, h = im.size
        pixels = im.load()

        def row_is_background(y):
            for x in (0, w // 4, w // 2, 3 * w // 4, w - 1):
                if pixels[x, y] != BG:
                    return False
            return True

        last_content_row = 0
        for y in range(h - 1, -1, -1):
            if not row_is_background(y):
                last_content_row = y
                break

        crop_h = min(h, last_content_row + PADDING)
        cropped = im.crop((0, 0, w, crop_h))
        out_path = f"{REPO}/templates/previews/{tid}.png"
        cropped.save(out_path)
        print(f"{tid}: {w}x{crop_h} -> {out_path}")
finally:
    server.terminate()
    server.wait()
