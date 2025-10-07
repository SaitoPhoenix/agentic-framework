from pathlib import Path
import yaml

config_path = Path('test_config.yaml')
with open(config_path) as f:
    config = yaml.safe_load(f)

payloads_base_dir = Path(config['runner']['payloads_base_dir'])
print(f"Payloads base dir: {payloads_base_dir}")
print(f"Exists: {payloads_base_dir.exists()}")
print(f"Absolute: {payloads_base_dir.absolute()}")

for hook_name, hook_config in config['hooks'].items():
    hook_dir = payloads_base_dir / hook_config['payload_dir']
    print(f"\n{hook_name}: {hook_dir}")
    print(f"  Exists: {hook_dir.exists()}")
    if hook_dir.exists():
        json_files = list(hook_dir.rglob("*.json"))
        print(f"  JSON files: {len(json_files)}")
        for f in json_files:
            print(f"    - {f}")
