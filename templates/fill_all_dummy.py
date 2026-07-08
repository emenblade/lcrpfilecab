import json, glob, os, re

os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.makedirs("_preview", exist_ok=True)

DUMMY = {
    "string": "Sample Value {n}",
    "text": "This is a longer sample paragraph of filled-in text used to sanity check wrapping and overflow behavior within the field {n}.",
    "date": "07/07/2026",
    "signature": "Jordan T. Vale",
    "choice": "Sample Choice",
}

for json_path in sorted(glob.glob("*.json")):
    if json_path == "index.json":
        continue
    with open(json_path) as f:
        manifest = json.load(f)
    html_path = manifest["html_file"]
    with open(html_path) as f:
        html = f.read()

    for i, field in enumerate(manifest["fields"]):
        token = "{{" + field["key"] + "}}"
        value = DUMMY.get(field["type"], "Sample").replace("{n}", str(i))
        if field["type"] == "choice" and field.get("options"):
            value = field["options"][0]
        html = html.replace(token, value)

    # letterhead/css paths are relative to poc/, preview dir is poc/_preview/ so add ../
    html = html.replace('src="letterhead.png"', 'src="../letterhead.png"')
    html = html.replace('href="template-base.css"', 'href="../template-base.css"')

    out_path = os.path.join("_preview", html_path)
    with open(out_path, "w") as f:
        f.write(html)
    print("wrote", out_path)
