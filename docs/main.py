import os
import subprocess
from pathlib import Path
import shutil

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
