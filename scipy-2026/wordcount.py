import argparse
from pathlib import Path
import re

p = argparse.ArgumentParser()
p.add_argument("file", type=Path)
a = p.parse_args()

if a.file.suffix.lower() not in (".md", ".txt"):
    p.error("file must be .md or .txt")

try:
    text = re.sub(r"\s+", " ", a.file.read_text(encoding="utf-8")).strip()
except OSError as e:
    p.error(str(e))

print(len(text.split()))