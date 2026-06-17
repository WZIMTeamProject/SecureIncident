import os
import subprocess

root = '../backend'
exclude = 'tests'
py_files = []
for dirpath, dirnames, filenames in os.walk(root):
    if exclude in dirpath.split(os.sep):
        continue
    for f in filenames:
        if f.endswith('.py'):
            py_files.append(os.path.join(dirpath, f))

for py in py_files[0]:
    subprocess.Popen(f"pdoc3 {py} --template-dir templates -o build", shell=True)