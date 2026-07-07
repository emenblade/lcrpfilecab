import json, re, glob, os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

errors = []
all_json_keys_by_template = {}

for json_path in sorted(glob.glob("*.json")):
    if json_path == "package.json":
        continue
    with open(json_path) as f:
        manifest = json.load(f)
    template_id = manifest["template_id"]
    html_path = manifest["html_file"]
    if not os.path.exists(html_path):
        errors.append(f"[{template_id}] html_file {html_path} does not exist")
        continue
    with open(html_path) as f:
        html = f.read()

    html_tokens = set(re.findall(r"\{\{(\w+)\}\}", html))
    json_keys = set(f["key"] for f in manifest["fields"])
    all_json_keys_by_template[template_id] = json_keys

    missing_in_json = html_tokens - json_keys
    unused_in_html = json_keys - html_tokens

    if missing_in_json:
        errors.append(f"[{template_id}] tokens in HTML with no JSON field: {sorted(missing_in_json)}")
    if unused_in_html:
        errors.append(f"[{template_id}] JSON fields never used in HTML: {sorted(unused_in_html)}")

    # every field needs filled_by and type
    for field in manifest["fields"]:
        for req_attr in ("key", "type", "filled_by", "required"):
            if req_attr not in field:
                errors.append(f"[{template_id}] field missing '{req_attr}': {field}")

    # judge fields should never be filled_by applicant, and vice versa is fine
    for field in manifest["fields"]:
        if field["key"].startswith("approving_judge") and field["filled_by"] not in ("judge",):
            errors.append(f"[{template_id}] approving_judge* field '{field['key']}' has filled_by={field['filled_by']!r}, expected 'judge'")

print(f"Checked {len(all_json_keys_by_template)} templates.")
if errors:
    print(f"\n{len(errors)} issue(s) found:\n")
    for e in errors:
        print(" -", e)
else:
    print("No issues found: every {{token}} has a matching JSON field, every JSON field is used, and all approving_judge_* fields are consistently filled_by \"judge\".")
