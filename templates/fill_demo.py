import json

with open("name_change.json") as f:
    manifest = json.load(f)

with open("name_change.html") as f:
    html = f.read()

# Sample answers a Discord bot would have collected/auto-filled.
answers = {
    "current_name": "Marcus Webb",
    "date_filed": "2026-07-07",
    "discordia_email": "marcus.webb@discordia.gg",
    "ssn": "445-19-2201",
    "legal_representative": "None",
    "requested_name": "Marcus Sterling",
    "reason_for_change": "Witness relocation following testimony in State v. Alvarez. No open warrants.",
    "approving_judge_name": "",  # left blank: not collected from applicant, judge signs at approval
    "approval_date": "",         # left blank: filled at approval time
}

submitted_html = html
for field in manifest["fields"]:
    key = field["key"]
    token = "{{" + key + "}}"
    value = answers.get(key, "")
    submitted_html = submitted_html.replace(token, value)

with open("name_change_filled.html", "w") as f:
    f.write(submitted_html)
print("Wrote name_change_filled.html (submitted, awaiting judge approval)")

# Second pass: simulate the bot auto-signing once a judge approves the request.
approved_answers = dict(answers)
approved_answers["approving_judge_name"] = "Cassius Hale"
approved_answers["approval_date"] = "2026-07-08"

approved_html = html
for field in manifest["fields"]:
    key = field["key"]
    token = "{{" + key + "}}"
    value = approved_answers.get(key, "")
    approved_html = approved_html.replace(token, value)

with open("name_change_approved.html", "w") as f:
    f.write(approved_html)
print("Wrote name_change_approved.html (judge signature auto-filled)")
