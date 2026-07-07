"""
Example of the contract the Discord cog should follow when it publishes a
signed filing: fill the template's {{tokens}}, write the result under
filings/<template_id>/<filing_id>.html, and write a sidecar
filings/<template_id>/<filing_id>.json with the metadata the site's search
index needs. This script is a worked example, not something the site itself
runs.
"""
import json, os

REPO = "/workspace/lcrpfilecab"
TEMPLATE_ID = "name_change"
FILING_ID = "name_change-2026-0001"

with open(f"{REPO}/templates/{TEMPLATE_ID}.json") as f:
    manifest = json.load(f)

with open(f"{REPO}/templates/{manifest['html_file']}") as f:
    html = f.read()

answers = {
    "current_name": "Marcus Webb",
    "date_filed": "2026-07-07",
    "discordia_email": "marcus.webb@discordia.gg",
    "ssn": "445-19-2201",
    "legal_representative": "None",
    "requested_name": "Marcus Sterling",
    "reason_for_change": "Witness relocation following testimony in State v. Alvarez. No open warrants.",
    "approving_judge_name": "Cassius Hale",
    "approval_date": "2026-07-08",
}

for field in manifest["fields"]:
    token = "{{" + field["key"] + "}}"
    html = html.replace(token, answers.get(field["key"], ""))

# filings/<template_id>/<filing_id>.html sits one level deeper than
# templates/<template_id>.html, but assets are referenced root-relative
# (/assets/...) so no path rewriting is needed here.

out_dir = f"{REPO}/filings/{TEMPLATE_ID}"
os.makedirs(out_dir, exist_ok=True)
with open(f"{out_dir}/{FILING_ID}.html", "w") as f:
    f.write(html)

sidecar = {
    "filing_id": FILING_ID,
    "template_id": TEMPLATE_ID,
    "title": manifest["title"],
    "category": manifest["category"],
    "html_file": f"{TEMPLATE_ID}/{FILING_ID}.html",
    "filed_date": answers["date_filed"],
    "signed_date": answers["approval_date"],
    "signed_by": answers["approving_judge_name"],
    "index_values": {k: answers[k] for k in manifest["index_fields"]},
}
with open(f"{out_dir}/{FILING_ID}.json", "w") as f:
    json.dump(sidecar, f, indent=2, ensure_ascii=False)
    f.write("\n")

print(f"Wrote {out_dir}/{FILING_ID}.html and .json")
