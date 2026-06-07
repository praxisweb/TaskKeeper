import subprocess
import os

try:
    subprocess.run([
        'git', 'commit', '-m',
        'docs(01-backend-foundation): create phase plan, validation strategy, and research'
    ], cwd='c:/Users/jason/Documents/Code/TaskKeeper')
finally:
    if os.path.exists(__file__):
        os.remove(__file__)
