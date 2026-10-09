"""House assembler in the same disposable offline Chromium environment."""
import importlib.util
import subprocess
import sys
from pathlib import Path

EP = Path(__file__).resolve().parent
ROOT = EP.parents[2]
spec = importlib.util.spec_from_file_location('episode_stills', EP/'scenes/render_stills.py')
stills = importlib.util.module_from_spec(spec)
spec.loader.exec_module(stills)
if __name__ == '__main__':
    with stills.offline_chrome() as env:
        subprocess.run([sys.executable, str(ROOT/'studio/tools/assemble.py'),str(EP),
                        '--jobs','4','--out-dir',__import__('os').environ.get('FA_RENDER_DIR',str(EP/'renders/draft')),*sys.argv[1:]],env=env,check=True)
