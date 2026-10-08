"""Run scramble-luck's delivery checks against this episode's draft."""
import importlib.util
from pathlib import Path

EP = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('house_delivery_checks', EP.parent/'scramble-luck/check_narrated.py')
checks = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checks)
checks.EP = EP
if __name__ == '__main__':
    checks.main()
