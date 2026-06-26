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

def parse_env_file():
    env = {}
    with open("../.env.example", "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            k = k.strip()
            v = v.strip()
            if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
                v = v[1:-1]
            env[k] = v
    return env

env = os.environ.copy()
env_from_file = parse_env_file()
env.update({k: v for k, v in env_from_file.items() if v is not None})

res = subprocess.run(
    ["pytest", "-v", "--no-header", "--no-summary", "-s", "--disable-warnings"],
    env=env, cwd="../backend", stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, check=False
)
with open("../docs/build/tests.md", "w", encoding="utf-8") as f:
    f.write(res.stdout)
try:
    res.check_returncode()
except:
    print("Error with tests")

with open("build/tests.md", "r") as f:
    lines = f.readlines()
with open("build/tests.md", "w") as f:
    f.writelines([line + "\n" for line in lines[3:-3]])

res = subprocess.run(
    ["npm.cmd", "test"],
    env=env, cwd="../Frontend", stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, check=False
)
with open("../docs/build/tests.md", "a", encoding="utf-8") as f:
    f.write(res.stdout)
try:
    res.check_returncode()
except:
    print("Error with tests")

subprocess.run(
    ["npm.cmd", "run", "docs"],
    cwd="../Frontend", check=True
)

subprocess.run(
    ["pandoc", "documentation.md", 
     "guides/README.md", *[str(f) for f in Path("guides").rglob("*.md") if f != "README.md"],
     "qa.md", "bandit.txt", "pip-audit.txt", "vulture.txt",
     "backend.md", *[str(f) for f in Path("build/backend").rglob("*.md")], 
     "tests.md", "build/tests.md", 
     "frontend.md", *[str(f) for f in Path("build/Frontend").rglob("*.md")], 
     "--from", "markdown-blank_before_header-space_in_atx_header+lists_without_preceding_blankline", 
     "--template", "templates/template.tex", 
     "-V", f"author={open("authors", "r").read()}",
     "--toc", 
     "-o", "dokumentacja.pdf"],
    check=True
)

shutil.rmtree(Path("build").absolute())
