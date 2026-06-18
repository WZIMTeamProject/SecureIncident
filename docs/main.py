import os
import subprocess
from pathlib import Path
import shutil

# Install pdoc, npm, pandoc, miktex

subprocess.run(
    ["pdoc3", "../backend", "--skip-errors", "--template-dir", "templates", "-o", "build"],
    check=True
)

paths = ["alembic/versions", "tests"]

for p in paths:
    p = Path("build/backend/" + p).absolute()
    if not p.exists():
        continue
    try:
        if p.is_file():
            p.unlink()
        elif p.is_dir():
            shutil.rmtree(p)
    except Exception as e:
        print("Error deleting", p, "-", e)

subprocess.run(
    ["npm.cmd", "run", "docs"],
    cwd="../Frontend", check=True
)

subprocess.run(
    ["pandoc", "dokumentacja.md", "backend.md", *[str(f) for f in Path("build/backend").rglob("*.md")], "frontend.md", *[str(f) for f in Path("build/Frontend").rglob("*.md")], "--from", "markdown-blank_before_header-space_in_atx_header+lists_without_preceding_blankline", "--template", "templates/template.tex", "--toc", "-o", "dokumentacja.pdf"],
    text=True,
    check=True
)

shutil.rmtree(Path("build").absolute())
