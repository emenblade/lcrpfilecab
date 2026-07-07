"""
Rebuilds the two indexes the site reads at runtime:
  - templates/index.json   list of blank fillable templates (for the cog + site)
  - filings-index.json     list of signed/published filings (for site search)

Run from the repo root. No external dependencies.
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = os.path.join(ROOT, "templates")
FILINGS_DIR = os.path.join(ROOT, "filings")


def build_templates_index():
    entries = []
    for name in sorted(os.listdir(TEMPLATES_DIR)):
        if not name.endswith(".json") or name == "index.json":
            continue
        with open(os.path.join(TEMPLATES_DIR, name)) as f:
            manifest = json.load(f)
        entries.append({
            "template_id": manifest["template_id"],
            "title": manifest["title"],
            "category": manifest.get("category", "Uncategorized"),
            "html_file": manifest["html_file"],
            "json_file": name,
        })
    entries.sort(key=lambda e: (e["category"], e["title"]))
    out_path = os.path.join(TEMPLATES_DIR, "index.json")
    with open(out_path, "w") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"templates/index.json: {len(entries)} template(s)")
    return entries


def build_filings_index():
    entries = []
    if os.path.isdir(FILINGS_DIR):
        for template_id in sorted(os.listdir(FILINGS_DIR)):
            subdir = os.path.join(FILINGS_DIR, template_id)
            if not os.path.isdir(subdir):
                continue
            for name in sorted(os.listdir(subdir)):
                if not name.endswith(".json"):
                    continue
                with open(os.path.join(subdir, name)) as f:
                    filing = json.load(f)

                search_parts = [filing["title"], filing["filing_id"]]
                search_parts.extend(str(v) for v in filing.get("index_values", {}).values())
                if filing.get("signed_by"):
                    search_parts.append(filing["signed_by"])

                entries.append({
                    "filing_id": filing["filing_id"],
                    "template_id": filing["template_id"],
                    "title": filing["title"],
                    "category": filing.get("category", "Uncategorized"),
                    "url": f"filings/{filing['html_file']}",
                    "filed_date": filing.get("filed_date"),
                    "signed_date": filing.get("signed_date"),
                    "signed_by": filing.get("signed_by"),
                    "index_values": filing.get("index_values", {}),
                    "search_text": " ".join(search_parts).lower(),
                })

    # newest first
    entries.sort(key=lambda e: (e.get("signed_date") or e.get("filed_date") or ""), reverse=True)
    out_path = os.path.join(ROOT, "filings-index.json")
    with open(out_path, "w") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"filings-index.json: {len(entries)} filing(s)")
    return entries


if __name__ == "__main__":
    build_templates_index()
    build_filings_index()
