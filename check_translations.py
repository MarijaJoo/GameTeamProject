import importlib.util
from pathlib import Path

base = Path("game/localization")

def load(name):
    spec = importlib.util.spec_from_file_location(name, base / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.TRANSLATIONS

langs = {k: load(k) for k in ["en", "tr", "sq"]}

all_keys = set().union(*[set(v.keys()) for v in langs.values()])

for lang, data in langs.items():
    missing = sorted(all_keys - set(data.keys()))
    extra = sorted(set(data.keys()) - all_keys)
    print(f"\n{lang}: {len(data)} strings")
    print(f"missing: {len(missing)}")
    print(f"extra: {len(extra)}")
    if missing:
        print("first missing:", missing[:20])