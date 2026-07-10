import json, re, glob, os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

errors = []
all_json_keys_by_template = {}

for json_path in sorted(glob.glob("*.json")):
    if json_path in ("package.json", "index.json"):
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

    # fields marked html_rendered:false drive another field's value (e.g. a
    # "which party is signing" selector) rather than appearing as their own token
    rendered_keys = set(f["key"] for f in manifest["fields"] if f.get("html_rendered", True))

    missing_in_json = html_tokens - json_keys
    unused_in_html = rendered_keys - html_tokens

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

    # signers roster: every field's filled_by must resolve to a known role,
    # and every non-applicant/judge/auto role must be declared with requires_handoff
    signers = manifest.get("signers")
    if signers is None:
        errors.append(f"[{template_id}] missing top-level 'signers' array")
    else:
        roles = {s["role"] for s in signers}
        for s in signers:
            for req_attr in ("role", "label", "requires_handoff"):
                if req_attr not in s:
                    errors.append(f"[{template_id}] signer entry missing '{req_attr}': {s}")
            name_field = s.get("name_field")
            if name_field and name_field not in json_keys:
                errors.append(f"[{template_id}] signer '{s['role']}' name_field {name_field!r} is not a known field key")

        for field in manifest["fields"]:
            fb = field["filled_by"]
            if fb == "auto":
                continue
            if fb not in roles:
                errors.append(f"[{template_id}] field '{field['key']}' has filled_by={fb!r} with no matching entry in signers[]")

        handoff_roles = {s["role"] for s in signers if s.get("requires_handoff")}
        for role in handoff_roles:
            if not any(f["filled_by"] == role for f in manifest["fields"]):
                errors.append(f"[{template_id}] signer '{role}' has requires_handoff=true but no field uses filled_by={role!r}")

    # Only "applicant" fields are asked during intake, so only they should have
    # a prompt. "auto"/"judge" fields are filled automatically; every handoff
    # role (partner1, witness, counsel, ...) is filled later by the separate
    # document hand-off/signature-routing system, not asked of the filer.
    for field in manifest["fields"]:
        fb = field["filled_by"]
        has_prompt = field.get("prompt") is not None
        if fb == "applicant" and not has_prompt:
            errors.append(f"[{template_id}] field '{field['key']}' is filled_by='applicant' but has no prompt")
        if fb != "applicant" and has_prompt:
            errors.append(f"[{template_id}] field '{field['key']}' has filled_by={fb!r} but has a prompt (should be null -- only 'applicant' fields are asked during intake)")

print(f"Checked {len(all_json_keys_by_template)} templates.")
if errors:
    print(f"\n{len(errors)} issue(s) found:\n")
    for e in errors:
        print(" -", e)
else:
    print("No issues found: every {{token}} has a matching JSON field, every JSON field is used, and all approving_judge_* fields are consistently filled_by \"judge\".")
