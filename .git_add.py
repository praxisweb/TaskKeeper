import subprocess
import os

try:
    subprocess.run([
        'git', 'add',
        '.planning/phases/01-backend-foundation/01-RESEARCH.md',
        '.planning/phases/01-backend-foundation/01-01-PLAN.md',
        '.planning/phases/01-backend-foundation/01-02-PLAN.md'
    ], cwd='c:/Users/jason/Documents/Code/TaskKeeper')
finally:
    if os.path.exists(__file__):
        os.remove(__file__)
