#!/usr/bin/env python3
"""Fix canonical and og:url tags in all HTML files in the repo root."""

import os
import re
import urllib.parse

REPO_ROOT = "/Users/ameliakrupnik/Documents/GitHub/marketingautomationbuyersguide"
BASE_URL = "https://marketingautomationbuyersguide.com"

# Only process .html files directly in the repo root (not subdirectories)
html_files = [
    f for f in os.listdir(REPO_ROOT)
    if f.endswith(".html") and os.path.isfile(os.path.join(REPO_ROOT, f))
]
html_files.sort()

modified_files = []
skipped_files = []

for filename in html_files:
    filepath = os.path.join(REPO_ROOT, filename)

    # Determine canonical URL
    if filename == "index.html":
        canonical_url = BASE_URL + "/"
    else:
        encoded_name = urllib.parse.quote(filename)
        canonical_url = BASE_URL + "/" + encoded_name

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    original_content = content

    has_canonical = bool(re.search(r'rel=["\']canonical["\']', content, re.IGNORECASE))
    has_ogurl = bool(re.search(r'property=["\']og:url["\']', content, re.IGNORECASE))

    tags_to_insert = []

    if not has_canonical:
        tags_to_insert.append(f'<link rel="canonical" href="{canonical_url}">')
        tags_to_insert.append(f'<meta property="og:url" content="{canonical_url}">')

    if has_ogurl:
        # Update existing og:url to the correct non-www URL
        new_content = re.sub(
            r'(<meta\s+property=["\']og:url["\']\s+content=["\'])[^"\']*(["\'])',
            lambda m: m.group(1) + canonical_url + m.group(2),
            content,
            flags=re.IGNORECASE
        )
        if new_content != content:
            content = new_content
    elif has_canonical and not has_ogurl:
        # Canonical already present but no og:url — add og:url before </head>
        tags_to_insert.append(f'<meta property="og:url" content="{canonical_url}">')

    if tags_to_insert:
        insert_block = "\n".join(tags_to_insert)
        # Insert before </head>
        if "</head>" in content:
            content = content.replace("</head>", insert_block + "\n</head>", 1)
        else:
            print(f"  WARNING: No </head> found in {filename}, skipping insertion.")

    if content != original_content:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        modified_files.append(filename)
        print(f"  MODIFIED: {filename}")
    else:
        skipped_files.append((filename, "no changes needed"))
        print(f"  SKIPPED:  {filename} (no changes needed)")

print(f"\n=== SUMMARY ===")
print(f"Total HTML files processed: {len(html_files)}")
print(f"Modified: {len(modified_files)}")
print(f"Skipped (no changes needed): {len(skipped_files)}")

# Fix 3: Dash check
print(f"\n=== DASH CHECK ===")
em_dash = "\u2014"
en_dash = "\u2013"
dash_issues = []

for filename in modified_files:
    filepath = os.path.join(REPO_ROOT, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    if em_dash in content or en_dash in content:
        dash_issues.append(filename)

if dash_issues:
    print(f"WARNING: Dash characters found in {len(dash_issues)} modified file(s):")
    for f in dash_issues:
        print(f"  - {f}")
else:
    print("OK: No em dashes or en dashes found in any modified files.")

# Also check robots.txt
robots_path = os.path.join(REPO_ROOT, "robots.txt")
with open(robots_path, "r", encoding="utf-8") as f:
    robots_content = f.read()
if em_dash in robots_content or en_dash in robots_content:
    print("WARNING: Dash characters found in robots.txt")
else:
    print("OK: robots.txt is clean.")
