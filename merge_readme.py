import os
import re
from collections import OrderedDict

# Paths to README files
BASE_README = "README.md"
DOCS_README = os.path.join("docs", "README.md")
FYP_README = os.path.join("final-year-project", "README.md")
OUTPUT_README = "README_merged.md"

# Helper: Read file if exists
def read_file(path):
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return f.read()
    else:
        print(f"[WARNING] {path} not found. Skipping.")
        return ""

# Helper: Split markdown into sections by headings
SECTION_RE = re.compile(r"^(#{1,6} .*)$", re.MULTILINE)
def split_sections(md):
    sections = OrderedDict()
    matches = list(SECTION_RE.finditer(md))
    if not matches:
        sections["__start__"] = md
        return sections
    for i, m in enumerate(matches):
        start = m.start()
        end = matches[i+1].start() if i+1 < len(matches) else len(md)
        heading = m.group(1).strip()
        content = md[start:end].strip()
        sections[heading] = content
    return sections

# Helper: Merge sections, preferring detailed/longest version
def merge_sections(base, *others):
    merged = OrderedDict(base)
    for other in others:
        for h, content in other.items():
            if h in merged:
                # Prefer the longer/more detailed version
                if len(content) > len(merged[h]):
                    merged[h] = content
            else:
                merged[h] = content
    return merged

# Helper: Remove duplicate paragraphs (simple)
def dedupe_paragraphs(text):
    paras = text.split('\n\n')
    seen = set()
    out = []
    for p in paras:
        p_clean = p.strip()
        if p_clean and p_clean not in seen:
            out.append(p)
            seen.add(p_clean)
    return '\n\n'.join(out)

# Helper: Build Table of Contents
def build_toc(sections):
    toc = ["## Table of Contents\n"]
    for h in sections:
        if h.startswith("#") and h != "__start__":
            level = h.count('#')
            title = h.lstrip('#').strip()
            anchor = re.sub(r'[^a-zA-Z0-9 ]', '', title).replace(' ', '-').lower()
            toc.append(f"{'  '*(level-2)}- [{title}](#{anchor})")
    return '\n'.join(toc) + '\n\n'

# Main merge logic
def main():
    # Read all README files
    base_md = read_file(BASE_README)
    docs_md = read_file(DOCS_README)
    fyp_md = read_file(FYP_README)

    # Split into sections
    base_sections = split_sections(base_md)
    docs_sections = split_sections(docs_md)
    fyp_sections = split_sections(fyp_md)

    # Merge sections
    merged_sections = merge_sections(base_sections, docs_sections, fyp_sections)

    # Build merged content
    merged_content = []
    toc = build_toc(merged_sections)
    merged_content.append(toc)
    for h, content in merged_sections.items():
        if h == "__start__":
            merged_content.append(content.strip())
        else:
            merged_content.append(content.strip())
    # Remove duplicate paragraphs
    final = dedupe_paragraphs('\n\n'.join(merged_content))
    # Normalize multiple blank lines
    final = re.sub(r'\n{3,}', '\n\n', final)
    # Write output
    with open(OUTPUT_README, "w", encoding="utf-8") as f:
        f.write(final)
    print(f"[INFO] Merged README written to {OUTPUT_README}")

if __name__ == "__main__":
    main()

# Usage: python merge_readme.py
# This script merges all README.md files into README_merged.md in the root.
# It skips missing files, deduplicates content, and adds a Table of Contents.
